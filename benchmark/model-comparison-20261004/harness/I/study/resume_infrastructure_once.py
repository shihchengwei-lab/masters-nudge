"""Continue unfinished trials once after a pre-edit capacity interruption.

No successful or failed solution is re-run. Only a transport failure with zero
file changes and zero Provider calls can be archived and started afresh.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import ctypes, json, os, subprocess, sys, time
import run

ROOT=run.ROOT
env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')

def wait_pid(pid):
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong]
    kernel.OpenProcess.restype=ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_ulong]
    kernel.CloseHandle.argtypes=[ctypes.c_void_p]
    handle=kernel.OpenProcess(0x00100000,False,pid)
    if handle:
        try: kernel.WaitForSingleObject(handle,0xFFFFFFFF)
        finally: kernel.CloseHandle(handle)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    first=run.read(ROOT/'pipeline-process.json')
    wait_pid(first['pid'])
    plan=run.prepare()
    if run.read(ROOT/'pipeline-status.json')['status']=='complete':raise SystemExit(0)
    before=run.read(ROOT/'execution-summary.json')
    moved=[]
    for p in ROOT.glob('runs/*/*/result.json'):
        r=run.read(p)
        if not r['execution_fault']:continue
        events=[json.loads(l) for l in (p.parent/'actor-events.jsonl').read_text(encoding='utf-8').splitlines() if l.startswith('{')]
        capacity=any('Selected model is at capacity' in json.dumps(e) for e in events if e.get('type') in ('error','turn.failed'))
        assert capacity and r['file_change_events']==0 and r['provider_attempt_count']==0 and (p.parent/'final.patch').stat().st_size==0, 'Not a pre-edit capacity failure: '+str(p)
        destination=(ROOT/'infrastructure-attempts'/r['case']/r['arm']/'capacity-before-edit').resolve()
        assert destination.is_relative_to(ROOT.resolve()) and not destination.exists()
        destination.parent.mkdir(parents=True,exist_ok=True)
        p.parent.rename(destination)
        moved.append({'case':r['case'],'arm':r['arm'],'directory':str(destination),'reason':'capacity before any edits or Provider calls'})
    assert moved, 'No eligible interruption to recover'
    recovery={'policy':'one recovery after capacity interruption; no outcome-based reruns','original_summary':before,'preserved_attempts':moved,'backoff_seconds':300,'started_utc':run.datetime.now(run.timezone.utc).isoformat()}
    run.save(ROOT/'infrastructure-recovery.json',recovery)
    run.emit({'stage':'capacity_backoff','seconds':300,'preserved_attempts':len(moved)})
    time.sleep(300)
    run.save(ROOT/'orchestrator.json',{'pid':os.getpid(),'started_utc':run.datetime.now(run.timezone.utc).isoformat(),'recovery':True})
    runner=run.load_harness('infrastructure_continuation');errors=[]
    pending_cases=[cid for cid in plan['cases'] if not all((ROOT/'runs'/cid/arm/'result.json').exists() for arm in plan['new_arms'])]
    with ThreadPoolExecutor(max_workers=plan['workers']) as pool:
        pending={pool.submit(run.run_case,cid,plan,runner):cid for cid in pending_cases}
        for future in as_completed(pending):
            cid=pending[future]
            try:future.result()
            except Exception as exc:
                run.STOP.set();row={'case':cid,'error':str(exc)};errors.append(row);run.save(ROOT/'errors'/(cid+'.json'),row);run.emit(row)
    run.save(ROOT/'execution-summary.json',{**run.status(plan),'errors':errors})
    run.verify_archive(plan)
    states={cid:run.read(ROOT/'worktree-backups'/cid/'restored-state.json')==run.read(ROOT/'worktree-backups'/cid/'original-state.json') for cid in plan['cases']}
    run.save(ROOT/'restoration-confirmed.json',{'case_states_match':all(states.values()),'references_C_F_unchanged':True,'restored_cases':list(states)})
    if errors:
        run.save(ROOT/'pipeline-status.json',{'status':'stopped','stage':'actors-capacity-recovery','errors':errors})
        raise SystemExit(1)
    assert run.status(plan)['completed']==24
    linux='/mnt/e/masters-nudge-benchmark/'+ROOT.name+'/diagnostics/flipt-segments/run.py'
    stages=[('flipt-original-clause',['wsl.exe','-u','root','--exec','python3',linux]),
            ('clap-original-clause',[sys.executable,'-X','utf8',str(ROOT/'diagnostic_clap_occurrences.py')]),
            ('execution-and-taste-grading',[sys.executable,'-X','utf8',str(ROOT/'finish.py')]),
            ('integrity',[sys.executable,'-X','utf8',str(ROOT/'verify_final.py')])]
    diagnostics={}
    for stage,command in stages:
        run.emit({'pipeline_stage':stage});started=time.monotonic()
        p=subprocess.run(command,cwd=ROOT,env=env,stdout=sys.stdout,stderr=sys.stderr,creationflags=subprocess.CREATE_NO_WINDOW)
        if p.returncode:
            run.save(ROOT/'pipeline-status.json',{'status':'stopped','stage':stage,'exit_code':p.returncode});raise SystemExit(p.returncode)
        if 'original-clause' in stage:
            diagnostics[stage]={'seconds':time.monotonic()-started}
            run.save(ROOT/'diagnostics-status.json',{'status':'complete' if len(diagnostics)==2 else 'in_progress','stages':diagnostics})
    run.save(ROOT/'pipeline-status.json',{'status':'complete','new_I_deliveries':24,'infrastructure_recovery':True})
    run.emit({'pipeline_stage':'complete','new_I_deliveries':24})
