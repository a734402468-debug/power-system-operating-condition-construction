# -*- coding: utf-8 -*-
"""Typed baseline expressions lowered to the retained numerical/PF contract.

Finite, CPython 3.4 standard-library interface. No task-name branches, guessed
objects, default requirements, tolerance substitution, or generated code.
"""
import copy
import json
import math
from . import redistribution_constraints_v1 as numeric

VERSION = 'state-reference-constraints-v1'
BASELINE_ID = 'base_v1'
COMMON = ['id', 'type', 'unit', 'timing', 'clause']
FIELDS = {
    'transfer': ['source', 'destination', 'amount', 'accuracy'],
    'input_sum': ['objects', 'target', 'accuracy'],
    'qp_policy': ['objects', 'state', 'policy', 'accuracy'],
    'fixed_inputs': ['objects', 'state', 'fields', 'accuracy'],
    'alpha_bounds': ['objects', 'lower', 'upper', 'precision'],
    'voltage_bounds': ['objects', 'bounds', 'precision'],
    'distribution': ['objects', 'mode'],
    'proportional_distribution': ['objects', 'precision']}
UNITS = {'transfer':'MW', 'input_sum':'MW', 'qp_policy':'Mvar',
         'alpha_bounds':'dimensionless', 'voltage_bounds':'pu',
         'distribution':'dimensionless', 'proportional_distribution':'dimensionless',
         'fixed_inputs':'per_field'}


class ContractError(ValueError):
    def __init__(self, path, category, actual, expected, instruction):
        self.diagnostic = {'field_path':path, 'category':category,
            'actual':actual, 'expected':expected, 'interface_instruction':instruction,
            'hidden_requirement_answer_provided':False}
        ValueError.__init__(self, path+': '+category)


def fail(path, category, actual, expected, instruction):
    raise ContractError(path, category, actual, expected, instruction)


def fields(value, required, path):
    if not isinstance(value, dict):
        fail(path,'type',value,'object','Use a JSON object with the fields specified for this type.')
    if set(value) != set(required):
        fail(path,'fields',value,required,'Use exactly the type-specific fields; omit fields not applicable to this type. Do not use null placeholders.')


def number(value, path):
    if not numeric.t2p.finite(value):
        fail(path,'type',value,'finite JSON number; not bool/null/array','Supply an explicit number when this field applies; otherwise use an allowed symbolic expression or policy reference.')
    return value


def state_id(value, snapshot, path):
    if value != snapshot['state_id']:
        fail(path,'state_reference',value,snapshot['state_id'],'Only the supplied versioned baseline is available. A current/candidate state is not a baseline reference.')


def ids(value, catalog, kind, path):
    if not isinstance(value,list) or not value or not all(isinstance(a,str) for a in value):
        fail(path,'type',value,'nonempty array of exact short IDs','Use the supplied directory IDs; do not produce full paths or inferred names.')
    if len(set(value)) != len(value):
        fail(path,'object',value,'unique IDs','Remove duplicate identifiers without changing the intended set.')
    if any(a not in catalog or catalog[a]['kind']!=kind for a in value):
        fail(path,'object',value,sorted(a for a,v in catalog.items() if v['kind']==kind),'Choose only registered IDs of the required object role. No fuzzy matching is performed.')
    return value


def grammar():
    return {'schema_version':VERSION,
        'root_required_only':['schema_version','baseline_state','variables','constraints','preserve'],
        'baseline_state':'the supplied state_id string',
        'variables':{'objects':'unique allowed load ID array','mapping':'baseline_PQ_times_absolute_alpha'},
        'constraint_common':{'id':'unique string','type':'single type string','unit':'see type',
            'timing':'ONE string baseline OR every_accepted_state OR final',
            'clause':'ONE original clause ID C1..C7; not a correctness certificate'},
        'type_specific_fields':{
            'transfer':{'source':'load IDs','destination':'disjoint load IDs','amount':'positive MW expression','accuracy':'P_SUM_V1','unit':'MW'},
            'input_sum':{'objects':'load IDs','target':'MW expression','accuracy':'P_SUM_V1','unit':'MW'},
            'qp_policy':{'objects':'load IDs','state':'baseline ID','policy':'each_baseline_ratio','accuracy':'QP_RESIDUAL_V1','unit':'Mvar'},
            'fixed_inputs':{'objects':'load IDs','state':'baseline ID','fields':'unique array of plini and/or qlini','accuracy':'FIXED_EXACT_V1','unit':'per_field'},
            'alpha_bounds':{'objects':'load IDs','lower':'number','upper':'number','precision':'ALPHA_READ_V1','unit':'dimensionless'},
            'voltage_bounds':{'objects':'voltage IDs','bounds':'baseline_band OR absolute form below','precision':'VOLTAGE_EDGE_ZERO_V1','unit':'pu'},
            'distribution':{'objects':'load IDs','mode':'free','unit':'dimensionless; NO accuracy/tolerance field; introduces no proportional equation'},
            'proportional_distribution':{'objects':'load IDs','precision':'PROP_ALPHA_V1','unit':'dimensionless; ONLY if equal multipliers required'}},
        'expressions':{
            'literal':['op=literal','value=number','unit=MW/Mvar/pu/dimensionless'],
            'baseline_sum':['op=baseline_sum','state=baseline ID','quantity=plini/qlini','objects=load ID array'],
            'baseline_value':['op=baseline_value','state=baseline ID','quantity=plini/qlini/voltage_pu','object=exact ID'],
            'scale':['op=scale','factor=number','base=expression'],
            'minimum':['op=minimum','items=array of 2..4 expressions of identical units']},
        'bounds_forms':{'baseline_band':['kind=baseline_band','state=baseline ID','lower_offset=number pu','upper_offset=number pu'],
                        'absolute':['kind=absolute','lower=number pu','upper=number pu']},
        'preserve':{k:'required boolean' for k in numeric.retained.PRESERVE},
        'rules':['No unspecified fields, null placeholders, option arrays or generated code.',
            'Choose sets, reference state, direction, quantities, stages and policies from the original text; the binder only computes the chosen expressions.',
            'Intervals stay intervals. Free distribution has no proportional equality or tolerance.',
            'Accuracy/precision IDs explicitly select published policies. No missing value is replaced.',
            'Plan remains separate: operation solve/stop, selected load IDs, reason string. Numerical tool computes alpha.']}


def snapshot_from(catalog, baseline_record, task, provenance):
    if not baseline_record.get('valid'):
        raise ValueError('Only a valid archived baseline can be referenced')
    quantities={}
    for a,v in catalog.items():
        if v['kind']=='load':
            b=baseline_record['actual_inputs'][v['path']]
            if b != v['base_inputs']:raise ValueError('Catalog/baseline input mismatch')
            quantities[a]=dict(b)
        else:
            quantities[a]={'voltage_pu':baseline_record['result_snapshot']['key_results'][v['path']+'|m:u']['value']}
            if quantities[a]['voltage_pu'] != v['baseline_voltage_pu']:raise ValueError('Catalog/baseline voltage mismatch')
    payload={'state_id':BASELINE_ID,'kind':'archived_original_baseline','version':1,
        'project_path':task['project_path'],'study_case_path':task['study_case_path'],
        'catalog_sha256':numeric.signature(catalog),'quantities':quantities,
        'actual_inputs_sha256':numeric.signature(baseline_record['actual_inputs']),
        'controls_sha256':numeric.signature(baseline_record['controls']),
        'fixed_conditions_sha256':numeric.signature(task['fixed_conditions']),
        'record_sha256':numeric.signature(baseline_record),'provenance':provenance}
    payload['snapshot_sha256']=numeric.signature(payload)
    return payload


def policies_from(precision):
    values={'P_SUM_V1':('MW',precision['P_sum_tolerance_MW']),
        'QP_RESIDUAL_V1':('Mvar',precision['QP_residual_tolerance_Mvar']),
        'ALPHA_READ_V1':('dimensionless',precision['alpha_read_tolerance']),
        'FIXED_EXACT_V1':('per_field',0.0),'VOLTAGE_EDGE_ZERO_V1':('pu',0.0),
        'PROP_ALPHA_V1':('dimensionless',precision['proportional_alpha_tolerance'])}
    return {'version':'precision-policy-v1','policies':{k:{'unit':unit,'user_allowed_error':val,
        'effective_evaluation_tolerance':val,
        'storage_policy':'existing preregistered float32 budget' if k in ('P_SUM_V1','QP_RESIDUAL_V1') else 'existing readback/exact-bound policy',
        'extra_storage_error_added':0.0,'solver_policy':'retained-active-face-v1.1',
        'solver_relation_check':'1e-10*max(1,abs(b)) equalities; 1e-12*max(1,abs(b)) inequalities; not added to user acceptance'} for k,(unit,val) in values.items()},
        'rule':'User allowed deviation, storage uncertainty and numerical residual checks are distinct. Existing user budget already includes its preregistered storage allowance; never add it twice.'}


def expression(x, catalog, snapshot, path, depth=0):
    if depth>4:fail(path,'expression',x,'depth <=4','Use the finite expression operators; arbitrary arithmetic/code is unsupported.')
    if not isinstance(x,dict) or not isinstance(x.get('op'),str):
        fail(path,'type',x,'typed expression object','Choose one operator with exactly its fields from the grammar.')
    op=x['op'];trace={'expression':copy.deepcopy(x),'source_state':None}
    if op=='literal':
        fields(x,['op','value','unit'],path);value=number(x['value'],path+'.value');unit=x['unit']
        if unit not in ('MW','Mvar','pu','dimensionless'):fail(path+'.unit','unit',unit,'MW/Mvar/pu/dimensionless','Use one supported physical unit.')
    elif op in ('baseline_sum','baseline_value'):
        fields(x,['op','state','quantity','objects' if op=='baseline_sum' else 'object'],path)
        state_id(x['state'],snapshot,path+'.state');q=x['quantity']
        if q not in ('plini','qlini','voltage_pu') or (op=='baseline_sum' and q=='voltage_pu'):
            fail(path+'.quantity','quantity',q,'plini/qlini for sum; plini/qlini/voltage_pu for value','Choose the physical quantity explicitly; summing voltage is unsupported.')
        objects=x['objects'] if op=='baseline_sum' else [x['object']]
        ids(objects,catalog,'voltage' if q=='voltage_pu' else 'load',path+'.objects')
        terms={a:snapshot['quantities'][a][q] for a in objects}
        value=math.fsum(terms.values());unit={'plini':'MW','qlini':'Mvar','voltage_pu':'pu'}[q]
        trace.update(source_state=snapshot['state_id'],snapshot_sha256=snapshot['snapshot_sha256'],quantity=q,objects=objects,terms=terms)
    elif op=='scale':
        fields(x,['op','factor','base'],path);factor=number(x['factor'],path+'.factor')
        value,unit,child=expression(x['base'],catalog,snapshot,path+'.base',depth+1);value*=factor
        trace.update(factor=factor,base=child)
    elif op=='minimum':
        fields(x,['op','items'],path)
        if not isinstance(x['items'],list) or not 2<=len(x['items'])<=4:fail(path+'.items','type',x['items'],'2..4 typed expressions','Use a finite minimum of same-unit quantities.')
        terms=[expression(e,catalog,snapshot,path+'.items[%d]'%i,depth+1) for i,e in enumerate(x['items'])]
        if len(set(t[1] for t in terms))!=1:fail(path+'.items','unit',[t[1] for t in terms],'identical units','A minimum cannot mix different physical quantities/units.')
        value=min(t[0] for t in terms);unit=terms[0][1];trace['items']=[t[2] for t in terms]
    else:fail(path+'.op','unsupported',op,list(grammar()['expressions']),'Use only one supported typed operator, never code.')
    number(value,path+'.resolved_value');trace.update(value=value,unit=unit)
    return value,unit,trace


def compile_spec(spec, catalog, snapshot, policies, allowed):
    fields(spec,['schema_version','baseline_state','variables','constraints','preserve'],'specification')
    if spec['schema_version']!=VERSION:fail('specification.schema_version','version',spec['schema_version'],VERSION,'Use the frozen interface version.')
    state_id(spec['baseline_state'],snapshot,'specification.baseline_state')
    fields(spec['variables'],['objects','mapping'],'specification.variables')
    variables=ids(spec['variables']['objects'],catalog,'load','specification.variables.objects')
    if not set(variables).issubset(set(allowed)):fail('specification.variables.objects','permission',variables,allowed,'Only declared authorized objects may be adjustable; fixed objects can still appear in relations.')
    if spec['variables']['mapping']!='baseline_PQ_times_absolute_alpha':fail('specification.variables.mapping','enum',spec['variables']['mapping'],'baseline_PQ_times_absolute_alpha','Use the verified baseline-relative P/Q actuator.')
    fields(spec['preserve'],numeric.retained.PRESERVE,'specification.preserve')
    if any(type(v)!=bool for v in spec['preserve'].values()):fail('specification.preserve','type',spec['preserve'],'boolean values','Use true or false explicitly; the program does not supply preservation requirements.')
    if not isinstance(spec['constraints'],list):fail('specification.constraints','type',spec['constraints'],'array','Emit only the actual required constraints/declarations.')
    wire={'schema_version':numeric.VERSION,'variables':copy.deepcopy(spec['variables']),'constraints':[], 'preserve':copy.deepcopy(spec['preserve'])}
    mapping=[];seen=set()
    def accuracy(c,key,required,path):
        if c[key]!=required:fail(path+'.'+key,'policy',c[key],required,'Select the published policy for this constraint type; do not use null, omitted numbers or guessed tolerances.')
        return policies['policies'][c[key]]['effective_evaluation_tolerance']
    for index,c in enumerate(spec['constraints']):
        path='specification.constraints[%d]'%index
        if not isinstance(c,dict) or not isinstance(c.get('type'),str) or c.get('type') not in FIELDS:fail(path+'.type','unsupported',c.get('type') if isinstance(c,dict) else c,list(FIELDS),'Use exactly one supported type string.')
        typ=c['type'];fields(c,COMMON+FIELDS[typ],path)
        if not isinstance(c['id'],str) or not c['id'] or c['id'] in seen:fail(path+'.id','identifier',c['id'],'unique nonempty string','Give each requirement a distinct ID.')
        seen.add(c['id'])
        if c['timing'] not in ('baseline','every_accepted_state','final') or not isinstance(c['timing'],str):fail(path+'.timing','enum',c['timing'],'baseline/every_accepted_state/final','Select one stage from the original requirement, not an option array.')
        if c['clause'] not in ['C'+str(i) for i in range(1,8)]:fail(path+'.clause','source',c['clause'],'C1..C7','Reference one actual clause; references do not establish semantic correctness.')
        if c['unit']!=UNITS[typ]:fail(path+'.unit','unit',c['unit'],UNITS[typ],'Use the type-specific physical unit.')
        refs=[];expanded=[]
        def add(t,objects,values,unit,tol):
            n={'id':c['id']+'::'+str(len(expanded)), 'type':t,'objects':objects,'values':values,
               'unit':unit,'tolerance':tol,'timing':c['timing'],'clause':c['clause']}
            expanded.append(n);wire['constraints'].append(n)
        if typ=='transfer':
            source=ids(c['source'],catalog,'load',path+'.source');dest=ids(c['destination'],catalog,'load',path+'.destination')
            if set(source)&set(dest):fail(path,'object_set',[source,dest],'disjoint source and destination','Choose disjoint sets; the program does not infer transfer direction.')
            value,unit,trace=expression(c['amount'],catalog,snapshot,path+'.amount');refs.append(trace)
            if unit!='MW' or value<=0:fail(path+'.amount','quantity',[value,unit],'positive MW amount','Direction is source to destination; amount must be positive MW.')
            tol=accuracy(c,'accuracy','P_SUM_V1',path)
            add('input_sum_delta',source,{'delta':-value},'MW',tol);add('input_sum_delta',dest,{'delta':value},'MW',tol)
        elif typ=='input_sum':
            objects=ids(c['objects'],catalog,'load',path+'.objects');value,unit,trace=expression(c['target'],catalog,snapshot,path+'.target');refs.append(trace)
            if unit!='MW':fail(path+'.target','unit',unit,'MW','Target must be a typed active-input quantity.')
            add('active_power_sum',objects,{'value':value},'MW',accuracy(c,'accuracy','P_SUM_V1',path))
        elif typ=='qp_policy':
            objects=ids(c['objects'],catalog,'load',path+'.objects');state_id(c['state'],snapshot,path+'.state')
            if c['policy']!='each_baseline_ratio':fail(path+'.policy','enum',c['policy'],'each_baseline_ratio','Use each selected object own baseline ratio; no shared ratio is assumed.')
            if any(snapshot['quantities'][a]['plini']<=0 for a in objects):fail(path+'.objects','unsupported',objects,'positive baseline P','Zero/nonpositive P ratio semantics are not covered; do not divide by zero.')
            add('baseline_qp',objects,{},'Mvar',accuracy(c,'accuracy','QP_RESIDUAL_V1',path))
            refs=[{'state':c['state'],'object':a,'P0':snapshot['quantities'][a]['plini'],'Q0':snapshot['quantities'][a]['qlini']} for a in objects]
        elif typ=='fixed_inputs':
            objects=ids(c['objects'],catalog,'load',path+'.objects');state_id(c['state'],snapshot,path+'.state')
            if not isinstance(c['fields'],list) or not c['fields'] or not all(isinstance(f,str) for f in c['fields']) or len(set(c['fields']))!=len(c['fields']) or any(f not in ('plini','qlini') for f in c['fields']):fail(path+'.fields','enum',c['fields'],'unique array of plini/qlini','Choose fixed input fields explicitly.')
            tol=accuracy(c,'accuracy','FIXED_EXACT_V1',path)
            for a in objects:
                for f in c['fields']:
                    v=snapshot['quantities'][a][f];add('fixed_parameter',[a],{'field':f,'value':v},'MW' if f=='plini' else 'Mvar',tol)
                    refs.append({'state':c['state'],'object':a,'quantity':f,'value':v})
        elif typ=='alpha_bounds':
            objects=ids(c['objects'],catalog,'load',path+'.objects');lo=number(c['lower'],path+'.lower');hi=number(c['upper'],path+'.upper')
            if not .99<=lo<=hi<=1.02:fail(path,'range',[lo,hi],'ordered bounds inside authorized [0.99,1.02]','Stay within actuator permissions; original semantic bounds are independently evaluated.')
            add('alpha_bounds',objects,{'lower':lo,'upper':hi},'dimensionless',accuracy(c,'precision','ALPHA_READ_V1',path))
        elif typ=='voltage_bounds':
            objects=ids(c['objects'],catalog,'voltage',path+'.objects');b=c['bounds']
            if not isinstance(b,dict) or b.get('kind') not in ('baseline_band','absolute'):fail(path+'.bounds','type',b,'baseline_band or absolute bounds object','Use one range representation, never a target point.')
            tol=accuracy(c,'precision','VOLTAGE_EDGE_ZERO_V1',path)
            if b['kind']=='baseline_band':
                fields(b,['kind','state','lower_offset','upper_offset'],path+'.bounds');state_id(b['state'],snapshot,path+'.bounds.state')
                lo=number(b['lower_offset'],path+'.bounds.lower_offset');hi=number(b['upper_offset'],path+'.bounds.upper_offset')
            else:
                fields(b,['kind','lower','upper'],path+'.bounds');lo=number(b['lower'],path+'.bounds.lower');hi=number(b['upper'],path+'.bounds.upper')
            if lo>hi:fail(path+'.bounds','range',[lo,hi],'lower <= upper','Supply ordered interval bounds.')
            for a in objects:
                base=snapshot['quantities'][a]['voltage_pu'] if b['kind']=='baseline_band' else 0.
                add('voltage_bounds',[a],{'lower':base+lo,'upper':base+hi},'pu',tol)
                refs.append({'state':snapshot['state_id'] if b['kind']=='baseline_band' else None,'object':a,'base':base,'resolved_bounds':[base+lo,base+hi]})
        else:
            objects=ids(c['objects'],catalog,'load',path+'.objects')
            if typ=='distribution':
                if c['mode']!='free':fail(path+'.mode','enum',c['mode'],'free','Free distribution declares no proportional equality; there is no tolerance field.')
            else:add('proportional_change',objects,{},'dimensionless',accuracy(c,'precision','PROP_ALPHA_V1',path))
        mapping.append({'constraint_id':c['id'],'source_clause':c['clause'],'timing':c['timing'],
            'expression':copy.deepcopy(c),'bindings':refs,'expanded_constraint_ids':[r['id'] for r in expanded],
            'policy_applied':{key:copy.deepcopy(policies['policies'][c[key]]) for key in ('accuracy','precision') if key in c},
            'no_physical_equation':typ=='distribution'})
    parsed=numeric.parse(json.dumps(wire),catalog)
    if not parsed['schema_valid']:fail('specification.numeric_expansion','numeric_contract',parsed['errors'],'retained finite numerical contract','The selected expressions must expand to supported numerical constraints; no requirement is supplied automatically.')
    return {'numeric_specification':parsed['compiled_specification'],'expression_bindings':mapping,
        'baseline_snapshot_sha256':snapshot['snapshot_sha256'],'policy_sha256':numeric.signature(policies),
        'generated_expression_sha256':numeric.signature(spec),'numeric_specification_sha256':numeric.signature(parsed['compiled_specification']),
        'requirements_added_or_replaced':False}


def parse_decision(content,catalog,snapshot,policies,allowed):
    result={'schema_valid':False,'errors':[],'diagnostics':[],'output_repaired':False,
            'generated_expression':None,'expansion':None,'plan':None}
    try:
        def unique(pairs):
            x={}
            for k,v in pairs:
                if k in x:fail('$','format',k,'unique keys','Duplicate JSON keys are rejected.')
                x[k]=v
            return x
        x=json.loads(content,object_pairs_hook=unique,parse_constant=lambda v:fail('$','type',v,'finite JSON','Nonfinite values are rejected.'))
        fields(x,['specification','plan'],'$');result['generated_expression']=x['specification']
        fields(x['plan'],['operation','selected','reason'],'plan');plan=x['plan']
        if plan['operation'] not in ('solve','stop') or not isinstance(plan['operation'],str):fail('plan.operation','enum',plan['operation'],'solve/stop','Use one operation string.')
        if not isinstance(plan['reason'],str):fail('plan.reason','type',plan['reason'],'short string','State a concise action reason; no internal chain of thought is required.')
        if plan['operation']=='stop':
            if plan['selected']!=[]:fail('plan.selected','operation',plan['selected'],'empty array for stop','Stop has no selected action objects.')
        else:ids(plan['selected'],catalog,'load','plan.selected')
        if not set(plan['selected']).issubset(set(allowed)):fail('plan.selected','permission',plan['selected'],allowed,'Stay within allowed modification objects.')
        expansion=compile_spec(x['specification'],catalog,snapshot,policies,allowed)
        if not set(plan['selected']).issubset(set(x['specification']['variables']['objects'])):fail('plan.selected','permission',plan['selected'],x['specification']['variables']['objects'],'Select only declared variables; fixed terms remain in constraints.')
        result.update(schema_valid=True,expansion=expansion,plan=plan)
    except ContractError as e:
        result.update(error_category=e.diagnostic['category'],errors=[str(e)],diagnostics=[e.diagnostic])
    except (ValueError,TypeError,KeyError) as e:
        result.update(error_category='format',errors=[str(e)],diagnostics=[{'field_path':'$','category':'format','actual':str(e),'expected':'valid typed JSON per supplied contract','interface_instruction':'Return one complete JSON object. No automatic repair is performed.','hidden_requirement_answer_provided':False}])
    return result


def expression_feedback(expansion,catalog,record,baseline_record,phase='final'):
    evaluated=numeric.evaluate(expansion['numeric_specification'],catalog,record,phase=phase,baseline_record=baseline_record)
    rows={r['constraint_id']:r for r in evaluated['checks']};checks=[]
    for m in expansion['expression_bindings']:
        details=[rows[i] for i in m['expanded_constraint_ids']]
        original=m['expression'];selected_record=baseline_record if m['timing']=='baseline' else record
        current_values=[]
        if original['type']=='transfer' and selected_record and selected_record.get('valid'):
            for key in ('source','destination'):
                objects=original[key]
                base=math.fsum(catalog[a]['base_inputs']['plini'] for a in objects)
                actual=math.fsum(selected_record['actual_inputs'][catalog[a]['path']]['plini'] for a in objects)
                current_values.append({'set_role':key,'objects':objects,'actual_sum_MW':actual,
                    'reference_baseline_sum_MW':base,'actual_delta_MW':actual-base,
                    'requested_delta_MW':(-1 if key=='source' else 1)*m['bindings'][0]['value']})
        checks.append({'constraint_id':m['constraint_id'],'clause':m['source_clause'],'timing':m['timing'],
            'kind':'actual_PF','evaluated_on':'original_baseline' if m['timing']=='baseline' else 'actual_candidate',
            'details':details,'status':'satisfied' if all(r['pass'] for r in details) else 'unmet',
            'declaration_only':m['no_physical_equation'],'bindings':m['bindings'],'current_transfer_values':current_values})
    evaluated['state_reference_feedback']=checks
    return evaluated


def semantic_evaluation(expression_spec, expansion, golden, catalog, task):
    """Independent scoring, never a runtime answer or specification replacement."""
    actual,_=numeric.lower(expansion['numeric_specification'],catalog)
    expected,_=numeric.lower(golden,catalog)
    raw=numeric.retained.semantic_check(actual,expected)
    requirements=[c for c in expression_spec['constraints'] if c['type']=='distribution']
    proportional=any(c['type']=='proportional_distribution' for c in expression_spec['constraints'])
    loads=set(a for a,v in catalog.items() if v['kind']=='load')
    free_coverage=set(a for c in requirements if c['mode']=='free' and c['clause']=='C2' for a in c['objects'])
    distribution_correct=free_coverage==loads and not proportional
    # Numeric equality does not rescue an incorrect symbolic set/reference.
    reference_errors=[]
    def referenced_leaves(e):
        if e.get('op') in ('baseline_sum','baseline_value'):return [e]
        if e.get('op')=='scale':return referenced_leaves(e['base'])
        if e.get('op')=='minimum':return [leaf for item in e['items'] for leaf in referenced_leaves(item)]
        return []
    for c in expression_spec['constraints']:
        if c['type']=='input_sum':
            for leaf in referenced_leaves(c['target']):
                selected=leaf.get('objects',[leaf.get('object')])
                if set(c['objects'])!=set(selected) or leaf['quantity']!='plini':
                    reference_errors.append({'id':c['id'],'reason':'baseline input-sum reference uses a different set or physical quantity, even if resolved numbers coincide','reference':leaf})
    result={'numeric_expression_match':raw,'distribution_correct':distribution_correct,
        'reference_errors':reference_errors,'expression_correct':raw['correct'] and distribution_correct and not reference_errors,
        'independent_only':True,'runtime_spec_replacement':False}
    return result
