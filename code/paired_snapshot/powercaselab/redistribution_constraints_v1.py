# -*- coding: utf-8 -*-
"""Finite redistribution expressions lowered to the retained composable core.

No task IDs, load names, golden specifications or candidate answers are used by
the builder. Input-sum offsets, per-device baseline Q/P, and equal multipliers
are explicit requirement types, not automatically supplied missing clauses.
CPython 3.4 standard library only.
"""
import copy
import itertools
import json
import math
from . import composable_constraints_v1_1 as retained
from . import t2p
from .h3_numeric import signature

VERSION='redistribution-constraints-v1'
EXTRA={'input_sum_delta':('load','MW',['delta']),
       'baseline_qp':('load','Mvar',[]),
       'proportional_change':('load','dimensionless',[])}


def grammar():
    g=retained.grammar()
    g['schema_version']=VERSION
    g['constraints']['types'].update({k:{'objects_role':v[0],'unit':v[1],
        'values_required_only':v[2]} for k,v in EXTRA.items()})
    g['constraints']['notes'] += [
        'input_sum_delta: SUM(current plini)-SUM(baseline plini)=values.delta for the exact objects; positive means increase. No arithmetic by LLM needed.',
        'baseline_qp: for EACH listed load separately Q-current = (its OWN Q0/P0)*P-current; residual in Mvar; values is {}.',
        'proportional_change: all listed loads have equal absolute alpha=P/P0; hence P changes in proportion to baseline P; values is {}.',
        'New group types permit multiple objects. Never replace a voltage interval with a target point.',
        'Numerical plan choices and predictions are separate artifacts; they cannot rewrite requirements.']
    return g


def bases(catalog):
    return {v['path']:v['base_inputs'] for v in catalog.values() if v['kind']=='load'}


def actuator_bounds(catalog, task):
    return retained.resolve_actuator_bounds(catalog, task.get('actuator_bounds'))


def lower(spec,catalog):
    b=bases(catalog); result=copy.deepcopy(spec); result['schema_version']=retained.VERSION
    result['constraints']=[]; mapping={}
    for c in spec['constraints']:
        expanded=[];typ=c['type']
        if typ=='input_sum_delta':
            n=copy.deepcopy(c);n['type']='active_power_sum'
            n['values']={'value':math.fsum(b[p]['plini'] for p in c['objects'])+c['values']['delta']};expanded=[n]
        elif typ=='baseline_qp':
            for p in c['objects']:
                if b[p]['plini']<=0:raise ValueError('Nonpositive baseline P outside supported Q/P semantics')
                n=copy.deepcopy(c);n.update(type='qp_ratio',objects=[p],values={'ratio':b[p]['qlini']/b[p]['plini']});expanded.append(n)
        elif typ=='proportional_change':pass
        else:expanded=[copy.deepcopy(c)]
        mapping[c['id']]=[]
        for i,n in enumerate(expanded):
            n['id']=c['id']+'::'+str(i);mapping[c['id']].append(n['id']);result['constraints'].append(n)
    return result,mapping


def parse(content,catalog,canonical=False,finish_reason=None,actuator_bounds=None):
    out={'schema_valid':False,'compiled_specification':None,'raw_specification':None,
         'errors':[],'error_category':None,'identifier_bindings':[],'output_repaired':False}
    if finish_reason=='length':
        out.update(error_category='truncated',errors=['finish_reason=length']);return out
    category='format'
    try:
        def unique(pairs):
            result={}
            for k,v in pairs:
                if k in result:raise ValueError('Duplicate key: '+k)
                result[k]=v
            return result
        x=json.loads(content,object_pairs_hook=unique,parse_constant=lambda s:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
        out['raw_specification']=x
        t2p.exact_fields(x,['schema_version','variables','constraints','preserve'])
        if x['schema_version']!=VERSION:raise ValueError('Wrong schema_version')
        t2p.exact_fields(x['variables'],['objects','mapping'])
        t2p.exact_fields(x['preserve'],retained.PRESERVE)
        if any(type(v)!=bool for v in x['preserve'].values()):raise ValueError('Preserve fields require booleans')
        if x['variables']['mapping']!='baseline_PQ_times_absolute_alpha':raise ValueError('Unsupported input mapping')
        paths=[v['path'] for v in catalog.values()]
        if len(paths)!=len(set(paths)):raise ValueError('Ambiguous directory')
        registry={v['path'] if canonical else a:a for a,v in catalog.items()}
        def bind(items,kind):
            if not isinstance(items,list) or not items or not all(isinstance(a,str) for a in items):raise ValueError('Nonempty ID array required')
            if len(set(items))!=len(items):raise ValueError('Duplicate ID')
            result=[]
            for a in items:
                if a not in registry or catalog[registry[a]]['kind']!=kind:raise ValueError('Unknown ID or incorrect object role: '+a)
                p=catalog[registry[a]]['path'];result.append(p)
                out['identifier_bindings'].append({'raw':a,'alias':registry[a],'path':p})
            return result
        y=copy.deepcopy(x);category='object';y['variables']['objects']=bind(x['variables']['objects'],'load')
        if not isinstance(x['constraints'],list):raise ValueError('Constraint array required')
        ids=set()
        for i,c in enumerate(x['constraints']):
            category='format';t2p.exact_fields(c,['id','type','objects','values','unit','tolerance','timing','clause'])
            if not isinstance(c['id'],str) or not c['id'] or c['id'] in ids:raise ValueError('Unique nonempty constraint ID required')
            ids.add(c['id'])
            if not isinstance(c['type'],str) or c['type'] not in dict(retained.TYPES,**EXTRA):raise ValueError('Unsupported constraint type')
            typ=c['type'];kind,unit,fields=dict(retained.TYPES,**EXTRA)[typ]
            t2p.exact_fields(c['values'],fields)
            if not isinstance(c['timing'],str) or c['timing'] not in ('baseline','final','every_accepted_state'):raise ValueError('timing must be one enum string')
            if c['clause'] not in ['C'+str(j) for j in range(1,8)]:raise ValueError('Unknown source clause')
            if not t2p.finite(c['tolerance']) or c['tolerance']<0:raise ValueError('Invalid tolerance')
            if any(not t2p.finite(v) for k,v in c['values'].items() if k!='field'):raise ValueError('Finite numeric values required')
            category='object';y['constraints'][i]['objects']=bind(c['objects'],kind)
            if typ in EXTRA and c['unit']!=unit:raise ValueError('Wrong group-constraint unit')
        validation,_=lower(y,catalog)
        checked=retained.parse(json.dumps(validation),catalog,canonical=True,actuator_bounds=actuator_bounds)
        if not checked['schema_valid']:
            category=checked['error_category'];raise ValueError('; '.join(checked['errors']))
        out.update(schema_valid=True,compiled_specification=y)
    except (ValueError,TypeError,KeyError) as error:
        out.update(errors=[str(error)],error_category=category)
    return out


def build_problem(spec,catalog,matrix,current,task):
    permitted_bounds=actuator_bounds(catalog,task)
    checked=parse(json.dumps(spec),catalog,canonical=True,actuator_bounds=permitted_bounds)
    if not checked['schema_valid']:raise ValueError('Contract: '+str(checked['errors']))
    old,mapping=lower(spec,catalog)
    problem=retained.build_problem(old,catalog,matrix,current,task)
    admission=evaluate(spec,catalog,current['baseline_record'],phase='baseline')
    if not admission['phase_satisfied']:raise ValueError('Original submitted process/baseline requirements fail admission')
    paths=problem['paths'];fixed=problem['fixed_alphas']
    # Physical actuator permission is separate from requirement completeness.
    # It cannot be relaxed by an omitted/loose generated bound or by read tolerance.
    for i,p in enumerate(paths):
        unit=[1.0 if j==i else 0.0 for j in range(len(paths))]
        problem['inequalities'] += [{'id':'actuator_permission_upper_'+str(i),'a':unit,'b':permitted_bounds[p]['upper']},
            {'id':'actuator_permission_lower_'+str(i),'a':[-v for v in unit],'b':-permitted_bounds[p]['lower']}]
    problem['hard_actuator_permission']=({'lower':0.99,'upper':1.02,'not_a_compiler_requirement_repair':True}
        if 'actuator_bounds' not in task else {'bounds':permitted_bounds,'source':'frozen_task_actuator_bounds',
            'not_a_compiler_requirement_repair':True})
    for c in spec['constraints']:
        if c['type']!='proportional_change' or c['timing']=='baseline':continue
        for i,(anchor,p) in enumerate(itertools.combinations(sorted(c['objects']),2)):
            coeff={p:1.,anchor:-1.};a=[coeff.get(q,0.) for q in paths]
            offset=math.fsum(coeff.get(q,0.)*v for q,v in fixed.items())
            problem['inequalities'] += [{'id':c['id']+'_%d upper'%i,'a':a,'b':c['tolerance']-offset},
                {'id':c['id']+'_%d lower'%i,'a':[-v for v in a],'b':c['tolerance']+offset}]
            problem['preferred_target_centers'].append({'id':c['id']+'_%d center'%i,'a':a,'b':-offset})
    problem.update(version=VERSION,generated_spec_sha256=signature(spec),baseline_admission=admission,
        lowering_map=mapping,original_constraint_consumption={c['id']:{'type':c['type'],'objects':c['objects'],
            'timing':c['timing'],'clause':c['clause'],'lowered_ids':mapping[c['id']],
            'consumer':'baseline_admission' if c['timing']=='baseline' else 'local_problem_and_actual_feedback'} for c in spec['constraints']})
    return problem


def evaluate(spec,catalog,record,source='actual_PF',phase='final',baseline_record=None):
    old,mapping=lower(spec,catalog)
    result=retained.evaluate(old,catalog,record,source,phase,baseline_record)
    rows={r['constraint_id']:r for r in result['checks']};out=[];b=bases(catalog)
    for c in spec['constraints']:
        sub=[rows[i] for i in mapping[c['id']]]
        applicable=c['timing'] in ({'baseline','every_accepted_state'} if phase=='baseline' else {'every_accepted_state'} if phase=='accepted' else {'baseline','every_accepted_state','final'})
        row={'constraint_id':c['id'],'type':c['type'],'objects':c['objects'],'clause':c['clause'],
             'unit':c['unit'],'tolerance':c['tolerance'],'timing':c['timing'],'applicable':applicable,
             'target_or_range':c['values'],'source':source,'evaluated_on':'original_baseline' if c['timing']=='baseline' else 'current_state',
             'current_value':None,'error':None,'margin':None,'pass':False,'status':'invalid','details':sub}
        if sub:
            row.update(current_value=[r['current_value'] for r in sub],error=[r['error'] for r in sub],
                margin=min([r['margin'] for r in sub]) if all(r['margin'] is not None for r in sub) else None,
                **{'pass':all(r['pass'] for r in sub)})
        elif c['type']=='proportional_change':
            rec=baseline_record if c['timing']=='baseline' and phase!='baseline' else record
            if rec and rec.get('valid') and rec.get('fixed_conditions_match') and rec.get('controls_unchanged'):
                alphas={p:rec['actual_inputs'][p]['plini']/b[p]['plini'] for p in c['objects']}
                error=max(alphas.values())-min(alphas.values())
                row.update(current_value=alphas,error=error,margin=c['tolerance']-error,**{'pass':error<=c['tolerance']})
        row['status']='satisfied' if row['pass'] else ('unmet' if row['margin'] is not None else 'invalid');out.append(row)
    guards=all(result['context_guards'].values())
    result.update(checks=out,generated_spec_sha256=signature(spec),
        all_requirements=guards and all(r['pass'] for r in out),
        phase_satisfied=guards and all(r['pass'] for r in out if r['applicable']),
        process_conditions=guards and all(r['pass'] for r in out if r['timing'] in ('baseline','every_accepted_state')))
    return result


def semantic_check(spec,golden):
    # Independent evaluation only. Never returned as a replacement or a repair.
    return retained.semantic_check(spec,golden)


def semantic_evaluation(spec,golden,catalog,problem,goldproblem,task):
    from . import finite_semantics_v1
    s,_=lower(spec,catalog);g,_=lower(golden,catalog)
    result=finite_semantics_v1.evaluate(s,g,catalog,problem,goldproblem,task)
    def extras(x):
        return {'constraints':[c for c in x['constraints'] if c['type']=='proportional_change']}
    extra=retained.semantic_check(extras(spec),extras(golden))
    result['proportional_requirements']=extra
    result['expression_correct']=result['expression_correct'] and extra['correct']
    result['requirements_covered']=result['requirements_covered'] and extra['correct']
    result['correct_specification_not_used_to_replace_output']=True
    return result


prediction_evidence=retained.prediction_evidence


def solve(problem):
    """Reuse the v1.1 active-face strategy, without its first-equality assumption."""
    paths = problem['paths']; x0 = [problem['current_alphas'][p] for p in paths]; n = len(paths)
    def dot(a, b): return math.fsum(x*y for x, y in zip(a, b))
    def independent(rows):
        result=[]
        for r in rows:
            norm=math.sqrt(dot(r['a'],r['a']))
            if norm == 0:
                if abs(r['b'])>1e-12:return None
                continue
            a=[v/norm for v in r['a']];b=r['b']/norm
            for pivot,u,v in result:
                factor=a[pivot];a=[x-factor*y for x,y in zip(a,u)];b-=factor*v
            pivot=max(range(n),key=lambda k:abs(a[k]))
            if abs(a[pivot])<1e-12:
                if abs(b)>1e-10:return None
                continue
            divisor=a[pivot];result.append((pivot,[v/divisor for v in a],b/divisor))
        return [{'a':a,'b':b} for _,a,b in result]
    def projection(rows):
        rows=independent(rows)
        if rows is None:return None
        scaled=[]
        for r in rows:
            norm=math.sqrt(dot(r['a'],r['a']));scaled.append(([v/norm for v in r['a']],r['b']/norm))
        m=len(scaled)
        g=[[dot(a,b) for b,_ in scaled]+[v-dot(a,x0)] for a,v in scaled]
        for i in range(m):
            pivot=max(range(i,m),key=lambda j:abs(g[j][i]))
            if abs(g[pivot][i])<1e-12:return None
            g[i],g[pivot]=g[pivot],g[i];divisor=g[i][i];g[i]=[v/divisor for v in g[i]]
            for j in range(m):
                if j!=i:
                    factor=g[j][i];g[j]=[v-factor*w for v,w in zip(g[j],g[i])]
        return [x0[k]+math.fsum(scaled[i][0][k]*g[i][-1] for i in range(m)) for k in range(n)]
    examined, best, phase = 0, None, None
    for preferred in (True, False):
        equal = problem['equalities']+(problem['preferred_target_centers'] if preferred else [])
        # Constant equations don't spend a variable dimension.
        reduced = independent(equal)
        if reduced is None: continue
        rank_count = len(reduced)
        for size in range(n-rank_count+1):
            for active in itertools.combinations(problem['inequalities'], size):
                examined += 1; x = projection(equal+list(active))
                if x is None or any(not t2p.finite(v) for v in x): continue
                if any(abs(dot(r['a'],x)-r['b']) > 1e-10*max(1.,abs(r['b'])) for r in equal): continue
                if any(dot(r['a'],x)-r['b'] > 1e-12*max(1.,abs(r['b'])) for r in problem['inequalities']): continue
                score = (dot([u-v for u,v in zip(x,x0)], [u-v for u,v in zip(x,x0)]), tuple(x))
                if best is None or score < best[0]: best = (score,x,[r['id'] for r in active]); phase = 'exact_centers' if preferred else 'tolerance_bands'
            if size == 0 and best is not None: break
        if best is not None: break
    if best is None: return {'status': 'local_approximation_has_no_feasible_candidate', 'faces_examined': examined, 'global_infeasibility_claim': False}
    x = best[1]; alphas = dict(problem['fixed_alphas']); alphas.update(dict(zip(paths,x)))
    return {'status': 'candidate', 'alphas': alphas, 'adjustable_alphas': dict(zip(paths,x)),
            'predicted_values_pu': {p: r['intercept']+dot(r['a'],x) for p,r in problem['voltage_rows'].items()},
            'equation_residuals': {r['id']: dot(r['a'],x)-r['b'] for r in problem['equalities']},
            'squared_multiplier_change': best[0][0], 'active_constraints': best[2], 'phase': phase,
            'faces_examined': examined, 'problem_sha256': signature(problem), 'is_physical_feasibility_evidence': False}


