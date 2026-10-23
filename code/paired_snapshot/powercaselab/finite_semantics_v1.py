"""Finite scope/time and nonvariable actuator implications; no answer repair."""
import copy
from . import finite_semantics as old
from . import composable_constraints_v1 as core

VERSION='finite-semantics-v0.2'
SCOPE={'baseline':set(['baseline']), 'every_accepted_state':set(['baseline','accepted','final']), 'final':set(['final'])}


def coverage(submitted,required,catalog,problem,task):
    result=old.coverage(submitted,required,catalog,problem,task,old.ENFORCEMENT)
    reqs=old.atoms(required);actual=old.atoms(submitted)
    for row,req in zip(result['constraints'],reqs):
        if row['covered']:continue
        for c in actual:
            a,b=old.meaning(c),old.meaning(req);a.pop('timing');b.pop('timing')
            if old.same(a,b) and SCOPE[req['timing']].issubset(SCOPE[c['timing']]):
                row.update(status='verified_temporal_implication',covered=True,one_way_strengthening=True,
                    basis=[{'constraint_id':c['id'],'provided_timing':c['timing'],'required_timing':req['timing'],
                            'policy':'baseline checks all process constraints; final is an accepted state'}])
                break
        if row['covered']:continue
        if req['type']=='alpha_bounds' and problem is not None:
            p=req['objects'][0]
            if (p not in submitted['variables']['objects'] and problem['fixed_alphas'].get(p)==1.
                    and problem['baseline_admission']['phase_satisfied']
                    and req['values']['lower']-req['tolerance']<=1.<=req['values']['upper']+req['tolerance']):
                row.update(status='verified_nonvariable_bound_implication',covered=True,
                    basis=[{'object':p,'fixed_alpha':1.,'implied_interval':[1.,1.],
                        'execution_binding':'exact original-baseline readback for nonselected inputs',
                        'not_inferred_from_candidate_success':True}])
                continue
        if (req['type']=='fixed_parameter' and problem is not None
                and submitted['variables']['mapping']=='baseline_PQ_times_absolute_alpha'):
            p=req['objects'][0];v=[v for v in catalog.values() if v['path']==p]
            if (len(v)==1 and p not in submitted['variables']['objects']
                    and problem['fixed_alphas'].get(p)==1. and problem['baseline_admission']['phase_satisfied']):
                value=v[0]['base_inputs'][req['values']['field']]
                if abs(value-req['values']['value'])<=req['tolerance']:
                    row.update(status='verified_nonvariable_input_implication',covered=True,
                        basis=[{'object':p,'field':req['values']['field'],'fixed_alpha':1.,'baseline_value':value,
                            'required_value':req['values']['value'],'tolerance':req['tolerance'],
                            'solver_binding':'nonvariable fixed_alphas=1',
                            'execution_binding':'complete baseline-linked PQ vector and exact nonselected readback check',
                            'not_inferred_from_candidate_success':True}])
    result['requirements_covered']=all(r['covered'] for r in result['constraints'])
    return result


def evaluate(spec,gold,catalog,problem,goldproblem,task):
    forward=coverage(spec,gold,catalog,problem,task);reverse=coverage(gold,spec,catalog,goldproblem,task)
    roots={'schema':spec['schema_version']==gold['schema_version'],
        'variables':set(spec['variables']['objects'])==set(gold['variables']['objects']),
        'mapping':spec['variables']['mapping']==gold['variables']['mapping'],
        'preserve':spec['preserve']==gold['preserve']}
    covered=all(roots.values()) and forward['requirements_covered']
    equivalent=covered and reverse['requirements_covered']
    return {'version':VERSION,'expression_correct':equivalent,'requirements_covered':covered,
        'equivalence_status':'finite_rules_equivalent' if equivalent else 'one_way_strengthening' if covered else 'missing_conflicting_or_unproven',
        'root_checks':roots,'original_requirements':forward['constraints'],'reverse_coverage':reverse,
        'generated_specification_unchanged':True,'candidate_coincidence_not_used':True}
