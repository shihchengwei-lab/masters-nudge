"""Fresh paired A/B study; frozen product and established fixed evaluator."""
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
HARNESS = Path('D:/masters-nudge-benchmark/round-10-b-quota2-20260927/run.py')
MODEL = 'gpt-6.1-sol'
PROMPT_HASH = '62b3dfeb9421f4b384886e5f019e23879e99784f41237961d3ecd4032b19c2cb'
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
def artifact(cid,arm): return ROOT/'runs'/cid/arm
def evaluation_directory(folder): return ROOT/'evaluation-v3'/folder.parent.name/folder.name
def score_path(folder): return folder/'score-v3.json'
def neutral_prompt(cid): return (ROOT/'prompts'/(cid+'.txt')).read_text(encoding='utf-8')

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def prepare():
    existing=ROOT/'plan.json'
    if existing.exists():
        plan=read(existing)
        assert plan['package_hashes']==files(PACKAGE)
        assert plan['evaluator_sha256']==evaluate.verify()
        assert plan['codex_binary_sha256']==sha(plan['codex_binary'])
        assert plan['harness_sha256']==sha(HARNESS)
        assert plan['experiment_script_sha256']==sha(__file__)
        assert all(textsha(neutral_prompt(cid))==meta['A_prompt_sha256']==meta['B_prompt_sha256']
                   for cid,meta in plan['cases'].items())
        return plan
    source=PRODUCT/'plugins/masters-nudge'
    prompt=(source/'buddy-prompt.txt').read_text(encoding='utf-8').strip()
    assert textsha(prompt)==PROMPT_HASH
    assert prompt==(PRODUCT/'buddy-prompt.txt').read_text(encoding='utf-8').strip()
    for origin,target in [(source,PACKAGE),(PRODUCT/'benchmark/formal-v11/evaluation-v3',EVALUATION)]:
        if not target.exists(): shutil.copytree(origin,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.pytest_cache'))
        assert files(origin)==files(target)
    old=read(PARENT/'plan.json')
    cases={}
    for i,(cid,previous) in enumerate(old['cases'].items()):
        assert len(old['cases'])==12
        original=(PARENT/'runs'/cid/'B1/prompt.txt').read_text(encoding='utf-8')
        assert textsha(original)==previous['B_prompt_sha256']
        task=(EVALUATION/'cases'/cid/'task.md').read_text(encoding='utf-8')
        assert task in original
        assert not original.endswith('請高品味的完成任務。\n')
        path=ROOT/'prompts'/(cid+'.txt');path.parent.mkdir(exist_ok=True)
        path.write_text(original,encoding='utf-8',newline='\n')
        work=CAL/'cases'/cid
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=work,text=True).strip()
        assert head==previous['base_commit']
        cases[cid]={**previous,'A_prompt_sha256':textsha(original),'B_prompt_sha256':textsha(original),
                    'new_order':['A1','B1','B2','A2'] if i%2==0 else ['B1','A1','A2','B2']}
    binary=Path(shutil.which('codex.exe'));assert binary.is_file()
    version=subprocess.check_output([str(binary),'--version'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).strip()
    plan={
        'name':'Fresh 12-case paired A/B, approved structural-responsibility-backward tool',
        'status':'sealed','created_utc':datetime.now(timezone.utc).isoformat(),
        'cases':cases,'actor_model':MODEL,'actor_reasoning':'medium','provider_model':MODEL,'provider_reasoning':'medium',
        'judge_model':'gpt-6-astra','judge_reasoning':'medium','feedback_limit':3,
        'new_arms':['A1','A2','B1','B2'],'trials_per_case':2,'expected_deliveries':48,'workers':2,
        'actor_wall_timeout_seconds':1800,'pairwise_comparisons':['A-B'],
        'A':'Neutral task; hooks and plugins disabled. Fresh trials.',
        'B':'Same neutral task; frozen current Masters Nudge enabled, maximum three delivered nudges. Fresh trials.',
        'product_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=PRODUCT,text=True).strip(),
        'product_working_changes':True,'prompt_semantic_sha256':PROMPT_HASH,
        'package_hashes':files(PACKAGE),'evaluator_sha256':evaluate.verify(),'harness_sha256':sha(HARNESS),
        'adapter_sha256':sha(PREVIOUS/'rerun.py'),'experiment_script_sha256':sha(__file__),
        'codex_binary':str(binary),'codex_binary_sha256':sha(binary),'codex_cli_version':version,
        'contract':'Frozen evaluation-v3 checks plus semantic execution-contract review; no extra requirements.',
        'taste':'Existing fixed rubric, anonymous full source, two independent reversed-order Astra medium judges; third for disagreement. Primary taste comparison only jointly completed pairs.',
        'cost':'Actor wall time includes Provider wait; Actor and Provider tokens summed once. Cached input and output shown separately; evaluation/judge costs reported separately.',
        'retry_policy':'No outcome-based reruns or repair. Preserve timed-out trials and product faults. Stop scheduling on genuine execution/evaluation infrastructure failure.',
        'restore':'Snapshot source, untracked additions, and original Git index before resets; restore case state after scheduled trials.',
        'output_location':'E drive; preserve existing studies and calibration environments.',
    }
    save(existing,plan)
    return plan

sys.path.insert(0,str(PRODUCT/'benchmark/formal-v11/evaluation-v3'))
import evaluate
evaluate.ROOT=EVALUATION
initialize=prepare

def load_harness(name='paired_harness'):
    plan=prepare()
    adapter=load_module(name+'_adapter',PREVIOUS/'rerun.py')
    adapter.ROOT=ROOT;adapter.PACKAGE=PACKAGE;adapter.EVALUATION=EVALUATION;adapter.evaluate.ROOT=EVALUATION
    runner=adapter.load_runner(plan)
    runner.MODEL=MODEL;runner.ARMS=plan['new_arms'];runner.TIMEOUT=plan['actor_wall_timeout_seconds'];runner.STOP=STOP
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
    return {'expected':48,'completed':sum(r['state']=='complete' for r in rows),'runs':rows}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','run','status'])
    args=parser.parse_args();sys.stdout.reconfigure(encoding='utf-8')
    plan=prepare()
    if args.action=='prepare': emit({'stage':'sealed','cases':12,'new_deliveries':48,'model':MODEL,'prompt_sha256':PROMPT_HASH});return
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
    emit({'stage':'actors_finished','completed':status(plan)['completed'],'errors':errors})
    if errors: raise SystemExit(1)

if __name__=='__main__': main()
