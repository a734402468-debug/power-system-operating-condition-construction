"""Isolated supplementary certification; does not alter compilation/execution.

Free allocation is a nonbinding permission in both frozen languages. Certify
its omission or fixed-member exclusion only when ALL effective primitive
requirements and available actions match the independent requirements.
This deliberately conservative rule is not a general equivalence prover.
"""
import json
from . import redistribution_constraints_v1 as numeric

VERSION = 'finite-free-permission-v1'
PHASES = {'baseline': ['baseline'], 'final': ['final'],
          'every_accepted_state': ['baseline', 'accepted', 'final']}
PER_OBJECT = {'alpha_bounds', 'qp_ratio', 'voltage_bounds', 'voltage_target', 'fixed_parameter'}


def primitive_conditions(spec, catalog):
    lowered, _ = numeric.lower(spec, catalog)
    # lower() intentionally handles proportional constraints separately.
    rows = lowered['constraints'] + [c for c in spec['constraints'] if c['type'] == 'proportional_change']
    result = set()
    for c in rows:
        groups = [[p] for p in c['objects']] if c['type'] in PER_OBJECT else [sorted(c['objects'])]
        for objects in groups:
            for phase in PHASES[c['timing']]:
                result.add(json.dumps(dict(type=c['type'], objects=objects, values=c['values'],
                    unit=c['unit'], tolerance=c['tolerance'], phase=phase), sort_keys=True, ensure_ascii=True))
    return result


def certify(parsed, task, snapshot, old_score):
    out = {'version': VERSION, 'old_score_retained': old_score.get('status'), 'qualified': False,
           'status': 'insufficient_evidence', 'output_changed': False, 'checks': {}}
    if not parsed.get('schema_valid'):
        out['reason'] = 'contract invalid'; return out
    cat = task['catalog']; submitted = parsed['expansion']['numeric_specification']; gold = task['golden']
    allowed = set(task['allowed_modifiable_paths'])
    try:
        candidate_rows = primitive_conditions(submitted, cat)
        original_rows = primitive_conditions(gold, cat)
        plan = parsed['plan']
        selected = {cat[a]['path'] for a in plan['selected']}
        all_loads = {v['path']: v for v in cat.values() if v['kind'] == 'load'}
        fixed = set(all_loads) - allowed
        fixed_checks = []
        for path in sorted(fixed):
            for field, unit in [('plini', 'MW'), ('qlini', 'Mvar')]:
                for phase in ('baseline', 'accepted', 'final'):
                    wanted = dict(type='fixed_parameter', objects=[path],
                        values={'field': field, 'value': all_loads[path]['base_inputs'][field]},
                        unit=unit, tolerance=0., phase=phase)
                    # Python numeric equality allows 0 and 0.0, without relaxing tolerance.
                    present = any(json.loads(row) == wanted for row in candidate_rows)
                    fixed_checks.append(dict(path=path, field=field, phase=phase, present=present))
        def rows_equal(a, b):
            aa, bb = [json.loads(x) for x in a], [json.loads(x) for x in b]
            return all(x in bb for x in aa) and all(x in aa for x in bb)
        out['checks'] = {
            'same_full_primitive_requirements_both_directions': rows_equal(candidate_rows, original_rows),
            'same_declared_adjustable_set': set(submitted['variables']['objects']) == set(gold['variables']['objects']) == allowed,
            'same_selected_action_space': plan['operation'] == 'solve' and selected == allowed,
            'same_mapping': submitted['variables']['mapping'] == gold['variables']['mapping'],
            'same_preservation_conditions': submitted['preserve'] == gold['preserve'],
            'same_baseline_snapshot': parsed['expansion']['baseline_snapshot_sha256'] == snapshot['snapshot_sha256'],
            'state_reference_review_passed': old_score.get('reference_errors') == [],
            'previous_numeric_semantics_certified': old_score.get('finite_evaluation', {}).get('expression_correct') is True,
            'all_nonadjustable_PQ_explicitly_fixed_at_baseline_each_phase': all(x['present'] for x in fixed_checks)}
        out.update(fixed_member_evidence=fixed_checks, statistical_sets_unchanged=True,
            missing_primitive_conditions=[json.loads(x) for x in original_rows if json.loads(x) not in [json.loads(y) for y in candidate_rows]],
            additional_primitive_conditions=[json.loads(x) for x in candidate_rows if json.loads(x) not in [json.loads(y) for y in original_rows]],
            evidence_basis='Frozen free declaration adds no equation. Complete bidirectional primitive identity and identical selectable variables establish the same feasible action set; fixed contributions remain in sums.',
            qualified=all(out['checks'].values()))
        out['status'] = 'equivalent_under_frozen_finite_semantics' if out['qualified'] else 'not_certified'
    except (KeyError, ValueError, TypeError) as exc:
        out['reason'] = type(exc).__name__ + ': ' + str(exc)
    return out
