"""Read-only F Sol xhigh plus Sol medium preflight; preserve C/E."""
import ast,json,subprocess,sys
from pathlib import Path
import run
plan=run.prepare()
runner=run.load_harness('preflight')
assert Path(runner.resolve_codex_bin()).resolve()==Path(plan['codex_binary']).resolve()
assert plan['codex_binary_sha256']==run.read(run.E_REFERENCE/'plan.json')['codex_binary_sha256']
run.verify_archive(plan)
assert runner.CAL.resolve()==run.CAL.resolve()
assert runner.PROVIDER_MODEL=='gpt-6.1-sol'
assert runner.ARMS==['F1','F2'] and runner.MODEL=='gpt-6.1-sol' and runner.TIMEOUT==1800
constants={n.value for n in ast.walk(ast.parse(run.HARNESS.read_text(encoding='utf-8'))) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
assert 'model_reasoning_effort="xhigh"' in constants
assert 'PROVIDER_REASONING_EFFORT = "medium"' in (run.PACKAGE/'masters_nudge/runtime.py').read_text(encoding='utf-8')
images=sorted({v['image_id'] for v in plan['cases'].values() if v['container']})
rows=[]
for image in images:
 p=subprocess.run(['wsl.exe','-u','root','--exec','docker','image','inspect','--format','{{.Id}}',image],capture_output=True,text=True,encoding='utf-8',timeout=60)
 assert p.returncode==0 and p.stdout.strip()==image,(image,p.stderr)
 rows.append({'image':image,'present':True})
for cid in plan['cases']:
 work=runner.safe_work(cid)
 assert runner.git(work,'rev-parse','HEAD').strip()==plan['cases'][cid]['base_commit']
 for arm in ('E1','E2'):
  launch=run.read(run.artifact(cid,arm)/'launch.json')
  assert launch['reasoning']=='xhigh' and launch['hooks'] is True
for cid in plan['cases']:
 for arm in ('C1','C2'):
  launch=run.read(run.artifact(cid,arm)/'launch.json')
  assert launch['reasoning']=='xhigh' and launch['hooks'] is False
run.save(run.ROOT/'preflight.json',{'status':'pass','fixed_images':rows,'case_roots_valid':12,'actor_model':runner.MODEL,'actor_reasoning':'xhigh','hooks':True,'plugins':False,'provider':'gpt-6.1-sol','provider_reasoning':'medium','references_C_E_unchanged':True,'only_new_trials':24})
print(json.dumps({'preflight':'pass','images':len(images),'cases':12,'reasoning':'xhigh','hooks':True}))
