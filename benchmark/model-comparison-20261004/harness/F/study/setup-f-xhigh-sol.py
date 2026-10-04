"""Create private F24 from E; preserve completed C/E and global product settings."""
from pathlib import Path
import shutil, ast, json
BASE=Path('E:/masters-nudge-benchmark')
SRC=BASE/'sol61-xhigh-astra-provider-12case-20261002'
OUT=BASE/'sol61-f-xhigh-sol-provider-12case-20261002'
assert not OUT.exists();OUT.mkdir()
def write(name,text):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
 if p.suffix=='.py':ast.parse(text)
 p.write_text(text,encoding='utf-8')
for name in ('frozen-plugin','frozen-evaluation','frozen-cli','prompts'):
 shutil.copytree(SRC/name,OUT/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for name in ('actor_runner.py','review.py','blind.py','transcript_reader.py','finish.py','pipeline.py','preflight.py','snapshot_harness.py'):
 shutil.copy2(SRC/name,OUT/name)
actor=(OUT/'actor_runner.py').read_text(encoding='utf-8')
actor=actor.replace("PROVIDER_MODEL = 'gpt-6-astra'","PROVIDER_MODEL = 'gpt-6.1-sol'").replace("['E1', 'E2']","['F1', 'F2']").replace("('E1','E2')","('F1','F2')")
write('actor_runner.py',actor)
s=(SRC/'run.py').read_text(encoding='utf-8')
s=s.replace('New E Sol xhigh Actor plus Astra medium Provider; immutable D effort comparison.','New F Sol xhigh Actor plus Sol medium Provider; immutable C/E comparisons.')
s=s.replace("D_REFERENCE = Path('E:/masters-nudge-benchmark/sol61-astra-provider-12case-20261001-desktop')\nCOMPARISON_ARMS = ['D1','D2','E1','E2']","C_REFERENCE = Path('E:/masters-nudge-benchmark/sol61-c-xhigh-direct-12case-20261001')\nE_REFERENCE = Path('E:/masters-nudge-benchmark/sol61-xhigh-astra-provider-12case-20261002')\nREFERENCES = {'C':C_REFERENCE,'E':E_REFERENCE}\nCOMPARISON_ARMS = ['C1','C2','E1','E2','F1','F2']")
s=s.replace("return (D_REFERENCE if arm.startswith('D') else ROOT)/'runs'/cid/arm","return (REFERENCES.get(arm[0],ROOT))/'runs'/cid/arm")
start=s.index('def reference_manifest():');end=s.index('\nsys.path.insert',start)
replacement='''def reference_manifest():
    names=('result.json','score-v3.json','final.patch','actor-events.jsonl','actor-final.txt','execution-review.json','execution-evidence.json','prompt.txt','launch.json','provider-attempts.json')
    paths=[]
    for arm,reference in REFERENCES.items():
        paths += [reference/'runs'/cid/(arm+str(i))/name for cid in read(reference/'plan.json')['cases'] for i in (1,2) for name in names]
        paths += [reference/name for name in ('plan.json','results-summary.json','REPORT.zh-TW.md','final-integrity.json','pipeline-status.json','harness-source-manifest.json')]
        paths += list((reference/'blind-v3/judges').glob('*/*/*/judge-*/output.json'))
        paths += list((reference/'diagnostics').rglob('comparison.json'))
    return {str(p):sha(p) for p in paths if p.is_file()}

def verify_archive(plan):
    assert reference_manifest()==plan['reference_manifest'], 'Completed C/E reference changed'

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
        assert all(textsha(neutral_prompt(cid))==meta['E_prompt_sha256']==meta['F_prompt_sha256'] for cid,meta in plan['cases'].items())
        return plan
    old=read(E_REFERENCE/'plan.json');cplan=read(C_REFERENCE/'plan.json')
    assert all(read(r/'pipeline-status.json')['status']=='complete' for r in REFERENCES.values())
    assert textsha((PACKAGE/'buddy-prompt.txt').read_text(encoding='utf-8').strip())==PROMPT_HASH
    assert files(PACKAGE)==files(E_REFERENCE/'frozen-plugin')
    assert files(EVALUATION)==files(E_REFERENCE/'frozen-evaluation')==files(C_REFERENCE/'frozen-evaluation')
    cases={}
    for cid,meta in old['cases'].items():
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=CAL/'cases'/cid,text=True).strip()==meta['base_commit']==cplan['cases'][cid]['base_commit']
        assert textsha(neutral_prompt(cid))==meta['E_prompt_sha256']
        for a in ('C','E'):
            for i in (1,2):
                r=read(artifact(cid,a+str(i))/'result.json')
                assert r['actor_model']==MODEL and r['actor_reasoning']=='xhigh'
                assert r['provider_model']==('gpt-6-astra' if a=='E' else None)
        cases[cid]={**meta,'C_prompt_sha256':cplan['cases'][cid]['C_prompt_sha256'],'F_prompt_sha256':meta['E_prompt_sha256'],'new_order':['F1','F2']}
    binary=ROOT/'frozen-cli/codex.exe'
    assert sha(binary)==old['codex_binary_sha256']
    assert subprocess.check_output([str(binary),'--version'],text=True).strip()=='codex-cli 0.159.2'
    plan={**old,'name':'F Sol xhigh Actor plus Sol medium Provider; 12 cases x2; C/E comparisons',
        'created_utc':datetime.now(timezone.utc).isoformat(),'actor_reasoning':'xhigh','provider_model':'gpt-6.1-sol','provider_reasoning':'medium',
        'cases':cases,'new_arms':['F1','F2'],'comparison_arms':COMPARISON_ARMS,'expected_deliveries':24,'comparison_deliveries':72,
        'pairwise_comparisons':['C-F','E-F'],'codex_binary':str(binary),'codex_binary_sha256':sha(binary),'codex_cli_version':'0.159.2',
        'reference_roots':{a:str(p) for a,p in REFERENCES.items()},'reference_manifest':reference_manifest(),
        'package_hashes':files(PACKAGE),'evaluator_sha256':evaluate.verify(),'harness_sha256':sha(HARNESS),
        'source_harness_sha256':sha(SOURCE_HARNESS),'adapter_sha256':sha(PREVIOUS/'rerun.py'),'experiment_script_sha256':sha(__file__),
        'workers':2,'actor_wall_timeout_seconds':1800,'feedback_limit':3,
        'comparison_scope':'Only new F24. Reuse C24/E24 unchanged. F-E same frozen CLI/tool/task/Actor xhigh; only Provider Astra -> Sol. C direct xhigh uses earlier CLI 0.159.0, disclose this difference.',
        'CLI_difference_C':{'version':cplan['codex_cli_version'],'sha256':cplan['codex_binary_sha256']},
        'contract_supplements':'Same confirmed original Flipt rollout and Clap occurrences fixtures applied symmetrically to C1/C2/E1/E2/F1/F2 before taste; frozen scores preserved.',
        'taste':'Unchanged rubric; C-F/E-F jointly complete only; two reversed Astra medium orders, third on disagreement.',
        'cost':'Actor plus Provider for E/F; Actor only for C; complete-usage pairs. All outcomes count for completion/time; grading/diagnostics separate.'}
    for obsolete in ('reference_root','archived_A_manifest','B_manifest_sha256','B_seal_sha256','A','B','D','CLI_recovery','archive_root','B_archive_root'):
        plan.pop(obsolete,None)
    save(existing,plan);save(ROOT/'reference-manifest.json',plan['reference_manifest'])
    return plan
'''
s=s[:start]+replacement+s[end:]
s=s.replace("'provider_model':'gpt-6-astra'","'provider_model':'gpt-6.1-sol'").replace("'reference_D_unchanged':True","'references_C_E_unchanged':True")
write('run.py',s)
s=(OUT/'preflight.py').read_text(encoding='utf-8').replace('run.D_REFERENCE','run.E_REFERENCE').replace("runner.PROVIDER_MODEL=='gpt-6-astra'","runner.PROVIDER_MODEL=='gpt-6.1-sol'").replace("['E1','E2']","['F1','F2']").replace("('D1','D2')","('E1','E2')").replace("launch['reasoning']=='medium'","launch['reasoning']=='xhigh'").replace("'provider':'gpt-6-astra'","'provider':'gpt-6.1-sol'").replace("'reference_D_unchanged':True","'references_C_E_unchanged':True")
s=s.replace("run.save(run.ROOT/'preflight.json'", "for cid in plan['cases']:\n for arm in ('C1','C2'):\n  launch=run.read(run.artifact(cid,arm)/'launch.json')\n  assert launch['reasoning']=='xhigh' and launch['hooks'] is False\nrun.save(run.ROOT/'preflight.json'")
write('preflight.py',s)
s=(OUT/'finish.py').read_text(encoding='utf-8').replace('D24 semantic execution review, fixed anonymous taste judges and Provider-model comparison.','F24 execution review, immutable C/E anonymous comparisons.').replace('Masters Nudge及其Astra Provider','Masters Nudge及其Sol Provider').replace('D-E only; completed D reference remains unchanged.','C-F and E-F only; completed C/E references unchanged.')
write('finish.py',s)
s=(OUT/'blind.py').read_text(encoding='utf-8').replace('if complete == 2:','if complete == 2 * len(plan[\'pairwise_comparisons\']):')
write('blind.py',s)
s=(OUT/'pipeline.py').read_text(encoding='utf-8').replace('E24 once','F24 once').replace('new_E_deliveries','new_F_deliveries')
write('pipeline.py',s)
s=(OUT/'snapshot_harness.py').read_text(encoding='utf-8').replace('setup-e-xhigh-astra-20261002.py','setup-f-xhigh-sol-20261002.py').replace('setup-e-xhigh-astra.py','setup-f-xhigh-sol.py').replace('run.D_REFERENCE','run.E_REFERENCE').replace('actor-runner-from-D.patch','actor-runner-from-E.patch').replace('reference_D_preserved','references_C_E_preserved')
write('snapshot_harness.py',s)
diag=OUT/'diagnostics'
(diag/'flipt-segments').mkdir(parents=True)
(diag/'clap-2297').mkdir()
for rel in ('flipt-segments/rollout_legacy_shape_audit_test.go','clap-2297/diagnostic_occurrences.rs'):
 shutil.copy2(SRC/'diagnostics'/rel,diag/rel)
s=(SRC/'diagnostics/flipt-segments/run.py').read_text(encoding='utf-8')
s=s.replace("roots={'D':Path('/mnt/e/masters-nudge-benchmark/sol61-astra-provider-12case-20261001-desktop'),'E':STUDY}","roots={'C':Path('/mnt/e/masters-nudge-benchmark/sol61-c-xhigh-direct-12case-20261001'),'E':Path('/mnt/e/masters-nudge-benchmark/sol61-xhigh-astra-provider-12case-20261002'),'F':STUDY}")
s=s.replace("('D1','D2','E1','E2')","('C1','C2','E1','E2','F1','F2')")
write('diagnostics/flipt-segments/run.py',s)
s=(SRC/'diagnostic_clap_occurrences.py').read_text(encoding='utf-8').replace("('BASE','D1','D2','E1','E2')","('BASE','C1','C2','E1','E2','F1','F2')")
write('diagnostic_clap_occurrences.py',s)
print(OUT)
