"""New E Sol xhigh Actor plus Astra medium Provider; immutable D effort comparison."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
PRODUCT = Path('C:/Users/kk789/Desktop/GH_repos/masters-nudge')
PARENT = Path('D:/masters-nudge-benchmark/round-11-three-arm-20260927')
CAL = Path('D:/masters-nudge-benchmark/round-10-calibration')
PREVIOUS = Path('E:/masters-nudge-benchmark/round-11-b-8f6db77-20260929')
PACKAGE = ROOT/'frozen-plugin'
EVALUATION = ROOT/'frozen-evaluation'
HARNESS = ROOT/'actor_runner.py'
SOURCE_HARNESS = Path('D:/masters-nudge-benchmark/round-10-b-quota2-20260927/run.py')
B_ARCHIVE = Path('E:/masters-nudge-benchmark/sol61-b-finalized-12case-20261001')
MODEL = 'gpt-6.1-sol'
PROMPT_HASH = 'e67172b2e0daa982139a2c99b1656b6e01982ec7ee54d96193395e3763eb0214'
ARCHIVE = Path('E:/masters-nudge-benchmark/sol61-ab-12case-20260930')
D_REFERENCE = Path('E:/masters-nudge-benchmark/sol61-astra-provider-12case-20261001-desktop')
COMPARISON_ARMS = ['D1','D2','E1','E2']
AMENDMENT = True
STOP = threading.Event()

def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def textsha(value): return hashlib.sha256(value.encode('utf-8')).hexdigest()
def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    pending=path.with_suffix(path.suffix+'.tmp')
    pending.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    pending.replace(path)
def emit(value): print(json.dumps(value,ensure_ascii=False),flush=True)
def files(root):
    return {p.relative_to(root).as_posix():sha(p) for p in root.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
def artifact(cid,arm):
    assert arm in COMPARISON_ARMS
    return (D_REFERENCE if arm.startswith('D') else ROOT)/'runs'/cid/arm

def evaluation_directory(folder): return ROOT/'evaluation-v3'/folder.parent.name/folder.name
def score_path(folder): return folder/'score-v3.json'
def neutral_prompt(cid): return (ROOT/'prompts'/(cid+'.txt')).read_text(encoding='utf-8')

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def reference_manifest():
    names=('result.json','score-v3.json','final.patch','actor-events.jsonl','actor-final.txt','execution-review.json','execution-evidence.json','prompt.txt','launch.json','provider-attempts.json')
    paths=[D_REFERENCE/'runs'/cid/arm/name for cid in read(D_REFERENCE/'plan.json')['cases'] for arm in ('D1','D2') for name in names]
    paths += [D_REFERENCE/name for name in ('plan.json','results-summary.json','diagnostic-adjusted-summary.json','REPORT.zh-TW.md','final-integrity.json','diagnostic-integrity.json','harness-source-manifest.json')]
    paths += list((D_REFERENCE/'blind-v3/judges').glob('*/*/*/judge-*/output.json'))
    paths += list((D_REFERENCE/'diagnostics').rglob('comparison.json'))
    return {str(p):sha(p) for p in paths if p.is_file()}

def verify_archive(plan):
    assert reference_manifest()==plan['reference_manifest'], 'Completed D reference changed'

def completed_score(cid,arm):
    score=dict(read(score_path(artifact(cid,arm))))
    score['frozen_task_completed']=score['task_completed']
    if cid in ('flipt-segments','clap-2297'):
        proof=read(ROOT/'diagnostics'/cid/'comparison.json')
        row=next(r for r in proof['rows'] if r['arm']==arm)
        if not row['contract_passed']:
            score['task_completed']=False
            score['confirmed_original_clause_gap']=proof['task_clause']
    return score

def prepare():
    existing=ROOT/'plan.json'
    if existing.exists():
        plan=read(existing)
        assert plan['package_hashes']==files(PACKAGE)
        assert plan['evaluator_sha256']==evaluate.verify()
        assert plan['codex_binary_sha256']==sha(plan['codex_binary'])
        assert plan['harness_sha256']==sha(HARNESS) and plan['experiment_script_sha256']==sha(__file__)
        assert plan['source_harness_sha256']==sha(SOURCE_HARNESS) and plan['adapter_sha256']==sha(PREVIOUS/'rerun.py')
        assert all(textsha(neutral_prompt(cid))==meta['D_prompt_sha256']==meta['E_prompt_sha256'] for cid,meta in plan['cases'].items())
        return plan
    old=read(D_REFERENCE/'plan.json')
    assert read(D_REFERENCE/'pipeline-status.json')['status']=='complete'
    assert textsha((PACKAGE/'buddy-prompt.txt').read_text(encoding='utf-8').strip())==PROMPT_HASH
    assert files(PACKAGE)==files(D_REFERENCE/'frozen-plugin') and files(EVALUATION)==files(D_REFERENCE/'frozen-evaluation')
    cases={}
    for cid,meta in old['cases'].items():
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=CAL/'cases'/cid,text=True).strip()==meta['base_commit']
        assert textsha(neutral_prompt(cid))==meta['D_prompt_sha256']
        for arm in ('D1','D2'):
            result=read(artifact(cid,arm)/'result.json')
            assert result['actor_model']==MODEL and result['actor_reasoning']=='medium'
            assert result['provider_model']=='gpt-6-astra' and result['provider_reasoning']=='medium'
        cases[cid]={**meta,'E_prompt_sha256':meta['D_prompt_sha256'],'new_order':['E1','E2']}
    binary=ROOT/'frozen-cli/codex.exe'
    assert sha(binary)==old['codex_binary_sha256']
    assert subprocess.check_output([str(binary),'--version'],text=True).strip()=='codex-cli 0.159.2'
    plan={**old,'name':'E Sol xhigh Actor plus Astra medium Provider; 12 cases x2; D medium primary comparison',
        'created_utc':datetime.now(timezone.utc).isoformat(),'actor_reasoning':'xhigh','provider_model':'gpt-6-astra','provider_reasoning':'medium',
        'cases':cases,'new_arms':['E1','E2'],'comparison_arms':COMPARISON_ARMS,'expected_deliveries':24,'comparison_deliveries':48,
        'pairwise_comparisons':['D-E'],'codex_binary':str(binary),'codex_binary_sha256':sha(binary),'codex_cli_version':'0.159.2',
        'reference_root':str(D_REFERENCE),'reference_manifest':reference_manifest(),
        'package_hashes':files(PACKAGE),'evaluator_sha256':evaluate.verify(),'harness_sha256':sha(HARNESS),
        'source_harness_sha256':sha(SOURCE_HARNESS),'adapter_sha256':sha(PREVIOUS/'rerun.py'),'experiment_script_sha256':sha(__file__),
        'workers':2,'actor_wall_timeout_seconds':1800,'feedback_limit':3,
        'comparison_scope':'Only new E24. Reuse D24 unchanged; same model, Provider medium, frozen CLI, task, base, tool and fixed timeout. Actor effort medium -> xhigh.',
        'contract_supplements':'Apply the same already-confirmed original Flipt rollout-shape and Clap occurrence-preservation probes symmetrically to D1/D2/E1/E2 before anonymous taste. Preserve frozen scores.',
        'taste':'Unchanged frozen rubric; D-E jointly completed only; two reversed Astra medium orders, third on disagreement.',
        'cost':'D/E Actor plus Provider complete-usage pairs. Completion and time include all trials. Grading and diagnostics separate.'}
    for obsolete in ('archived_A_manifest','B_manifest_sha256','B_seal_sha256','A','B','D','CLI_recovery','archive_root','B_archive_root'):
        plan.pop(obsolete,None)
    save(existing,plan);save(ROOT/'reference-manifest.json',plan['reference_manifest'])
    return plan

sys.path.insert(0,str(PRODUCT/'benchmark/formal-v11/evaluation-v3'))
import evaluate
evaluate.ROOT=EVALUATION
initialize=prepare

def load_harness(name='paired_harness'):
    plan=prepare()
    adapter=load_module(name+'_adapter',PREVIOUS/'rerun.py')
    adapter.ROOT=ROOT;adapter.PACKAGE=PACKAGE;adapter.EVALUATION=EVALUATION;adapter.evaluate.ROOT=EVALUATION;adapter.HARNESS=HARNESS
    runner=adapter.load_runner(plan)
    runner.MODEL=MODEL;runner.PROVIDER_MODEL=plan['provider_model'];runner.ARMS=plan['new_arms'];runner.TIMEOUT=plan['actor_wall_timeout_seconds'];runner.STOP=STOP
    runner.prompts=lambda cid:(neutral_prompt(cid),neutral_prompt(cid))
    return runner

def case_state(runner,cid):
    work=runner.safe_work(cid)
    patch=subprocess.check_output(['git','diff','--binary','HEAD'],cwd=work)
    names=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=work).decode().split('\0')
    return {'patch_sha256':hashlib.sha256(patch).hexdigest(),
            'untracked':{name:sha(work/name) for name in names if name and (work/name).is_file()},
            'head':runner.git(work,'rev-parse','HEAD').strip()}

def run_case(cid,plan,runner):
    work=runner.safe_work(cid)
    backup=ROOT/'worktree-backups'/cid;backup.mkdir(parents=True,exist_ok=True)
    original=case_state(runner,cid)
    save(backup/'original-state.json',original)
    index=Path(runner.git(work,'rev-parse','--path-format=absolute','--git-path','index').strip())
    assert index.is_file()
    shutil.copy2(index,backup/'index')
    runner.git(work,'add','-N','.')
    snapshot=backup/'original.patch'
    snapshot.write_text(runner.git(work,'diff','--binary','HEAD'),encoding='utf-8',newline='\n')
    try:
        for arm in plan['cases'][cid]['new_order']:
            if STOP.is_set(): break
            result=runner.run_one(cid,arm,plan)
            fault=result['execution_fault']
            if result['verification_error'] and not result['tests_modified']:
                STOP.set();raise RuntimeError(cid+'/'+arm+': verification infrastructure '+result['verification_error'])
            if fault and fault not in ('Actor exceeded 1800 second wall budget','Provider fault','No Provider judgment after file change'):
                STOP.set();raise RuntimeError(cid+'/'+arm+': '+fault)
    finally:
        runner.reset(cid,plan['cases'][cid]['base_commit'])
        runner.apply(work,snapshot)
        shutil.copy2(backup/'index',index)
        restored=case_state(runner,cid)
        save(backup/'restored-state.json',restored)
        assert restored==original, 'Original case state was not restored: '+cid
        emit({'case':cid,'stage':'calibration_worktree_restored','state_matches':True})

def status(plan):
    rows=[]
    for cid in plan['cases']:
        for arm in plan['new_arms']:
            out=artifact(cid,arm)
            if (out/'result.json').exists():
                result=read(out/'result.json')
                rows.append({'case':cid,'arm':arm,'state':'complete','fixed_checks_pass':result['contract_passed'],
                             'seconds':result['actor_elapsed_seconds'],'fault':result['execution_fault']})
            elif (out/'running.json').exists(): rows.append({'case':cid,'arm':arm,'state':'running',**read(out/'running.json')})
    return {'expected':24,'completed':sum(r['state']=='complete' for r in rows),'runs':rows}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','run','status'])
    args=parser.parse_args();sys.stdout.reconfigure(encoding='utf-8')
    plan=prepare()
    if args.action=='prepare': emit({'stage':'sealed','cases':12,'new_deliveries':24,'model':MODEL,'actor_reasoning':'xhigh','provider_model':'gpt-6-astra','provider_reasoning':'medium','hooks':True});return
    if args.action=='status': emit(status(plan));return
    assert not list((ROOT/'runs').glob('*/*/result.json')),'Do not resume or repeat recorded outcomes through the run action.'
    save(ROOT/'orchestrator.json',{'pid':os.getpid(),'started_utc':datetime.now(timezone.utc).isoformat()})
    runner=load_harness();errors=[]
    with ThreadPoolExecutor(max_workers=plan['workers']) as pool:
        pending={pool.submit(run_case,cid,plan,runner):cid for cid in plan['cases']}
        for future in as_completed(pending):
            cid=pending[future]
            try: future.result()
            except Exception as exc:
                STOP.set();row={'case':cid,'error':str(exc)};errors.append(row);save(ROOT/'errors'/(cid+'.json'),row);emit(row)
    save(ROOT/'execution-summary.json',{**status(plan),'errors':errors})
    verify_archive(plan)
    save(ROOT/'restoration-confirmed.json',{'case_states_match':all(read(ROOT/'worktree-backups'/cid/'restored-state.json')==read(ROOT/'worktree-backups'/cid/'original-state.json') for cid in plan['cases'] if (ROOT/'worktree-backups'/cid/'restored-state.json').exists()),'reference_D_unchanged':True,'restored_cases':[cid for cid in plan['cases'] if (ROOT/'worktree-backups'/cid/'restored-state.json').exists()]})
    emit({'stage':'actors_finished','completed':status(plan)['completed'],'errors':errors})
    if errors: raise SystemExit(1)

if __name__=='__main__': main()
