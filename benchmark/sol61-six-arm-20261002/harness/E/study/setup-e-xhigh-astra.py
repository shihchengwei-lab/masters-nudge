"""Build a private E24 study from the completed D harness; preserve D inputs."""
from pathlib import Path
import shutil,ast,json,hashlib
SRC=Path('E:/masters-nudge-benchmark/sol61-astra-provider-12case-20261001-desktop')
OUT=Path('E:/masters-nudge-benchmark/sol61-xhigh-astra-provider-12case-20261002')
assert not OUT.exists();OUT.mkdir()
for name in ('frozen-plugin','frozen-evaluation','frozen-cli','prompts'):
 shutil.copytree(SRC/name,OUT/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for name in ('actor_runner.py','review.py','blind.py','transcript_reader.py'):
 shutil.copy2(SRC/name,OUT/name)
actor=(OUT/'actor_runner.py').read_text(encoding='utf-8')
actor=actor.replace("ARMS = ['D1', 'D2']","ARMS = ['E1', 'E2']").replace("assert arm in ('D1','D2')","assert arm in ('E1','E2')")
actor=actor.replace("'-c','model_reasoning_effort=\"medium\"'","'-c','model_reasoning_effort=\"xhigh\"'")
actor=actor.replace("'actor_reasoning':'medium'","'actor_reasoning':'xhigh'").replace("'reasoning':'medium',\n        'provider_model'","'reasoning':'xhigh',\n        'provider_model'")
(OUT/'actor_runner.py').write_text(actor,encoding='utf-8')
original=(SRC/'run.py').read_text(encoding='utf-8')
original=original.replace('New D Sol medium Actor plus Astra medium Provider; sealed B model-switch comparison.','New E Sol xhigh Actor plus Astra medium Provider; immutable D effort comparison.')
original=original.replace("COMPARISON_ARMS = ['A1','A2','B1','B2','D1','D2']","D_REFERENCE = Path('"+SRC.as_posix()+"')\nCOMPARISON_ARMS = ['D1','D2','E1','E2']")
start=original.index('def artifact(');end=original.index('\ndef evaluation_directory',start)
original=original[:start]+"def artifact(cid,arm):\n    assert arm in COMPARISON_ARMS\n    return (D_REFERENCE if arm.startswith('D') else ROOT)/'runs'/cid/arm\n"+original[end:]
start=original.index('def archive_manifest():');end=original.index('\nsys.path.insert',start)
replacement='''def reference_manifest():
    names=('result.json','score-v3.json','final.patch','actor-events.jsonl','actor-final.txt','execution-review.json','execution-evidence.json','prompt.txt','launch.json','provider-attempts.json')
    paths=[D_REFERENCE/'runs'/cid/arm/name for cid in read(D_REFERENCE/'plan.json')['cases'] for arm in ('D1','D2') for name in names]
    paths += [D_REFERENCE/name for name in ('plan.json','results-summary.json','diagnostic-adjusted-summary.json','REPORT.zh-TW.md','final-integrity.json','diagnostic-integrity.json','harness-source-manifest.json')]
    paths += list((D_REFERENCE/'blind-v3/judges').glob('*/*/*/judge-*/output.json'))
    paths += list((D_REFERENCE/'diagnostics').rglob('comparison.json'))
    return {str(p):sha(p) for p in paths if p.is_file()}

def verify_archive(plan):
    assert reference_manifest()==plan['reference_manifest'], 'Completed D reference changed'

def completed_score(cid,arm):
    score=dict(read(score_path(artifact(cid,arm))))
    score['frozen_task_completed']=score['task_completed']
    if cid in ('flipt-segments','clap-2297'):
        proof=read(ROOT/'diagnostics'/cid/'comparison.json')
        row=next(r for r in proof['rows'] if r['arm']==arm)
        if not row['contract_passed']:
            score['task_completed']=False
            score['confirmed_original_clause_gap']=proof['task_clause']
    return score

def prepare():
    existing=ROOT/'plan.json'
    if existing.exists():
        plan=read(existing)
        assert plan['package_hashes']==files(PACKAGE)
        assert plan['evaluator_sha256']==evaluate.verify()
        assert plan['codex_binary_sha256']==sha(plan['codex_binary'])
        assert plan['harness_sha256']==sha(HARNESS) and plan['experiment_script_sha256']==sha(__file__)
        assert plan['source_harness_sha256']==sha(SOURCE_HARNESS) and plan['adapter_sha256']==sha(PREVIOUS/'rerun.py')
        assert all(textsha(neutral_prompt(cid))==meta['D_prompt_sha256']==meta['E_prompt_sha256'] for cid,meta in plan['cases'].items())
        return plan
    old=read(D_REFERENCE/'plan.json')
    assert read(D_REFERENCE/'pipeline-status.json')['status']=='complete'
    assert textsha((PACKAGE/'buddy-prompt.txt').read_text(encoding='utf-8').strip())==PROMPT_HASH
    assert files(PACKAGE)==files(D_REFERENCE/'frozen-plugin') and files(EVALUATION)==files(D_REFERENCE/'frozen-evaluation')
    cases={}
    for cid,meta in old['cases'].items():
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=CAL/'cases'/cid,text=True).strip()==meta['base_commit']
        assert textsha(neutral_prompt(cid))==meta['D_prompt_sha256']
        for arm in ('D1','D2'):
            result=read(artifact(cid,arm)/'result.json')
            assert result['actor_model']==MODEL and result['actor_reasoning']=='medium'
            assert result['provider_model']=='gpt-6-astra' and result['provider_reasoning']=='medium'
        cases[cid]={**meta,'E_prompt_sha256':meta['D_prompt_sha256'],'new_order':['E1','E2']}
    binary=ROOT/'frozen-cli/codex.exe'
    assert sha(binary)==old['codex_binary_sha256']
    assert subprocess.check_output([str(binary),'--version'],text=True).strip()=='codex-cli 0.159.2'
    plan={**old,'name':'E Sol xhigh Actor plus Astra medium Provider; 12 cases x2; D medium primary comparison',
        'created_utc':datetime.now(timezone.utc).isoformat(),'actor_reasoning':'xhigh','provider_model':'gpt-6-astra','provider_reasoning':'medium',
        'cases':cases,'new_arms':['E1','E2'],'comparison_arms':COMPARISON_ARMS,'expected_deliveries':24,'comparison_deliveries':48,
        'pairwise_comparisons':['D-E'],'codex_binary':str(binary),'codex_binary_sha256':sha(binary),'codex_cli_version':'0.159.2',
        'reference_root':str(D_REFERENCE),'reference_manifest':reference_manifest(),
        'package_hashes':files(PACKAGE),'evaluator_sha256':evaluate.verify(),'harness_sha256':sha(HARNESS),
        'source_harness_sha256':sha(SOURCE_HARNESS),'adapter_sha256':sha(PREVIOUS/'rerun.py'),'experiment_script_sha256':sha(__file__),
        'workers':2,'actor_wall_timeout_seconds':1800,'feedback_limit':3,
        'comparison_scope':'Only new E24. Reuse D24 unchanged; same model, Provider medium, frozen CLI, task, base, tool and fixed timeout. Actor effort medium -> xhigh.',
        'contract_supplements':'Apply the same already-confirmed original Flipt rollout-shape and Clap occurrence-preservation probes symmetrically to D1/D2/E1/E2 before anonymous taste. Preserve frozen scores.',
        'taste':'Unchanged frozen rubric; D-E jointly completed only; two reversed Astra medium orders, third on disagreement.',
        'cost':'D/E Actor plus Provider complete-usage pairs. Completion and time include all trials. Grading and diagnostics separate.'}
    for obsolete in ('archived_A_manifest','B_manifest_sha256','B_seal_sha256','A','B','D','CLI_recovery','archive_root','B_archive_root'):
        plan.pop(obsolete,None)
    save(existing,plan);save(ROOT/'reference-manifest.json',plan['reference_manifest'])
    return plan
'''
original=original[:start]+replacement+original[end:]
original=original.replace("'actor_reasoning':'medium','provider_model':'gpt-6-astra'","'actor_reasoning':'xhigh','provider_model':'gpt-6-astra'")
original=original.replace("'archived_A_unchanged':True","'reference_D_unchanged':True")
(OUT/'run.py').write_text(original,encoding='utf-8')
# Execution review and anonymized source access are unchanged. Only Actor settings in the payload differ.
finish=(SRC/'finish.py').read_text(encoding='utf-8')
prefix=finish[:finish.index('\ndef summarize(')].replace("'actor_reasoning':'medium','hooks_enabled':True","'actor_reasoning':'xhigh','hooks_enabled':True")
tail=finish[finish.index('\ndef main():'):].replace('A-D and B-D only; archived A-B votes retained.','D-E only; completed D reference remains unchanged.')
(OUT/'finish.py').write_text(prefix+'\nfrom report import summarize\n'+tail,encoding='utf-8')
blind=(OUT/'blind.py').read_text(encoding='utf-8')
blind=blind.replace("scores = {arm: run.read(path) for arm, path in paths.items()}","scores = {arm: run.completed_score(cid, arm + str(trial)) for arm in paths}")
blind=blind.replace('兩份交付均通過同版封存驗收與執行契約核對','兩份交付均通過同版封存驗收、執行契約及相同原條款補查')
blind=blind.replace('if complete == 6:','if complete == 2:')
(OUT/'blind.py').write_text(blind,encoding='utf-8')
preflight=(SRC/'preflight.py').read_text(encoding='utf-8')
preflight=preflight.replace("['D1','D2']","['E1','E2']").replace("model_reasoning_effort=\"medium\"","model_reasoning_effort=\"xhigh\"")
preflight=preflight.replace("('A1','A2')","('D1','D2')").replace("launch['hooks'] is False","launch['hooks'] is True")
preflight=preflight.replace("'actor_reasoning':'medium'","'actor_reasoning':'xhigh'").replace("'reasoning':'medium','hooks':True","'reasoning':'xhigh','hooks':True")
preflight=preflight.replace("'A_unchanged':True,'sealed_B_unchanged':True","'reference_D_unchanged':True")
preflight=preflight.replace("assert plan['CLI_recovery']['binary_sha256']!=plan['CLI_recovery']['expected_archived_binary_sha256']","assert plan['codex_binary_sha256']==run.read(run.D_REFERENCE/'plan.json')['codex_binary_sha256']\nrun.verify_archive(plan)")
(OUT/'preflight.py').write_text(preflight,encoding='utf-8')
# Reuse exact fixtures; adapt only sample locations and arm inventory.
diag=OUT/'diagnostics';diag.mkdir()
flipt=diag/'flipt-segments';flipt.mkdir()
source=(SRC/'diagnostics/rollout-shape/run.py').read_text(encoding='utf-8')
start=source.index("roots={'A':");end=source.index(' output=ROOT/arm;',start)
source=source[:start]+"roots={'D':Path('/mnt/e/masters-nudge-benchmark/sol61-astra-provider-12case-20261001-desktop'),'E':STUDY}\nfor arm in ('D1','D2','E1','E2'):\n"+source[end:]
source=source.replace(" and next(x for x in probes if x['case']=='scalar_key_control')['passed']",'')
source=source.replace("assert len(probes)==2,text[-3000:]","assert len(probes)==2 or p.returncode!=0,text[-3000:]")
source=source.replace("'network':'none','original_actor_and_scores_unchanged':True","'network':'none','contract_passed':len(probes)==2 and all(x['passed'] for x in probes),'original_actor_and_scores_unchanged':True")
(flipt/'run.py').write_text(source,encoding='utf-8')
clap=(SRC/'diagnostic_clap_occurrences.py').read_text(encoding='utf-8')
clap=clap.replace("ROOT=run.ROOT/'diagnostics/clap-occurrences-valid'","ROOT=run.ROOT/'diagnostics/clap-2297'")
clap=clap.replace('ROOT.mkdir(parents=True,exist_ok=False)','ROOT.mkdir(parents=True,exist_ok=True)\nassert not (ROOT/\'comparison.json\').exists() and not (ROOT/\'BASE\').exists(), \'Preserve recorded diagnostics\'')
clap=clap.replace("('BASE','A1','A2','B1','B2','D1','D2')","('BASE','D1','D2','E1','E2')")
clap=clap.replace("assert p.returncode==0 and len(probes)==3,text[-4000:]","assert (p.returncode==0 and len(probes)==3) or arm!='BASE',text[-4000:]")
clap=clap.replace("  assert next(x for x in probes if x['case']=='non_overriding_control')['occurrences']==2","  if arm=='BASE':assert next(x for x in probes if x['case']=='non_overriding_control')['occurrences']==2")
clap=clap.replace("row['occurrences_preserved']=all(p['occurrences']==baseline[p['case']] for p in row['probes'])","row['occurrences_preserved']=len(row['probes'])==3 and all(p['occurrences']==baseline[p['case']] for p in row['probes'])\n row['contract_passed']=row['occurrences_preserved']")
(OUT/'diagnostic_clap_occurrences.py').write_text(clap,encoding='utf-8')
for path in OUT.rglob('*.py'):
 if 'frozen-plugin' not in path.parts and 'frozen-evaluation' not in path.parts:ast.parse(path.read_text(encoding='utf-8-sig'))
print(json.dumps({'root':str(OUT),'new_trials':24,'primary_comparison':'D-E','actor':'gpt-6.1-sol xhigh','provider':'gpt-6-astra medium','same_frozen_cli':True}))
