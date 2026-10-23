"""Lossless root-format diagnosis only; retained v2 contract/semantics/expansion."""
import copy
import hashlib
import json
import re
from . import state_reference_constraints_v2 as retained

REVISION = 'state-reference-root-diagnostics-v2.1'
VERSION = retained.VERSION
INTERNAL_VERSION = retained.INTERNAL_VERSION
prior = retained.prior
contract = retained.contract
grammar = retained.grammar
fictional_example = retained.fictional_example
independent_score = retained.independent_score


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def root_format(text, finish_reason=None):
    out = {'raw_text_sha256': sha(text) if isinstance(text, str) else None,
           'raw_json_format_valid': False, 'extraction_applied': False,
           'extraction_rule': 'single whole-answer JSON fence plus outer whitespace only',
           'diagnostic_revision': REVISION, 'content_repaired': False}
    if finish_reason == 'length':
        out['category'] = 'truncated'
        return out, None
    if not isinstance(text, str):
        out['category'] = 'non_string_content'
        return out, None
    try:
        json.loads(text)
        out.update(raw_json_format_valid=True, category='plain_json')
        return out, text
    except ValueError:
        pass
    match = re.fullmatch(r'\s*```json[ \t]*\r?\n(.*?)\r?\n```\s*', text, re.DOTALL)
    if match and text.count('```') == 2:
        inner = match.group(1)
        out.update(category='whole_json_fence', extraction_applied=True,
                   extracted_text_sha256=sha(inner))
        return out, inner
    stripped = text.strip()
    if '```' in stripped:
        out['category'] = 'additional_text_or_multiple_fences'
    else:
        try:
            _, end = json.JSONDecoder().raw_decode(stripped)
            out['category'] = 'additional_text' if stripped[end:].strip() else 'json_error'
        except ValueError:
            out['category'] = 'additional_text' if stripped and stripped[0] not in '{[' else 'json_error'
    return out, None


def parse_decision(text, catalog, snapshot, policies, allowed, finish_reason=None):
    fmt, content = root_format(text, finish_reason)
    raw = retained.parse_decision(text, catalog, snapshot, policies, allowed) if (
        isinstance(text, str) and finish_reason != 'length') else {'schema_valid': False}
    out = retained.parse_decision(content, catalog, snapshot, policies, allowed) if content is not None else {
        'schema_valid': False, 'diagnostics': [], 'unchecked': [], 'errors': [], 'output_repaired': False}
    out = copy.deepcopy(out)
    out.update(raw_contract_valid=raw['schema_valid'], format_diagnosis=fmt,
               raw_diagnostics=raw.get('diagnostics', []), original_text_preserved=True)
    roots = [d for d in out.get('diagnostics', []) if d['field_path'] == '$' and d['category'] == 'format']
    if content is None or roots:
        category = fmt['category'] if content is None else 'json_error'
        out['diagnostics'] = [d for d in out['diagnostics'] if d not in roots] + [{
            'field_path': '$', 'category': category,
            'actual_type': type(text).__name__, 'actual': text[:180] if isinstance(text, str) else repr(text)[:80],
            'expected': 'One finite JSON object with specification and plan; optional single whole-answer JSON fence only. No explanation or multiple candidates.',
            'interface_instruction': 'Return the unchanged public contract without editing requirement semantics. Truncated output is not a semantic failure.',
            'hidden_requirement_answer_provided': False}]
        out['unchecked'] += [{'field_path': p, 'status': 'not_checked',
            'reason': 'Root content unavailable or invalid; no child/type/semantic claim.'}
            for p in ('$.specification', '$.plan', '$.specification.binding', '$.independent_semantics')]
        out['errors'] = [d['field_path'] + ': ' + d['category'] for d in out['diagnostics']]
    return out


def final_flags(parsed, score):
    """Always derive the final summary from the LAST actual response, not a prior success."""
    valid = bool(parsed and parsed.get('schema_valid'))
    return {'final_contract_valid': valid,
            'final_raw_contract_valid': bool(parsed and parsed.get('raw_contract_valid')),
            'final_semantic_qualified': bool(valid and score and score.get('qualified')),
            'plan': parsed.get('plan') if valid else None}
