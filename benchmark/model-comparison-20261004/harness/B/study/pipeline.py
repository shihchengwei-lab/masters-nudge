"""Run 24 new B deliveries, then the established evaluation and reports."""
import json, os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
steps=[('actors',['run.py','run']),('execution-and-taste-grading',['finish.py']),('comparison-report',['complete_report.py']),('historical-B-reference',['finalize_report.py']),('integrity',['verify_final.py'])]
for stage,args in steps:
    print(json.dumps({'pipeline_stage':stage},ensure_ascii=False),flush=True)
    p=subprocess.run([sys.executable,'-X','utf8',str(ROOT/args[0]),*args[1:]],cwd=ROOT,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
    if p.returncode:
        (ROOT/'pipeline-status.json').write_text(json.dumps({'status':'stopped','stage':stage,'exit_code':p.returncode}),encoding='utf-8')
        raise SystemExit(p.returncode)
    if stage=='actors':
        outcome=json.loads((ROOT/'execution-summary.json').read_text(encoding='utf-8'))
        assert outcome['completed']==24 and not outcome['errors']
(ROOT/'pipeline-status.json').write_text(json.dumps({'status':'complete','deliveries':24}),encoding='utf-8')
print(json.dumps({'pipeline_stage':'complete','deliveries':24}),flush=True)
