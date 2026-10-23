# -*- coding: utf-8 -*-
"""Shared finite output contract and aggregate diagnostics; CPython 3.4 compatible.

Only mechanical version metadata is wrapped. Physical selections are never repaired.
The retained v1 expander and numerical interface are deliberately unchanged.
"""
import copy
import json
from . import state_reference_constraints_v1 as prior

VERSION = 'state-reference-output-v2'
INTERNAL_VERSION = prior.numeric.VERSION
MAPPING = 'baseline_PQ_times_absolute_alpha'
INTERFACE_REVISION = 'steady-state-interface-v1'


def interface_rules():
    """Shared public scope/plan rules; enforced by both finite parsers."""
    return {
        'revision': INTERFACE_REVISION,
        'constraint_objects': 'Any role-compatible ID in device_directory may be referenced, including fixed loads. References do not grant write permission.',
        'authorized_load_ids': 'Caller-supplied maximum set allowed to receive P/Q writes; separate from the full device directory.',
        'variables.objects': 'Nonempty unique adjustable load IDs, a subset of authorized_load_ids. Do NOT list fixed or merely referenced objects here.',
        'plan.selected': 'The subset of variables.objects chosen for this solve; unselected loads enter the numerical problem at their baseline inputs.',
        'solve': 'operation=solve requires nonempty selected, contained in variables.objects and authorized_load_ids.',
        'stop': 'operation=stop requires selected=[]. No numerical solve or PF action is requested.',
        'execution_mode': 'compile_only/execute is a caller setting, not an electrical requirement or plan operation. compile_only does not imply stop.',
        'no_semantic_completion': 'No automatic baseline, object selection, interval alteration, or omitted-condition repair. Source citations record provenance only.'}


def enum(*values):
    return {'type':'string', 'enum':list(values)}


def obj(fields, optional=None):
    return {'type':'object', 'fields':fields, 'optional':optional or {}, 'extra':False}


def ids(role, empty=False):
    return {'type':'array', 'items':{'type':'string','role':role},
            'min':0 if empty else 1, 'unique':True}


NUM = {'type':'number','finite':True}
EXPR = {'ref':'expression'}
STATE = {'type':'string','role':'state'}
COMMON = {'id':{'type':'string','nonempty':True}, 'type':enum(*sorted(prior.FIELDS)),
          'unit':{'type':'string'}, 'timing':enum('baseline','every_accepted_state','final'),
          'clause':enum(*['C'+str(i) for i in range(1,8)])}
# One registry is rendered into prompt explanations AND used for validation.
TYPE_FIELDS = {
    'transfer':{'source':ids('load'),'destination':ids('load'),'amount':EXPR,'accuracy':enum('P_SUM_V1')},
    'input_sum':{'objects':ids('load'),'target':EXPR,'accuracy':enum('P_SUM_V1')},
    'qp_policy':{'objects':ids('load'),'state':STATE,'policy':enum('each_baseline_ratio'),'accuracy':enum('QP_RESIDUAL_V1')},
    'fixed_inputs':{'objects':ids('load'),'state':STATE,'fields':{'type':'array','items':enum('plini','qlini'),'min':1,'unique':True},'accuracy':enum('FIXED_EXACT_V1')},
    'alpha_bounds':{'objects':ids('load'),'lower':NUM,'upper':NUM,'precision':enum('ALPHA_READ_V1')},
    'voltage_bounds':{'objects':ids('voltage'),'bounds':{'ref':'bounds'},'precision':enum('VOLTAGE_EDGE_ZERO_V1')},
    'distribution':{'objects':ids('load'),'mode':enum('free')},
    'proportional_distribution':{'objects':ids('load'),'precision':enum('PROP_ALPHA_V1')}
}


def contract():
    variants = {}
    for typ, specific in TYPE_FIELDS.items():
        fields = copy.deepcopy(COMMON)
        fields.update(copy.deepcopy(specific), type=enum(typ), unit=enum(prior.UNITS[typ]))
        variants[typ] = obj(fields)
    expression = {'variant':'op','common':{'op':enum('literal','baseline_sum','baseline_value','scale','minimum')},
        'choices':{
            'literal':obj({'op':enum('literal'),'value':NUM,'unit':enum('MW','Mvar','pu','dimensionless')}),
            'baseline_sum':obj({'op':enum('baseline_sum'),'state':STATE,'quantity':enum('plini','qlini'),'objects':ids('load')}),
            'baseline_value':obj({'op':enum('baseline_value'),'state':STATE,'quantity':enum('plini','qlini','voltage_pu'),'object':{'type':'string','role':'registered'}}),
            'scale':obj({'op':enum('scale'),'factor':NUM,'base':EXPR}),
            'minimum':obj({'op':enum('minimum'),'items':{'type':'array','items':EXPR,'min':2,'max':4}})}}
    bounds = {'variant':'kind','common':{'kind':enum('baseline_band','absolute')},'choices':{
        'baseline_band':obj({'kind':enum('baseline_band'),'state':STATE,'lower_offset':NUM,'upper_offset':NUM}),
        'absolute':obj({'kind':enum('absolute'),'lower':NUM,'upper':NUM})}}
    spec = obj({'baseline_state':STATE,'variables':obj({'objects':ids('load'),'mapping':enum(MAPPING)}),
                'constraints':{'type':'array','items':{'ref':'constraint'},'min':1},
                'preserve':obj({k:{'type':'boolean'} for k in prior.numeric.retained.PRESERVE})},
               {'schema_version':enum(VERSION)})
    root = obj({'specification':spec,'plan':obj({'operation':enum('solve','stop'),
                'selected':ids('load',True),'reason':{'type':'string'}})})
    return {'protocol_version':VERSION,'root':root,'definitions':{
        'constraint':{'variant':'type','common':COMMON,'choices':variants},
        'expression':expression,'bounds':bounds},
        'cross_field_rules':interface_rules(),
        'metadata_policy':{'specification.schema_version':'optional; if present must equal '+VERSION,
            'program_envelope_state_reference_version':prior.VERSION,
            'expanded_executable_version':INTERNAL_VERSION,
            'physical_fields_added_or_corrected':False},
        'expression_depth_limit':4}


def compact(node):
    """Lossless field/container/enum explanation generated from the registry."""
    if 'ref' in node:return '@'+node['ref']
    if 'variant' in node:
        return {'dispatch_by':node['variant'],'forms':{k:compact(v) for k,v in node['choices'].items()}}
    typ=node['type']
    if typ=='object':
        d={k:compact(v) for k,v in node['fields'].items()}
        if node['optional']:d['OPTIONAL_FIELDS']={k:compact(v) for k,v in node['optional'].items()}
        return {'OBJECT_REQUIRED_ONLY':d}
    if typ=='array':
        return {'ARRAY':compact(node['items']),'min_items':node.get('min',0),
                'max_items':node.get('max','none'),'unique':node.get('unique',False)}
    if 'enum' in node:return 'ONE string: '+ ' | '.join(node['enum'])
    if 'role' in node:return 'ONE '+node['role']+' ID string from supplied directory/state'
    if typ=='number':return 'finite JSON number, not boolean/null'
    return typ+(' nonempty' if node.get('nonempty') else '')


def grammar():
    c=contract()
    return {'protocol':VERSION, 'root':compact(c['root']),
        'root_instruction':'The output itself has exactly specification and plan at its root. Do not wrap it in decision. Examples show the actual output root.',
        'cross_field_rules':c['cross_field_rules'],
        'constraint_common':{k:compact(v) for k,v in COMMON.items()},
        'constraint_specific_required':{t:{k:compact(v) for k,v in fs.items()}
            for t,fs in TYPE_FIELDS.items()},
        'constraint_units':prior.UNITS,
        'expression_forms':compact(c['definitions']['expression']),
        'interval_forms':compact(c['definitions']['bounds']),
        'metadata_policy':c['metadata_policy'],'expression_depth_limit':4,
        'rules':['Each constraint combines ALL common and type-specific fields; no null, option arrays or extra fields.',
            'A raw number is NOT an expression. Wrap numbers as {"op":"literal","value":NUMBER,"unit":"MW"}.',
            'Baseline references must name the chosen state/quantity/object set; binder does arithmetic only.',
            'All constraints are read literally; stage, direction, preservation and allocation are not supplied by the program.']}


def brief(value):
    if isinstance(value,dict):return {'actual_type':'object','keys':sorted(value)}
    if isinstance(value,list):return {'actual_type':'array','length':len(value),'sample':value[:3]}
    return {'actual_type':type(value).__name__,'value':value[:100] if isinstance(value,str) else value}


def parse_decision(content,catalog,snapshot,policies,allowed):
    out={'schema_valid':False,'diagnostics':[],'unchecked':[],'errors':[],
         'raw_decision':None,'wrapped_decision':None,'generated_expression':None,
         'expansion':None,'plan':None,'output_repaired':False}
    c=contract(); problems=out['diagnostics']; unchecked=out['unchecked']
    def error(path,kind,value,node,info=None):
        problems.append({'field_path':path,'category':kind,'actual':brief(value),
            'expected':compact(node),'interface_instruction':info or 'Use exactly this public contract shape; no physical requirement is supplied.',
            'hidden_requirement_answer_provided':False})
    def skip(path,node,reason):
        if node.get('type')=='object':
            children=[path+'.'+k for k in node['fields']]
        elif node.get('type')=='array':children=[path+'[*]']
        else:children=[path+'.children']
        unchecked.append({'field_path':path,'children':children,'status':'not_checked','reason':reason})
    def walk(v,node,path,depth=0):
        if 'ref' in node:
            if node['ref']=='expression' and depth>4:
                error(path,'expression_depth',v,{'type':'number'},'Expression depth must be <=4.');return
            walk(v,c['definitions'][node['ref']],path,depth);return
        if 'variant' in node:
            if not isinstance(v,dict):
                error(path,'type',v,{'type':'object','fields':node['common'],'optional':{},'extra':False},
                      'Choose one typed object form from '+node['variant']+'. Bare numbers/arrays are not typed expressions.')
                skip(path,node,'parent is not an object');return
            tag=v.get(node['variant'])
            if not isinstance(tag,str) or tag not in node['choices']:
                for k,sub in node['common'].items():
                    if k in v:walk(v[k],sub,path+'.'+k,depth)
                    else:error(path+'.'+k,'missing',None,sub)
                unchecked.append({'field_path':path,'status':'not_checked','reason':'type-specific fields unavailable until valid '+node['variant']})
                return
            walk(v,node['choices'][tag],path,depth);return
        typ=node['type']
        valid=(isinstance(v,dict) if typ=='object' else isinstance(v,list) if typ=='array'
               else isinstance(v,str) if typ=='string' else type(v)==bool if typ=='boolean'
               else prior.numeric.t2p.finite(v))
        if not valid:
            error(path,'type',v,node);skip(path,node,'parent type invalid');return
        if typ=='object':
            fs=node['fields']; optional=node['optional']
            extra=sorted(set(v)-set(fs)-set(optional))
            if extra:error(path,'extra_fields',{k:v[k] for k in extra},node)
            for k,sub in list(fs.items())+[(k,n) for k,n in optional.items() if k in v]:
                if k not in v:error(path+'.'+k,'missing',None,sub);skip(path+'.'+k,sub,'field missing')
                else:walk(v[k],sub,path+'.'+k,depth+1 if sub.get('ref')=='expression' and k=='base' else depth)
        elif typ=='array':
            if len(v)<node.get('min',0) or len(v)>node.get('max',float('inf')):error(path,'array_size',v,node)
            if node.get('unique') and len({json.dumps(x,sort_keys=True) for x in v})!=len(v):error(path,'duplicate',v,node)
            for i,x in enumerate(v):walk(x,node['items'],path+'[%d]'%i,depth+1 if node['items'].get('ref')=='expression' else depth)
        elif typ=='string':
            if 'enum' in node and v not in node['enum']:error(path,'enum',v,node)
            if node.get('nonempty') and not v:error(path,'identifier',v,node)
            if 'role' in node:
                role=node['role']; permitted=[snapshot['state_id']] if role=='state' else [a for a,x in catalog.items() if role=='registered' or x['kind']==role]
                if v not in permitted:error(path,'state_reference' if role=='state' else 'object',v,enum(*sorted(permitted)))
    try:
        def unique(pairs):
            result={}
            for k,v in pairs:
                if k in result:raise ValueError('Duplicate JSON key: '+k)
                result[k]=v
            return result
        x=json.loads(content,object_pairs_hook=unique,parse_constant=lambda v:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
        out['raw_decision']=copy.deepcopy(x)
        walk(x,c['root'],'$')
        if isinstance(x,dict):
            if 'decision' in x:
                error('$','root_structure',x,c['root'],
                      'Emit specification and plan directly at the root; decision is not an output container. Do not change physical fields while correcting structure.')
            spec=x.get('specification');plan=x.get('plan')
            if isinstance(spec,dict) and isinstance(spec.get('variables'),dict):
                vars=spec['variables'].get('objects')
                if isinstance(vars,list) and all(isinstance(a,str) for a in vars) and not set(vars).issubset(set(allowed)):
                    error('$.specification.variables.objects','permission',vars,ids('load'),'Authorized adjustable IDs: '+','.join(allowed))
            if isinstance(plan,dict) and isinstance(plan.get('selected'),list):
                selected=plan['selected']
                if all(isinstance(a,str) for a in selected):
                    if not set(selected).issubset(set(allowed)):error('$.plan.selected','permission',selected,ids('load'),'Authorized adjustable IDs: '+','.join(allowed))
                    if plan.get('operation')=='solve' and not selected:error('$.plan.selected','array_size',selected,ids('load'))
                    if plan.get('operation')=='stop' and selected:error('$.plan.selected','logical_consistency',selected,ids('load',True),'stop requires selected=[].')
                    if isinstance(spec,dict) and isinstance(spec.get('variables'),dict) and isinstance(spec['variables'].get('objects'),list):
                        variables=spec['variables']['objects']
                        if all(isinstance(a,str) for a in variables) and not set(selected).issubset(set(variables)):
                            error('$.plan.selected','logical_consistency',selected,ids('load'),'Selected IDs must belong to your declared variables.objects.')
            constraints=spec.get('constraints') if isinstance(spec,dict) else None
            if isinstance(constraints,list):
                seen=set()
                for i,entry in enumerate(constraints):
                    if isinstance(entry,dict) and isinstance(entry.get('id'),str):
                        if entry['id'] in seen:error('$.specification.constraints[%d].id'%i,'duplicate',entry['id'],COMMON['id'])
                        seen.add(entry['id'])
        # Independently validate/bind each structurally valid constraint. No gold is read.
        spec=x.get('specification') if isinstance(x,dict) else None
        root_bad=any(d['field_path'].startswith(('$.specification.baseline_state','$.specification.variables','$.specification.preserve'))
                     or d['field_path']=='$.specification' for d in problems)
        if isinstance(spec,dict) and isinstance(spec.get('constraints'),list) and not root_bad:
            shell=copy.deepcopy(spec);shell['schema_version']=prior.VERSION
            for i,entry in enumerate(spec['constraints']):
                prefix='$.specification.constraints[%d]'%i
                if any(d['field_path'].startswith(prefix) for d in problems):
                    unchecked.append({'field_path':prefix+'.binding','status':'not_checked','reason':'constraint has structural errors'});continue
                one=copy.deepcopy(shell);one['constraints']=[entry]
                try:prior.compile_spec(one,catalog,snapshot,policies,allowed)
                except prior.ContractError as exc:
                    d=exc.diagnostic
                    problems.append({'field_path':'$.'+d['field_path'].replace('constraints[0]','constraints[%d]'%i),
                        'category':d['category'],'actual':brief(d['actual']),'expected':d['expected'],
                        'interface_instruction':d['interface_instruction'],'hidden_requirement_answer_provided':False})
        else:
            unchecked.append({'field_path':'$.specification.binding','status':'not_checked','reason':'baseline/variables/preserve or parent container unavailable'})
        if not problems:
            wrapped=copy.deepcopy(x); wrapped['specification']['schema_version']=prior.VERSION
            out['wrapped_decision']=wrapped;out['generated_expression']=wrapped['specification']
            expansion=prior.compile_spec(wrapped['specification'],catalog,snapshot,policies,allowed)
            out.update(schema_valid=True,expansion=expansion,plan=x['plan'],
                metadata_envelope={'protocol':VERSION,'state_reference_version':prior.VERSION,'executable_version':INTERNAL_VERSION,
                    'provided_version':x['specification'].get('schema_version'),'mechanical_metadata_only':True})
    except (ValueError,TypeError,KeyError) as exc:
        error('$','format',str(exc),c['root'],'Return valid finite JSON per the unchanged public contract. No automatic repair.')
    out['errors']=[d['field_path']+': '+d['category'] for d in problems]
    return out


def fictional_example():
    """Independent four-load example, not a renamed E1/E2 answer."""
    cat={}
    for name,p,q in [('FA',40.,12.),('FB',20.,2.),('FC',15.,3.),('FD',5.,1.)]:
        cat[name]={'kind':'load','path':'fictional::'+name,'base_inputs':{'plini':p,'qlini':q}}
    for name,u in [('FX',1.03),('FY',.95)]:
        cat[name]={'kind':'voltage','path':'fictional::'+name,'baseline_voltage_pu':u}
    snap={'state_id':'fictional_base','snapshot_sha256':'fictional-only','quantities':{
        a:dict(v['base_inputs']) if v['kind']=='load' else {'voltage_pu':v['baseline_voltage_pu']} for a,v in cat.items()}}
    policies=prior.policies_from({'P_sum_tolerance_MW':2e-5,'QP_residual_tolerance_Mvar':1e-5,'alpha_read_tolerance':1e-7,'proportional_alpha_tolerance':1e-7})
    def row(cid,typ,clause,**values):
        r=dict(id=cid,type=typ,unit=prior.UNITS[typ],timing='every_accepted_state',clause=clause);r.update(values);return r
    constraints=[
        row('move','transfer','C1',source=['FA','FB'],destination=['FC'],amount={'op':'scale','factor':.005,
            'base':{'op':'baseline_sum','state':'fictional_base','quantity':'plini','objects':['FA','FB']}},accuracy='P_SUM_V1'),
        row('equal_source','proportional_distribution','C2',objects=['FA','FB'],precision='PROP_ALPHA_V1'),
        row('free_dest','distribution','C2',objects=['FC'],mode='free'),
        row('sum','input_sum','C3',objects=['FA','FB','FC','FD'],target={'op':'baseline_sum','state':'fictional_base','quantity':'plini','objects':['FA','FB','FC','FD']},accuracy='P_SUM_V1'),
        row('qp','qp_policy','C4',objects=['FA','FB','FC','FD'],state='fictional_base',policy='each_baseline_ratio',accuracy='QP_RESIDUAL_V1'),
        row('lock','fixed_inputs','C5',objects=['FD'],state='fictional_base',fields=['plini','qlini'],accuracy='FIXED_EXACT_V1'),
        row('limits','alpha_bounds','C5',objects=['FA','FB','FC','FD'],lower=.99,upper=1.02,precision='ALPHA_READ_V1'),
        row('volts','voltage_bounds','C6',objects=['FX','FY'],bounds={'kind':'baseline_band','state':'fictional_base','lower_offset':-.01,'upper_offset':.02},precision='VOLTAGE_EDGE_ZERO_V1')]
    constraints[0]['timing']='final'
    decision={'specification':{'baseline_state':'fictional_base','variables':{'objects':['FA','FB','FC'],'mapping':MAPPING},
        'constraints':constraints,'preserve':{k:True for k in prior.numeric.retained.PRESERVE}},
        'plan':{'operation':'solve','selected':['FA','FB','FC'],'reason':'fictional example: proportional source, free destination, FD fixed'}}
    return {'origin':'independent fictional syntax fixture, no actual-task gold/solution','catalog':cat,'snapshot':snap,
            'policies':policies,'allowed':['FA','FB','FC'],'decision':decision}


def independent_score(parsed,task,state):
    """Isolated gold scoring. Its output must NEVER enter correction messages."""
    result={'qualified':False,'status':'undecided','independent_only':True,
            'runtime_repair':False,'numerical_search_calls':0}
    if not parsed['schema_valid']:
        result['status']='not_checked_contract_failure';return result
    spec=parsed['expansion']['numeric_specification'];cat=task['catalog']
    try:
        problem=prior.numeric.build_problem(spec,cat,task['response_matrix'],state,task)
        goldproblem=prior.numeric.build_problem(task['golden'],cat,task['response_matrix'],state,task)
        finite=prior.numeric.semantic_evaluation(spec,task['golden'],cat,problem,goldproblem,task)
        refs=prior.semantic_evaluation(parsed['generated_expression'],parsed['expansion'],task['golden'],cat,task)
        result.update(finite_evaluation=finite,distribution_correct=refs['distribution_correct'],
                      reference_errors=refs['reference_errors'])
        result['qualified']=finite['expression_correct'] and refs['distribution_correct'] and not refs['reference_errors']
        result['status']='qualified_within_finite_rules' if result['qualified'] else (
            'undecided' if finite.get('equivalence_status')=='missing_conflicting_or_unproven'
            and any(r['status']=='undetermined' for r in finite.get('original_requirements',[]))
            else 'not_equivalent_or_missing')
    except (ValueError,TypeError,KeyError) as exc:
        result.update(status='undecided_build_or_baseline_condition',error_type=type(exc).__name__,error=str(exc))
    return result
