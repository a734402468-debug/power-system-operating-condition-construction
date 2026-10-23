"""Finite public clause-linked revision, without a hidden correct specification.

The wire contract and solver are retained. This module adds only public diagnostic
linking, an auditable edit boundary, and an isolated allocation-aware score.
"""
import copy
import json
import re
from . import state_reference_constraints_v2_1 as wire

VERSION = 'clause-linked-revision-v1'
numeric = wire.prior.numeric


def canonical(value):
    if isinstance(value, dict):
        return {k: canonical(v) for k, v in value.items() if k != 'id'}
    if isinstance(value, list):
        vals = [canonical(v) for v in value]
        # Contract arrays are unordered object sets, expressions or constraints.
        return sorted(vals, key=lambda v: json.dumps(v, sort_keys=True))
    return value


def clause_groups(raw):
    spec = raw.get('specification', {}) if isinstance(raw, dict) else {}
    rows = spec.get('constraints', []) if isinstance(spec, dict) else []
    result = {}
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict):
                result.setdefault(row.get('clause', '<unbound>'), []).append(canonical(row))
    return {k: canonical(v) for k, v in result.items()}


def revision_delta(before, after):
    a, b = clause_groups(before), clause_groups(after)
    changed = [c for c in sorted(set(a) | set(b)) if a.get(c) != b.get(c)]
    sa = before.get('specification', {}) if isinstance(before, dict) else {}
    sb = after.get('specification', {}) if isinstance(after, dict) else {}
    roots = [k for k in ('baseline_state', 'variables', 'preserve')
             if not isinstance(sa, dict) or not isinstance(sb, dict)
             or canonical(sa.get(k)) != canonical(sb.get(k))]
    return {'changed_clause_ids': changed, 'changed_root_fields': roots,
            'plan_changed': canonical(before.get('plan')) != canonical(after.get('plan')),
            'before_sha256': numeric.signature(before), 'after_sha256': numeric.signature(after),
            'semantic_representation_changed': bool(changed or roots),
            'cosmetic_ID_or_order_changes_not_counted': True,
            'human_specification_used': False}


def linked_diagnosis(parsed, tool_feedback, original_clauses, original_sha256):
    """Only model output, public contract, own tool feedback and supplied clauses.

    No independent-score argument is accepted. Unknown causes stay unlocalized.
    """
    raw = parsed.get('raw_decision') or {}
    spec = raw.get('specification', {}) if isinstance(raw, dict) else {}
    rows = spec.get('constraints', []) if isinstance(spec, dict) else []
    valid_rows = [r for r in rows if isinstance(r, dict)] if isinstance(rows, list) else []
    by_id = {r.get('id'): r for r in valid_rows}
    associations, editable_clauses, editable_roots = [], set(), set()
    rebuild = not isinstance(spec, dict) or not isinstance(rows, list) or not raw

    def link(reason, row=None, path=None, constraint_id=None):
        clause = row.get('clause') if row else None
        if clause in [c['id'] for c in original_clauses]:
            editable_clauses.add(clause)
        associations.append({'field_path': path, 'constraint_id': constraint_id,
            'declared_source_clause': clause, 'objects': (row or {}).get('objects'),
            'source': (row or {}).get('source'), 'destination': (row or {}).get('destination'),
            'reference_state': (row or {}).get('state', spec.get('baseline_state') if isinstance(spec, dict) else None),
            'timing': (row or {}).get('timing'), 'public_evidence': reason,
            'association_is_not_semantic_correctness': True})

    for d in parsed.get('diagnostics', []):
        path = d.get('field_path', '')
        m = re.search(r'constraints\[(\d+)\]', path)
        if m and isinstance(rows, list) and int(m.group(1)) < len(rows):
            row = rows[int(m.group(1))]
            link(d, row if isinstance(row, dict) else None, path, (row or {}).get('id') if isinstance(row, dict) else None)
            if not isinstance(row, dict) or row.get('clause') not in [c['id'] for c in original_clauses]:
                rebuild = True  # A structurally unbound row has no reliable clause lock.
        else:
            link(d, path=path)
            if 'variables' in path:
                editable_roots.add('variables'); editable_clauses.add('C5')
            elif 'preserve' in path:
                editable_roots.add('preserve'); editable_clauses.add('C7')
            elif 'baseline_state' in path:
                editable_roots.add('baseline_state')
            elif path in ('$', '$.specification', 'specification') or not m:
                rebuild = True

    bindings = (parsed.get('expansion') or {}).get('expression_bindings', [])
    expanded_to_original = {cid: b['constraint_id'] for b in bindings for cid in b['expanded_constraint_ids']}
    for r in tool_feedback.get('own_constraint_rows', []):
        if r.get('applicable', True) and r.get('status') != 'satisfied':
            cid = expanded_to_original.get(r.get('constraint_id'), r.get('constraint_id'))
            link(r, by_id.get(cid), constraint_id=cid)
    declared = set(clause_groups(raw))
    missing_links = [c['id'] for c in original_clauses if c['id'] not in declared and c['id'] != 'C7']
    # This is a public citation coverage check, not a semantic missing-answer hint.
    for cid in missing_links:
        editable_clauses.add(cid)
        associations.append({'declared_source_clause': cid,
            'public_evidence': 'No submitted constraint cites this already supplied original clause.',
            'association_is_not_semantic_correctness': True})
    if tool_feedback.get('kind') in ('problem_build_failure', 'no_local_candidate', 'physical_feedback'):
        # A finite solver result cannot localize blame to one requirement.
        # Planning changes are allowed; requirement edits require an original-text reason.
        if not editable_clauses:
            editable_clauses.update(declared - {'<unbound>'})
            associations.append({'public_evidence': 'Problem-level diagnosis is not localized. Re-read the unchanged text; no constraint is identified as wrong.',
                'association_is_not_semantic_correctness': True})
    return {'version': VERSION, 'original_requirements_sha256': original_sha256,
        'associations': associations, 'missing_citation_ids': missing_links,
        'allowed_revision': {'constraint_clause_ids': sorted(editable_clauses),
            'root_fields': sorted(editable_roots), 'plan': True,
            'whole_contract_rebuild_allowed': rebuild},
        'preserved_original_clause_ids': [c['id'] for c in original_clauses],
        'instruction': 'Keep the original text/version unchanged. Correct only from that text, public contract and own feedback. A clause citation does not prove correctness. Return the complete specification and separate plan; explain the targeted change briefly in plan.reason. Unaffected declared clauses must remain unchanged unless the diagnostic explicitly permits contract reconstruction.',
        'independent_answers_or_differences_supplied': False}


def verify_revision(before, after, diagnosis):
    delta = revision_delta(before, after)
    allowed = diagnosis['allowed_revision']
    unrelated = [] if allowed['whole_contract_rebuild_allowed'] else [
        c for c in delta['changed_clause_ids'] if c not in allowed['constraint_clause_ids']]
    roots = [] if allowed['whole_contract_rebuild_allowed'] else [
        k for k in delta['changed_root_fields'] if k not in allowed['root_fields']]
    return dict(delta, allowed_revision=allowed, unrelated_clause_changes=unrelated,
                unauthorized_root_changes=roots, revision_boundary_pass=not unrelated and not roots,
                original_requirement_text_changed=False, changed_output_not_assumed_correct=True)


def independent_score(parsed, task, state):
    """Isolated generic score for any supported allocation/scope combination.

    The old admission scorer assumed all six loads were free; it is not used for
    this new proportional/subset batch. Neither this result nor the gold task is
    an input to linking/correction.
    """
    result = {'qualified': False, 'status': 'not_checked_contract_failure',
              'independent_only': True, 'runtime_repair': False, 'numerical_search_calls': 0}
    if not parsed.get('schema_valid'):
        return result
    spec = parsed['expansion']['numeric_specification']
    cat = task['catalog']
    try:
        problem = numeric.build_problem(spec, cat, task['response_matrix'], state, task)
        gp = numeric.build_problem(task['golden'], cat, task['response_matrix'], state, task)
        finite = numeric.semantic_evaluation(spec, task['golden'], cat, problem, gp, task)
        expression = parsed['generated_expression']
        expected_free = set(a for r in task['allocation_requirements'] if r['mode'] == 'free' for a in r['objects'])
        actual_free = set(a for c in expression['constraints'] if c['type'] == 'distribution' and c['timing'] == 'final' for a in c['objects'])
        allocation = actual_free == expected_free
        reference_errors = []
        def leaves(e):
            if e['op'] in ('baseline_sum', 'baseline_value'): return [e]
            if e['op'] == 'scale': return leaves(e['base'])
            if e['op'] == 'minimum': return [x for i in e['items'] for x in leaves(i)]
            return []
        for c in expression['constraints']:
            if c['type'] == 'input_sum':
                for leaf in leaves(c['target']):
                    if set(c['objects']) != set(leaf.get('objects', [leaf.get('object')])) or leaf['quantity'] != 'plini':
                        reference_errors.append({'id': c['id'], 'reason': 'different sum reference set or quantity', 'reference': leaf})
        result.update(finite_evaluation=finite, distribution_correct=allocation,
            expected_free_objects=sorted(expected_free), submitted_free_objects=sorted(actual_free), reference_errors=reference_errors)
        result['qualified'] = finite['expression_correct'] and allocation and not reference_errors
        result['status'] = 'qualified_within_finite_rules' if result['qualified'] else 'missing_conflicting_stronger_or_unproven'
    except (ValueError, TypeError, KeyError) as exc:
        result.update(status='undecided_build_or_baseline_condition', error_type=type(exc).__name__, error=str(exc))
    return result
