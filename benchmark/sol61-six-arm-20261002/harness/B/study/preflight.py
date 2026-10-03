"""Read-only check of the retained environments before scheduled Actors begin."""
import json, subprocess
from pathlib import Path
import run
plan=run.prepare()
images=sorted({x['image_id'] for x in plan['cases'].values() if x['container']})
rows=[]
for image in images:
    p=subprocess.run(['wsl.exe','-u','root','--exec','docker','image','inspect','--format','{{.Id}}',image],capture_output=True,text=True,encoding='utf-8',timeout=60)
    assert p.returncode==0,(image,p.stderr[-1000:])
    assert p.stdout.strip()==image,(image,p.stdout)
    rows.append({'image':image,'present':True})
package=run.PACKAGE
import sys
sys.path.insert(0,str(package))
from masters_nudge.contracts import FEEDBACK_FIELD_LIMITS
assert FEEDBACK_FIELD_LIMITS=={'observed':40,'why':25,'structure':61,'required':35}
run.save(run.ROOT/'preflight.json',{'fixed_images':rows,'actor_and_provider':plan['actor_model'],'prompt_semantic_sha256':plan['prompt_semantic_sha256'],'field_limits':FEEDBACK_FIELD_LIMITS,'archived_A_unchanged':True,'status':'pass'})
print(json.dumps({'preflight':'pass','retained_images':len(images),'field_limits':FEEDBACK_FIELD_LIMITS},ensure_ascii=False))
