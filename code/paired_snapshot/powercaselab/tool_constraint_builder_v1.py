"""Thin, explicit constraint-building tools for the F/T contribution comparison.

T does NOT call compile_spec/parse_decision of the declarative F interface.
It explicitly adds primitive numerical relations, using shared state arithmetic
and the unchanged numerical/PF contract. No task answer or task-name branch.
Standard library, Python 3.4 compatible.
"""
import copy
import json
from . import state_reference_constraints_v2_1 as wire

numeric = wire.prior.numeric
VERSION = 'explicit-constraint-tools-v1'
MAPPING = 'baseline_PQ_times_absolute_alpha'
ROOT_FIELDS = ['baseline_state', 'variables', 'calls', 'preserve', 'plan']
TOOLS = {
    'input_sum_delta': ('load', 'MW', ['delta'], 'P_SUM_V1'),
    'active_power_sum': ('load', 'MW', ['value'], 'P_SUM_V1'),
    'baseline_qp': ('load', 'Mvar', [], 'QP_RESIDUAL_V1'),
    'alpha_bounds': ('load', 'dimensionless', ['lower', 'upper'], 'ALPHA_READ_V1'),
    'fixed_parameter': ('load', None, ['field', 'value'], 'FIXED_EXACT_V1'),
    'voltage_bounds': ('voltage', 'pu', ['lower', 'upper'], 'VOLTAGE_EDGE_ZERO_V1'),
    'proportional_change': ('load', 'dimensionless', [], 'PROP_ALPHA_V1')}


def grammar():
    return {'protocol': VERSION,
        'root_required_only': list(ROOT_FIELDS),
        'root_instruction': 'These fields are directly at the output root; no decision wrapper.',
        'cross_field_rules': wire.retained.interface_rules(),
        'variables': {'objects': 'nonempty unique authorized load ID array', 'mapping': MAPPING},
        'calls': {'shape': 'array of explicit tool calls; batching is allowed in one answer',
            'constraint_call_required_only': ['id','tool','type','objects','values','unit','policy','timing','clause','each'],
            'tool': 'ONE string constraint',
            'types': {k:{'role':v[0],'unit':v[1] or 'MW for plini; Mvar for qlini',
                'values_required_only':v[2],'policy':v[3]} for k,v in TOOLS.items()},
            'free_call_required_only': ['id','tool','objects','timing','clause'],
            'free_tool': 'ONE string free_allocation; no equation or numeric tolerance',
            'each': 'boolean. true explicitly iterates objects and substitutes $object in expressions; fixed_parameter and voltage_bounds require one object per constructed row (use each:true for a batch).',
            'values': 'finite numbers or typed expressions; fixed_parameter.field is ONE string plini/qlini. baseline_qp/proportional_change values is {}.',
            'timing': 'ONE string baseline/every_accepted_state/final',
            'clause': 'ONE source tag C1..C7 chosen to cite original text; does not certify semantics',
            'id': 'unique nonempty string'},
        'state_arithmetic': dict(wire.prior.grammar()['expressions'],
            offset=['op=offset','base=typed expression','value=number in SAME unit; result=base+value']),
        'baseline_state': 'supplied state_id; baseline_qp uses this explicit reference',
        'preserve': {k:'required boolean' for k in numeric.retained.PRESERVE},
        'plan': {'operation':'ONE solve/stop string','selected':'unique authorized load ID array (empty for stop)','reason':'short string'},
        'semantics': [
            'input_sum_delta explicitly constructs SUM(plini) - its OWN baseline SUM = delta. Add source and destination relations yourself; no automatic transfer macro.',
            'active_power_sum explicitly constructs SUM(plini)=value. baseline_sum reads exactly the supplied object set.',
            'baseline_qp preserves EACH listed load own baseline ratio; the shared numeric kernel performs the ratio arithmetic.',
            'proportional_change explicitly enforces equal multipliers for its set; free_allocation adds NO equation.',
            'Fixed inputs: add separate fixed_parameter calls for plini and qlini. Values may read baseline_value of $object with each:true.',
            'Voltage bands: add voltage_bounds calls with explicit lower and upper expressions. offset(baseline_value(voltage_pu), offset) computes each bus own interval.',
            'All rows enter the SAME bounded solver, actual evaluator and stage rules as F. No generated Python or hidden requirement completion.',
            'Mechanical internal schema version is wrapped by program. This is NOT the F declarative specification/transfer expander.']}


def parse(text, catalog, snapshot, policies, allowed, finish_reason=None, _validate_calls=True,
          actuator_bounds=None):
    fmt, content = wire.root_format(text, finish_reason)
    result = {'schema_valid':False,'raw_contract_valid':False,'format_diagnosis':fmt,
        'diagnostics':[],'unchecked':[],'errors':[],'output_repaired':False,
        'original_text_preserved':True,'adapter_version':VERSION}
    def fail(path, category, actual, expected):
        raise wire.prior.ContractError(path,category,actual,expected,
            'Use the frozen public tool shape; select semantics from unchanged original requirements. No hidden answer supplied.')
    def fields(x, required, path):
        if not isinstance(x,dict):fail(path,'type',type(x).__name__,'object')
        if set(x)!=set(required):fail(path,'fields',sorted(x),
            {'required_root_keys':required,'instruction':'Emit these keys directly at the root; no decision wrapper.'} if path=='$' else required)
    if content is None:
        result['diagnostics']=[{'field_path':'$','category':fmt['category'],'actual_type':type(text).__name__,
            'expected':'one tool-batch JSON object; optional whole JSON fence only','hidden_requirement_answer_provided':False}]
        result['unchecked']=[{'field_path':'$.calls','status':'not_checked','reason':'invalid root'}]
        return result
    try:
        def unique(pairs):
            obj={}
            for k,v in pairs:
                if k in obj:fail('$','duplicate_key',k,'unique JSON keys')
                obj[k]=v
            return obj
        x=json.loads(content,object_pairs_hook=unique,parse_constant=lambda _: fail('$','nonfinite',None,'finite JSON'))
        result['generated_tool_batch']=copy.deepcopy(x)
        fields(x,ROOT_FIELDS,'$')
        wire.prior.state_id(x['baseline_state'],snapshot,'$.baseline_state')
        fields(x['variables'],['objects','mapping'],'$.variables')
        variables=wire.prior.ids(x['variables']['objects'],catalog,'load','$.variables.objects')
        if not set(variables).issubset(set(allowed)):fail('$.variables.objects','permission',variables,allowed)
        if x['variables']['mapping']!=MAPPING:fail('$.variables.mapping','enum',x['variables']['mapping'],MAPPING)
        fields(x['preserve'],numeric.retained.PRESERVE,'$.preserve')
        if any(type(v)!=bool for v in x['preserve'].values()):fail('$.preserve','type',x['preserve'],'booleans')
        fields(x['plan'],['operation','selected','reason'],'$.plan');plan=x['plan']
        if plan['operation'] not in ('solve','stop') or not isinstance(plan['operation'],str):fail('$.plan.operation','enum',plan['operation'],['solve','stop'])
        if not isinstance(plan['reason'],str):fail('$.plan.reason','type',plan['reason'],'string')
        if plan['operation']=='solve':wire.prior.ids(plan['selected'],catalog,'load','$.plan.selected')
        elif plan['selected']!=[]:fail('$.plan.selected','operation',plan['selected'],[])
        if not set(plan['selected']).issubset(set(variables)):fail('$.plan.selected','permission',plan['selected'],variables)
        if not isinstance(x['calls'],list):fail('$.calls','type',type(x['calls']).__name__,'array')
        # Check independent calls together before executing the batch. A parent
        # failure is not interpreted as successful checking of its children.
        # Both methods get one public repair opportunity with useful paths.
        if _validate_calls and len(x['calls'])>1:
            diagnostics=[]
            for i,call in enumerate(x['calls']):
                singleton=copy.deepcopy(x);singleton['calls']=[call]
                one=parse(json.dumps(singleton),catalog,snapshot,policies,allowed,
                          _validate_calls=False,actuator_bounds=actuator_bounds)
                for d in one.get('diagnostics',[]):
                    d=copy.deepcopy(d);d['field_path']=d['field_path'].replace('$.calls[0]','$.calls[%d]'%i)
                    diagnostics.append(d)
            if diagnostics:
                result.update(diagnostics=diagnostics,errors=[d['field_path']+': '+d['category'] for d in diagnostics],
                    unchecked=[{'field_path':'$.calls.execution','status':'not_checked','reason':'One or more independent call contracts failed; no numerical execution.'}])
                return result
        rows=[];bindings=[];free=[];seen=set()
        def substitute(obj, alias):
            if isinstance(obj,dict):return {k:substitute(v,alias) for k,v in obj.items()}
            if isinstance(obj,list):return [substitute(v,alias) for v in obj]
            return alias if obj=='$object' else obj
        def value(e,path):
            if isinstance(e,dict) and e.get('op')=='offset':
                fields(e,['op','base','value'],path)
                a,u,t=wire.prior.expression(e['base'],catalog,snapshot,path+'.base')
                delta=wire.prior.number(e['value'],path+'.value')
                return a+delta,u,{'expression':e,'base':t,'unit':u,'value':a+delta}
            return wire.prior.expression(e,catalog,snapshot,path)
        for i,c in enumerate(x['calls']):
            path='$.calls[%d]'%i
            if not isinstance(c,dict):fail(path,'type',type(c).__name__,'tool-call object')
            if c.get('tool')=='free_allocation':
                fields(c,['id','tool','objects','timing','clause'],path)
                objects=wire.prior.ids(c['objects'],catalog,'load',path+'.objects');free.append(copy.deepcopy(c))
            else:
                fields(c,['id','tool','type','objects','values','unit','policy','timing','clause','each'],path)
                if c['tool']!='constraint':fail(path+'.tool','enum',c['tool'],'constraint/free_allocation')
                if not isinstance(c['type'],str) or c['type'] not in TOOLS:fail(path+'.type','unsupported',c['type'],sorted(TOOLS))
                role,unit,required,policy=TOOLS[c['type']]
                objects=wire.prior.ids(c['objects'],catalog,role,path+'.objects')
                fields(c['values'],required,path+'.values')
                if type(c['each'])!=bool:fail(path+'.each','type',type(c['each']).__name__,'boolean')
                if c['policy']!=policy:fail(path+'.policy','policy',c['policy'],policy)
                if c['type']=='fixed_parameter':
                    field=c['values']['field']
                    if field not in ('plini','qlini') or not isinstance(field,str):fail(path+'.values.field','enum',field,['plini','qlini'])
                    unit='MW' if field=='plini' else 'Mvar'
                if c['unit']!=unit:fail(path+'.unit','unit',c['unit'],unit)
                groups=[[a] for a in objects] if c['each'] else [objects]
                if c['type'] in ('fixed_parameter','voltage_bounds') and any(len(g)!=1 for g in groups):fail(path+'.each','shape',False,'true for multiple-object fixed/voltage batch')
                for j,group in enumerate(groups):
                    values={};traces=[]
                    for key,e in c['values'].items():
                        if key=='field':values[key]=e;continue
                        selected=substitute(e,group[0]) if c['each'] else e
                        if isinstance(selected,dict):
                            val,u,trace=value(selected,path+'.values.'+key)
                            if u!=unit:fail(path+'.values.'+key,'unit',u,unit)
                            traces.append({'field':key,'trace':trace});values[key]=val
                        else:values[key]=wire.prior.number(selected,path+'.values.'+key)
                    rid=c['id']+'::'+str(j)
                    rows.append(dict(id=rid,type=c['type'],objects=group,values=values,unit=unit,
                        tolerance=policies['policies'][policy]['effective_evaluation_tolerance'],timing=c['timing'],clause=c['clause']))
                    bindings.append({'call_id':c['id'],'constraint_id':rid,'objects':group,'type':c['type'],
                        'source_call':copy.deepcopy(c),'value_traces':traces,'reference_state':x['baseline_state']})
            if not isinstance(c['id'],str) or not c['id'] or c['id'] in seen:fail(path+'.id','identifier',c['id'],'unique nonempty string')
            seen.add(c['id'])
            if not isinstance(c['timing'],str) or c['timing'] not in ('baseline','every_accepted_state','final'):fail(path+'.timing','enum',c['timing'],['baseline','every_accepted_state','final'])
            if c['clause'] not in ['C'+str(k) for k in range(1,8)]:fail(path+'.clause','source',c['clause'],'C1..C7')
        spec=dict(schema_version=numeric.VERSION,variables=x['variables'],constraints=rows,preserve=x['preserve'])
        # Existing common permission contract; omitted keeps historical limits.
        checked=numeric.parse(json.dumps(spec),catalog,actuator_bounds=actuator_bounds)
        if not checked['schema_valid']:fail('$.calls','numeric_contract',checked['errors'],'public retained numerical types')
        result.update(schema_valid=True,raw_contract_valid=fmt['raw_json_format_valid'],plan=plan,
            expansion={'numeric_specification':checked['compiled_specification'],'tool_bindings':bindings,
                'free_declarations':free,'baseline_snapshot_sha256':snapshot['snapshot_sha256'],
                'declarative_F_expander_called':False,'requirements_added_or_replaced':False})
    except wire.prior.ContractError as exc:
        result['diagnostics']=[exc.diagnostic];result['error_category']=exc.diagnostic['category']
    except (ValueError,KeyError,TypeError) as exc:
        result['diagnostics']=[{'field_path':'$','category':'format','actual':str(exc),'expected':'frozen tool batch contract','hidden_requirement_answer_provided':False}]
        result['error_category']='format'
    result['errors']=[d['field_path']+': '+d['category'] for d in result['diagnostics']]
    return result
