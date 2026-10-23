"""Limited response prediction and action selection; no PF or LLM calls."""
import hashlib
import json
import math


def predict_bound_voltage(state, action, responses):
    """H3-v1 pure numerical check/prediction, not an executor or LLM repair.

    Bind an absolute-alpha vector and measured responses to the same checked
    state. A caller must independently verify the supplied binding/provenance;
    matching labels do not establish physical applicability by themselves.
    The original select_action policy and archived P0/P1 protocol stay intact.
    """
    def finite(value):
        return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)

    required = {'task_spec_sha256', 'state_version', 'project_path', 'study_case_path',
                'network_path', 'observation_path', 'inputs_sha256',
                'fixed_conditions_sha256', 'controls_sha256'}
    binding = state.get('binding', {})
    if set(binding) != required or not all(isinstance(v, str) and v for v in binding.values()):
        raise ValueError('Incomplete state/identity/condition binding')
    if any(len(binding[k]) != 64 or any(c not in '0123456789abcdef' for c in binding[k])
           for k in required if k.endswith('_sha256')):
        raise ValueError('Invalid binding digest')
    if state.get('valid') is not True or state.get('voltage_unit') != 'pu' or not finite(state.get('voltage_pu')):
        raise ValueError('Require an effective finite pu baseline')
    if action.get('binding') != binding or not isinstance(action.get('action_id'), str) or not action['action_id']:
        raise ValueError('Action does not bind to the current state')
    alpha_from, alpha_to = action.get('alpha_from', {}), action.get('alpha_to', {})
    delta_alpha = action.get('delta_alpha', {})
    current, bounds = state.get('alphas', {}), state.get('bounds', {})
    if not current or not all(set(v) == set(current) for v in (alpha_from, alpha_to, delta_alpha, bounds)):
        raise ValueError('Incomplete or unexpected full-path alpha vector')
    if not all(finite(v) for v in current.values()):
        raise ValueError('Nonfinite or nonnumeric current alpha state')
    if alpha_from != current:
        raise ValueError('Action origin differs from current nominal alpha state')
    changed = []
    for path in sorted(current):
        if not isinstance(path, str) or not path.startswith(binding['network_path'] + '\\') or not path.endswith('.ElmLod'):
            raise ValueError('Action load is outside the bound network')
        limit = bounds[path]
        if not isinstance(limit, (list, tuple)) or len(limit) != 2 or not all(finite(x) for x in limit) or limit[0] > limit[1]:
            raise ValueError('Invalid fixed alpha bounds')
        if not all(finite(v[path]) for v in (alpha_from, alpha_to, delta_alpha)):
            raise ValueError('Nonfinite or nonnumeric alpha')
        if not all(limit[0] <= v[path] <= limit[1] for v in (alpha_from, alpha_to)):
            raise ValueError('Alpha outside the fixed bounds')
        actual_delta = alpha_to[path] - alpha_from[path]
        if abs(delta_alpha[path] - actual_delta) > 1e-15:
            raise ValueError('delta_alpha does not equal alpha_to minus alpha_from')
        if actual_delta != 0:
            changed.append(path)
    if set(responses) != set(changed):
        raise ValueError('Require exactly one bound response for each changed load')
    contributions, origins = {}, {}
    for path in changed:
        response = responses[path]
        if (response.get('valid') is not True or response.get('binding') != binding or
                response.get('load_path') != path or response.get('unit') != 'pu/alpha' or
                not isinstance(response.get('response_id'), str) or not response['response_id']):
            raise ValueError('Response state/object/unit/provenance mismatch')
        fields = ('baseline_voltage_pu', 'probe_voltage_pu', 'baseline_alpha', 'probe_alpha',
                  'probe_delta_alpha', 'sensitivity_pu_per_alpha')
        if not all(finite(response.get(k)) for k in fields):
            raise ValueError('Missing finite measured response values')
        step = response['probe_delta_alpha']
        if (response['baseline_voltage_pu'] != state['voltage_pu'] or
                response['baseline_alpha'] != current[path] or step == 0 or
                abs(step - (response['probe_alpha'] - response['baseline_alpha'])) > 1e-15):
            raise ValueError('Historical measurement origin or step mismatch')
        measured = (response['probe_voltage_pu'] - response['baseline_voltage_pu']) / step
        if abs(measured - response['sensitivity_pu_per_alpha']) > 1e-12:
            raise ValueError('Sensitivity does not agree with its recorded measurement')
        # Same P2 computation: S * action increment, never the historical probe step.
        contributions[path] = response['sensitivity_pu_per_alpha'] * (alpha_to[path] - alpha_from[path])
        origins[path] = response['response_id']
    delta = math.fsum(contributions.values())
    predicted = state['voltage_pu'] + delta
    if not finite(delta) or not finite(predicted):
        raise ValueError('Nonfinite numerical prediction')
    return {'method_version': 'H3-v1-deterministic-prediction', 'prediction_source': 'deterministic_response_tool',
            'binding': dict(binding), 'action_id': action['action_id'],
            'action_sha256': hashlib.sha256(json.dumps(action, sort_keys=True, ensure_ascii=False,
                separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest(),
            'alpha_from': dict(alpha_from), 'alpha_to': dict(alpha_to),
            'delta_alpha': {p: alpha_to[p] - alpha_from[p] for p in sorted(current)},
            'response_ids': origins, 'component_delta_V_pu': contributions,
            'delta_V_pu': delta, 'V_pred_pu': predicted,
            'direction': 'increase' if delta > 0 else 'decrease' if delta < 0 else 'unchanged',
            'assumption': 'Local linear response; coordinated sums are unverified approximations, not simulated feasibility',
            'is_simulation_result': False, 'replaces_llm_prediction': False}


def select_action(task, baseline, responses, candidates):
    target = task['target']['voltage_pu']
    residual = baseline['target_voltage_pu'] - target
    lower, upper = task['parameter']['bounds']
    step = task['feedback']['probe_step']
    minimum_delta = task['feedback']['minimum_voltage_response_pu']
    scores = []
    for candidate, response in zip(candidates, responses):
        path = candidate['path']
        row = {'path': path, 'usable': False, 'reason': None, 'sensitivity_pu_per_alpha': None}
        scores.append(row)
        if (not baseline.get('valid') or not response.get('valid')
                or not response.get('controls_unchanged') or not response.get('fixed_conditions_match')):
            row['reason'] = 'Invalid baseline/flow or unhandled control/fixed-condition change'
            continue
        expected = {c['path']: 1.0 + step if c['path'] == path else 1.0 for c in candidates}
        if response.get('alphas') != expected:
            row['reason'] = 'Response is not an isolated probe from the same baseline'
            continue
        voltage = response.get('target_voltage_pu')
        if not isinstance(voltage, (float, int)) or not math.isfinite(voltage):
            row['reason'] = 'Missing/nonfinite voltage'
            continue
        delta = voltage - baseline['target_voltage_pu']
        row['measured_delta_voltage_pu'] = delta
        row['sensitivity_pu_per_alpha'] = delta / step
        if abs(delta) < minimum_delta:
            row['reason'] = 'Response below predeclared minimum voltage change'
            continue
        sensitivity = row['sensitivity_pu_per_alpha']
        unconstrained = 1.0 - residual / sensitivity
        alpha = min(upper, max(lower, unconstrained))
        predicted_delta = sensitivity * (alpha - 1.0)
        predicted_residual = residual + predicted_delta
        reduction = abs(residual) - abs(predicted_residual)
        row.update(unconstrained_alpha=unconstrained, alpha=alpha,
                   bound_clipped=alpha != unconstrained, direction='increase' if alpha > 1 else 'decrease' if alpha < 1 else 'none',
                   predicted_voltage_pu=baseline['target_voltage_pu'] + predicted_delta,
                   predicted_delta_voltage_pu=predicted_delta,
                   predicted_residual_pu=predicted_residual,
                   score_predicted_absolute_residual_reduction_pu=reduction,
                   usable=reduction > task['feedback']['score_tie_tolerance_pu'],
                   reason='Finite isolated response and bounded predicted improvement' if reduction > task['feedback']['score_tie_tolerance_pu'] else 'No predicted improvement within bounds')
    usable = [x for x in scores if x['usable']]
    selected = None
    if usable:
        best = max(x['score_predicted_absolute_residual_reduction_pu'] for x in usable)
        tied = [x for x in usable if best-x['score_predicted_absolute_residual_reduction_pu'] <= task['feedback']['score_tie_tolerance_pu']]
        selected = min(tied, key=lambda x: (abs(x['alpha']-1), x['path']))
    return {'baseline_residual_pu': residual, 'candidates': scores, 'selected': selected,
            'selection_reason': 'Maximum predicted absolute residual reduction; ties within 1e-12 pu use smaller |alpha-1|, then full path' if selected else 'No usable improving candidate; no replacement, expansion or extra search',
            'one_round_only': True, 'global_feasibility_claim': False}
