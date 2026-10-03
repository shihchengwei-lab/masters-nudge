"""Resume only requests interrupted by the explicit server-capacity error; preserve valid outcomes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import ctypes,json,os,sys,subprocess,shutil,time
import run
ROOT=run.ROOT
plan=run.prepare()

def wait_original():
 info=run.read(ROOT/'orchestrator.json')
 kernel=ctypes.WinDLL('kernel32',use_last_error=True)
 kernel.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];kernel.OpenProcess.restype=ctypes.c_void_p
 kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_ulong];kernel.CloseHandle.argtypes=[ctypes.c_void_p]
 handle=kernel.OpenProcess(0x00100000,False,info['pid'])
 if handle:
  try:
   while kernel.WaitForSingleObject(handle,60000)==258:pass
  finally:kernel.CloseHandle(handle)
 assert (ROOT/'execution-summary.json').is_file()

wait_original()
prior=run.read(ROOT/'execution-summary.json')
assert prior['errors']
assert run.read(ROOT/'restoration-confirmed.json')['case_states_match']
recovery=ROOT/'infrastructure-recovery/server-capacity-1';recovery.mkdir(parents=True,exist_ok=False)
for name in ('execution-summary.json','restoration-confirmed.json','pipeline-status.json'):
 if (ROOT/name).exists():shutil.copy2(ROOT/name,recovery/name)
failed=[]
for cid in plan['cases']:
 for arm in plan['new_arms']:
  folder=run.artifact(cid,arm)
  if not (folder/'result.json').exists():continue
  result=run.read(folder/'result.json')
  if result['execution_fault']!='Actor exit 1':continue
  events=(folder/'actor-events.jsonl').read_text(encoding='utf-8')
  assert 'Selected model is at capacity. Please try a different model.' in events
  failed.append({'case':cid,'arm':arm,'seconds':result['actor_elapsed_seconds'],'patch_sha256':result['patch_sha256'],'actor_usage_available':bool(result['actor_usage']),'file_changes':result['file_change_events']})
assert failed
# Confirm the originally working desktop model can again complete a minimal request before resuming tasks.
probe=recovery/'availability-probe';probe.mkdir()
args=[plan['codex_binary'],'-c','project_doc_max_bytes=0','-c','features.multi_agent=false','-c','model_reasoning_effort="medium"','--disable','hooks','--disable','plugins','exec','--ignore-user-config','--ignore-rules','--skip-git-repo-check','--ephemeral','--json','-s','read-only','-m',run.MODEL,'-C',str(probe),'-o',str(probe/'answer.txt'),'-']
started=time.monotonic();p=subprocess.run(args,input='Reply exactly READY. Do not use tools.',capture_output=True,text=True,encoding='utf-8',timeout=90,env=dict(os.environ,MASTERS_NUDGE_ACTIVE='0'),creationflags=subprocess.CREATE_NO_WINDOW)
(probe/'events.jsonl').write_text(p.stdout,encoding='utf-8');(probe/'stderr.txt').write_text(p.stderr,encoding='utf-8')
run.save(probe/'transport.json',{'exit_code':p.returncode,'seconds':time.monotonic()-started,'command':args})
assert p.returncode==0 and (probe/'answer.txt').read_text().strip()=='READY','Capacity still unavailable; keep records and stop.'
for row in failed:
 cid,arm=row['case'],row['arm'];dest=recovery/cid/arm;dest.mkdir(parents=True)
 folder=run.artifact(cid,arm).resolve();assert folder.is_relative_to((ROOT/'runs').resolve())
 shutil.move(str(folder),str(dest/'original-run'))
 evaluation=(ROOT/'evaluation-v3'/cid/arm).resolve();assert evaluation.is_relative_to((ROOT/'evaluation-v3').resolve())
 if evaluation.exists():shutil.move(str(evaluation),str(dest/'fixed-evaluation'))
 console=ROOT/'evaluation-v3'/cid/(arm+'-console.txt')
 if console.exists():shutil.move(str(console),str(dest/'fixed-evaluation-console.txt'))
retained={str(p.relative_to(ROOT)):run.sha(p) for p in (ROOT/'runs').glob('*/*/*') if p.is_file() and p.name in ('result.json','final.patch','actor-events.jsonl','actor-final.txt','launch.json','prompt.txt')}
receipt={'reason':'Explicit external server-capacity response; no task outcome based retries.','failed_requests_preserved':failed,'retained_outcome_file_hashes':retained,'actor_valid_results_retained':len(list((ROOT/'runs').glob('*/*/result.json'))),'availability_probe_ready':True,'recovery_started_utc':datetime.now(timezone.utc).isoformat()}
run.save(recovery/'receipt.json',receipt)
# Audit source is appended, while all original 26 source snapshots remain unchanged.
manifest=run.read(ROOT/'harness-source-manifest.json');source=Path(__file__).resolve();snapshot=ROOT/'harness-sources/study'/source.name;shutil.copy2(source,snapshot)
manifest.append({'source':str(source),'snapshot':snapshot.relative_to(ROOT).as_posix(),'sha256':run.sha(source)});run.save(ROOT/'harness-source-manifest.json',manifest)
run.save(ROOT/'orchestrator.json',{'pid':os.getpid(),'started_utc':datetime.now(timezone.utc).isoformat(),'stage':'capacity_recovery'})
runner=run.load_harness('capacity_recovery');run.STOP.clear();errors=[]
jobs=[cid for cid in plan['cases'] if any(not (run.artifact(cid,arm)/'result.json').exists() for arm in plan['new_arms'])]
run.emit({'stage':'capacity_recovered_resuming','retained_valid_results':receipt['actor_valid_results_retained'],'pending_cases':len(jobs)})
with ThreadPoolExecutor(max_workers=plan['workers']) as pool:
 futures={pool.submit(run.run_case,cid,plan,runner):cid for cid in jobs}
 for future in as_completed(futures):
  try:future.result()
  except Exception as exc:
   run.STOP.set();row={'case':futures[future],'error':str(exc)};errors.append(row);run.emit(row)
run.save(ROOT/'execution-summary.json',{**run.status(plan),'errors':errors,'infrastructure_recovery':str(recovery)})
run.verify_archive(plan)
for path,digest in retained.items():assert run.sha(ROOT/path)==digest,'Existing outcome changed'
run.save(ROOT/'restoration-confirmed.json',{'case_states_match':all(run.read(ROOT/'worktree-backups'/cid/'restored-state.json')==run.read(ROOT/'worktree-backups'/cid/'original-state.json') for cid in plan['cases']),'archived_A_unchanged':True,'restored_cases':list(plan['cases'])})
if errors:
 run.save(ROOT/'pipeline-status.json',{'status':'stopped','stage':'capacity_recovery','errors':errors});raise SystemExit(1)
assert run.status(plan)['completed']==24
run.emit({'pipeline_stage':'execution-and-taste-grading'})
p=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'finish.py')],cwd=ROOT,env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1'),stdout=sys.stdout,stderr=sys.stderr,creationflags=subprocess.CREATE_NO_WINDOW)
assert p.returncode==0,'Grading stopped; preserve judgments'
summary=run.read(ROOT/'results-summary.json');summary['infrastructure_recovery']=receipt;run.save(ROOT/'results-summary.json',summary)
with (ROOT/'REPORT.zh-TW.md').open('a',encoding='utf-8') as report:
 report.write('\n## 服務端容量中斷與接續\n\nElement首份在閱讀程式後被服務端「模型容量不足」中斷，沒有修改檔案或呼叫Provider。原始Actor、驗收與失敗紀錄保留於infrastructure-recovery/server-capacity-1；確認Sol恢復回覆READY後只接續此中斷及尚未執行的份數，已完成交付未重抽。中斷請求'+str(len(failed))+'份、耗時'+str(round(sum(x['seconds'] for x in failed),3))+'秒，沒有完整Actor用量；這是另列的基礎設施開銷，未當成模型解題失敗或0 Token。來源快照保留原26份並追加恢復程式供審計。\n')
p=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'verify_final.py')],cwd=ROOT,env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1'),stdout=sys.stdout,stderr=sys.stderr,creationflags=subprocess.CREATE_NO_WINDOW)
assert p.returncode==0
run.save(ROOT/'pipeline-status.json',{'status':'complete','new_D_deliveries':24,'infrastructure_recovery':str(recovery)})
run.emit({'pipeline_stage':'complete','new_D_deliveries':24})
