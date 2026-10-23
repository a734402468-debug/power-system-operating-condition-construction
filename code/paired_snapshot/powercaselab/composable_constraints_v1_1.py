# -*- coding: utf-8 -*-
"""Composable, finite alpha/PQ constraints. Standard library; Python 3.4 compatible.

The verified parameterization is baseline P/Q times one absolute load alpha.
It is an actuator definition, not an inferred/default requirement. Constraints
are never added by the builder. Hardware permissions remain outside the spec.
"""
import copy
import itertools
import json
import math
from . import t2p
from .h3_numeric import signature, pf_unit

VERSION = 'composable-constraints-v1'
# Wire schema remains unchanged so the four frozen compiler requests are exact.
IMPLEMENTATION_VERSION = 'composable-constraints-v1.1'
PRESERVE = ['other_load_inputs', 'topology', 'control_settings', 'flow_settings']
TYPES = {
    'alpha_bounds': ('load', 'dimensionless', ['lower', 'upper']),
    'fixed_parameter': ('load', None, ['field', 'value']),
    'active_power_sum': ('load', 'MW', ['value']),
    'qp_ratio': ('load', 'Mvar', ['ratio']),
    'voltage_target': ('voltage', 'pu', ['value']),
    'voltage_bounds': ('voltage', 'pu', ['lower', 'upper'])}


def resolve_actuator_bounds(catalog, bounds=None):
    """Trusted task permission, separate from submitted requirement bounds.

    Absent task data keeps the historical experiment domain exactly unchanged.
    An explicit domain must cover the whole registered load set, including
    nonvariables, and contain the baseline alpha=1. No inferred enlargement.
    """
    paths = set(v['path'] for v in catalog.values() if v['kind'] == 'load')
    if bounds is None:
        return {p: {'lower': .99, 'upper': 1.02} for p in paths}
    if not isinstance(bounds, dict) or set(bounds) != paths:
        raise ValueError('Task actuator bounds must cover exactly the registered load paths')
    for p, row in bounds.items():
        if (not isinstance(row, dict) or set(row) != set(('lower', 'upper'))
                or not all(t2p.finite(row[k]) for k in ('lower', 'upper'))
                or not 0 < row['lower'] <= 1.0 <= row['upper']):
            raise ValueError('Invalid task actuator bounds: ' + p)
    return copy.deepcopy(bounds)


def grammar():
    # Descriptions, not an instance containing answers or default clauses.
    return {
        'root_required_only': ['schema_version', 'variables', 'constraints', 'preserve'],
        'schema_version': VERSION,
        'variables': {'required_only': ['objects', 'mapping'],
                      'objects': 'unique nonempty array of allowed load short IDs',
                      'mapping': 'ONE string: baseline_PQ_times_absolute_alpha'},
        'constraints': {'container': 'array; no automatic completion',
            'each_required_only': ['id', 'type', 'objects', 'values', 'unit', 'tolerance', 'timing', 'clause'],
            'id': 'unique nonempty string chosen by compiler',
            'type': 'ONE string from the types below, never an option array',
            'objects': 'unique nonempty array of registered IDs of the indicated role',
            'tolerance': 'finite nonnegative number; voltage_target strictly positive',
            'timing': 'ONE string: baseline OR final OR every_accepted_state',
            'clause': 'ONE original requirement clause ID C1..C7; a reference alone proves nothing',
            'types': {k: {'objects_role': v[0], 'unit': v[1] or 'MW for plini; Mvar for qlini',
                          'values_required_only': v[2]} for k, v in TYPES.items()},
            'notes': ['fixed_parameter, qp_ratio and voltage constraints each have exactly one object',
                'fixed_parameter.field is ONE string plini OR qlini',
                'ratio means baseline Q/P; residual Q-ratio*P and tolerance are in Mvar',
                'active_power_sum.value is the input sum in MW; objects need not equal adjustable objects',
                'values are finite numbers except the fixed_parameter field',
                'bounds have lower <= upper; alpha bounds stay inside hardware scope [0.99,1.02]']},
        'preserve': {'required_only': PRESERVE, 'values': 'each is a boolean; express requirement, not a default'},
        'actuator_semantics': 'P=P0*alpha and Q=Q0*alpha; fixed/nonvariable loads keep baseline inputs; no independent PQ actuator'}


def parse(content, catalog, canonical=False, finish_reason=None, actuator_bounds=None):
    out = {'schema_valid': False, 'compiled_specification': None, 'raw_specification': None,
           'identifier_bindings': [], 'errors': [], 'error_category': None, 'output_repaired': False}
    category = 'format'
    if finish_reason == 'length':
        out.update(error_category='truncated', errors=['finish_reason=length'], status='truncated')
        return out
    try:
        permitted_bounds = resolve_actuator_bounds(catalog, actuator_bounds)
        def unique(pairs):
            d = {}
            for k, v in pairs:
                if k in d: raise ValueError('Duplicate JSON key: ' + k)
                d[k] = v
            return d
        x = json.loads(content, object_pairs_hook=unique,
                       parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
        out['raw_specification'] = x
        t2p.exact_fields(x, ['schema_version', 'variables', 'constraints', 'preserve'])
        if x['schema_version'] != VERSION: raise ValueError('Wrong version')
        t2p.exact_fields(x['variables'], ['objects', 'mapping'])
        t2p.exact_fields(x['preserve'], PRESERVE)
        if any(type(x['preserve'][k]) is not bool for k in PRESERVE): raise ValueError('Preserve booleans required')
        category = 'allowed_operation'
        if x['variables']['mapping'] != 'baseline_PQ_times_absolute_alpha': raise ValueError('Unsupported actuator mapping')
        paths = [v['path'] for v in catalog.values()]
        if len(paths) != len(set(paths)): raise ValueError('Ambiguous directory')
        registry = {v['path'] if canonical else a: a for a, v in catalog.items()}
        y = copy.deepcopy(x)
        def bind(objects, kind):
            if not isinstance(objects, list) or not objects: raise ValueError('Nonempty object array required')
            found = []
            for raw in objects:
                if not isinstance(raw, str) or raw not in registry: raise ValueError('Unknown/unauthorized ID: ' + str(raw))
                a = registry[raw]
                if catalog[a]['kind'] != kind: raise ValueError('Wrong object role')
                found.append(catalog[a]['path'])
                out['identifier_bindings'].append({'raw': raw, 'alias': a, 'path': catalog[a]['path']})
            if len(found) != len(set(found)): raise ValueError('Repeated object')
            return found
        category = 'object'
        y['variables']['objects'] = bind(x['variables']['objects'], 'load')
        if not isinstance(x['constraints'], list): raise ValueError('Constraint array required')
        ids = set()
        for i, c in enumerate(x['constraints']):
            category = 'format'
            t2p.exact_fields(c, ['id', 'type', 'objects', 'values', 'unit', 'tolerance', 'timing', 'clause'])
            if not isinstance(c['id'], str) or not c['id'].strip() or c['id'] in ids: raise ValueError('Unique constraint ID required')
            ids.add(c['id'])
            category = 'unsupported_constraint_type'
            if not isinstance(c['type'], str) or c['type'] not in TYPES: raise ValueError('Unsupported constraint type')
            kind, unit, fields = TYPES[c['type']]
            category = 'format'
            t2p.exact_fields(c['values'], fields)
            if c['timing'] not in ('baseline', 'final', 'every_accepted_state') or not isinstance(c['timing'], str): raise ValueError('Timing must be one enum string')
            if c['clause'] not in ['C'+str(j) for j in range(1, 8)]: raise ValueError('Unknown original clause reference')
            if not t2p.finite(c['tolerance']) or c['tolerance'] < 0: raise ValueError('Invalid tolerance')
            for k, v in c['values'].items():
                if k != 'field' and not t2p.finite(v): raise ValueError('Finite numeric value required')
            category = 'object'
            y['constraints'][i]['objects'] = bind(c['objects'], kind)
            if c['type'] not in ('alpha_bounds', 'active_power_sum') and len(c['objects']) != 1: raise ValueError('Exactly one object required')
            category = 'unit'
            if c['type'] == 'fixed_parameter':
                if c['values']['field'] not in ('plini', 'qlini'): raise ValueError('Unsupported input field')
                unit = 'MW' if c['values']['field'] == 'plini' else 'Mvar'
            if c['unit'] != unit: raise ValueError('Wrong constraint unit')
            category = 'allowed_operation'
            if 'lower' in fields and c['values']['lower'] > c['values']['upper']: raise ValueError('Reversed bounds')
            if c['type'] == 'alpha_bounds' and any(
                    not permitted_bounds[p]['lower'] <= c['values']['lower'] <= c['values']['upper'] <= permitted_bounds[p]['upper']
                    for p in y['constraints'][i]['objects']):
                raise ValueError('Bounds exceed task actuator permission')
            if c['type'] == 'voltage_target' and c['tolerance'] <= 0: raise ValueError('Positive target tolerance required')
        out.update(schema_valid=True, compiled_specification=y)
    except (ValueError, TypeError, KeyError) as exc:
        out.update(error_category=category, errors=[str(exc)])
    return out


def semantic_check(spec, golden):
    # Multiset of typed meanings; compiler may choose different unique IDs/order.
    # No merging, omitted-clause repair, numeric-value substitution or fuzzy match.
    def norm(x):
        if isinstance(x, dict): return {k: norm(v) for k, v in x.items() if k != 'id'}
        if isinstance(x, list): return sorted([norm(v) for v in x], key=lambda v: json.dumps(v, sort_keys=True))
        return x
    def same(a, b):
        if t2p.finite(a) and t2p.finite(b): return abs(a-b) <= 1e-12*max(1., abs(b))
        if isinstance(a, dict) and isinstance(b, dict): return set(a) == set(b) and all(same(a[k], b[k]) for k in a)
        if isinstance(a, list) and isinstance(b, list): return len(a) == len(b) and all(same(u, v) for u, v in zip(a, b))
        return type(a) == type(b) and a == b
    checks = [{'requirement': k, 'pass': same(norm(spec.get(k)), norm(golden[k])),
               'actual': spec.get(k), 'expected': golden[k]} for k in golden]
    return {'correct': all(c['pass'] for c in checks), 'checks': checks, 'generated_output_not_overwritten': True}


def build_problem(spec, catalog, matrix, current, task):
    checked = parse(json.dumps(spec), catalog, canonical=True,
                    actuator_bounds=task.get('actuator_bounds'))
    if not checked['schema_valid']: raise ValueError('Invalid specification: '+str(checked['errors']))
    paths = sorted(spec['variables']['objects'])
    bases = {v['path']: v['base_inputs'] for v in catalog.values() if v['kind'] == 'load'}
    permitted = set(task['allowed_modifiable_paths'])
    if not set(paths).issubset(permitted): raise ValueError('Variables exceed task write permissions')
    if any(not t2p.finite(b['plini']) or b['plini'] <= 0 for b in bases.values()): raise ValueError('Zero/nonpositive baseline P is outside verified Q/P actuator scope')
    fixed = {p: 1. for p in bases if p not in paths}
    # Exiting a selected combination explicitly returns nonvariables to baseline.
    reset_paths = [p for p in fixed if current['alphas'][p] != 1.0]
    baseline_record = current.get('baseline_record')
    if baseline_record is None: raise ValueError('Explicit baseline record required')
    admission = evaluate(spec, catalog, baseline_record, phase='baseline')
    if not admission['phase_satisfied']: raise ValueError('Declared baseline/accepted-state conditions fail baseline admission')
    binding = matrix['shared_binding']
    for k in ('project_path', 'study_case_path', 'network_path'):
        if binding[k] != task[k]: raise ValueError('Response identity mismatch')
    if (binding['fixed_conditions_sha256'] != signature(task['fixed_conditions']) or
            binding['controls_sha256'] != signature(current['record']['controls']) or not current['record']['valid']):
        raise ValueError('Response fixed/control/valid-state mismatch')
    if not set(bases).issubset(set(matrix['alphas'])): raise ValueError('Response expansion variables missing')
    eq, ineq, centers, rows, consumed = [], [], [], {}, {}
    def relation(c, coefficients, value, tolerance, exact=False):
        a = [coefficients.get(p, 0.) for p in paths]
        fixed_value = math.fsum(coefficients.get(p, 0.)*alpha for p, alpha in fixed.items())
        b = value-fixed_value
        consumed[c['id']]['fixed_contribution'] = fixed_value
        if exact:
            # Same frozen strategy: solve conserved-input centers exactly, then
            # independently evaluate the declared float32 storage tolerance.
            eq.append({'id': c['id'], 'a': a, 'b': b})
        else:
            ineq.extend([{'id': c['id']+' upper', 'a': a, 'b': b+tolerance},
                         {'id': c['id']+' lower', 'a': [-v for v in a], 'b': -b+tolerance}])
    def voltage(p):
        if p in rows: return rows[p]
        matches = [r for r in matrix['rows'].values() if r['path'] == p]
        if len(matches) != 1: raise ValueError('Observation outside verified response matrix')
        source = matches[0]
        slopes = {q: source['responses'][q]['sensitivity_pu_per_alpha'] for q in bases}
        measured = current['record']['result_snapshot']['key_results'][p+'|m:u']
        if pf_unit(measured['unit']) != 'p.u.' or not t2p.finite(measured['value']): raise ValueError('Invalid measured expansion value')
        original = source['voltage_pu']+math.fsum(slopes[q]*(current['alphas'][q]-matrix['alphas'][q]) for q in bases)
        correction = measured['value']-original
        intercept = source['voltage_pu']+correction-math.fsum(slopes[q]*matrix['alphas'][q] for q in bases)+math.fsum(slopes[q]*fixed[q] for q in fixed)
        rows[p] = {'a': [slopes[q] for q in paths], 'intercept': intercept,
                   'fixed_response_contribution_pu': math.fsum(slopes[q]*fixed[q] for q in fixed),
                   'measured_offset_correction_pu': correction, 'slope_expansion_state': matrix['version'],
                   'slope_expansion_alphas': matrix['alphas'], 'current_anchor_alphas': current['alphas']}
        return rows[p]
    ordered_constraints = sorted(spec['constraints'], key=lambda c: json.dumps(
        {k:v for k,v in c.items() if k!='id'}, sort_keys=True, separators=(',',':')))
    for c in ordered_constraints:
        typ, objects, values, tol = c['type'], c['objects'], c['values'], c['tolerance']
        consumed[c['id']] = {'type': typ, 'clause': c['clause'], 'timing': c['timing'], 'objects': objects, 'consumer': 'local_problem_and_actual_feedback'}
        if c['timing'] == 'baseline':
            consumed[c['id']]['consumer'] = 'baseline_admission_only'
            continue
        if typ == 'active_power_sum':
            relation(c, {p: bases[p]['plini'] for p in objects}, values['value'], tol)
            centers.append({'id':c['id']+' center','a':[bases[p]['plini'] if p in objects else 0. for p in paths],
                            'b':values['value']-math.fsum(bases[p]['plini'] for p in objects if p in fixed)})
        elif typ == 'fixed_parameter': relation(c, {objects[0]: bases[objects[0]][values['field']]}, values['value'], tol)
        elif typ == 'qp_ratio':
            p = objects[0]
            relation(c, {p: bases[p]['qlini']-values['ratio']*bases[p]['plini']}, 0., tol)
            consumed[c['id']]['actuator_semantics'] = 'baseline-linked PQ; ratio constraint explicitly consumed, never filled'
        elif typ == 'alpha_bounds':
            for p in objects:
                relation(c, {p: 1.}, (values['lower']+values['upper'])/2., (values['upper']-values['lower'])/2.+tol)
        elif typ in ('voltage_target', 'voltage_bounds'):
            r = voltage(objects[0]); a, offset = r['a'], r['intercept']
            if typ == 'voltage_target':
                lo, hi = values['value']-tol, values['value']+tol
                centers.append({'id': c['id']+' center', 'a': a, 'b': values['value']-offset})
            else: lo, hi = values['lower']-tol, values['upper']+tol
            ineq.extend([{'id': c['id']+' upper', 'a': a, 'b': hi-offset},
                         {'id': c['id']+' lower', 'a': [-s for s in a], 'b': offset-lo}])
        else: raise ValueError('Unsupported constraint type: '+typ)
    return {'version': VERSION, 'paths': paths, 'fixed_alphas': fixed, 'current_alphas': current['alphas'],
            'current_state_version': current['version'], 'reset_to_baseline_paths': reset_paths, 'baseline_admission': admission, 'equalities': eq, 'inequalities': ineq,
            'preferred_target_centers': centers, 'voltage_rows': rows, 'constraint_consumption': consumed,
            'execution_guards': spec['preserve'], 'generated_spec_sha256': signature(spec),
            'current_task_sha256': signature(task), 'historical_response_binding': binding,
            'numeric_policy': 'Rank-aware active-face projection; conserved-input and target centers preferred, declared tolerance bands retained; measured current offset and all exiting-combination responses explicit.'}


def solve(problem):
    """Reuse the v1.1 active-face strategy, without its first-equality assumption."""
    paths = problem['paths']; x0 = [problem['current_alphas'][p] for p in paths]; n = len(paths)
    def dot(a, b): return math.fsum(x*y for x, y in zip(a, b))
    def independent(rows):
        result=[]
        for r in rows:
            norm=math.sqrt(dot(r['a'],r['a']))
            if norm == 0:
                if abs(r['b'])>1e-12:return None
                continue
            a=[v/norm for v in r['a']];b=r['b']/norm
            for pivot,u,v in result:
                factor=a[pivot];a=[x-factor*y for x,y in zip(a,u)];b-=factor*v
            pivot=max(range(n),key=lambda k:abs(a[k]))
            if abs(a[pivot])<1e-12:
                if abs(b)>1e-10:return None
                continue
            divisor=a[pivot];result.append((pivot,[v/divisor for v in a],b/divisor))
        return [{'a':a,'b':b} for _,a,b in result]
    def projection(rows):
        rows=independent(rows)
        if rows is None:return None
        scaled=[]
        for r in rows:
            norm=math.sqrt(dot(r['a'],r['a']));scaled.append(([v/norm for v in r['a']],r['b']/norm))
        m=len(scaled)
        g=[[dot(a,b) for b,_ in scaled]+[v-dot(a,x0)] for a,v in scaled]
        for i in range(m):
            pivot=max(range(i,m),key=lambda j:abs(g[j][i]))
            if abs(g[pivot][i])<1e-12:return None
            g[i],g[pivot]=g[pivot],g[i];divisor=g[i][i];g[i]=[v/divisor for v in g[i]]
            for j in range(m):
                if j!=i:
                    factor=g[j][i];g[j]=[v-factor*w for v,w in zip(g[j],g[i])]
        return [x0[k]+math.fsum(scaled[i][0][k]*g[i][-1] for i in range(m)) for k in range(n)]
    examined, best, phase = 0, None, None
    for preferred in (True, False):
        equal = problem['equalities']+(problem['preferred_target_centers'] if preferred else [])
        # Constant equations don't spend a variable dimension.
        reduced = independent(equal)
        if reduced is None: continue
        rank_count = len(reduced)
        for size in range(n-rank_count+1):
            for active in itertools.combinations(problem['inequalities'], size):
                examined += 1; x = projection(equal+list(active))
                if x is None or any(not t2p.finite(v) for v in x): continue
                if any(abs(dot(r['a'],x)-r['b']) > 1e-10*max(1.,abs(r['b'])) for r in equal): continue
                if any(dot(r['a'],x)-r['b'] > 1e-12*max(1.,abs(r['b'])) for r in problem['inequalities']): continue
                score = (dot([u-v for u,v in zip(x,x0)], [u-v for u,v in zip(x,x0)]), tuple(x))
                if best is None or score < best[0]: best = (score,x,[r['id'] for r in active]); phase = 'exact_centers' if preferred else 'tolerance_bands'
        if best is not None: break
    if best is None: return {'status': 'local_approximation_has_no_feasible_candidate', 'faces_examined': examined, 'global_infeasibility_claim': False}
    x = best[1]; alphas = dict(problem['fixed_alphas']); alphas.update(dict(zip(paths,x)))
    return {'status': 'candidate', 'alphas': alphas, 'adjustable_alphas': dict(zip(paths,x)),
            'predicted_values_pu': {p: r['intercept']+dot(r['a'],x) for p,r in problem['voltage_rows'].items()},
            'equation_residuals': {r['id']: dot(r['a'],x)-r['b'] for r in problem['equalities']},
            'squared_multiplier_change': best[0][0], 'active_constraints': best[2], 'phase': phase,
            'faces_examined': examined, 'problem_sha256': signature(problem), 'is_physical_feasibility_evidence': False}


def voltage_evidence(record, catalog, state_role):
    """Read one physical snapshot; never merge values from constraint rows."""
    valid = bool(record and record.get('valid') and record.get('fixed_conditions_match')
                 and record.get('controls_unchanged'))
    values = {}
    if valid:
        for item in catalog.values():
            if item['kind'] != 'voltage': continue
            measured = record['result_snapshot']['key_results'][item['path']+'|m:u']
            if pf_unit(measured['unit']) != 'p.u.' or not t2p.finite(measured['value']):
                raise ValueError('Invalid voltage evidence')
            values[item['path']] = measured['value']
    return {'state_role': state_role, 'source': 'raw_PF_result_snapshot', 'valid': valid,
            'record_label': None if record is None else record.get('label'),
            'ac_flow_number': None if record is None else record.get('ac_flow_number'),
            'values_pu': values}


def prediction_evidence(catalog, baseline_record, actual_record, predicted_values_pu):
    """Keep baseline, saved numerical prediction and actual state independent."""
    permitted = set(v['path'] for v in catalog.values() if v['kind']=='voltage')
    if not set(predicted_values_pu).issubset(permitted) or not all(t2p.finite(v) for v in predicted_values_pu.values()):
        raise ValueError('Invalid predicted observation or value')
    base = voltage_evidence(baseline_record, catalog, 'original_baseline')
    actual = voltage_evidence(actual_record, catalog, 'actual_candidate')
    return {'implementation_version': IMPLEMENTATION_VERSION, 'baseline_state': base,
            'predicted_state': {'state_role': 'numerical_prediction', 'source': 'saved_pre_execution_candidate',
                                'values_pu': dict(predicted_values_pu)},
            'actual_state': actual,
            'prediction_error_actual_minus_predicted_pu':
                {p: actual['values_pu'][p]-v for p,v in predicted_values_pu.items()} if actual['valid'] else None}


def evaluate(spec, catalog, record, source='actual_PF', phase='final', baseline_record=None):
    if phase not in ('baseline','accepted','final'):raise ValueError('Unknown evaluation phase')
    bases = {v['path']: v['base_inputs'] for v in catalog.values() if v['kind'] == 'load'}
    valid = bool(record.get('valid') and record.get('fixed_conditions_match') and record.get('controls_unchanged'))
    guards = {'valid_AC_identity_settings_controls': valid,
              'other_load_inputs_unchanged': record.get('other_load_inputs_unchanged') is True,
              'requested_context_guards': all(spec['preserve'].values())}
    actual_voltage = voltage_evidence(record, catalog, 'evaluated_actual_state')
    baseline_voltage = voltage_evidence(record if phase=='baseline' else baseline_record, catalog, 'original_baseline')
    feedback, values_pu, residuals = [], actual_voltage['values_pu'], {}
    for c in spec['constraints']:
        row = {'constraint_id': c['id'], 'type': c['type'], 'clause': c['clause'], 'objects': c['objects'],
               'unit': c['unit'], 'timing': c['timing'], 'target_or_range': c['values'], 'tolerance': c['tolerance'],
               'source': source, 'current_value': None, 'error': None, 'margin': None, 'status': 'invalid', 'pass': False}
        evaluation_record = baseline_record if c['timing']=='baseline' and phase!='baseline' else record
        row_valid = bool(evaluation_record and evaluation_record.get('valid') and evaluation_record.get('fixed_conditions_match') and evaluation_record.get('controls_unchanged'))
        row['evaluated_on'] = 'original_baseline' if c['timing']=='baseline' else 'current_state'
        row['applicable'] = c['timing'] in ({'baseline','every_accepted_state'} if phase=='baseline' else {'every_accepted_state'} if phase=='accepted' else {'baseline','every_accepted_state','final'})
        if row_valid:
            typ, p, val, tol = c['type'], c['objects'][0], c['values'], c['tolerance']; inputs = evaluation_record['actual_inputs']
            if typ == 'active_power_sum': actual = math.fsum(inputs[q]['plini'] for q in c['objects']); error = actual-val['value']; margin = tol-abs(error)
            elif typ == 'fixed_parameter': actual = inputs[p][val['field']]; error = actual-val['value']; margin = tol-abs(error)
            elif typ == 'qp_ratio':
                if bases[p]['plini'] <= 0: raise ValueError('Nonpositive baseline P unsupported')
                actual = {'P_MW': inputs[p]['plini'], 'Q_Mvar': inputs[p]['qlini'], 'Q_over_P': inputs[p]['qlini']/inputs[p]['plini'] if inputs[p]['plini'] else None}
                error = inputs[p]['qlini']-val['ratio']*inputs[p]['plini']; margin = tol-abs(error)
            elif typ == 'alpha_bounds':
                actual = {q: inputs[q]['plini']/bases[q]['plini'] for q in c['objects']}
                error = max([val['lower']-a for a in actual.values()]+[a-val['upper'] for a in actual.values()])
                margin = tol-error
            else:
                item = evaluation_record['result_snapshot']['key_results'][p+'|m:u']
                if pf_unit(item['unit']) != 'p.u.' or not t2p.finite(item['value']): raise ValueError('Invalid voltage result')
                actual = item['value']
                if typ == 'voltage_target': error = actual-val['value']; margin = tol-abs(error); residuals[p] = error
                elif typ == 'voltage_bounds': error = max(val['lower']-actual, actual-val['upper']); margin = tol-error
                else: raise ValueError('Unsupported constraint type')
            row.update(current_value=actual, error=error, margin=margin, status='satisfied' if margin >= 0 else 'unmet', **{'pass': margin >= 0})
        feedback.append(row)
    process = all(guards.values()) and all(r['pass'] for r in feedback if r['timing'] == 'every_accepted_state')
    baseline_ok = all(r['pass'] for r in feedback if r['timing']=='baseline')
    phase_ok = all(guards.values()) and all(r['pass'] for r in feedback if r['applicable'])
    return {'valid': valid, 'phase':phase, 'phase_satisfied':phase_ok, 'baseline_conditions':baseline_ok, 'process_conditions': process and baseline_ok, 'all_requirements': all(guards.values()) and all(r['pass'] for r in feedback),
            'checks': feedback, 'context_guards': guards, 'values_pu': values_pu, 'target_residuals_pu': residuals,
            'baseline_values_pu': baseline_voltage['values_pu'],
            'voltage_sources': {'original_baseline': baseline_voltage, 'evaluated_actual_state': actual_voltage},
            'R': max([abs(r['error'])/r['tolerance'] for r in feedback if r['type'] == 'voltage_target'] or [0.]) if valid else None,
            'generated_spec_sha256': signature(spec), 'source': source, 'input_setpoints_only_not_system_balance': True}


def physical_check(task, record, baseline_record=None, phase="final"):
    # Independent gold is used only for acceptance, never for problem replacement.
    return evaluate(task['t2p']['golden'], task['t2p']['catalog'], record, phase=phase, baseline_record=baseline_record)


def select_specification(spec, selected, policy):
    """Bind a device plan, without changing any requirement in the supplied task."""
    if (not isinstance(selected, list) or not selected or len(set(selected)) != len(selected)
            or len(selected) > policy['maximum_selected']
            or not set(selected).issubset(set(policy['eligible_objects']))
            or policy['unselected_inputs'] != 'original_baseline'):
        raise ValueError('Illegal selected combination')
    if not set(policy['eligible_objects']).issubset(set(spec['variables']['objects'])):
        raise ValueError('Task and candidate universe disagree')
    bound = copy.deepcopy(spec)
    bound['variables']['objects'] = sorted(selected)
    return bound


def transition_inputs(catalog, alphas, selected, policy):
    """A whole action includes exact baseline values for objects leaving a plan."""
    loads = {v['path']:v for v in catalog.values() if v['kind']=='load'}
    if set(alphas)!=set(loads) or len(selected)>policy['maximum_selected']:
        raise ValueError('Incomplete coordinated input vector')
    if not set(selected).issubset(set(policy['eligible_objects'])):
        raise ValueError('Unauthorized selection')
    if any(not t2p.finite(a) or not .99<=a<=1.02 for a in alphas.values()):
        raise ValueError('Unsafe multiplier')
    if any(alphas[p]!=1. for p in loads if p not in selected):
        raise ValueError('Exited/unselected device would retain accumulated change')
    return {p:{k:v*alphas[p] for k,v in entry['base_inputs'].items()} for p,entry in loads.items()}


def two_variable_diagnosis(spec, catalog, matrix, problem):
    """Limited elimination certificate for two loads and one conserved input sum.

    This uses the frozen affine response, never claims nonlinear PF infeasibility.
    A conservative outer interval also allows the declared input-sum tolerance.
    """
    paths=problem['paths']
    sums=[c for c in spec['constraints'] if c['type']=='active_power_sum' and c['timing']!='baseline']
    goals=[c for c in spec['constraints'] if c['type']=='voltage_target' and c['timing']!='baseline']
    unknown={'classification':'insufficient_evidence','global_physical_infeasibility_claim':False}
    if len(paths)!=2 or len(sums)!=1 or len(goals)!=1:return unknown
    if not set(paths).issubset(set(sums[0]['objects'])):return unknown
    bases={v['path']:v['base_inputs']['plini'] for v in catalog.values() if v['kind']=='load'}
    bounds={}
    for c in spec['constraints']:
        if c['type']=='alpha_bounds' and c['timing']!='baseline':
            for p in c['objects']:
                old=bounds.get(p,[-float('inf'),float('inf')])
                bounds[p]=[max(old[0],c['values']['lower']-c['tolerance']),min(old[1],c['values']['upper']+c['tolerance'])]
    if any(p not in bounds for p in paths):return unknown
    x,y=paths; px,py=bases[x],bases[y];total=sums[0]['values']['value']
    shift=total-math.fsum(bases[p] for p in sums[0]['objects'])
    lo,hi=bounds[y][0]-1,bounds[y][1]-1
    # px*dx+py*dy=shift; eliminate dx. Intersect both multiplier intervals.
    exact_lo=max(lo,(shift-px*(bounds[x][1]-1))/py)
    exact_hi=min(hi,(shift-px*(bounds[x][0]-1))/py)
    vp=goals[0]['objects'][0];row=problem['voltage_rows'][vp];sx,sy=row['a']
    center=row['intercept']+sx+sy
    slope=sy-sx*py/px;offset=center+sx*shift/px
    exact=[offset+slope*exact_lo,offset+slope*exact_hi]
    # Ignore the x bound and every other constraint to get a SAFE outer set.
    # If even that set misses the target, extra constraints cannot repair it.
    outer=[offset+slope*lo,offset+slope*hi]
    allowance=abs(sx)*sums[0]['tolerance']/px+1e-12
    outer=[min(outer)-allowance,max(outer)+allowance]
    goal=[goals[0]['values']['value']-goals[0]['tolerance'],goals[0]['values']['value']+goals[0]['tolerance']]
    gap=max(goal[0]-outer[1],outer[0]-goal[1],0.)
    return {'classification':'certified_local_linear_infeasible' if gap>0 else 'elimination_does_not_certify_infeasibility',
        'global_physical_infeasibility_claim':False,'eliminated_variable':x,'remaining_variable':y,
        'equation':'delta_x=(sum_shift-P_y*delta_y)/P_x','sum_shift_MW':shift,'P_x':px,'P_y':py,
        'exact_sum_delta_y_interval':[exact_lo,exact_hi],'exact_sum_voltage_interval':sorted(exact),
        'outer_delta_y_interval_ignoring_other_conditions':[lo,hi],'outer_voltage_interval_including_sum_tolerance':outer,
        'sum_tolerance_MW':sums[0]['tolerance'],'voltage_roundoff_allowance_pu':1e-12,
        'effective_slope_pu':slope,'required_voltage_interval':goal,'separation_pu':gap,
        'supporting_constraint_ids':[sums[0]['id'],goals[0]['id']]+[c['id'] for c in spec['constraints'] if c['type']=='alpha_bounds'],
        'scope':'Only this frozen affine model and declared actuator/input domain; actual nonlinear system unknown.'}
