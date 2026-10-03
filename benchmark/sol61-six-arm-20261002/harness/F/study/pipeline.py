"""F24 once, symmetric existing-clause probes, execution/taste review, integrity."""
import os,json,sys,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
linux='/mnt/e/masters-nudge-benchmark/'+ROOT.name+'/diagnostics/flipt-segments/run.py'
stages=[('actors',[sys.executable,'-X','utf8',str(ROOT/'run.py'),'run']),
 ('flipt-original-clause',['wsl.exe','-u','root','--exec','python3',linux]),
 ('clap-original-clause',[sys.executable,'-X','utf8',str(ROOT/'diagnostic_clap_occurrences.py')]),
 ('execution-and-taste-grading',[sys.executable,'-X','utf8',str(ROOT/'finish.py')]),
 ('integrity',[sys.executable,'-X','utf8',str(ROOT/'verify_final.py')])]
diagnostics={}
for stage,command in stages:
 print(json.dumps({'pipeline_stage':stage}),flush=True);started=time.monotonic()
 p=subprocess.run(command,cwd=ROOT,env=env,stdout=sys.stdout,stderr=sys.stderr,creationflags=subprocess.CREATE_NO_WINDOW)
 if p.returncode:
  (ROOT/'pipeline-status.json').write_text(json.dumps({'status':'stopped','stage':stage,'exit_code':p.returncode}),encoding='utf-8');raise SystemExit(p.returncode)
 if 'original-clause' in stage:
  diagnostics[stage]={'seconds':time.monotonic()-started}
  (ROOT/'diagnostics-status.json').write_text(json.dumps({'status':'complete' if len(diagnostics)==2 else 'in_progress','stages':diagnostics}),encoding='utf-8')
 if stage=='actors':
  outcome=json.loads((ROOT/'execution-summary.json').read_text(encoding='utf-8'));assert outcome['completed']==24 and not outcome['errors']
(ROOT/'pipeline-status.json').write_text(json.dumps({'status':'complete','new_F_deliveries':24}),encoding='utf-8')
print(json.dumps({'pipeline_stage':'complete','new_F_deliveries':24}),flush=True)
