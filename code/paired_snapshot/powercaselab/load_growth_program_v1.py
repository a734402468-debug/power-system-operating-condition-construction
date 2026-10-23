"""Finite proportional-load-growth front ends over the existing numeric core.

C is a domain program; T submits primitive constraints. No task-ID branching,
gold-answer completion, PF, arbitrary code, response update, or new optimizer.
"""
import copy
import json
from . import stage_set_constraints_v1 as entry
from . import state_reference_constraints_v2_1 as format_tools
from . import redistribution_constraints_v1 as core

VERSION='load-growth-program-v1'
POLICY='PQ_ALPHA_TECHNICAL_V1'
STAGES=('baseline','every_accepted_state','final')
C_FIELDS=['reference_state','public_policy','growth','voltages','preserve']
T_FIELDS=['reference_state','public_policy','variables','constraints','preserve']
GROWTH_FIELDS=['set','exclude','policy','q_policy','bounds','stages','fixed_policy','fixed_stages','clauses']
T_TYPES=['alpha_bounds','proportional_change','baseline_qp','fixed_inputs','voltage_interval']
VALUES={'alpha_bounds':['lower','upper'],'proportional_change':[],'baseline_qp':[],
        'fixed_inputs':[],'voltage_interval':['basis','lower','upper']}


def contract(method):
    if method not in ('C','T'):raise ValueError('Method must be C or T')
    common={'root_required_only':C_FIELDS if method=='C' else T_FIELDS,
        'reference_state':'one published reference-state ID', 'public_policy':POLICY,
        'preserve':'unique string array of other_load_inputs, topology, control_settings, flow_settings; choices are requirements, not defaults',
        'stages':'nonempty unique array of baseline | every_accepted_state | final; only declared stages are expanded',
        'clauses':'nonempty array of C1..C7 clause IDs; provenance only, not semantic proof; no quotations required',
        'object_ids':'Only exact public short IDs. Never output full PF paths, P0/Q0 formulas, schema versions, units or technical tolerances.',
        'automatic_fields':'Program binds paths, snapshot values, input law, units, version and technical tolerance from the explicitly referenced public policy.',
        'voltage_interval':'ONE bus, basis ONE string delta or absolute, finite lower<=upper, stages and clauses. delta means voltage minus that SAME bus reference voltage. No regional-minimum aggregate.',
        'physical_tools':'Both methods jointly use the same bounded local solver, PF verifier and recovery. Numerical amplitude is NOT computed by the LLM.'}
    if method=='C':
        common['growth']={'required_only':GROWTH_FIELDS,'set':'ONE published load-set ID','exclude':'unique array of members of that set; may be empty',
            'policy':'ONE string BASELINE_P_PROPORTIONAL','q_policy':'ONE string OWN_BASELINE_QP',
            'bounds':{'lower':'number','upper':'number'},'stages':'applies to alpha bounds, proportional growth and own Q/P',
            'fixed_policy':'ONE string BASELINE_INPUTS','fixed_stages':'explicit stages for all catalog loads outside the growth set minus exclusions',
            'meaning':'Every nonexcluded set member shares an absolute alpha, so its P increment is proportional to its own P0; excluded/nonmembers stay at P0/Q0.'}
        common['voltages']={'container':'nonempty array','each_required_only':['bus','basis','lower','upper','stages','clauses']}
    else:
        common['variables']='nonempty unique load-ID array; nonvariables are baseline-fixed by the published actuator'
        common['constraints']={'container':'nonempty array','each_required_only':['id','type','objects','values','stages','clauses'],
            'types':T_TYPES,'values_required_only':VALUES,
            'role':'voltage_interval has exactly one voltage ID; other types use load IDs',
            'fixed_inputs':'binds both P/Q to the reference snapshot for listed loads; values is {}',
            'proportional_change':'all listed loads have equal absolute alpha; values is {}',
            'baseline_qp':'each listed load preserves its OWN reference Q/P; values is {}',
            'same_tools':'Reference arithmetic and technical-field binding are available here too; do not manually calculate ratios or multipliers.'}
    return common


def request_packet(original,public,example,method):
    packet=entry.request_packet(original,public['devices'],public['reference_snapshot'],public['precision_policies'],
        public['authorized_load_ids'],example,method='F',execution_mode='execute')
    packet.update(output_contract=contract(method),public_catalog={k:public[k] for k in
        ('id','load_sets','reference_state_id','policy_id','balance_policy','scenario_criteria')},
        legal_output_example=copy.deepcopy(example['decision']),
        execution_settings={'mode':'construct_requested_state','not_an_electrical_requirement':True,
            'solve_and_amplitude_by_shared_numeric_tool':True,'no_stop_or_plan_field_required':True})
    packet['public_catalog']['object_growth_bounds']={
        a:copy.deepcopy(public['growth_permission'][v['path']])
        for a,v in public['private_catalog'].items() if v['kind']=='load'}
    return packet


def parse(method,text,catalog,public,finish_reason=None):
    fmt,content=format_tools.root_format(text,finish_reason)
    out={'schema_valid':False,'raw_contract_valid':False,'format_diagnosis':fmt,'diagnostics':[],
         'unchecked':[],'output_repaired':False,'compiler_version':VERSION,'model_output':None}
    def error(path,category,actual,expected):
        out['diagnostics'].append({'field_path':path,'category':category,'actual':actual,
            'expected':expected,'hidden_answer_provided':False})
    def fields(x,keys,path):
        if not isinstance(x,dict):
            error(path,'container',type(x).__name__,{'required_keys':keys});return False
        if set(x)!=set(keys):
            error(path,'fields',sorted(x),{'required_keys':keys});return False
        return True
    def ids(x,kind,path,empty=False):
        if not isinstance(x,list) or (not x and not empty) or any(not isinstance(a,str) for a in x):
            error(path,'type',type(x).__name__,'unique '+kind+' ID array');return []
        if len(x)!=len(set(x)) or any(a not in catalog or catalog[a]['kind']!=kind for a in x):
            error(path,'object_or_role',x,[a for a,v in catalog.items() if v['kind']==kind]);return []
        return sorted(x)
    def stages(x,path):
        if (not isinstance(x,list) or not x or any(not isinstance(a,str) or a not in STAGES for a in x)
                or len(x)!=len(set(x))):
            error(path,'stage_set',x,list(STAGES));return []
        return x
    def clauses(x,path):
        if (not isinstance(x,list) or not x or any(a not in ['C'+str(i) for i in range(1,8)] for a in x)):
            error(path,'clause_ids',x,'nonempty C1..C7 array');return []
        return x
    if content is None:
        error('$',fmt['category'],None,'one JSON object, optional single whole JSON fence');return out
    try:
        def unique(pairs):
            d={}
            for k,v in pairs:
                if k in d:raise ValueError('Duplicate key: '+k)
                d[k]=v
            return d
        model=json.loads(content,object_pairs_hook=unique,parse_constant=lambda s:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
        out['model_output']=copy.deepcopy(model)
        if not fields(model,C_FIELDS if method=='C' else T_FIELDS,'$'):
            out['unchecked'].append({'field_path':'$.children','status':'not_checked','reason':'invalid root'});return out
        if model['reference_state']!=public['reference_state_id']:error('$.reference_state','reference',model['reference_state'],public['reference_state_id'])
        if model['public_policy']!=POLICY:error('$.public_policy','policy',model['public_policy'],POLICY)
        keep=model['preserve']
        if (not isinstance(keep,list) or any(k not in core.retained.PRESERVE for k in keep)
                or len(keep)!=len(set(keep))):
            error('$.preserve','enum_array',keep,core.retained.PRESERVE);keep=[]
        numerical=[];bindings=[]
        def row(identifier,typ,objects,values,ss,cc):
            paths=[catalog[a]['path'] for a in objects]
            for stage in ss:
                common={'timing':stage,'clause':cc[0] if cc else 'C1'}
                if typ=='fixed_inputs':
                    for a in objects:
                        for f in ('plini','qlini'):
                            numerical.append(dict(id=identifier+'_'+a+'_'+f+'_'+stage,type='fixed_parameter',objects=[catalog[a]['path']],
                                values={'field':f,'value':catalog[a]['base_inputs'][f]},unit='MW' if f=='plini' else 'Mvar',tolerance=0.,**common))
                else:
                    unit={'alpha_bounds':'dimensionless','proportional_change':'dimensionless','baseline_qp':'Mvar','voltage_interval':'pu'}[typ]
                    policy={'alpha_bounds':'ALPHA_READ_V1','proportional_change':'PROP_ALPHA_V1','baseline_qp':'QP_RESIDUAL_V1','voltage_interval':'VOLTAGE_EDGE_ZERO_V1'}[typ]
                    vv=copy.deepcopy(values);numeric_type=typ
                    if typ=='voltage_interval':
                        numeric_type='voltage_bounds';basis=vv.pop('basis')
                        if basis=='delta':
                            b=catalog[objects[0]]['baseline_voltage_pu'];vv={k:b+v for k,v in vv.items()}
                    numerical.append(dict(id=identifier+'_'+stage,type=numeric_type,objects=paths,values=vv,unit=unit,
                        tolerance=public['precision_policies']['policies'][policy]['effective_evaluation_tolerance'],**common))
                bindings.append({'model_id':identifier,'explicit_stage':stage,'objects':objects,'paths':paths,'clauses':cc,
                    'units_and_precision_from':POLICY,'reference_state':model['reference_state']})
        def numbers(values,required,path):
            if not fields(values,required,path):return False
            for k,v in values.items():
                if k=='basis':
                    if v not in ('delta','absolute'):error(path+'.basis','enum',v,['delta','absolute'])
                elif not core.t2p.finite(v):error(path+'.'+k,'finite_number',v,'finite number')
            if all(k in values and core.t2p.finite(values[k]) for k in ('lower','upper')) and values['lower']>values['upper']:
                error(path,'interval_direction',values,'lower <= upper')
            return True
        if method=='C':
            g=model['growth'];selected=[]
            if fields(g,GROWTH_FIELDS,'$.growth'):
                if g['set'] not in public['load_sets']:error('$.growth.set','set_id',g['set'],list(public['load_sets']))
                else:
                    excluded=ids(g['exclude'],'load','$.growth.exclude',True)
                    members=public['load_sets'][g['set']]['members']
                    if not set(excluded).issubset(set(members)):error('$.growth.exclude','set_membership',excluded,members)
                    selected=sorted(set(members)-set(excluded))
                    if not selected:error('$.growth','empty_growth',selected,'at least one nonexcluded set member')
                for k,expected in [('policy','BASELINE_P_PROPORTIONAL'),('q_policy','OWN_BASELINE_QP'),('fixed_policy','BASELINE_INPUTS')]:
                    if g[k]!=expected:error('$.growth.'+k,'policy_enum',g[k],expected)
                ss=stages(g['stages'],'$.growth.stages');fixed_ss=stages(g['fixed_stages'],'$.growth.fixed_stages');cc=clauses(g['clauses'],'$.growth.clauses')
                if numbers(g['bounds'],['lower','upper'],'$.growth.bounds') and selected:
                    row('growth_bounds','alpha_bounds',selected,g['bounds'],ss,cc)
                    row('growth_ratio','proportional_change',selected,{},ss,cc)
                    row('growth_qp','baseline_qp',selected,{},ss,cc)
                    others=sorted(a for a,v in catalog.items() if v['kind']=='load' and a not in selected)
                    row('non_growth','fixed_inputs',others,{},fixed_ss,cc)
            vs=model['voltages']
            if not isinstance(vs,list) or not vs:error('$.voltages','container',type(vs).__name__,'nonempty voltage array')
            else:
                for i,v in enumerate(vs):
                    p='$.voltages[%d]'%i
                    if not fields(v,['bus','basis','lower','upper','stages','clauses'],p):continue
                    objects=ids([v['bus']],'voltage',p+'.bus');ss=stages(v['stages'],p+'.stages');cc=clauses(v['clauses'],p+'.clauses')
                    vv={k:v[k] for k in ('basis','lower','upper')}
                    if numbers(vv,VALUES['voltage_interval'],p) and objects:row('voltage_'+str(i),'voltage_interval',objects,vv,ss,cc)
        else:
            selected=ids(model['variables'],'load','$.variables')
            cs=model['constraints'];seen=set()
            if not isinstance(cs,list) or not cs:error('$.constraints','container',type(cs).__name__,'nonempty constraint array')
            else:
                for i,c in enumerate(cs):
                    p='$.constraints[%d]'%i
                    if not fields(c,['id','type','objects','values','stages','clauses'],p):continue
                    if not isinstance(c['id'],str) or not c['id'] or c['id'] in seen:error(p+'.id','identifier',c['id'],'unique nonempty string')
                    else:seen.add(c['id'])
                    if not isinstance(c['type'],str) or c['type'] not in T_TYPES:error(p+'.type','enum',c['type'],T_TYPES);continue
                    typ=c['type'];objects=ids(c['objects'],'voltage' if typ=='voltage_interval' else 'load',p+'.objects')
                    if typ=='voltage_interval' and len(objects)!=1:error(p+'.objects','cardinality',objects,'exactly one voltage ID')
                    ss=stages(c['stages'],p+'.stages');cc=clauses(c['clauses'],p+'.clauses')
                    if numbers(c['values'],VALUES[typ],p+'.values') and objects and (typ!='voltage_interval' or len(objects)==1):
                        row(c['id'],typ,objects,c['values'],ss,cc)
        if out['diagnostics']:return out
        spec={'schema_version':core.VERSION,'variables':{'objects':[catalog[a]['path'] for a in selected],
            'mapping':'baseline_PQ_times_absolute_alpha'},'constraints':numerical,
            'preserve':{k:k in keep for k in core.retained.PRESERVE}}
        checked=core.parse(json.dumps(spec),catalog,canonical=True,actuator_bounds=public['growth_permission'])
        if not checked['schema_valid']:
            error('$.expanded_specification','numeric_contract',checked['errors'],'public bounds, roles, stages and registered constraint types');return out
        out.update(schema_valid=True,raw_contract_valid=fmt['raw_json_format_valid'],
            expansion={'numeric_specification':spec,'bindings':bindings},
            plan={'operation':'solve','selected':selected,'reason':'deterministic execution of submitted program/specification'},
            schema_version_generated=True,source_quotes_required=False,answer_or_requirements_repaired=False)
    except (ValueError,KeyError,TypeError,AttributeError) as exc:
        error('$','structure',str(exc),'the method-specific public contract; no automatic JSON repair')
    return out


prepare_problem=entry.prepare_problem


def semantic_evaluation(parsed,gold,catalog,matrix,current,task):
    """Existing finite equivalence rules; provenance labels are not predicates."""
    spec=copy.deepcopy(parsed['expansion']['numeric_specification']);g=copy.deepcopy(gold)
    # Only scoring copies normalize clause labels. Actual generated inputs and
    # the model-source bindings remain untouched and never get replaced.
    for x in (spec,g):
        for c in x['constraints']:c['clause']='C1'
    p=core.build_problem(spec,catalog,matrix,current,task);gp=core.build_problem(g,catalog,matrix,current,task)
    score=core.semantic_evaluation(spec,g,catalog,p,gp,task)
    score['source_clause_matching_not_semantic_proof']=True
    score['runtime_model_specification_unchanged']=True
    return score
