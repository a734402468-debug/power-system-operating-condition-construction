"""Shared, explicit stage-set envelope. No semantic completion or PF calls."""
import copy
import json
from . import state_reference_constraints_v2_1 as F
from . import tool_constraint_builder_v1 as T

VERSION = 'shared-stage-set-v1.1'
STAGES = ['baseline', 'every_accepted_state', 'final']
FIELDS = {
    'stages': {'type': 'array', 'items': 'ONE string: baseline | every_accepted_state | final',
               'min_items': 1, 'unique': True},
    'stage_source': {'type': 'string', 'rule': 'Nonempty exact excerpt from original_requirements supporting the stage choice; provenance only, not semantic certification.'},
}


def grammar(method, require_source=True):
    if method not in ('F', 'T'):
        raise ValueError('method must be F or T')
    g = copy.deepcopy(F.grammar() if method == 'F' else T.grammar())
    g['protocol'] = VERSION + '/' + method
    if method == 'F':
        g['constraint_common'].pop('timing')
        g['constraint_common'].update(copy.deepcopy(FIELDS))
    else:
        for key in ('constraint_call_required_only', 'free_call_required_only'):
            g['calls'][key].remove('timing')
            g['calls'][key] += ['stages', 'stage_source']
        g['calls'].pop('timing')
        g['calls'].update(copy.deepcopy(FIELDS))
    g['shared_stage_semantics'] = {
        'baseline': ['baseline'], 'final': ['final'],
        'every_accepted_state': ['baseline', 'accepted', 'final'],
        'expansion': 'Each constraint/call is copied ONLY for stages explicitly supplied; all physical fields are unchanged. No automatic baseline for final.',
        'same_condition_multiple_stages': 'Use one row with a stages array when objects, bounds and all other conditions are identical.',
        'different_conditions': 'Use separate rows for different objects/bounds/conditions. Never merge their requirements into one range.',
        'source_does_not_prove_semantics': True,
        'old_timing_field': 'Not accepted in this new envelope; use stages and stage_source.',
    }
    if not require_source:
        if method == 'F':
            g['constraint_common'].pop('stage_source', None)
        else:
            for key in ('constraint_call_required_only', 'free_call_required_only'):
                g['calls'][key].remove('stage_source')
            g['calls'].pop('stage_source', None)
        g['optional_stage_source'] = 'Optional provenance string; exact quotations are not required and do not certify semantics.'
        g['shared_stage_semantics']['old_timing_field'] = 'Use the stages array, not timing. stage_source is optional provenance.'
        g['protocol'] += '/optional-provenance-v1'
    return g


def request_packet(original, directory, snapshot, policies, allowed, example,
                   method='F', execution_mode='compile_only'):
    """One public request entry; no credentials, generation, or execution."""
    if execution_mode not in ('compile_only', 'execute'):
        raise ValueError('execution_mode must be compile_only or execute')
    return {
        'original_requirements': original,
        'device_directory': copy.deepcopy(directory),
        'baseline_snapshot': copy.deepcopy(snapshot),
        'precision_policies': copy.deepcopy(policies),
        'authorized_load_ids': list(allowed),
        'output_contract': grammar(method),
        # Example context is data ABOUT the example, never its output wrapper.
        'legal_output_example': copy.deepcopy(example['decision']),
        'example_context': {k: copy.deepcopy(v) for k, v in example.items() if k != 'decision'},
        'execution_settings': {
            'mode': execution_mode,
            'not_an_electrical_requirement': True,
            'plan_intent': 'Use solve when proposing construction even in compile_only mode. Use stop only to request no solve; selected must then be empty.'}}


def prepare_problem(parsed, catalog, matrix, current, task):
    """Model specification and selected plan drive the unchanged numeric core."""
    if not parsed.get('schema_valid'):
        raise ValueError('A contract-valid compilation is required')
    plan = parsed['plan']
    if plan['operation'] == 'stop':
        return {'status': 'stopped', 'operational_specification': None, 'problem': None}
    spec = copy.deepcopy(parsed['expansion']['numeric_specification'])
    spec['variables']['objects'] = [catalog[a]['path'] for a in plan['selected']]
    problem = F.prior.numeric.build_problem(spec, catalog, matrix, current, task)
    return {'status': 'built', 'operational_specification': spec, 'problem': problem}


def parse(method, text, catalog, snapshot, policies, allowed, original, finish_reason=None,
          require_source=True, actuator_bounds=None):
    if method not in ('F', 'T'):
        raise ValueError('method must be F or T')
    fmt, content = F.root_format(text, finish_reason)
    out = {'schema_valid': False, 'raw_contract_valid': False,
           'stage_envelope_version': VERSION, 'format_diagnosis': fmt,
           'diagnostics': [], 'unchecked': [], 'errors': [], 'output_repaired': False}
    def error(path, category, actual, expected):
        out['diagnostics'].append({'field_path': path, 'category': category,
            'actual': actual, 'expected': expected, 'hidden_requirement_answer_provided': False})
    if content is None:
        error('$', fmt['category'], None, 'one JSON object, optional single whole JSON fence')
        return out
    def unique(pairs):
        d = {}
        for k, v in pairs:
            if k in d:
                raise ValueError('duplicate JSON key: ' + k)
            d[k] = v
        return d
    try:
        model = json.loads(content, object_pairs_hook=unique,
                           parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite ' + x)))
        out['model_stage_output'] = copy.deepcopy(model)
        required = list(F.contract()['root']['fields']) if method == 'F' else list(T.ROOT_FIELDS)
        root_instruction = ('Output exactly these root keys: ' + ', '.join(required) +
                            '. No decision wrapper. Keep physical conditions unchanged.')
        if not isinstance(model, dict) or set(model) != set(required):
            error('$', 'root_structure', F.retained.brief(model),
                  {'required_keys': required, 'instruction': root_instruction})
            out['unchecked'].append({'field_path': '$.children', 'status': 'not_checked',
                'reason': 'Root container invalid; no child or semantic claim.'})
            out['errors'] = ['$: root_structure']
            return out
        if method == 'F':
            spec = model['specification']
            if not isinstance(spec, dict) or 'constraints' not in spec:
                error('$.specification', 'container', F.retained.brief(spec),
                      'object with baseline_state, variables, constraints, preserve; constraints is a nonempty array')
                out['unchecked'].append({'field_path': '$.specification.constraints',
                    'status': 'not_checked', 'reason': 'Parent specification unavailable'})
                return out
            rows = spec['constraints']
            prefix = '$.specification.constraints'
        else:
            rows = model['calls']
            prefix = '$.calls'
        if not isinstance(rows, list) or not rows:
            raise ValueError(prefix + ' must be a nonempty array')
        expanded = []; mappings = []; seen = set()
        for i, row in enumerate(rows):
            path = prefix + '[%d]' % i
            if not isinstance(row, dict):
                error(path, 'type', type(row).__name__, 'object'); continue
            identifier = row.get('id')
            if not isinstance(identifier, str) or not identifier or identifier in seen:
                error(path + '.id', 'identifier', identifier, 'unique nonempty string')
            if isinstance(identifier, str):
                seen.add(identifier)
            stages = row.get('stages'); quote = row.get('stage_source')
            if 'timing' in row:
                error(path + '.timing', 'old_field', row['timing'], 'stages array instead of timing')
            if (not isinstance(stages, list) or not stages or
                    any(not isinstance(s, str) or s not in STAGES for s in stages) or
                    len(set(s for s in stages if isinstance(s, str))) != len(stages)):
                error(path + '.stages', 'stage_set', stages, FIELDS['stages']); continue
            if require_source and (not isinstance(quote, str) or not quote.strip() or quote not in original):
                error(path + '.stage_source', 'source_excerpt', quote, FIELDS['stage_source'])
            if not isinstance(identifier, str):
                continue
            for stage in stages:
                item = copy.deepcopy(row)
                item.pop('stages'); item.pop('stage_source', None)
                item['timing'] = stage
                item['id'] = identifier + '__stage_' + stage
                expanded.append(item)
                mappings.append({'model_row': path, 'model_id': identifier,
                    'expanded_id': item['id'], 'explicit_stage': stage, 'stage_source': quote})
        if out['diagnostics']:
            out['errors'] = [d['field_path'] + ': ' + d['category'] for d in out['diagnostics']]
            return out
        legacy = copy.deepcopy(model)
        if method == 'F':
            legacy['specification']['constraints'] = expanded
        else:
            legacy['calls'] = expanded
        parser = F.parse_decision if method == 'F' else T.parse
        kwargs = {'actuator_bounds': actuator_bounds} if method == 'T' else {}
        parsed = parser(json.dumps(legacy, ensure_ascii=False), catalog, snapshot, policies, allowed, **kwargs)
        parsed.update(model_stage_output=copy.deepcopy(model),
            legacy_stage_expansion=legacy, stage_bindings=mappings,
            stage_envelope_version=VERSION, format_diagnosis=fmt,
            raw_contract_valid=bool(parsed['schema_valid'] and fmt['raw_json_format_valid']),
            requested_stages_added_or_repaired=False, stage_source_is_provenance_only=True)
        return parsed
    except (ValueError, KeyError, TypeError) as exc:
        error('$', 'structure', str(exc), 'F specification.constraints or T calls with the shared stage fields')
        return out
