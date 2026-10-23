# -*- coding: utf-8 -*-
"""Finite T2-P compiler contract and independent acceptance. Python 3.4 stdlib."""
import copy
import json
import math

VERSION = 'T2-P-compile-v1'
FIELDS = set(['schema_version', 'objects', 'transfer', 'conservation',
              'reactive_policy', 'allowed_edits', 'alpha_bounds', 'voltage_bands', 'preserve'])


def finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def exact_fields(x, fields):
    if not isinstance(x, dict) or set(x) != set(fields):
        raise ValueError('Exact fields required: ' + ','.join(sorted(fields)))


def grammar():
    # Grammar only: no filled correct instance, reference action or result.
    return {
        'root_fields': sorted(FIELDS), 'schema_version': VERSION,
        'objects': {'source': 'catalog load identifier', 'destination': 'catalog load identifier',
                    'U87': 'catalog voltage identifier', 'U101': 'catalog voltage identifier'},
        'transfer': {'direction': ['source_to_destination', 'destination_to_source'],
                     'amount': 'positive finite number', 'unit': 'MW', 'field': 'plini'},
        'conservation': {'objects': 'list of load identifiers', 'field': 'plini',
                         'relation': ['sum_equals_baseline', 'not_constrained'], 'unit': 'MW'},
        'reactive_policy': {'objects': 'list of load identifiers',
                            'relation': ['preserve_baseline_Q_over_P', 'hold_Q_constant', 'not_constrained']},
        'allowed_edits': {'objects': 'list of load identifiers', 'fields': 'list from plini,qlini',
                          'mapping': ['baseline_PQ_times_absolute_alpha', 'independent_PQ']},
        'alpha_bounds': {'objects': 'list of load identifiers', 'lower': 'number', 'upper': 'number',
                         'unit': 'dimensionless'},
        'voltage_bands': [{'object': 'catalog voltage identifier', 'field': 'm:u',
                           'relation': 'baseline_plus_minus', 'half_width': 'positive finite number', 'unit': 'pu'}],
        'preserve': {k: 'boolean' for k in ('other_load_inputs', 'topology', 'control_settings', 'flow_settings')},
        'instructions': 'Return just JSON. Lists contain no duplicate object. Identifiers are exact catalog aliases or full paths. Do not generate executable code.'}


def parse(content, catalog):
    result = {'schema_valid': False, 'raw_specification': None, 'compiled_specification': None,
              'identifier_bindings': [], 'errors': [], 'output_repaired': False}
    try:
        def unique(pairs):
            value = {}
            for k, v in pairs:
                if k in value:
                    raise ValueError('Duplicate JSON key: ' + k)
                value[k] = v
            return value
        value = json.loads(content, object_pairs_hook=unique,
                           parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
        result['raw_specification'] = value
        exact_fields(value, FIELDS)
        if value['schema_version'] != VERSION:
            raise ValueError('Unknown compiler version')
        exact_fields(value['objects'], ['source', 'destination', 'U87', 'U101'])
        normalized = copy.deepcopy(value)
        ids = {}
        for alias, item in catalog.items():
            ids[alias] = alias
            if item['path'] in ids:
                raise ValueError('Ambiguous catalog')
            ids[item['path']] = alias
        def bind(identifier, kind):
            if not isinstance(identifier, str) or identifier not in ids:
                raise ValueError('Unknown or unauthorized object: ' + str(identifier))
            alias = ids[identifier]
            if catalog[alias]['kind'] != kind:
                raise ValueError('Object class/role mismatch: ' + identifier)
            result['identifier_bindings'].append({'raw': identifier, 'alias': alias, 'path': catalog[alias]['path']})
            return catalog[alias]['path']
        for role in normalized['objects']:
            normalized['objects'][role] = bind(value['objects'][role], 'load' if role in ('source', 'destination') else 'voltage')
        if len(set(normalized['objects'].values())) != 4:
            raise ValueError('Duplicate role binding')
        shapes = {'transfer': ['direction','amount','unit','field'],
                  'conservation': ['objects','field','relation','unit'],
                  'reactive_policy': ['objects','relation'],
                  'allowed_edits': ['objects','fields','mapping'],
                  'alpha_bounds': ['objects','lower','upper','unit'],
                  'preserve': ['other_load_inputs','topology','control_settings','flow_settings']}
        for key, shape in shapes.items():
            exact_fields(value[key], shape)
        tr = value['transfer']
        if (tr['direction'] not in ('source_to_destination','destination_to_source')
                or not finite(tr['amount']) or tr['amount'] <= 0 or tr['unit'] != 'MW' or tr['field'] != 'plini'):
            raise ValueError('Invalid transfer syntax/unit/input field')
        for key in ('conservation','reactive_policy','allowed_edits','alpha_bounds'):
            listed = value[key]['objects']
            if not isinstance(listed, list):
                raise ValueError('Object list required: '+key)
            normalized[key]['objects'] = [bind(x,'load') for x in listed]
            if len(set(normalized[key]['objects'])) != len(listed):
                raise ValueError('Duplicate object: '+key)
        co = value['conservation']
        if co['field'] != 'plini' or co['unit'] != 'MW' or co['relation'] not in ('sum_equals_baseline','not_constrained'):
            raise ValueError('Invalid input conservation syntax')
        if value['reactive_policy']['relation'] not in ('preserve_baseline_Q_over_P','hold_Q_constant','not_constrained'):
            raise ValueError('Invalid reactive syntax')
        edit = value['allowed_edits']
        if (not isinstance(edit['fields'],list) or len(set(edit['fields'])) != len(edit['fields'])
                or not set(edit['fields']).issubset(set(['plini','qlini']))
                or edit['mapping'] not in ('baseline_PQ_times_absolute_alpha','independent_PQ')):
            raise ValueError('Invalid edit syntax/permission')
        bounds = value['alpha_bounds']
        if (not finite(bounds['lower']) or not finite(bounds['upper'])
                or not .99 <= bounds['lower'] <= bounds['upper'] <= 1.02 or bounds['unit'] != 'dimensionless'):
            raise ValueError('Invalid or expanded multiplier domain')
        if not isinstance(value['voltage_bands'],list):
            raise ValueError('Voltage list required')
        for i, band in enumerate(value['voltage_bands']):
            exact_fields(band,['object','field','relation','half_width','unit'])
            normalized['voltage_bands'][i]['object'] = bind(band['object'],'voltage')
            if (band['field'] != 'm:u' or band['unit'] != 'pu' or band['relation'] != 'baseline_plus_minus'
                    or not finite(band['half_width']) or band['half_width'] <= 0):
                raise ValueError('Invalid voltage syntax/unit')
        if len(set(b['object'] for b in normalized['voltage_bands'])) != len(value['voltage_bands']):
            raise ValueError('Duplicate voltage object')
        if any(not isinstance(v,bool) for v in value['preserve'].values()):
            raise ValueError('Preserve flags must be boolean')
        result.update(schema_valid=True,compiled_specification=normalized)
    except Exception as exc:
        result['errors'].append(type(exc).__name__+': '+str(exc))
    return result


def semantic_check(generated, golden):
    """Independent expected semantics; never edits the generated specification."""
    checks = []
    def equivalent(a, b):
        if finite(a) and finite(b):
            return abs(a-b) <= 1e-12*max(1.,abs(b))
        if isinstance(a,dict) and isinstance(b,dict):
            return set(a)==set(b) and all(equivalent(a[k],b[k]) for k in b)
        if isinstance(a,list) and isinstance(b,list):
            return len(a)==len(b) and all(equivalent(x,y) for x,y in zip(a,b))
        return type(a)==type(b) and a==b
    for key in sorted(FIELDS):
        actual, expected = generated.get(key), golden[key]
        if key in ('conservation','reactive_policy','allowed_edits','alpha_bounds'):
            actual = copy.deepcopy(actual)
            expected = copy.deepcopy(expected)
            if isinstance(actual,dict):
                actual['objects'] = sorted(actual['objects'])
            expected['objects'] = sorted(expected['objects'])
            if key == 'allowed_edits':
                if isinstance(actual,dict):
                    actual['fields'] = sorted(actual['fields'])
                expected['fields'] = sorted(expected['fields'])
        if key == 'voltage_bands' and isinstance(actual,list):
            actual, expected = sorted(actual,key=lambda b:b['object']),sorted(expected,key=lambda b:b['object'])
        checks.append({'requirement':key,'pass':equivalent(actual,expected),
                       'actual':actual,'expected':expected})
    return {'correct':all(c['pass'] for c in checks),'checks':checks,'generated_output_not_overwritten':True,
            'numeric_serialization_tolerance':1e-12}


def derive_patch(compiled, catalog):
    """The saved GENERATED spec, not a golden patch, drives this arithmetic."""
    if compiled['reactive_policy']['relation'] != 'preserve_baseline_Q_over_P' or compiled['allowed_edits']['mapping'] != 'baseline_PQ_times_absolute_alpha':
        raise ValueError('Unsupported generated parameter mapping')
    bases = {item['path']:item['base_inputs'] for item in catalog.values() if item['kind']=='load'}
    source, dest = compiled['objects']['source'], compiled['objects']['destination']
    amount = compiled['transfer']['amount']
    sign = 1 if compiled['transfer']['direction']=='source_to_destination' else -1
    requested, alphas = {}, {}
    for path, change in ((source,-sign*amount),(dest,sign*amount)):
        base = bases[path]
        if base['plini'] <= 0:
            raise ValueError('Nonpositive original input P')
        p = base['plini']+change
        alpha = p/base['plini']
        if not compiled['alpha_bounds']['lower'] <= alpha <= compiled['alpha_bounds']['upper']:
            raise ValueError('Derived action outside generated/authorized bounds')
        alphas[path] = alpha
        requested[path] = {'plini':p,'qlini':base['qlini']*alpha}
    return {'alphas':alphas,'requested_inputs':requested,'input_sum_before_MW':sum(b['plini'] for b in bases.values()),
            'input_sum_after_MW':sum(b['plini'] for b in requested.values()),
            'derived_from':{'objects':compiled['objects'],'transfer':compiled['transfer'],
                            'reactive_policy':compiled['reactive_policy'],'alpha_bounds':compiled['alpha_bounds']}}


def physical_check(task, record):
    """Always uses original task, independent of the generated constraints."""
    golden, catalog = task['t2p']['golden'], task['t2p']['catalog']
    tol = task['t2p']['tolerances']
    checks = []
    def add(name, passed, actual=None, required=None):
        checks.append({'requirement':name,'pass':bool(passed),'actual':actual,'required':required})
    valid = bool(record.get('valid') and record.get('fixed_conditions_match') and record.get('controls_unchanged'))
    add('valid_AC_and_fixed_state',valid)
    add('other_load_inputs_unchanged',record.get('other_load_inputs_unchanged') is True)
    if not valid:
        return {'all_requirements':False,'valid':False,'checks':checks,'actual_results_not_read_when_invalid':True}
    inputs = record['actual_inputs']
    source, dest = golden['objects']['source'], golden['objects']['destination']
    bases = {x['path']:x['base_inputs'] for x in catalog.values() if x['kind']=='load'}
    d = golden['transfer']['amount']
    add('source_transfer_MW',abs((bases[source]['plini']-inputs[source]['plini'])-d)<=tol['P_MW'][source],
        bases[source]['plini']-inputs[source]['plini'],d)
    add('destination_transfer_MW',abs((inputs[dest]['plini']-bases[dest]['plini'])-d)<=tol['P_MW'][dest],
        inputs[dest]['plini']-bases[dest]['plini'],d)
    difference = sum(inputs[p]['plini']-bases[p]['plini'] for p in bases)
    add('two_plini_sum_preserved_MW',abs(difference)<=tol['sum_P_MW'],difference,tol['sum_P_MW'])
    for path in sorted(bases):
        base = bases[path]
        alpha = inputs[path]['plini']/base['plini']
        q_error = inputs[path]['qlini']-base['qlini']*alpha
        add(path+' Q_over_P',abs(q_error)<=tol['Q_ratio_Mvar'][path],q_error,tol['Q_ratio_Mvar'][path])
        add(path+' multiplier_bounds',.99<=alpha<=1.02,alpha,[.99,1.02])
    keys = record['result_snapshot']['key_results']
    voltages = {}
    for alias in ('U87','U101'):
        item = catalog[alias]
        reading = keys[item['path']+'|m:u']
        unit = reading['unit']
        unit = unit[0] if isinstance(unit,(list,tuple)) and len(unit)==2 and unit[1]=='m:u' else unit
        v = reading['value']
        delta = v-item['baseline_voltage_pu']
        voltages[alias] = v
        add(alias+' voltage_band',unit=='p.u.' and finite(v) and abs(delta)<=.005,
            {'voltage_pu':v,'delta_pu':delta},.005)
    return {'all_requirements':all(c['pass'] for c in checks),'valid':True,'checks':checks,
            'values_pu':voltages,'actual_input_sum_error_MW':difference,
            'input_conservation_only_not_system_power_balance':True}
