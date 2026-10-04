"""Round 10 B-only rerun; original A1/A2 and original B artifacts remain fixed."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import threading
import time

OUT = Path(__file__).resolve().parent
CAL = Path('D:/masters-nudge-benchmark/round-10-calibration')
SELECTION = Path('D:/masters-nudge-benchmark/selection/round-10')
PRODUCT = Path(r'C:\Users\kk789\Desktop\GH_repos\masters-nudge')
PACKAGE = OUT / 'frozen-plugin'
sys.path.insert(0, str(CAL))
import runner as calibration
sys.path.insert(0, str(PRODUCT))
from masters_nudge.providers import resolve_codex_bin

MODEL = 'gpt-6.1-sol'
PROVIDER_MODEL = 'gpt-6.1-sol'
TIMEOUT = 1800
ARMS = ['F1', 'F2']
STOP = threading.Event()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def save(p, data):
    calibration.save(Path(p), data)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def textsha(s):
    return hashlib.sha256(s.encode()).hexdigest()

def emit(data):
    print(json.dumps(data, ensure_ascii=False), flush=True)

def package_hashes():
    return {p.relative_to(PACKAGE).as_posix(): sha(p) for p in sorted(PACKAGE.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}

def prompts(cid):
    a = (CAL/'actors'/cid/'prompt.txt').read_text(encoding='utf-8')
    assert a.endswith('請高品味的完成任務。\n'), cid
    return a, a.removesuffix('請高品味的完成任務。\n')

def initialize():
    manifest = read(SELECTION/'selected-manifest.json')
    if (OUT/'plan.json').exists():
        plan = read(OUT/'plan.json')
        assert sha(SELECTION/'selected-manifest.json') == plan['selection_sha256']
        assert package_hashes() == plan['package_hashes']
        return plan
    assert manifest['case_count'] == 12
    if not PACKAGE.exists():
        shutil.copytree(PRODUCT/'plugins/masters-nudge', PACKAGE,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.pytest_cache'))
    cases = {}
    for c in manifest['cases']:
        cid = c['case_id']
        a1 = read(CAL/'state'/cid/'actor.json')
        prepared = read(CAL/'state'/cid/'prepare.json')
        launch = read(CAL/'actors'/cid/'launch.json')
        a, b = prompts(cid)
        assert textsha(a) == a1['prompt_sha256'] == launch['prompt_sha256']
        assert sha(CAL/'actors'/cid/'final.patch') == a1['patch_sha256']
        assert read(CAL/'state'/cid/'preflight.json')['valid']
        assert prepared['base_commit'] == launch['base_commit']
        assert a1['model'] == MODEL and a1['reasoning'] == 'medium'
        for name, digest in c['artifact_sha256'].items():
            assert sha(SELECTION/'cases'/cid/name) == digest
        cases[cid] = {'base_commit': launch['base_commit'], 'container': 'image' in prepared,
            'A1_result_sha256': sha(CAL/'state'/cid/'actor.json'), 'A1_patch_sha256': a1['patch_sha256'],
            'A_prompt_sha256': textsha(a), 'B_prompt_sha256': textsha(b),
            'artifact_sha256': c['artifact_sha256'], 'image_id': prepared.get('image', {}).get('image_id')}
    plan = {'name': 'Round 10 B-only rerun, same 12 cases and two trials',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'product_commit': calibration.checked(['git','rev-parse','HEAD'],PRODUCT).strip(),
        'selection_sha256': sha(SELECTION/'selected-manifest.json'),
        'actor_model': MODEL, 'actor_reasoning': 'medium', 'provider_model': MODEL, 'provider_reasoning': 'medium',
        'actor_wall_timeout_seconds': TIMEOUT, 'workers': 2, 'reused_arms': ['A1', 'A2'], 'new_arms': ARMS,
        'package_hashes': package_hashes(), 'cases': cases,
        'A': 'Original A1 prompt, including 請高品味的完成任務。; hooks/plugins disabled.',
        'B': 'Same task and environment, final generic taste sentence removed; frozen Masters Nudge enabled.',
        'evaluation': 'Fixed public-contract checks; two independent GPT-6 Astra medium judges with reversed anonymous order; third on disagreement. Concrete behavior concerns are checked against the task and replayed when material.',
        'retry_policy': 'Preserve infrastructure failures separately. Never rerun based on contract failure or quality outcome.',
        'cost_scope': 'Actor wall time includes synchronous Provider waits; Provider token usage is added separately. A1 source data retained.'}
    baseline = OUT.parent / 'round-10-benchmark'
    plan['baseline_root'] = str(baseline)
    plan['baseline_product_commit'] = read(baseline/'plan.json')['product_commit']
    plan['baseline_results_sha256'] = sha(baseline/'results.json')
    for cid, meta in plan['cases'].items():
        meta['A2_result_sha256'] = sha(baseline/'runs'/cid/'A2'/'result.json')
        meta['A2_patch_sha256'] = sha(baseline/'runs'/cid/'A2'/'final.patch')
    save(OUT/'plan.json',plan)
    shutil.copy2(SELECTION/'selected-manifest.json',OUT/'selected-manifest.json')
    shutil.copy2(CAL/'taste-review.json',OUT/'selection-taste-review.json')
    emit({'stage':'plan_fixed','cases':12,'reused_A1':12,'new_runs':24,'product_commit':plan['product_commit']})
    return plan

def toml(value):
    if isinstance(value, dict): return '{'+','.join(json.dumps(k)+'='+toml(v) for k,v in value.items())+'}'
    if isinstance(value, list): return '['+','.join(toml(v) for v in value)+']'
    return json.dumps(value)

def hook_arguments():
    def resolve(v):
        if isinstance(v,dict): return {k:resolve(x) for k,x in v.items()}
        if isinstance(v,list): return [resolve(x) for x in v]
        return v.replace('${PLUGIN_ROOT}',PACKAGE.as_posix()) if isinstance(v,str) else v
    args=[]
    for k,v in read(PACKAGE/'.mcp.json')['mcpServers'].items():
        args += ['-c',f'mcp_servers.{k}={toml(resolve(v))}']
    for k,v in read(PACKAGE/'hooks/hooks.json')['hooks'].items():
        args += ['-c',f'hooks.{k}={toml(v)}']
    return args

def git(work,*args):
    return calibration.checked(['git',*args],work)

def safe_work(cid):
    work = (CAL/'cases'/cid).resolve(strict=True)
    assert work.parent == (CAL/'cases').resolve(strict=True)
    assert Path(git(work,'rev-parse','--show-toplevel').strip()).resolve() == work
    return work

def reset(cid, base):
    work=safe_work(cid)
    git(work,'reset','--hard',base)
    git(work,'clean','-fd')

def apply(work, patch, excludes=()):
    calibration.checked(['git','apply','--allow-empty','--whitespace=nowarn',
        *['--exclude='+x for x in excludes],str(patch)],work)

def is_test(name):
    return bool(re.search(r'(^|/)(tests?|__tests__|specs?)(/|$)|(^|/)test_[^/]+|(?:_test|\.test|\.spec)\.(?:go|py|jsx?|tsx?)$',name))

def attempts(data):
    db=data/'feedback.sqlite3'
    if not db.exists(): return [],0
    with sqlite3.connect(db) as con:
        con.row_factory=sqlite3.Row
        rows=[dict(x) for x in con.execute('SELECT * FROM attempts ORDER BY started')]
        for row in rows: row['detail']=json.loads(row['detail']) if row.get('detail') else {}
        columns={x[1] for x in con.execute('PRAGMA table_info(rounds)')}
        field=next((x for x in ['skipped_test_patches','skipped_new_test_patches'] if x in columns),None)
        skipped=con.execute(f'SELECT COALESCE(SUM({field}),0) FROM rounds').fetchone()[0] if field else 0
    return rows,skipped

def verification(cid,arm,meta,artifact,added_tests):
    if meta['container']:
        label='round10-quota2-'+arm
        patch='/mnt/d/'+(artifact/'final.patch').as_posix()[3:]
        p=calibration.command(['wsl.exe','-u','root','--exec','python3',
            '/mnt/d/masters-nudge-benchmark/round-10-calibration/pro_env.py','verify',cid,
            '--patch',patch,'--label',label],OUT,2400)
        (artifact/'verification-console.txt').write_text(p.stdout+p.stderr,encoding='utf-8')
        if p.returncode: raise RuntimeError((p.stdout+p.stderr)[-4000:])
        source=CAL/'logs'/cid/label
        shutil.copytree(source,artifact/'verification',dirs_exist_ok=True)
        return [read(source/'result.json')]
    reset(cid,meta['base_commit'])
    apply(safe_work(cid),artifact/'final.patch',added_tests)
    calibration.test_patch(cid)
    results=calibration.verify(cid,'round10-quota2-'+arm)
    for i,result in enumerate(results,1):
        dest=artifact/f'contract-{i}.txt'
        shutil.copy2(result['log'],dest)
        result['log']=str(dest)
    return results

def run_one(cid,arm,plan):
    meta=plan['cases'][cid]
    artifact=OUT/'runs'/cid/arm
    if (artifact/'result.json').exists(): return read(artifact/'result.json')
    artifact.mkdir(parents=True,exist_ok=True)
    assert package_hashes()==plan['package_hashes']
    assert sha(CAL/'state'/cid/'actor.json')==meta['A1_result_sha256']
    reset(cid,meta['base_commit'])
    work=safe_work(cid)
    tracked=set(git(work,'ls-tree','-r','--name-only','HEAD').splitlines())
    assert arm in ('F1','F2')
    enabled=True
    prompt=prompts(cid)[int(enabled)]
    assert textsha(prompt)==meta['B_prompt_sha256' if enabled else 'A_prompt_sha256']
    (artifact/'prompt.txt').write_text(prompt,encoding='utf-8',newline='\n')
    env=calibration.env(cid)
    pinned_binary=Path(plan['codex_binary']).resolve()
    env['PATH']=str(pinned_binary.parent)+os.pathsep+env.get('PATH','')
    assert Path(shutil.which('codex.exe',path=env['PATH'])).resolve()==pinned_binary
    env.update(MASTERS_NUDGE_ACTIVE='0',PYTHONDONTWRITEBYTECODE='1')
    data=artifact/'masters-nudge-data'
    if enabled:
        data.mkdir(exist_ok=True)
        save(data/'config.json',{'provider':'openai','model':PROVIDER_MODEL})
        env.update(MASTERS_NUDGE_TEST_MODE='1',PLUGIN_ROOT=str(PACKAGE),
            MASTERS_NUDGE_DATA_DIR=str(data),MASTERS_NUDGE_RUNTIME_DIR=str(PACKAGE))
    args=[resolve_codex_bin(),'-c','project_doc_max_bytes=0','-c','features.multi_agent=false',
        '-c','model_reasoning_effort="xhigh"',
        *(['--enable','hooks','--disable','plugins',*hook_arguments()] if enabled else ['--disable','hooks','--disable','plugins']),
        'exec','--ignore-user-config','--ignore-rules',
        *(['--dangerously-bypass-hook-trust'] if enabled else []),
        '--skip-git-repo-check','--ephemeral','--json','-s','danger-full-access','-m',MODEL,
        '-C',str(work),'-o',str(artifact/'actor-final.txt'),'-']
    save(artifact/'launch.json',{'command':args,'hooks':enabled,'prompt_sha256':textsha(prompt),
        'base_commit':meta['base_commit'],'timeout_seconds':TIMEOUT,'model':MODEL,'reasoning':'xhigh',
        'provider_model':PROVIDER_MODEL,'provider_reasoning':'medium','provider_binary':str(pinned_binary),'provider_binary_sha256':sha(pinned_binary)})
    started=time.monotonic()
    fault=''
    with (artifact/'actor-events.jsonl').open('w',encoding='utf-8') as stdout, (artifact/'actor-stderr.txt').open('w',encoding='utf-8') as stderr:
        proc=subprocess.Popen(args,cwd=work,env=env,stdin=subprocess.PIPE,stdout=stdout,stderr=stderr,
            text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
        save(artifact/'running.json',{'pid':proc.pid,'started_utc':datetime.now(timezone.utc).isoformat()})
        emit({'case':cid,'arm':arm,'stage':'actor_started','pid':proc.pid})
        try: proc.communicate(prompt,timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            calibration.command(['taskkill.exe','/PID',str(proc.pid),'/T','/F'],OUT,60)
            proc.wait(timeout=30)
            fault='Actor exceeded 1800 second wall budget'
    seconds=round(time.monotonic()-started,3)
    events=[]
    for line in (artifact/'actor-events.jsonl').read_text(encoding='utf-8').splitlines():
        try: events.append(json.loads(line))
        except ValueError: pass
    usage=next((e.get('usage') or {} for e in reversed(events) if e.get('type')=='turn.completed'),{})
    changes=sum(e.get('type')=='item.completed' and e.get('item',{}).get('type')=='file_change' for e in events)
    git(work,'add','-N','.')
    names=git(work,'diff','--name-only','HEAD').splitlines()
    modified_tests=[n for n in names if n in tracked and is_test(n)]
    added_tests=[n for n in names if n not in tracked and is_test(n)]
    patch=git(work,'diff','--binary','HEAD')
    (artifact/'final.patch').write_text(patch,encoding='utf-8',newline='\n')
    records,skipped=attempts(data) if enabled else ([],0)
    save(artifact/'provider-attempts.json',records)
    provider_usage={k:sum(int(x.get('detail',{}).get('usage',{}).get(k) or 0) for x in records)
        for k in ['input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens']}
    provider_faults=[x for x in records if x.get('outcome') not in ('feedback','silence')]
    if proc.returncode and not fault: fault='Actor exit '+str(proc.returncode)
    if enabled and provider_faults and not fault: fault='Provider fault'
    if enabled and changes and not records and not skipped and not fault: fault='No Provider judgment after file change'
    checks=[]
    verification_error=''
    try:
        if modified_tests: verification_error='Actor modified pre-existing tests'
        else: checks=verification(cid,arm,meta,artifact,added_tests)
    except Exception as exc: verification_error=str(exc)
    passed=proc.returncode==0 and not modified_tests and not verification_error and bool(checks) and all(
        (v.get('reward')=='1' if meta['container'] else v['exit_code']==0) and v['passed']>0 for v in checks)
    result={'case':cid,'arm':arm,'actor_model':MODEL,'actor_reasoning':'xhigh',
        'provider_model':PROVIDER_MODEL if enabled else None,'provider_reasoning':'medium' if enabled else None,
        'base_commit':meta['base_commit'],'prompt_sha256':textsha(prompt),'patch_sha256':sha(artifact/'final.patch'),
        'actor_exit':proc.returncode,'actor_elapsed_seconds':seconds,'total_elapsed_seconds':round(time.monotonic()-started,3),
        'verification_elapsed_seconds':round(sum(v['elapsed_seconds'] for v in checks),3),
        'actor_usage':usage,'provider_usage':provider_usage,'file_change_events':changes,
        'provider_attempt_count':len(records),'provider_feedback_count':sum(x['outcome']=='feedback' for x in records),
        'provider_silence_count':sum(x['outcome']=='silence' for x in records),'provider_fault_count':len(provider_faults),
        'provider_delivered_count':sum(bool(x.get('delivered')) for x in records),'provider_skipped_test_patches':skipped,
        'tests_modified':modified_tests,'actor_added_tests':added_tests,'verification':checks,
        'verification_error':verification_error,'execution_fault':fault,'contract_passed':passed,'artifact_dir':str(artifact)}
    save(artifact/'result.json',result)
    (artifact/'running.json').unlink(missing_ok=True)
    emit({'case':cid,'arm':arm,'stage':'complete','passed':passed,'fault':fault,
        'verification_error':verification_error,'seconds':seconds,'feedback':result['provider_feedback_count'],
        'silence':result['provider_silence_count']})
    return result

def _run_case(cid,plan):
    if STOP.is_set():
        emit({'case':cid,'stage':'not_started_after_infrastructure_fault'})
        return
    work=safe_work(cid)
    snapshot=OUT/'worktree-backups'/f'{cid}.patch'
    snapshot.parent.mkdir(exist_ok=True)
    if not snapshot.exists():
        git(work,'add','-N','.')
        snapshot.write_text(git(work,'diff','--binary','HEAD'),encoding='utf-8',newline='\n')
    try:
        for arm in ARMS:
            if STOP.is_set():
                emit({'case':cid,'arm':arm,'stage':'not_started_after_infrastructure_fault'})
                break
            result=run_one(cid,arm,plan)
            if result['execution_fault'] or (result['verification_error'] and not result['tests_modified']):
                STOP.set()
                raise RuntimeError(f'{cid}/{arm}: '+result['execution_fault']+' '+result['verification_error'])
    except Exception:
        STOP.set()
        raise
    finally:
        reset(cid,plan['cases'][cid]['base_commit'])
        apply(work,snapshot)
        emit({'case':cid,'stage':'calibration_worktree_restored'})

def run_case(cid,plan):
    # Recovery commands can overlap in time, but a case must have one worktree owner.
    import msvcrt
    lockfile=OUT/'case-locks'/(cid+'.lock')
    lockfile.parent.mkdir(exist_ok=True)
    with lockfile.open('a+b') as guard:
        if lockfile.stat().st_size==0: guard.write(b'0'); guard.flush()
        while True:
            guard.seek(0)
            try:
                msvcrt.locking(guard.fileno(),msvcrt.LK_NBLCK,1)
                break
            except OSError: time.sleep(1)
        try:
            ready=[OUT/'runs'/cid/arm/'result.json' for arm in ARMS]
            if all(p.exists() and not read(p)['execution_fault'] for p in ready):
                emit({'case':cid,'stage':'already_complete'})
                return
            return _run_case(cid,plan)
        finally:
            guard.seek(0)
            msvcrt.locking(guard.fileno(),msvcrt.LK_UNLCK,1)

def status(plan):
    done=[]; running=[]
    for cid in plan['cases']:
        for arm in ARMS:
            p=OUT/'runs'/cid/arm
            if (p/'result.json').exists():
                r=read(p/'result.json')
                done.append({'case':cid,'arm':arm,'passed':r['contract_passed'],'fault':r['execution_fault'],
                    'verification_error':r['verification_error']})
            elif (p/'running.json').exists():running.append({'case':cid,'arm':arm,**read(p/'running.json')})
    return {'completed':len(done),'expected':24,'results':done,'running':running}

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','run','status']);p.add_argument('cases',nargs='*')
    args=p.parse_args();plan=initialize()
    if args.action=='status':emit(status(plan))
    if args.action=='run':
        save(OUT/'orchestrator.json', {'pid':os.getpid(),'started_utc':datetime.now(timezone.utc).isoformat()})
        selected=args.cases or list(plan['cases'])
        assert set(selected)<=set(plan['cases'])
        errors=[]
        with ThreadPoolExecutor(max_workers=plan['workers']) as pool:
            pending={pool.submit(run_case,cid,plan):cid for cid in selected}
            for future in as_completed(pending):
                try:future.result()
                except Exception as exc:
                    error={'case':pending[future],'error':str(exc)};errors.append(error);emit(error)
                    save(OUT/'errors'/f'{pending[future]}.json',error)
        save(OUT/'execution-summary.json',{**status(plan),'errors':errors})
        if errors:raise SystemExit(1)
