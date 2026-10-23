# -*- coding: utf-8 -*-
"""Finite, evidence-producing semantic review; never modifies generated specs.

Only exact typed conjunctions, split/grouped alpha bounds, interval inclusion
for explicit bounds, and fixed-plini -> alpha-bound implication are covered.
The registered baseline-linked actuator is required for the last rule.
"""
import copy
from . import composable_constraints as core
from . import t2p

VERSION = 'finite-semantics-v0.1'
ENFORCEMENT = 'same_submitted_spec_build_and_actual_process_check'


def same(a, b):
    if t2p.finite(a) and t2p.finite(b): return abs(a-b) <= 1e-12*max(1.,abs(b))
    if isinstance(a,dict) and isinstance(b,dict):return set(a)==set(b) and all(same(a[k],b[k]) for k in a)
    if isinstance(a,list) and isinstance(b,list):return len(a)==len(b) and all(same(u,v) for u,v in zip(a,b))
    return type(a)==type(b) and a==b


def atoms(spec):
    result=[]
    for c in spec['constraints']:
        objects=[[p] for p in sorted(c['objects'])] if c['type']=='alpha_bounds' else [sorted(c['objects'])]
        for obj in objects:
            row=copy.deepcopy(c);row['objects']=obj;result.append(row)
    return result


def meaning(c):
    return {k:v for k,v in c.items() if k not in ('id','clause')}


def coverage(submitted, required, catalog, problem, task, enforcement):
    """A -> B coverage, not automatically equivalence. No candidate-result input."""
    candidates=atoms(submitted);report=[]
    for req in atoms(required):
        record={'constraint_id':req['id'],'objects':req['objects'],'type':req['type'],
                'status':'missing_or_conflicting','covered':False,'basis':[],'required_clause':req['clause']}
        exact=[c for c in candidates if same(meaning(c),meaning(req))]
        if exact:
            record.update(status='explicit_coverage',covered=True,basis=[{'constraint_id':c['id'],'clause':c['clause']} for c in exact])
            report.append(record);continue
        if req['type']=='alpha_bounds':
            p=req['objects'][0];lo=req['values']['lower']-req['tolerance'];hi=req['values']['upper']+req['tolerance']
            # Explicit interval inclusion is one-way; reverse coverage is checked
            # separately. A stricter interval must never be labelled equivalent.
            narrower=[c for c in candidates if c['type']=='alpha_bounds' and c['objects']==[p]
                      and c['timing']==req['timing'] and c['unit']==req['unit']
                      and c['values']['lower']-c['tolerance']>=lo and c['values']['upper']+c['tolerance']<=hi]
            if narrower:
                record.update(status='explicit_coverage',covered=True,one_way_strengthening=True,
                              basis=[{'constraint_id':c['id'],'rule':'explicit_interval_subset'} for c in narrower])
                report.append(record);continue
            fixed=[c for c in candidates if c['type']=='fixed_parameter' and c['objects']==[p] and c['values']['field']=='plini'
                   and c['unit']=='MW' and (c['timing']==req['timing'] or c['timing']=='every_accepted_state')]
            if fixed:
                if (submitted['variables']['mapping']!='baseline_PQ_times_absolute_alpha' or enforcement!=ENFORCEMENT or problem is None):
                    record.update(status='undetermined',basis=[{'reason':'No certified matching actuator/build/execution binding'}])
                else:
                    matches=[v for v in catalog.values() if v['path']==p and v['kind']=='load']
                    if len(matches)!=1 or matches[0]['base_inputs']['plini']<=0:
                        record.update(status='undetermined',basis=[{'reason':'Missing unique positive baseline P'}])
                    else:
                        base=matches[0]['base_inputs']['plini'];consumption=problem['constraint_consumption'];read_tol=task['load']['input_readback_tolerance']
                        for c in fixed:
                            used=consumption.get(c['id'],{});cid=c['id'];rows={r['id'] for r in problem['inequalities']}
                            bound_into_solver=(used.get('type')=='fixed_parameter' and used.get('objects')==[p]
                                               and cid+' upper' in rows and cid+' lower' in rows)
                            if not bound_into_solver:
                                record.update(status='undetermined');record['basis'].append({'constraint_id':cid,'reason':'Fixed input not consumed in this problem'});continue
                            v=c['values']['value'];storage=task['t2p']['tolerances']['P_MW'][p]
                            reading=read_tol['abs']+read_tol['rel']*(abs(v)+c['tolerance'])
                            radius=c['tolerance']+storage+reading
                            fixed_interval=[v-radius,v+radius];alpha_interval=[z/base for z in fixed_interval]
                            consistent= p not in problem['fixed_alphas'] or abs(v-base)<=c['tolerance']
                            certified=consistent and lo<=alpha_interval[0] and alpha_interval[1]<=hi
                            evidence={'constraint_id':cid,'same_object':p,'same_physical_parameter':'plini',
                                'requested_alpha_bound_mapped_to_plini_MW':[base*lo,base*hi],
                                'actuator_inverse':'alpha=plini/P0; registered baseline-linked PQ only','baseline_P_MW':base,
                                'fixed_value_MW':v,'constraint_tolerance_MW':c['tolerance'],'storage_allowance_MW':storage,
                                'reading_allowance_MW':reading,'fixed_allowed_interval_MW':fixed_interval,'implied_alpha_interval':alpha_interval,
                                'required_alpha_interval':[lo,hi],'solver_consumed':bound_into_solver,'execution_policy':enforcement,
                                'consistent_with_fixed_nonvariable':consistent,'entire_interval_inside':certified}
                            record['basis'].append(evidence)
                            if certified:record.update(status='verified_fixed_implication',covered=True);break
                            record.update(status='missing_or_conflicting')
            elif any(c['type']=='fixed_parameter' and c['objects']==[p] and c['values']['field']=='qlini' for c in candidates):
                record.update(status='undetermined',basis=[{'reason':'Q-only inversion not implemented; no cross-parameter exemption'}])
        report.append(record)
    return {'requirements_covered':all(c['covered'] for c in report),'constraints':report}


def evaluate(submitted, golden, catalog, submitted_problem, golden_problem, task, enforcement=ENFORCEMENT):
    forward=coverage(submitted,golden,catalog,submitted_problem,task,enforcement)
    reverse=coverage(golden,submitted,catalog,golden_problem,task,enforcement)
    roots={'version':submitted['schema_version']==golden['schema_version'],
           'adjustable_scope':set(submitted['variables']['objects'])==set(golden['variables']['objects']),
           'actuator_mapping':submitted['variables']['mapping']==golden['variables']['mapping'],
           'preserve':same(submitted['preserve'],golden['preserve'])}
    covered=forward['requirements_covered'] and all(roots.values())
    equivalent=covered and reverse['requirements_covered']
    status='verified_equivalent_within_finite_rules' if equivalent else 'one_way_entailment_only' if covered else 'undetermined' if any(c['status']=='undetermined' for c in forward['constraints']) else 'missing_or_conflicting'
    return {'version':VERSION,'requirements_covered':covered,'expression_correct':equivalent,
            'equivalence_status':status,'root_checks':roots,'original_requirements':forward['constraints'],
            'reverse_coverage':reverse,'generated_spec_sha256':core.signature(submitted),
            'gold_spec_sha256':core.signature(golden),'generated_output_not_overwritten':True,
            'candidate_success_not_used_as_semantic_evidence':True,
            'proof_scope':'Only recorded finite rules; no general theorem proving or physical feasibility claim.'}
