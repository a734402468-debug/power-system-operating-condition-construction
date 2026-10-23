"""Two-observation tools for the fixed H3-v1 task. Standard library, no APIs."""
import hashlib
import itertools
import json
import math
from .physical_feedback import predict_bound_voltage


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
        separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def pf_unit(value, field='m:u'):
    """PF15 returns [unit, field]; support that verified shape explicitly."""
    if isinstance(value, (list, tuple)) and len(value) == 2 and value[1] == field:
        return value[0]
    return value if isinstance(value, str) else None


def constraints(task, record):
    """Independent fixed-spec acceptance, never accepts stale or invalid results."""
    if not record.get('valid') or not record.get('fixed_conditions_match') or not record.get('controls_unchanged'):
        return {'valid': False, 'all_targets': False, 'process_conditions': False, 'R': None}
    values = {}
    for name, spec in task['observations'].items():
        entry = record['result_snapshot']['key_results'][spec['path'] + '|m:u']
        if pf_unit(entry['unit']) != 'p.u.' or not math.isfinite(entry['value']):
            raise ValueError('Invalid observation unit/value')
        values[name] = entry['value']
    residuals = {name: values[name] - spec['target_pu'] for name, spec in task['observations'].items()}
    satisfied = {name: abs(residuals[name]) <= spec['tolerance_pu'] for name, spec in task['observations'].items()}
    keep = task['process_condition']
    margin = values['U101'] - keep['lower_pu']
    alphas = record.get('alphas') or {c['path']: 1.0 for c in task['frozen_candidates']}
    bounds_ok = set(alphas) == {c['path'] for c in task['frozen_candidates']} and all(
        isinstance(a, (float, int)) and not isinstance(a, bool) and math.isfinite(a) and
        task['parameter']['bounds'][0] <= a <= task['parameter']['bounds'][1] for a in alphas.values())
    return {'valid': True, 'values_pu': values, 'residuals_pu': residuals, 'targets_satisfied': satisfied,
            'all_targets': all(satisfied.values()), 'process_conditions': margin >= -keep['boundary_tolerance_pu'] and bounds_ok,
            'U101_nominal_margin_pu': margin, 'bounds_satisfied': bounds_ok,
            'R': max(abs(residuals[k]) / task['observations'][k]['tolerance_pu'] for k in values)}


def bounded_amplitudes(matrix, current, selected, goals, bounds):
    """Enumerate box faces; minimum least-squares voltage residual, then motion.

    Free rank-two variables use A^T(AA^T)^-1 b (minimum movement from
    current); rank-one variables use the nonzero row projection. No PF calls.
    All permitted subsets, including the three-device group, use this tool.
    """
    selected = sorted(selected)
    if not selected or len(set(selected)) != len(selected) or any(p not in current for p in selected):
        raise ValueError('Invalid selected load subset')
    if set(current) != set(matrix['alphas']) or any(not bounds[0] <= a <= bounds[1] for a in current.values()):
        raise ValueError('Current vector/bounds mismatch')
    names = sorted(goals)
    if len(names) != 2:
        raise ValueError('H3 tool requires exactly two observations')
    rows = matrix['rows']
    best = None
    tried = 0
    for face in itertools.product(('free', 'low', 'high'), repeat=len(selected)):
        tried += 1
        proposal = dict(current)
        free = []
        for p, mode in zip(selected, face):
            if mode == 'free':
                free.append(p)
            else:
                proposal[p] = bounds[0 if mode == 'low' else 1]
        b = [goals[n] - rows[n]['voltage_pu'] - math.fsum(
            rows[n]['responses'][p]['sensitivity_pu_per_alpha'] * (proposal[p] - matrix['alphas'][p])
            for p in sorted(proposal)) for n in names]
        a = [[rows[n]['responses'][p]['sensitivity_pu_per_alpha'] for p in free] for n in names]
        if free:
            g00 = math.fsum(v*v for v in a[0]); g11 = math.fsum(v*v for v in a[1])
            g01 = math.fsum(x*y for x, y in zip(*a)); det = g00*g11-g01*g01
            if det > 1e-14 * max(g00*g11, 1e-30):
                y0, y1 = (g11*b[0]-g01*b[1])/det, (g00*b[1]-g01*b[0])/det
                steps = [x*y0+y*y1 for x, y in zip(*a)]
            elif max(g00, g11) > 0:
                row = a[0] if g00 >= g11 else a[1]
                norm = max(g00, g11)
                other = a[1] if g00 >= g11 else a[0]
                ratio = math.fsum(x*y for x, y in zip(row, other)) / norm
                primary, secondary = (b[0], b[1]) if g00 >= g11 else (b[1], b[0])
                scalar = (primary + ratio*secondary) / (1+ratio*ratio)
                steps = [x*scalar/norm for x in row]
            else:
                steps = [0.0]*len(free)
            for p, step in zip(free, steps):
                proposal[p] += step
        if any(not math.isfinite(v) or not bounds[0] <= v <= bounds[1] for v in proposal.values()):
            continue
        predictions = {n: rows[n]['voltage_pu'] + math.fsum(rows[n]['responses'][p]['sensitivity_pu_per_alpha'] *
            (proposal[p]-matrix['alphas'][p]) for p in sorted(proposal)) for n in names}
        score = math.fsum((predictions[n]-goals[n])**2 for n in names)
        motion = math.fsum((proposal[p]-current[p])**2 for p in selected)
        candidate = (score, motion, tuple(proposal[p] for p in sorted(proposal)))
        # Residual ties within 1e-24 pu^2 prefer smaller current-state movement.
        if best is None or score < best[0]-1e-24 or (abs(score-best[0]) <= 1e-24 and candidate[1:] < best[1:3]):
            best = (score, motion, candidate[2], proposal, predictions)
    if best is None:
        raise ValueError('No bounded numerical candidate')
    return {'alphas': best[3], 'predicted_values_pu': best[4], 'squared_residual_pu2': best[0],
            'faces_examined': tried, 'policy': 'Bounded two-row least squares; residual ties 1e-24 pu^2 then minimum movement, then path order',
            'is_feasibility_evidence': False}


def forecast(matrix, current_state, proposed, action_id):
    """Reuse strict P2 binding at the explicitly recorded expansion point.

    Do NOT retag old responses as current. Absolute affine V(expansion, to)
    is returned; its difference from actual current V is the step prediction.
    """
    current = current_state['alphas']
    if set(current) != set(proposed) or set(current) != set(matrix['alphas']):
        raise ValueError('Incomplete action vector')
    for k in ('project_path', 'study_case_path', 'network_path', 'fixed_conditions_sha256', 'controls_sha256'):
        if matrix['shared_binding'][k] != current_state['shared_binding'][k]:
            raise ValueError('Response context/control applicability mismatch')
    result = {'prediction_source': 'deterministic_response_tool', 'method_version': 'H3-v1-deterministic-prediction',
              'action_id': action_id, 'current_state_version': current_state['version'],
              'alpha_from': current, 'alpha_to': proposed,
              'delta_alpha_from_current': {p: proposed[p]-current[p] for p in current},
              'expansion_point_state_version': matrix['version'], 'expansion_point_alphas': matrix['alphas'],
              'delta_alpha_from_expansion': {p: proposed[p]-matrix['alphas'][p] for p in current}, 'observations': {}}
    for name, row in matrix['rows'].items():
        binding = dict(matrix['shared_binding'], observation_path=row['path'])
        state = {'binding': binding, 'valid': True, 'voltage_unit': 'pu', 'voltage_pu': row['voltage_pu'],
                 'alphas': matrix['alphas'], 'bounds': matrix['bounds']}
        action = {'binding': binding, 'action_id': action_id, 'alpha_from': matrix['alphas'], 'alpha_to': proposed,
                  'delta_alpha': {p: proposed[p]-matrix['alphas'][p] for p in current}}
        changed = {p: row['responses'][p] for p in current if proposed[p] != matrix['alphas'][p]}
        prediction = predict_bound_voltage(state, action, changed)
        prediction['delta_from_actual_current_pu'] = prediction['V_pred_pu'] - current_state['values_pu'][name]
        prediction['expansion_prediction_error_at_current_pu'] = (row['voltage_pu'] + math.fsum(
            row['responses'][p]['sensitivity_pu_per_alpha']*(current[p]-matrix['alphas'][p]) for p in current)
            - current_state['values_pu'][name])
        result['observations'][name] = prediction
    result['action_sha256'] = signature(result)
    return result
