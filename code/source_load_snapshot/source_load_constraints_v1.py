# -*- coding: utf-8 -*-
"""Finite source/load extension; reuses the existing active-face solver.

Physical controls are load alpha and generator pgini increments in MW. A fixed
diagonal coordinate change expresses both in registered engineering step units.
No task IDs, device names, gold specifications, or physical search are used.
Python 3.4 compatible for native independent reconstruction.
"""
import copy
import json
import math
from . import redistribution_constraints_v1 as retained
from . import t2p
from .h3_numeric import signature, pf_unit

VERSION = 'source-load-constraints-v1'
PRESERVE = retained.retained.PRESERVE + ['other_source_inputs']
TYPES = dict(retained.retained.TYPES, **retained.EXTRA)
TYPES.update({
    'generator_delta_bounds': ('generator', 'MW', ['lower','upper']),
    'generator_delta_sum': ('generator', 'MW', ['value']),
    'fixed_generator': ('generator', 'MW', []),
    'generator_output_bounds': ('source', None, ['field','lower','upper']),
    'line_active_power_bounds': ('line', 'MW', ['lower','upper'])})


def contract():
    return dict(root_required_only=['schema_version','reference_state','variables','constraints','preserve'],
        schema_version=VERSION, reference_state='ONE registered state ID',
        variables=dict(required_only=['loads','generators'],loads='unique allowed load IDs, may be []',
                       generators='unique allowed non-reference generator IDs, may be []; at least one variable total'),
        constraints=dict(each_required_only=['id','type','objects','values','unit','tolerance','timing','clause'],
            id='unique nonempty string', objects='nonempty unique legal IDs of the indicated role',
            timing='ONE string: baseline OR every_accepted_state OR final; every_accepted_state covers baseline and final',
            clause='source clause ID; several clauses may use the same source ID; a source ID is not a proof',
            types={k:dict(role=v[0],unit=v[1] or 'MW if field P, Mvar if field Q; fixed_parameter uses plini MW/qlini Mvar',values_required_only=v[2]) for k,v in TYPES.items()},
            notes=['All rows conjoin; later rows never replace earlier rows. No empty optional row.',
                'input_sum_delta is current load plini sum minus the SAME reference sum; no hand calculation needed.',
                'baseline_qp preserves EACH load own baseline Q/P; proportional_change imposes equal absolute load alphas.',
                'generator_delta_bounds and generator_delta_sum refer to pgini-Pgini0 in MW, not alpha and not computed Q.',
                'fixed_generator fixes pgini exactly to its own baseline; generator Q and balancing outputs may vary.',
                'generator_output_bounds field is P or Q and uses actual AC m:P:bus1/m:Q:bus1. Exactly one source per row.',
                'Each voltage/line interval applies to ONE object. line_active_power_bounds uses signed m:P:bus1 in MW at public bus1 endpoint.',
                'Intervals are absolute; their tolerance is separate. Baseline need not satisfy final-only goals.',
                'Continuous alpha and generator MW values are computed by the common numerical tool; do not return a solution.']),
        preserve=dict(required_only=PRESERVE,values='boolean true when required by the original; other_source_inputs excludes explicitly permitted pgini writes, but includes their Q/voltage/control inputs'),
        mechanical_mapping='Program applies P=P0*alpha,Q=Q0*alpha; generator Pgini=Pgini0+delta_MW. Nonvariable controls keep baseline.')


def parse(content,catalog,task,finish_reason=None,canonical=False):
    result=dict(schema_valid=False,compiled_specification=None,errors=[],output_repaired=False)
    path='$'
    try:
        if finish_reason=='length': raise ValueError('Truncated final answer (finish_reason=length)')
        def unique(pairs):
            d={}
            for k,v in pairs:
                if k in d:raise ValueError('Duplicate JSON key: '+k)
                d[k]=v
            return d
        x=json.loads(content,object_pairs_hook=unique,parse_constant=lambda s:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
        t2p.exact_fields(x,['schema_version','reference_state','variables','constraints','preserve'])
        if x['schema_version']!=VERSION:raise ValueError('Wrong schema_version')
        if x['reference_state']!=task['reference_state']:raise ValueError('Unknown/conflicting reference state')
        t2p.exact_fields(x['variables'],['loads','generators'])
        t2p.exact_fields(x['preserve'],PRESERVE)
        if any(type(v)!=bool for v in x['preserve'].values()):raise ValueError('Preserve values must be booleans')
        reg={v['path'] if canonical else a:v for a,v in catalog.items()}
        def bind(items,role,allow_empty=False):
            if not isinstance(items,list) or (not allow_empty and not items):raise ValueError('Nonempty legal ID array required')
            if any(not isinstance(a,str) or a not in reg for a in items):raise ValueError('Unknown object ID')
            if len(set(items))!=len(items):raise ValueError('Duplicate object ID')
            if any(reg[a]['kind']!=role and not (role=='source' and reg[a]['kind'] in ('generator','balance')) for a in items):raise ValueError('Wrong object role')
            return [reg[a]['path'] for a in items]
        y=copy.deepcopy(x)
        for key,role in [('loads','load'),('generators','generator')]:
            path='$.variables.'+key
            y['variables'][key]=bind(x['variables'][key],role,True)
            allowed=task['allowed_modifiable_paths'] if key=='loads' else task['allowed_generator_paths']
            if not set(y['variables'][key]).issubset(set(allowed)):raise ValueError('Variables exceed frozen task write permission')
        if not y['variables']['loads'] and not y['variables']['generators']:raise ValueError('At least one variable required')
        if not isinstance(x['constraints'],list):raise ValueError('constraints must be an array')
        ids=set()
        for i,c in enumerate(x['constraints']):
            path='$.constraints[%d]'%i
            t2p.exact_fields(c,['id','type','objects','values','unit','tolerance','timing','clause'])
            if not isinstance(c['id'],str) or not c['id'] or c['id'] in ids:raise ValueError('Unique nonempty constraint id required')
            ids.add(c['id'])
            if not isinstance(c['type'],str) or c['type'] not in TYPES:raise ValueError('Unsupported constraint type')
            role,unit,fields=TYPES[c['type']]
            t2p.exact_fields(c['values'],fields)
            if c['timing'] not in ('baseline','final','every_accepted_state'):raise ValueError('Wrong timing enum')
            if not isinstance(c['clause'],str) or not c['clause']:raise ValueError('Nonempty source clause ID required')
            if not t2p.finite(c['tolerance']) or c['tolerance']<0:raise ValueError('Finite nonnegative tolerance required')
            if any(not t2p.finite(v) for k,v in c['values'].items() if k!='field'):raise ValueError('Finite numeric values required')
            y['constraints'][i]['objects']=bind(c['objects'],role)
            if c['type'] not in ('alpha_bounds','active_power_sum','input_sum_delta','baseline_qp','proportional_change','generator_delta_bounds','generator_delta_sum','fixed_generator') and len(c['objects'])!=1:
                raise ValueError('Exactly one object for this type')
            if c['type']=='fixed_parameter':
                if c['values']['field'] not in ('plini','qlini'):raise ValueError('Load fixed field must be plini or qlini')
                unit='MW' if c['values']['field']=='plini' else 'Mvar'
            if c['type']=='generator_output_bounds':
                if c['values']['field'] not in ('P','Q'):raise ValueError('Source output field must be P or Q')
                unit='MW' if c['values']['field']=='P' else 'Mvar'
            if c['unit']!=unit:raise ValueError('Wrong unit: expected '+str(unit))
            if 'lower' in c['values'] and c['values']['lower']>c['values']['upper']:raise ValueError('Reversed interval')
            if c['type']=='voltage_target' and c['tolerance']<=0:raise ValueError('Positive point-target tolerance required')
            if c['type']=='alpha_bounds':
                if any(not task['actuator_bounds'][p]['lower']<=c['values']['lower']<=c['values']['upper']<=task['actuator_bounds'][p]['upper'] for p in y['constraints'][i]['objects']):
                    raise ValueError('Declared load bounds exceed registered task permission')
            if c['type']=='generator_delta_bounds':
                permissions={r['path']:r for r in task['source_load']['generators']}
                if any(p not in permissions or not permissions[p]['lower_MW']-permissions[p]['base_pgini_MW']<=c['values']['lower']<=c['values']['upper']<=permissions[p]['upper_MW']-permissions[p]['base_pgini_MW'] for p in y['constraints'][i]['objects']):
                    raise ValueError('Declared generator bounds exceed registered task permission')
        result.update(schema_valid=True,compiled_specification=y)
    except (ValueError,TypeError,KeyError) as exc:
        result['errors']=[dict(path=path,category='contract',message=str(exc))]
    return result


def observed(record,path,field):
    key=path+'|'+field
    if key in record['result_snapshot']['key_results']:
        item=record['result_snapshot']['key_results'][key]
    elif path in record['result_snapshot'].get('line_observations',{}):
        item=record['result_snapshot']['line_observations'][path]['results'][field]
    else:item=record['source_outputs'][path]['fields'][field]
    unit='p.u.' if field=='m:u' else '%' if field=='c:loading' else 'MW' if field=='m:P:bus1' else 'Mvar'
    if pf_unit(item.get('unit'),field)!=unit or not t2p.finite(item.get('value')):
        raise ValueError('Unverified physical result value/unit: '+key)
    return item['value']


def evaluate(spec,catalog,record,phase='final',baseline_record=None):
    cat={v['path']:v for v in catalog.values()}
    rows=[]
    for c in spec['constraints']:
        applicable=c['timing']=='every_accepted_state' or c['timing']==phase
        rec=baseline_record if c['timing']=='baseline' and phase!='baseline' else record
        if rec is None:rec=record
        typ=c['type'];ps=c['objects'];v=c['values'];tol=c['tolerance']
        values=None;passed=False;error=None;margin=None
        valid=rec.get('valid') and rec.get('fixed_conditions_match') and rec.get('controls_unchanged')
        if valid:
            loads=rec['actual_inputs'];gens=rec.get('actual_generator_inputs',{})
            if typ=='input_sum_delta':
                values=math.fsum(loads[p]['plini']-cat[p]['base_inputs']['plini'] for p in ps);error=abs(values-v['delta'])
            elif typ=='active_power_sum':values=math.fsum(loads[p]['plini'] for p in ps);error=abs(values-v['value'])
            elif typ=='baseline_qp':
                values={p:loads[p]['qlini']-cat[p]['base_inputs']['qlini']/cat[p]['base_inputs']['plini']*loads[p]['plini'] for p in ps};error=max(abs(x) for x in values.values())
            elif typ=='qp_ratio':values=loads[ps[0]]['qlini']-v['ratio']*loads[ps[0]]['plini'];error=abs(values)
            elif typ=='fixed_parameter':values=loads[ps[0]][v['field']];error=abs(values-v['value'])
            elif typ=='fixed_generator':
                values={p:gens[p]['pgini']-cat[p]['base_pgini_MW'] for p in ps};error=max(abs(x) for x in values.values())
            elif typ=='generator_delta_sum':values=math.fsum(gens[p]['pgini']-cat[p]['base_pgini_MW'] for p in ps);error=abs(values-v['value'])
            elif typ=='proportional_change':values={p:loads[p]['plini']/cat[p]['base_inputs']['plini'] for p in ps};error=max(values.values())-min(values.values())
            elif typ in ('alpha_bounds','generator_delta_bounds'):
                values={p:(loads[p]['plini']/cat[p]['base_inputs']['plini'] if typ=='alpha_bounds' else gens[p]['pgini']-cat[p]['base_pgini_MW']) for p in ps}
                margin=min(min(x-v['lower']+tol,v['upper']+tol-x) for x in values.values());passed=margin>=0
            else:
                field='m:u' if typ.startswith('voltage') else 'c:loading' if typ=='line_loading_bounds' else 'm:P:bus1' if typ=='line_active_power_bounds' or v.get('field')=='P' else 'm:Q:bus1'
                values=observed(rec,ps[0],field)
                if typ=='voltage_target':error=abs(values-v['value'])
                else:margin=min(values-v['lower']+tol,v['upper']+tol-values);passed=margin>=0
            if error is not None:margin=tol-error;passed=error<=tol
        rows.append(dict(constraint_id=c['id'],type=typ,objects=ps,timing=c['timing'],clause=c['clause'],
                         applicable=applicable,current_value=values,error=error,margin=margin,**{'pass':passed}))
    guards=dict(valid=bool(record.get('valid')),fixed_conditions=bool(record.get('fixed_conditions_match')),
                controls=bool(record.get('controls_unchanged')),other_load_inputs=bool(record.get('other_load_inputs_unchanged')),
                source_input_guard=record.get('source_input_guard_passed') is True,
                source_calculated_controls=record.get('source_calculated_controls_unchanged') is True,
                known_source_model_bounds=record.get('source_model_bound_checks',{}).get('pass') is True,
                preserve_all=all(spec['preserve'].values()))
    return dict(checks=rows,context_guards=guards,phase_satisfied=all(guards.values()) and all(r['pass'] for r in rows if r['applicable']),
                all_requirements=all(guards.values()) and all(r['pass'] for r in rows),
                process_conditions=all(guards.values()) and all(r['pass'] for r in rows if r['timing']!='final'))


def build_problem(spec,catalog,matrix,current,task):
    validation=parse(json.dumps(spec),catalog,task,canonical=True)
    if not validation['schema_valid']:raise ValueError(validation['errors'])
    baseline=current['baseline_record'];admission=evaluate(spec,catalog,baseline,phase='baseline')
    if not admission['phase_satisfied']:raise ValueError('Declared baseline requirements fail admission')
    binding=matrix['shared_binding']
    for k in ('project_path','study_case_path','network_path'):
        if binding[k]!=task[k]:raise ValueError('Mixed response identity mismatch')
    if (binding['controls_sha256']!=signature(current['record']['controls']) or
        binding['baseline_inputs_sha256']!=signature(baseline['actual_inputs']) or
        binding['generator_inputs_sha256']!=signature(baseline['actual_generator_inputs']) or
        binding['line_metadata_sha256']!=signature(task['reference_line_metadata'])):
        raise ValueError('Mixed response baseline/control/input/line binding mismatch')
    if current['version']!=0:raise ValueError('This bounded extension uses one baseline candidate, no response update')
    cat={v['path']:v for v in catalog.values()}
    paths=sorted(spec['variables']['loads']+spec['variables']['generators'])
    loadpaths=sorted(p for p,v in cat.items() if v['kind']=='load')
    genpaths=sorted(p for p,v in cat.items() if v['kind']=='generator')
    scales=task['source_load']['normalization']
    eq=[];ineq=[];centers=[];volts={};lines={};observations={};consumed={}
    def row(c,coeff,value,tol,center=False):
        a=[coeff.get(p,0.) for p in paths]
        ineq.extend([dict(id=c['id']+' upper',a=a,b=value+tol),dict(id=c['id']+' lower',a=[-x for x in a],b=-value+tol)])
        if center:centers.append(dict(id=c['id']+' center',a=a,b=value))
    for p in paths:
        if cat[p]['kind']=='load':lo,hi=task['actuator_bounds'][p]['lower'],task['actuator_bounds'][p]['upper'];s=scales[p];lo=(lo-1)/s;hi=(hi-1)/s
        else:
            perm=next(r for r in task['source_load']['generators'] if r['path']==p);s=scales[p]
            lo=(perm['lower_MW']-perm['base_pgini_MW'])/s;hi=(perm['upper_MW']-perm['base_pgini_MW'])/s
        ineq.extend([dict(id='permission '+p+' upper',a=[1. if q==p else 0. for q in paths],b=hi),
                     dict(id='permission '+p+' lower',a=[-1. if q==p else 0. for q in paths],b=-lo)])
    for c in sorted(spec['constraints'],key=lambda x:json.dumps({k:v for k,v in x.items() if k!='id'},sort_keys=True)):
        typ=c['type'];ps=c['objects'];v=c['values'];tol=c['tolerance']
        consumed[c['id']]=dict(type=typ,objects=ps,timing=c['timing'],clause=c['clause'],consumer='baseline_admission_only' if c['timing']=='baseline' else 'joint_local_problem_and_actual_acceptance')
        if c['timing']=='baseline':continue
        if typ=='input_sum_delta':row(c,{p:cat[p]['base_inputs']['plini']*scales[p] for p in ps},v['delta'],tol,True)
        elif typ=='active_power_sum':row(c,{p:cat[p]['base_inputs']['plini']*scales[p] for p in ps},v['value']-math.fsum(cat[p]['base_inputs']['plini'] for p in ps),tol,True)
        elif typ=='baseline_qp':pass # The explicitly registered actuator mapping enforces it; actual residual still checked.
        elif typ=='qp_ratio':
            p=ps[0];base=cat[p]['base_inputs'];d=base['qlini']-v['ratio']*base['plini'];row(c,{p:d*scales[p]},-d,tol)
        elif typ=='fixed_parameter':
            p=ps[0];base=cat[p]['base_inputs'][v['field']];row(c,{p:base*scales[p]},v['value']-base,tol,True)
        elif typ=='fixed_generator':
            for p in ps:row(dict(c,id=c['id']+p),{p:scales[p]},0.,tol,True)
        elif typ=='generator_delta_sum':row(c,{p:scales[p] for p in ps},v['value'],tol,True)
        elif typ=='proportional_change':
            for p in ps[1:]:row(dict(c,id=c['id']+p),{p:scales[p],ps[0]:-scales[ps[0]]},0.,tol,True)
        elif typ in ('alpha_bounds','generator_delta_bounds'):
            for p in ps:
                origin=1. if typ=='alpha_bounds' else 0.
                row(dict(c,id=c['id']+p),{p:scales[p]},(v['upper']+v['lower'])/2-origin,(v['upper']-v['lower'])/2+tol)
        else:
            field='m:u' if typ.startswith('voltage') else 'c:loading' if typ=='line_loading_bounds' else 'm:P:bus1' if typ=='line_active_power_bounds' or v.get('field')=='P' else 'm:Q:bus1'
            key=ps[0]+'|'+field
            if key not in matrix['observations']:raise ValueError('Missing verified mixed response row: '+key)
            source=matrix['observations'][key];origin=observed(baseline,ps[0],field)
            coefficients={p:source['slopes'][p]*scales[p] for p in paths}
            if typ=='voltage_target':row(c,coefficients,v['value']-origin,tol)
            else:row(c,coefficients,(v['lower']+v['upper'])/2-origin,(v['upper']-v['lower'])/2+tol)
            obs=dict(a=[coefficients[p] for p in paths],intercept=origin,field=field,path=ps[0],unit=c['unit'])
            observations[key]=obs
            if field=='m:u':volts[ps[0]]=obs
            elif field=='c:loading':lines[ps[0]]=obs
    return dict(version=VERSION,paths=paths,current_alphas={p:0. for p in paths},fixed_alphas={},equalities=eq,
                inequalities=ineq,preferred_target_centers=centers,voltage_rows=volts,line_rows=lines,
                observation_rows=observations,normalization=scales,
                physical_mapping=dict(loads=loadpaths,generators=genpaths,baseline_generator_inputs=baseline['actual_generator_inputs']),
                generated_spec_sha256=signature(spec),baseline_admission=admission,constraint_consumption=consumed,
                objective='sum((alpha-1)/registered_alpha_step)^2 + sum(delta_pgini_MW/registered_MW_step)^2; existing centers-first then tolerance-band active-face projection')


def solve(problem):
    raw=retained.solve(problem)
    if raw['status']!='candidate':return raw
    coordinates=raw['alphas'];mapping=problem['physical_mapping'];scale=problem['normalization']
    alphas={p:1.+coordinates.get(p,0.)*scale[p] for p in mapping['loads']}
    deltas={p:coordinates.get(p,0.)*scale[p] for p in mapping['generators']}
    pgini={p:mapping['baseline_generator_inputs'][p]['pgini']+deltas[p] for p in mapping['generators']}
    result=dict(raw,normalized_coordinates=coordinates,alphas=alphas,generator_delta_MW=deltas,generator_pgini_MW=pgini,
                predictions={key:r['intercept']+math.fsum(a*coordinates[p] for a,p in zip(r['a'],problem['paths'])) for key,r in problem['observation_rows'].items()},
                objective_interpretation=problem['objective'],not_an_economic_dispatch_cost=True)
    return result


def residual_margin_problem(problem, spec, task, baseline, witness):
    """One candidate-only offset+abs(residual) transform, original acceptance.

    Adaptation of core_mechanism_closeout_v2's registered rule to observation
    rows with mixed coordinates. No change to slopes, objective or permissions.
    The rejected point supplies error evidence, never an accepted-state anchor.
    """
    import copy
    if witness.get('version')!='mixed-residual-margin-v1' or witness.get('coefficient')!=1.0:
        raise ValueError('Unregistered residual-margin rule')
    if witness['task_sha256']!=signature(task) or witness['response_sha256']!=signature(task['response_matrix']):
        raise ValueError('Residual witness task/response mismatch')
    wb=witness['baseline'];record=witness['record'];point=witness['candidate'];source=witness['problem']
    for key in ('actual_inputs','actual_generator_inputs','controls','settings_after','source_calculated_control_state'):
        if wb[key]!=baseline[key]:raise ValueError('Residual witness baseline mismatch: '+key)
    if not record['valid'] or witness['restoration']!='passed':
        raise ValueError('Residual witness lacks valid AC/restoration')
    for key in ('controls','settings_after','source_calculated_control_state'):
        if record[key]!=baseline[key]:raise ValueError('Residual witness changed control context: '+key)
    if record['local_problem_sha256']!=signature(source) or record['alphas']!=point['alphas']:
        raise ValueError('Residual point/prediction identity mismatch')
    for entry in task['source_load']['generators']:
        p=entry['path']
        if abs(record['actual_generator_inputs'][p]['pgini']-point['generator_pgini_MW'][p])>entry['input_readback_tolerance_MW']:
            raise ValueError('Residual generator readback mismatch')
    if source['normalization']!=problem['normalization']:
        raise ValueError('Residual normalization mismatch')
    rebuilt=build_problem(witness['specification'],task['catalog'],task['response_matrix'],
        dict(version=0,alphas=baseline['alphas'],record=baseline,baseline_record=baseline),task)
    if rebuilt!=source:raise ValueError('Residual source problem reconstruction mismatch')
    for key,r in problem['observation_rows'].items():
        sr=source['observation_rows'][key]
        if any(r[k]!=sr[k] for k in ('intercept','field','path','unit')):
            raise ValueError('Residual observation identity mismatch')
        for p,a in zip(problem['paths'],r['a']):
            if p not in source['paths'] or a!=sr['a'][source['paths'].index(p)]:
                raise ValueError('Residual response column mismatch')
        for p in set(source['paths'])-set(problem['paths']):
            if point['normalized_coordinates'][p]!=0.:
                raise ValueError('Eliminated residual coordinate is not fixed zero')
    errors={}
    for key,r in source['observation_rows'].items():
        predicted=r['intercept']+math.fsum(a*point['normalized_coordinates'][p] for a,p in zip(r['a'],source['paths']))
        if abs(predicted-point['predictions'][key])>1e-12:raise ValueError('Residual prediction mismatch')
        actual=observed(record,r['path'],r['field'])
        errors[key]=dict(actual=actual,predicted=predicted,error=actual-predicted,margin=abs(actual-predicted),unit=r['unit'])
    result=copy.deepcopy(problem);transforms=[]
    eligible=('voltage_bounds','voltage_target','line_loading_bounds','line_active_power_bounds','generator_output_bounds')
    for c in spec['constraints']:
        if c['type'] not in eligible or c['timing']=='baseline':continue
        typ=c['type'];v=c['values'];tol=c['tolerance'];p=c['objects'][0]
        field='m:u' if typ.startswith('voltage') else 'c:loading' if typ=='line_loading_bounds' else 'm:P:bus1' if typ=='line_active_power_bounds' or v.get('field')=='P' else 'm:Q:bus1'
        er=errors[p+'|'+field];e,m=er['error'],er['margin']
        lo=v['value']-tol if typ=='voltage_target' else v['lower']-tol
        hi=v['value']+tol if typ=='voltage_target' else v['upper']+tol
        if lo+m>hi-m:raise ValueError('Empty residual-margin interval: '+c['id'])
        upper=next(r for r in result['inequalities'] if r['id']==c['id']+' upper')
        lower=next(r for r in result['inequalities'] if r['id']==c['id']+' lower')
        upper['b']-=e+m;lower['b']+=e-m
        transforms.append(dict(constraint_id=c['id'],observation=p+'|'+field,original=[lo,hi],
            internal_raw_prediction=[lo+m-e,hi-m-e],error=e,margin=m,timing=c['timing']))
    result['residual_margin']=dict(version=witness['version'],witness_sha256=signature(witness),
        errors=errors,transforms=transforms,acceptance_unchanged=True,baseline_objective_unchanged=True)
    return result


def semantic_view(spec):
    """Only already exact typed meaning: IDs/order do not change conjunction."""
    def normal(x):
        if isinstance(x,dict):return {k:normal(v) for k,v in x.items() if k not in ('id','clause')}
        if isinstance(x,list):return sorted([normal(v) for v in x],key=lambda v:json.dumps(v,sort_keys=True))
        return x
    return normal(spec)
