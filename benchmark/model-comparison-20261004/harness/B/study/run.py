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
PROMPT_HASH = 'e67172b2e0daa982139a2c99b1656b6e01982ec7ee54d96193395e3763eb0214'
ARCHIVE = Path('E:/masters-nudge-benchmark/sol61-ab-12case-20260930')
COMPARISON_ARMS = ['A1','A2','B1','B2']
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
def artifact(cid,arm): return (ARCHIVE if arm.startswith('A') else ROOT)/'runs'/cid/arm
def evaluation_directory(folder): return ROOT/'evaluation-v3'/folder.parent.name/folder.name
def score_path(folder): return folder/'score-v3.json'
def neutral_prompt(cid): return (ROOT/'prompts'/(cid+'.txt')).read_text(encoding='utf-8')

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def archive_manifest():
    names=('result.json','score-v3.json','final.patch','actor-events.jsonl','actor-final.txt',
           'execution-review.json','execution-evidence.json','prompt.txt','launch.json')
    return {str(path):sha(path) for cid in read(ARCHIVE/'plan.json')['cases'] for arm in ('A1','A2')
            for name in names if (path:=ARCHIVE/'runs'/cid/arm/name).is_file()}

def verify_archive(plan):
    assert archive_manifest()==plan['archived_A_manifest'], 'Archived A changed'

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
        verify_archive(plan)
        return plan
    old=read(ARCHIVE/'plan.json')
    source=PRODUCT/'plugins/masters-nudge'
    prompt=(source/'buddy-prompt.txt').read_text(encoding='utf-8').strip()
    assert textsha(prompt)==PROMPT_HASH
    assert prompt==(PRODUCT/'buddy-prompt.txt').read_text(encoding='utf-8').strip()
    for origin,target in [(source,PACKAGE),(ARCHIVE/'frozen-evaluation',EVALUATION)]:
        if not target.exists():shutil.copytree(origin,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.pytest_cache'))
        assert files(origin)==files(target)
    cases={}
    assert len(old['cases'])==12
    for cid,previous in old['cases'].items():
        original=(ARCHIVE/'prompts'/(cid+'.txt')).read_text(encoding='utf-8')
        assert textsha(original)==previous['A_prompt_sha256']==previous['B_prompt_sha256']
        assert (EVALUATION/'cases'/cid/'task.md').read_text(encoding='utf-8') in original
        path=ROOT/'prompts'/(cid+'.txt');path.parent.mkdir(exist_ok=True)
        path.write_text(original,encoding='utf-8',newline='\n')
        work=CAL/'cases'/cid
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=work,text=True).strip()==previous['base_commit']
        for arm in ('A1','A2'):
            folder=artifact(cid,arm)
            result=read(folder/'result.json');score=read(folder/'score-v3.json')
            assert result['actor_model']==MODEL and result['actor_reasoning']=='medium'
            assert result['base_commit']==previous['base_commit']
            assert textsha((folder/'prompt.txt').read_text(encoding='utf-8'))==previous['A_prompt_sha256']
            assert score['evaluator_sha256']==old['evaluator_sha256'] and isinstance(score['task_completed'],bool)
        cases[cid]={**previous,'new_order':['B1','B2']}
    binary=Path(old['codex_binary']);assert binary.is_file() and sha(binary)==old['codex_binary_sha256']
    plan={**old,
        'name':'Fresh B 12 cases x 2, finalized data/distinctions/information prompt and file-origin facts; archived Sol61 A comparison',
        'created_utc':datetime.now(timezone.utc).isoformat(),'cases':cases,
        'new_arms':['B1','B2'],'comparison_arms':COMPARISON_ARMS,'expected_deliveries':24,'comparison_deliveries':48,
        'A':'Reuse the immutable 24 archived A results; do not run or rescore A.',
        'B':'24 fresh B trials using the finalized package with file-origin facts and 40/25/61/35 field limits; maximum three delivered nudges.',
        'archive_root':str(ARCHIVE),'archived_A_manifest':archive_manifest(),
        'product_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=PRODUCT,text=True).strip(),
        'prompt_semantic_sha256':PROMPT_HASH,'package_hashes':files(PACKAGE),
        'evaluator_sha256':evaluate.verify(),'harness_sha256':sha(HARNESS),
        'adapter_sha256':sha(PREVIOUS/'rerun.py'),'experiment_script_sha256':sha(__file__),
        'workers':2,'restore':'Restore original worktree contents, nonignored untracked files, and original Git index.',
        'comparison_scope':'New B versus archived same-model A. Historical comparison; original study and the one-case pilot remain separate.',
        'taste':'Same frozen rubric; newly judge jointly completed archived-A/new-B pairs, two swapped-order Astra medium judges, third for disagreement.',
        'cost':'Compare recorded original A cost with new B Actor plus Provider cost. Current execution/taste grading costs separate; no new A cost incurred.'}
    assert plan['evaluator_sha256']==old['evaluator_sha256']
    save(existing,plan)
    save(ROOT/'archived-A-manifest.json',plan['archived_A_manifest'])
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
    return {'expected':24,'completed':sum(r['state']=='complete' for r in rows),'runs':rows}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','run','status'])
    args=parser.parse_args();sys.stdout.reconfigure(encoding='utf-8')
    plan=prepare()
    if args.action=='prepare': emit({'stage':'sealed','cases':12,'new_deliveries':24,'model':MODEL,'prompt_sha256':PROMPT_HASH});return
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
    save(ROOT/'restoration-confirmed.json',{'case_states_match':all(read(ROOT/'worktree-backups'/cid/'restored-state.json')==read(ROOT/'worktree-backups'/cid/'original-state.json') for cid in plan['cases'] if (ROOT/'worktree-backups'/cid/'restored-state.json').exists()),'archived_A_unchanged':True,'restored_cases':[cid for cid in plan['cases'] if (ROOT/'worktree-backups'/cid/'restored-state.json').exists()]})
    emit({'stage':'actors_finished','completed':status(plan)['completed'],'errors':errors})
    if errors: raise SystemExit(1)

if __name__=='__main__': main()
