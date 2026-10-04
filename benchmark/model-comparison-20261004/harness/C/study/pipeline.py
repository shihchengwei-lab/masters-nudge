"""Run C24 once, then semantic review, anonymous comparisons and integrity."""
import os,json,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
for stage,args in [('actors',['run.py','run']),('execution-and-taste-grading',['finish.py']),('integrity',['verify_final.py'])]:
 print(json.dumps({'pipeline_stage':stage}),flush=True)
 # Explicit handles retain child progress on Windows without opening a console.
 result=subprocess.run([sys.executable,'-X','utf8',str(ROOT/args[0]),*args[1:]],cwd=ROOT,env=env,stdout=sys.stdout,stderr=sys.stderr,creationflags=subprocess.CREATE_NO_WINDOW)
 if result.returncode:
  (ROOT/'pipeline-status.json').write_text(json.dumps({'status':'stopped','stage':stage,'exit_code':result.returncode}),encoding='utf-8')
  raise SystemExit(result.returncode)
 if stage=='actors':
  outcome=json.loads((ROOT/'execution-summary.json').read_text(encoding='utf-8'))
  assert outcome['completed']==24 and not outcome['errors']
(ROOT/'pipeline-status.json').write_text(json.dumps({'status':'complete','new_C_deliveries':24}),encoding='utf-8')
print(json.dumps({'pipeline_stage':'complete','new_C_deliveries':24}),flush=True)
