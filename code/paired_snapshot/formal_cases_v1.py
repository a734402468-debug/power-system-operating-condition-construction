"""Four registered cases; retained frontends, kernel and physical Session.

Only orchestration, input-driven structural group equalities, and the frozen
zero/one residual-margin switch. No task-name-specific numerical branch.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

import core_mechanism_closeout_v2 as c
from powercaselab import stage_set_constraints_v1 as stages
from powercaselab import state_reference_constraints_v2_1 as refs
from powercaselab import finite_free_permission_v1 as freecert

m=c.m; e=c.e; ROOT=e.ROOT; core=e.core; read=e.read; write=e.write; digest=e.digest
VERSION='formal-cases-v1'
PARENT=c.PARENT
PROCESS=['baseline','every_accepted_state']
LOADS=['L'+str(i) for i in range(1,7)]
BUSES=['V'+str(i) for i in range(1,7)]
ITEMS=[
 dict(id='G1',frontend='growth_T',groups={'A':['L2'],'B':['L3','L4']},upper={'A':1.20,'B':1.20},fixed=['L1','L5','L6'],target={'V2':[-.0028,-.0024]},keep={'V3':[-.002,.002]}),
 dict(id='G2',frontend='growth_T',groups={'A':['L2'],'B':['L3','L4']},upper={'A':1.14,'B':1.20},fixed=['L1','L5','L6'],target={'V3':[-.00255,-.00215]},keep={'V2':[-.00285,.00285]}),
 dict(id='R1',frontend='state_F',source=['L1','L3','L5'],destination=['L2','L4','L6'],amount=.25,fixed=[]),
 dict(id='R2',frontend='state_F',source=['L2','L4','L6'],destination=['L1','L3','L5'],amount=.20,fixed=['L3'])]


def chinese(item,cat,pol):
    def names(ids):return '{'+','.join(a+'='+cat[a]['name'] for a in ids)+'}'
    tol={k:v['effective_evaluation_tolerance'] for k,v in pol['policies'].items()}
    if item['frontend']=='growth_T':
        text='研究者定义的负荷增长需求 '+item['id']+'。\n'
        text+='C1：增长集合'+ '、'.join(g+'='+names(ids)+'，绝对倍率在[1.00,'+str(item['upper'][g])+']' for g,ids in item['groups'].items())+'；两组倍率独立，仅允许调整这些成员，边界适用于基准及每个接受状态（含最终）。\n'
        text+='C2：每组内部使用同一绝对倍率；六负荷各自保持自身基准Q/P，P=P0×alpha、Q=Q0×alpha，从B_BASELINE_V1计算、禁止累乘。组内关系及Q/P在基准及每个接受状态（含最终）生效；不要求六负荷总P守恒。\n'
        text+='C3：'+names(item['fixed'])+'的P/Q保持基准，适用于基准及每个接受状态（含最终）。\n'
        text+='C4：'+'；'.join(a+'（'+cat[a]['name']+'）最终电压相对B_BASELINE_V1的变化在'+str(b)+' pu内' for a,b in item['target'].items())+'。目标仅最终生效。\n'
        text+='C5：'+'；'.join(a+'（'+cat[a]['name']+'）在基准及每个接受状态（含最终）的电压相对基准变化在'+str(b)+' pu内' for a,b in item['keep'].items())+'。\n'
    else:
        text='研究者定义的集合负荷转移需求 '+item['id']+'。\n'
        text+='C1：最终从'+names(item['source'])+'向'+names(item['destination'])+'转移'+str(item['amount'])+' MW有功输入：转出集合plini输入和相对B_BASELINE_V1减少该量，转入集合增加该量。仅最终要求转移完成。\n'
        text+='C2：集合内部自由协调分配，不要求比例或相同倍率、等量变化；固定成员仍参与集合总量统计但其变化必须为零。\n'
        text+='C3：六负荷'+names(LOADS)+'的plini输入和在基准及每个接受状态（含最终）保持B_BASELINE_V1的输入和，不将其称为实际系统总负荷或发电保持。\n'
        text+='C4：六负荷各自保持自身基准Q/P，P=P0×alpha、Q=Q0×alpha，从B_BASELINE_V1计算、禁止累乘；在基准及每个接受状态（含最终）生效。\n'
        text+='C5：六负荷绝对倍率均在[0.99,1.02]内；'+(names(item['fixed'])+'的P/Q保持基准，其余五个负荷允许调整' if item['fixed'] else '六负荷均允许调整')+'。边界和固定项在基准及每个接受状态（含最终）生效。\n'
        text+='C6：'+names(BUSES)+'的电压在基准及每个接受状态（含最终）分别保持自身基准电压±0.005 pu，不是六母线共享同一绝对区间。\n'
    text+='C7：其他负荷输入、拓扑、共享设备类型、控制及潮流配置保持不变；沿用登记的有限参考机组边界检查，不附加全网健康要求。基准不必满足仅最终目标；不合格试算不是接受状态，不要求虚构连续路径。\n'
    text+='精度采用precision-policy-v1：有功转移/输入和误差≤'+str(tol['P_SUM_V1'])+' MW；各自Q/P残差≤'+str(tol['QP_RESIDUAL_V1'])+' Mvar；倍率读回误差≤'+str(tol['ALPHA_READ_V1'])+'；组内同倍率读回误差≤'+str(tol['PROP_ALPHA_V1'])+'；固定P/Q精确恢复，误差0；电压以所列端点验收，附加放宽量0 pu。存储预算已包含在上述精度中，不再叠加。'
    # Each retained frontend exposes its own explicit ID for the same snapshot.
    # Do not present the growth frontend's label to the state-reference parser.
    return text if item['frontend']=='growth_T' else text.replace('B_BASELINE_V1',refs.prior.BASELINE_ID)


def reference(item,cat,pub,snapshot,original):
    if item['frontend']=='growth_T':
        obj=m.symbolic(item,pub)
        for row in obj['constraints']:
            if row['type']=='baseline_qp':row['objects']=LOADS[:]
        parsed=e.front.parse('T',json.dumps(obj),cat,pub,'stop')
    else:
        ss=snapshot['state_id'];rows=[]
        def add(typ,clause,phases,**kw):
            rows.append(dict(id='r'+str(len(rows)+1),type=typ,unit=refs.prior.UNITS[typ],stages=phases,stage_source='基准及每个接受状态（含最终）' if phases==PROCESS else '仅最终要求转移完成',clause=clause,**kw))
        add('transfer','C1',['final'],source=item['source'],destination=item['destination'],amount={'op':'literal','value':item['amount'],'unit':'MW'},accuracy='P_SUM_V1')
        add('distribution','C2',['final'],objects=LOADS,mode='free')
        add('input_sum','C3',PROCESS,objects=LOADS,target={'op':'baseline_sum','state':ss,'quantity':'plini','objects':LOADS},accuracy='P_SUM_V1')
        add('qp_policy','C4',PROCESS,objects=LOADS,state=ss,policy='each_baseline_ratio',accuracy='QP_RESIDUAL_V1')
        add('alpha_bounds','C5',PROCESS,objects=LOADS,lower=.99,upper=1.02,precision='ALPHA_READ_V1')
        if item['fixed']:add('fixed_inputs','C5',PROCESS,objects=item['fixed'],state=ss,fields=['plini','qlini'],accuracy='FIXED_EXACT_V1')
        add('voltage_bounds','C6',PROCESS,objects=BUSES,bounds={'kind':'baseline_band','state':ss,'lower_offset':-.005,'upper_offset':.005},precision='VOLTAGE_EDGE_ZERO_V1')
        allowed=[a for a in LOADS if a not in item['fixed']]
        obj={'specification':{'baseline_state':ss,'variables':{'objects':allowed,'mapping':'baseline_PQ_times_absolute_alpha'},'constraints':rows,'preserve':{k:True for k in core.retained.PRESERVE}},'plan':{'operation':'solve','selected':allowed,'reason':'isolated researcher reference'}}
        parsed=stages.parse('F',json.dumps(obj),cat,snapshot,pub['precision_policies'],allowed,original,'stop')
    if not parsed['schema_valid']:raise ValueError(json.dumps(parsed,ensure_ascii=False))
    return obj,parsed['expansion']['numeric_specification']


def problem(spec,task,base):
    p=core.build_problem(spec,task['catalog'],task['response_matrix'],e.retained.state_for(base,task['catalog']),task)
    # Generalize the retained structural group equation by declared object set.
    for row in spec['constraints']:
        if row['type']!='proportional_change' or row['timing']=='baseline':continue
        ids=row['objects']
        for path in ids[1:]:
            coeff=[float(x==path)-float(x==ids[0]) for x in p['paths']]
            eq={'id':'group_command_'+row['id']+'_'+str(ids.index(path)),'a':coeff,'b':0.}
            if not any(x['a']==coeff and x['b']==0. for x in p['equalities']):p['equalities'].append(eq)
    return p


def math_view(p):
    def rows(key):return sorted(set(json.dumps({'a':r['a'],'b':r['b']},sort_keys=True) for r in p[key]))
    return {k:p[k] for k in ('paths','current_alphas','fixed_alphas')}|{k:rows(k) for k in ('equalities','inequalities','preferred_target_centers')}


def solve(folder,spec,task,base,ledger,purpose):
    folder.mkdir(parents=True,exist_ok=True)
    if len(ledger['target_solves'])>=16:raise RuntimeError('Target solver budget exhausted')
    p=problem(spec,task,base);write(folder/'solver_specification.json',spec);write(folder/'problem.json',p)
    entry={'task':task['task_id'],'purpose':purpose,'folder':str(folder)};ledger['target_solves'].append(entry)
    t=time.monotonic();candidate=core.solve(p);entry.update(seconds=time.monotonic()-t,status=candidate['status']);write(folder/'candidate.json',candidate)
    if candidate['status']=='candidate':
        pt=copy.deepcopy(candidate['alphas'])
        for row in spec['constraints']:
            if row['type']=='proportional_change' and row['timing']!='baseline':
                for path in row['objects']:
                    value=pt[row['objects'][0]]
                    if abs(pt[path]-value)>1e-12:raise RuntimeError('Nonidentical structural group command')
                    pt[path]=value
        if any(not task['actuator_bounds'][p]['lower']<=v<=task['actuator_bounds'][p]['upper'] for p,v in pt.items()):raise RuntimeError('Unsafe numeric point')
        write(folder/'point.json',pt)
    return candidate


def correction(spec,task,point,observation,coefficient):
    pred=m.predictions(task,point);errors={};cat=task['catalog'];transforms=[];sub=copy.deepcopy(spec)
    if not observation['valid']:raise ValueError('No valid first-point feedback')
    for row in sub['constraints']:
        if row['type']!='voltage_bounds' or row['timing']=='baseline':continue
        path=row['objects'][0];a=next(a for a,v in cat.items() if v['path']==path)
        raw=observation['evaluation']['result_snapshot']['key_results'][path+'|m:u']
        unit=raw['unit'][0] if isinstance(raw['unit'],list) else raw['unit']
        if unit!='p.u.' or not m.arithmetic.finite(raw['value']):raise ValueError('Invalid measured voltage')
        err=raw['value']-pred[a]['predicted_pu'];margin=coefficient*abs(err);old=copy.deepcopy(row['values'])
        row['values']={'lower':old['lower']+margin-err,'upper':old['upper']-margin-err}
        errors[a]=dict(e_pu=err,margin_pu=margin,actual_pu=raw['value'],original_prediction_pu=pred[a]['predicted_pu'])
        transforms.append(dict(id=row['id'],timing=row['timing'],original=old,internal=row['values']))
    return sub,{'coefficient':coefficient,'errors':errors,'transforms':transforms,'empty':any(r['internal']['lower']>r['internal']['upper'] for r in transforms),'original_requirements_unchanged':True,'feedback_source':'same own-task first candidate only'}


def prepare(run):
    run.mkdir(parents=True,exist_ok=False)
    for name in ['catalog.json','baseline_record.json','source_base_task.json','runtime_public_catalog.json','fictional_T.json','configuration.json']:shutil.copy2(PARENT/name,run/name)
    shutil.copy2(ROOT/'PowerCaseLab_Formal_Cases_Task_v1.txt',run/'task_package.txt')
    cat=read(run/'catalog.json');base=read(run/'baseline_record.json');source=read(run/'source_base_task.json');pub=read(run/'runtime_public_catalog.json');cfg=read(run/'configuration.json')
    live=e.provider.read(e.provider.CONFIG)
    assert cfg['model']==live['model']==e.provider.MODEL and cfg['endpoint']==live['endpoint']==e.provider.ENDPOINT
    assert cfg['request_parameters']==dict(live['request_parameters'],stream=True) and live['automatic_retries']==0
    snapshot=refs.prior.snapshot_from(cat,base,source,{'file':str(PARENT/'baseline_record.json'),'sha256':digest(PARENT/'baseline_record.json')});write(run/'reference_snapshot.json',snapshot)
    fake=refs.fictional_example();fake['original_requirements']='最终完成转移。其余条件在每个接受状态满足。'
    for row in fake['decision']['specification']['constraints']:
        phase=row.pop('timing');row.update(stages=[phase],stage_source='最终完成转移' if phase=='final' else '每个接受状态满足')
    assert stages.parse('F',json.dumps(fake['decision']),fake['catalog'],fake['snapshot'],fake['policies'],fake['allowed'],fake['original_requirements'],'stop')['schema_valid']
    write(run/'fictional_state_F.json',fake);write(run/'tasks_input.json',ITEMS)
    ledger={'target_solves':[]};matrix_lines=['# 四题预登记矩阵','研究者定义的工况与数值，不是行业标准、随机抽样或认证区域。基准与响应保持归档绑定。',
      '[MATPOWER负荷修改](https://matpower.app/manual/matpower/ModifyingaCase.html)支持集合负荷缩放的用途；[稳态参数变化](https://matpower.app/manual/matpower/ContinuationPowerFlow.html)支持研究负荷变化响应。本方法不是CPF，不估计崩溃裕度。',
      '相比开发题：G1新增目标/保持组合；G2交换目标并收紧A权限；R1采用交错统计集合；R2反向且固定统计成员L3。历史响应获取11 AC单列。']
    for item in ITEMS:
        f=run/'tasks'/item['id'];f.mkdir(parents=True);original=chinese(item,cat,pub['precision_policies']);e.create_requirement_file(f/'original_requirements.txt',original)
        localpub=copy.deepcopy(pub)
        bounds={v['path']:{'lower':1. if item['frontend']=='growth_T' else .99,'upper':1.2 if item['frontend']=='growth_T' else 1.02} for v in cat.values() if v['kind']=='load'}
        if item['frontend']=='growth_T':
            for g,ids in item['groups'].items():
                for a in ids:bounds[cat[a]['path']]['upper']=item['upper'][g]
        localpub['growth_permission']=bounds;write(f/'public_catalog.json',localpub)
        symbolic,gold=reference(item,cat,localpub,snapshot,original);write(f/'correct_symbolic.json',symbolic);write(f/'correct_specification.json',gold)
        task=e.envelope(source,gold,item['id']);task.update(actuator_bounds=bounds,budget={'maximum_ac_flows':3},original_requirements_sha256=digest(f/'original_requirements.txt'),specification_origin='isolated_correct_specification',purpose='Frozen growth/transfer original requirements, one physical candidate then recovery')
        task=e.retained.bridge_execution_task(task,VERSION);write(f/'final_task.json',task)
        allowed=[a for a in LOADS if a not in item['fixed']]
        if item['frontend']=='growth_T':packet=e.front.request_packet(original,localpub,read(run/'fictional_T.json'),'T')
        else:packet=stages.request_packet(original,e.retained.public_directory(cat),snapshot,pub['precision_policies'],allowed,fake,'F','execute')
        body={'model':cfg['model'],**cfg['request_parameters'],'messages':[{'role':'system','content':e.SYSTEM},{'role':'user','content':json.dumps(packet,ensure_ascii=False,separators=(',',':'))}]}
        write(f/'request.json',body);audit=f/'wire_check';audit.mkdir();write(audit/'trusted_requirements_source.json',{'path':str(f/'original_requirements.txt'),'sha256':digest(f/'original_requirements.txt'),'provenance':'developer_new_task'})
        wire,check=e.prepare_request_bytes(body,audit);(audit/'http_request_body.utf8').write_bytes(wire);write(audit/'check.json',check)
        matrix_lines+=['\n## '+item['id'],original]
    write(run/'all_tasks_registered_before_solver.json',{'at':e.retained.client.stamp(),'tasks':{i['id']:digest(run/'tasks'/i['id']/'correct_specification.json') for i in ITEMS}})
    for item in ITEMS:
        f=run/'tasks'/item['id'];task=read(f/'final_task.json');r=solve(f/'precheck',task['golden'],task,base,ledger,'isolated_precheck')
        matrix_lines+=['\n'+item['id']+' 离线预检：'+r['status']+'。不构成物理可行性证明。']
        # All baseline stage clauses must be genuinely evaluated, not a label.
        check=core.evaluate(task['golden'],cat,base,phase='baseline');write(f/'baseline_offline_acceptance.json',check);assert check['phase_satisfied'],check
    (run/'case_matrix.md').write_text('\n\n'.join(matrix_lines)+'\n',encoding='utf-8',errors='strict')
    checks=[]
    for tid in ['G1','R1']:
        task=read(run/'tasks'/tid/'final_task.json');pt=read(run/'tasks'/tid/'precheck/point.json');f=run/'offline_dispatch'/tid/'correct';f.mkdir(parents=True);write(f/'task.json',task)
        req,sec=m.action(f,task,e.retained.state_for(base,cat),base,pt);write(f/'request.json',req);write(f/'baseline.json',base);write(f/'accepted.json',{'version':0,'alphas':e.retained.state_for(base,cat)['alphas'],'record':base})
        native=ROOT/'src/powercaselab/adapters/pf15/redistribution_v1.py';write(f/'offline_fixture.json',{'native_source_text_sha256':hashlib.sha256(native.read_text(encoding='utf-8').encode('utf-8')).hexdigest(),'starting_ac':1})
        for name in ['correct','tampered']:
            dest=f.parent/name
            if name=='tampered':
                shutil.copytree(f,dest);bad=copy.deepcopy(task);bad['actuator_bounds'][cat['L2']['path']]['upper']+=.001;write(dest/'task.json',bad)
            cp=subprocess.run([task['backend']['legacy_python'],'-B',str(e.OFFLINE_DISPATCH),str(dest)],cwd=ROOT,capture_output=True,text=True)
            result=read(dest/'offline_result.json') if (dest/'offline_result.json').exists() else {'stderr':cp.stderr}
            checks.append({'case':tid,'variant':name,'result':result,'seconds':sec})
            assert cp.returncode==0 and result['status']==('execution_boundary_reached' if name=='correct' else 'rejected'),result
    # Formula checked without search; baseline and nonvoltage rows must stay identical.
    task=read(run/'tasks/G1/final_task.json');pt=read(run/'tasks/G1/precheck/point.json');fixture=copy.deepcopy(base)
    for a,p in m.predictions(task,pt).items():fixture['result_snapshot']['key_results'][cat[a]['path']+'|m:u']['value']=p['predicted_pu']-1e-5
    for coefficient in [0.,1.]:
        sub,audit=correction(task['golden'],task,pt,{'valid':True,'evaluation':fixture},coefficient)
        for old,new in zip(task['golden']['constraints'],sub['constraints']):
            if old['type']!='voltage_bounds' or old['timing']=='baseline':assert old==new
        for row in audit['transforms']:
            assert abs(row['internal']['lower']-(row['original']['lower']+coefficient*1e-5+1e-5))<1e-12
    write(run/'offline_checks.json',{'passed':True,'dispatch':checks,'target_solves':ledger['target_solves'],'pin_verification_calls':4,'LLM':0,'PF':0,'AC':0,'formula_coefficients':[0,1],'independent_fictional_example_valid':True})
    write(run/'protocol.json',{'version':VERSION,'task_order':[i['id'] for i in ITEMS],'frontend_order':[i['id'] for i in ITEMS],'component_order':['N0_shared_first','N1','F'],'chat_cap':8,'AC_normal_cap':36,'AC_hard_cap':40,'reserve_only_for_abnormal_recovery':4,'target_solve_cap':16,'first_failure_stops_unsent_API':True,'no_service_probe':True,'history_response_AC':11,'same_first_error_for_N1_F':True,'method_selection_objective':'retained per-device minimum change at original baseline; declared group commands exact','representative_appendix':['G2','R2'],'frontend_contracts':{'growth':'existing load_growth_program_v1 T','transfer':'existing shared-stage-set-v1.1 F'},'semantic_evaluators':'unchanged finite-v0.2 and finite-free-permission-v1; no new equivalence rules','original_physical_requirements_not_internal_margin':'independent acceptance always original correct specification'})
    deps={Path(__file__),Path(c.__file__),Path(m.__file__),Path(e.__file__),Path(e.retained.__file__),Path(e.provider.__file__),e.provider.CONFIG,e.SIDECAR,e.OFFLINE_DISPATCH,ROOT/'experiments/siliconflow_stream_diagnostic_v1.py',ROOT/'experiments/request_text_integrity_v1.py',ROOT/'experiments/h3_mechanism_probe.py',ROOT/'experiments/llm_prediction_probe.py'}
    deps|={Path(x.__file__).resolve() for x in list(sys.modules.values()) if getattr(x,'__file__',None) and Path(x.__file__).suffix=='.py' and Path(x.__file__).resolve().is_relative_to(ROOT/'src/powercaselab')}
    deps|=set((ROOT/'src/powercaselab/adapters/pf15').glob('*.py'));deps|={p for p in run.rglob('*') if p.is_file()}
    write(run/'freeze.json',{'version':VERSION,'at':e.retained.client.stamp(),'files':{str(p.relative_to(ROOT)):digest(p) for p in deps}})
    print('PREPARED '+str(run),flush=True)


def generate(run,ledger):
    cat=read(run/'catalog.json');base=read(run/'baseline_record.json');snap=read(run/'reference_snapshot.json')
    for item in ITEMS:
        f=run/'tasks'/item['id'];out=run/item['id']/'frontend';out.mkdir(parents=True);task=read(f/'final_task.json');pub=read(f/'public_catalog.json');body=read(f/'request.json');original=(f/'original_requirements.txt').read_text(encoding='utf-8')
        row={'task':item['id'],'attempts':[],'qualified':False,'status':'not_sent_after_service_stop' if ledger['API_blocked'] else 'not_started'};ledger['frontends'].append(row)
        if ledger['API_blocked']:write(out/'trajectory.json',row);continue
        for number in [1,2]:
            e.check(run);print(item['id']+' compile '+str(number),flush=True)
            raw,answer=e.stream_call(run,out/('generation_'+str(number)),body,f/'original_requirements.txt')
            ledger['chat_attempts']+=raw.get('attempt_count',0);ledger['local_process_attempts']+=1;ledger['HTTP_attempts']+=raw.get('http_request_attempts') or 0;ledger['complete_returns']+=raw.get('complete_returns',0)
            attempt={'number':number,'transport':raw};row['attempts'].append(attempt)
            if raw['status']!='completed' or not answer or not answer.get('content'):
                row['status']='call_incomplete';ledger['API_blocked']=True;break
            if any(x!=e.provider.MODEL for x in answer.get('response_models',[])):row['status']='model_mismatch';ledger['API_blocked']=True;break
            allowed=[a for a in LOADS if a not in item['fixed']]
            parsed=e.front.parse('T',answer['content'],cat,pub,answer.get('finish_reason')) if item['frontend']=='growth_T' else stages.parse('F',answer['content'],cat,snap,pub['precision_policies'],allowed,original,answer.get('finish_reason'))
            write(out/('parsed_'+str(number)+'.json'),parsed);attempt['contract']=parsed['schema_valid'];attempt['raw_contract']=parsed.get('raw_contract_valid')
            if not parsed['schema_valid']:
                row['status']='contract_failure'
                if number==1:
                    feedback={'public_contract_diagnostics':parsed['diagnostics'],'unchecked':parsed.get('unchecked',[])};write(out/'public_feedback.json',feedback)
                    body['messages'] += [{'role':'assistant','content':answer['content']},{'role':'user','content':json.dumps(feedback,ensure_ascii=False)}]
                continue
            state=e.retained.state_for(base,cat)
            if item['frontend']=='growth_T':
                score=e.front.semantic_evaluation(parsed,task['golden'],cat,task['response_matrix'],state,task);qualified=score['expression_correct']
            else:
                score=refs.independent_score(parsed,task,state);supp=freecert.certify(parsed,task,snap,score);score['existing_free_permission_supplement']=supp;qualified=score['qualified'] or supp['qualified']
            write(out/'independent_semantics.json',score);attempt['semantic_qualified']=qualified
            row.update(status='semantic_qualified' if qualified else 'semantic_not_certified',qualified=qualified)
            write(out/'model_specification.json',parsed['expansion']['numeric_specification'])
            if qualified:
                built=(e.front if item['frontend']=='growth_T' else stages).prepare_problem(parsed,cat,task['response_matrix'],state,task)
                if built['status']!='built':row.update(status='model_stopped',qualified=False);break
                spec=built['operational_specification'];p=problem(spec,task,base);gp=read(f/'precheck/problem.json');equal=math_view(p)==math_view(gp)
                write(out/'math_binding.json',{'same_problem':equal,'model':math_view(p),'independent':math_view(gp),'no_solver_call':True})
                if not equal:row.update(status='certified_but_mathematical_binding_unresolved',qualified=False);break
                write(out/'operational_specification.json',spec)
            break
        write(out/'trajectory.json',row);write(run/'results.json',ledger)


def physical(run,folder,task,spec,pt,ledger):
    # The actual chosen specification supplies execution constraints. The
    # independent correct specification remains solely the acceptance oracle.
    original=m.pins
    def selected_pins(t,p):
        local=copy.deepcopy(t);local['golden']=spec;return original(local,p)
    m.pins=selected_pins
    try:return m.physics(run,folder,task,pt,ledger)
    finally:m.pins=original


def execute(run):
    e.check(run)
    with (run/'started.json').open('x',encoding='utf-8') as f:json.dump({'at':e.retained.client.stamp()},f)
    start=time.monotonic();ledger={'version':VERSION,'chat_attempts':0,'HTTP_attempts':0,'complete_returns':0,'local_process_attempts':0,'API_blocked':False,'physical_blocked':False,'AC':0,'connections':0,'frontends':[],'cases':[],'observations':[],'target_solves':read(run/'offline_checks.json')['target_solves']}
    write(run/'results.json',ledger)
    try:
        generate(run,ledger)
        base=read(run/'baseline_record.json')
        for item in ITEMS:
            e.check(run);tid=item['id'];task=read(run/'tasks'/tid/'final_task.json');front=next(r for r in ledger['frontends'] if r['task']==tid)
            spec=read(run/tid/'frontend/operational_specification.json') if front['qualified'] else task['golden']
            row={'task':tid,'numerical_source':'actual_model_specification' if front['qualified'] else 'isolated_correct_specification','end_to_end':False,'methods':{}};ledger['cases'].append(row)
            first=run/tid/'first';candidate=solve(first,spec,task,base,ledger,'shared_first');write(run/'results.json',ledger)
            if candidate['status']!='candidate':
                row['methods']={k:{'status':candidate['status'],'physical':'not_executed'} for k in ('N0','N1','F')};continue
            pt=read(first/'point.json');observations={}
            def observe(label,path,sub):
                point=read(path/'point.json');key=core.signature({'task':task,'point':point})
                if key in observations:
                    saved=copy.deepcopy(observations[key]);saved['shared']=True;saved['new_AC']=0;return saved
                if ledger['physical_blocked'] or ledger['AC']+3>36:return {'status':'physical_not_executed','reason':'binding/recovery blocked or normal AC budget reserved'}
                folder=path/'physical';print(tid+' '+label+' physical baseline/candidate/restore',flush=True)
                out=physical(run,folder,task,sub,point,ledger);out.update(observation_id=tid+'_'+label,physical_source=str(folder),shared=False,new_AC=out['AC'])
                ledger['observations'].append(copy.deepcopy(out));observations[key]=out;write(run/'results.json',ledger);return out
            initial=observe('first',first,spec);row['methods']['N0']=initial
            if initial['status']=='passed':
                for label in ['N1','F']:row['methods'][label]=dict(initial,shared=True,new_AC=0,stopped_after_initial_success=True)
            elif initial['status']=='original_conditions_unmet' and initial.get('restoration')=='passed':
                raw=read(Path(initial['physical_source'])/'candidate_response.json')
                for label,coefficient in [('N1',0.),('F',1.)]:
                    sub,audit=correction(spec,task,pt,raw,coefficient);folder=run/tid/label;folder.mkdir(exist_ok=True)
                    audit['first_observation']=initial['observation_id'];write(folder/'correction.json',audit)
                    if audit['empty']:row['methods'][label]={'status':'empty_internal_interval','physical':'not_executed'};continue
                    cand=solve(folder,sub,task,base,ledger,label+'_one_correction')
                    if cand['status']!='candidate':row['methods'][label]={'status':cand['status'],'physical':'not_executed'}
                    else:row['methods'][label]=observe(label,folder,sub)
            else:
                for label in ['N1','F']:row['methods'][label]={'status':'no_valid_restored_first_feedback','physical':'not_executed'}
            row['end_to_end']=front['qualified'] and row['methods']['F']['status']=='passed'
            write(run/'results.json',ledger)
    except Exception as exc:
        ledger['execution_error']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
        write(run/'execution_error.json',ledger['execution_error'])
    finally:
        ledger.update(finished_at=e.retained.client.stamp(),wall_seconds=time.monotonic()-start,status='stopped_on_error' if ledger.get('execution_error') else 'finished')
        write(run/'results.json',ledger);print(json.dumps({k:ledger[k] for k in ('status','chat_attempts','complete_returns','AC','connections','wall_seconds')}),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['prepare','execute']);ap.add_argument('--run',required=True);args=ap.parse_args()
    {'prepare':prepare,'execute':execute}[args.command](Path(args.run).resolve())
