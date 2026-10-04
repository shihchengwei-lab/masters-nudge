from pathlib import Path
import shutil,json
ROOT=Path('E:/masters-nudge-benchmark/sol61-c-xhigh-direct-12case-20261001')
B=Path('E:/masters-nudge-benchmark/sol61-b-finalized-12case-20261001')
ROOT.mkdir(exist_ok=True)
assert not (ROOT/'run.py').exists(), 'Study already prepared'
def repl(s,a,b,count=1):
 assert s.count(a)==count,(a,s.count(a),count)
 return s.replace(a,b)
source=Path('D:/masters-nudge-benchmark/round-10-b-quota2-20260927/run.py').read_text(encoding='utf-8')
actor=source.replace('model_reasoning_effort="medium"','model_reasoning_effort="xhigh"')
actor=actor.replace("'reasoning':'medium'","'reasoning':'xhigh'").replace("'actor_reasoning':'medium'","'actor_reasoning':'xhigh'")
actor=actor.replace("ARMS = ['B1', 'B2']","ARMS = ['C1', 'C2']")
assert actor!=source
(ROOT/'actor_runner.py').write_text(actor,encoding='utf-8')
s=(B/'run.py').read_text(encoding='utf-8')
s=s.replace('Fresh paired A/B study; frozen product and established fixed evaluator.', 'New C xhigh direct trials; archived A medium and sealed B medium tool results.')
s=repl(s,"HARNESS = Path('D:/masters-nudge-benchmark/round-10-b-quota2-20260927/run.py')", "HARNESS = ROOT/'actor_runner.py'\nSOURCE_HARNESS = Path('D:/masters-nudge-benchmark/round-10-b-quota2-20260927/run.py')\nB_ARCHIVE = Path('E:/masters-nudge-benchmark/sol61-b-finalized-12case-20261001')")
s=repl(s,"COMPARISON_ARMS = ['A1','A2','B1','B2']","COMPARISON_ARMS = ['A1','A2','B1','B2','C1','C2']")
s=repl(s,"def artifact(cid,arm): return (ARCHIVE if arm.startswith('A') else ROOT)/'runs'/cid/arm", "def artifact(cid,arm): return (ARCHIVE if arm.startswith('A') else B_ARCHIVE if arm.startswith('B') else ROOT)/'runs'/cid/arm")
s=repl(s,"    assert archive_manifest()==plan['archived_A_manifest'], 'Archived A changed'", "    assert archive_manifest()==plan['archived_A_manifest'], 'Archived A changed'\n    manifest=read(B_ARCHIVE/'archive-manifest.json')\n    assert sha(B_ARCHIVE/'archive-manifest.json')==plan['B_manifest_sha256']\n    assert sha(B_ARCHIVE/'archive-seal.json')==plan['B_seal_sha256']\n    assert all((B_ARCHIVE/name).is_file() and sha(B_ARCHIVE/name)==value for name,value in manifest.items()), 'Sealed B changed'")
s=repl(s,"        assert plan['harness_sha256']==sha(HARNESS)","        assert plan['harness_sha256']==sha(HARNESS)\n        assert plan['source_harness_sha256']==sha(SOURCE_HARNESS)\n        assert plan['adapter_sha256']==sha(PREVIOUS/'rerun.py')")
s=repl(s,"        assert all(textsha(neutral_prompt(cid))==meta['A_prompt_sha256']==meta['B_prompt_sha256']", "        assert all(textsha(neutral_prompt(cid))==meta['A_prompt_sha256']==meta['B_prompt_sha256']==meta['C_prompt_sha256']")
a="    source=PRODUCT/'plugins/masters-nudge'\n    prompt=(source/'buddy-prompt.txt').read_text(encoding='utf-8').strip()\n    assert textsha(prompt)==PROMPT_HASH\n    assert prompt==(PRODUCT/'buddy-prompt.txt').read_text(encoding='utf-8').strip()"
b="    source=B_ARCHIVE/'frozen-plugin'\n    assert read(B_ARCHIVE/'archive-seal.json')['status']=='archived'\n    assert textsha((source/'buddy-prompt.txt').read_text(encoding='utf-8').strip())==PROMPT_HASH"
s=repl(s,a,b)
s=repl(s,"        cases[cid]={**previous,'new_order':['B1','B2']}", "        for arm in ('B1','B2'):\n            result=read(artifact(cid,arm)/'result.json')\n            assert result['actor_model']==MODEL and result['actor_reasoning']=='medium'\n            assert result['base_commit']==previous['base_commit']\n            assert result['prompt_sha256']==previous['A_prompt_sha256']\n        cases[cid]={**previous,'C_prompt_sha256':previous['A_prompt_sha256'],'new_order':['C1','C2']}")
s=repl(s,"'name':'Fresh B 12 cases x 2, finalized data/distinctions/information prompt and file-origin facts; archived Sol61 A comparison'", "'name':'C direct GPT-6.1 Sol xhigh, 12 cases x 2; archived A direct medium and sealed B tool medium'\n        ,'actor_reasoning':'xhigh','provider_model':None,'provider_reasoning':None,'feedback_limit':0,'pairwise_comparisons':['A-C','B-C']")
s=repl(s,"'new_arms':['B1','B2'],'comparison_arms':COMPARISON_ARMS,'expected_deliveries':24,'comparison_deliveries':48", "'new_arms':['C1','C2'],'comparison_arms':COMPARISON_ARMS,'expected_deliveries':24,'comparison_deliveries':72")
s=repl(s,"'B':'24 fresh B trials using the finalized package with file-origin facts and 40/25/61/35 field limits; maximum three delivered nudges.'", "'B':'Reuse sealed B24 without new Actors or rescoring.',\n        'C':'24 fresh direct trials; only actor reasoning changes medium to xhigh against A; hooks/plugins/Provider disabled.'")
s=repl(s,"'archive_root':str(ARCHIVE),'archived_A_manifest':archive_manifest()", "'archive_root':str(ARCHIVE),'archived_A_manifest':archive_manifest(),\n        'B_archive_root':str(B_ARCHIVE),'B_manifest_sha256':sha(B_ARCHIVE/'archive-manifest.json'),'B_seal_sha256':sha(B_ARCHIVE/'archive-seal.json')")
s=repl(s,"'evaluator_sha256':evaluate.verify(),'harness_sha256':sha(HARNESS)", "'evaluator_sha256':evaluate.verify(),'harness_sha256':sha(HARNESS),'source_harness_sha256':sha(SOURCE_HARNESS)")
s=repl(s,"'comparison_scope':'New B versus archived same-model A. Historical comparison; original study and the one-case pilot remain separate.'", "'comparison_scope':'C24 new xhigh direct; archived A24 medium direct isolates requested effort; sealed B24 medium tool comparison; no archived sampling/rescoring.'")
s=repl(s,"'taste':'Same frozen rubric; newly judge jointly completed archived-A/new-B pairs, two swapped-order Astra medium judges, third for disagreement.'", "'taste':'Same frozen rubric; anonymous A-C and B-C jointly completed pairs; two reversed Astra medium judges, third for disagreement; preserve archived A-B votes.'")
s=repl(s,"'cost':'Compare recorded original A cost with new B Actor plus Provider cost. Current execution/taste grading costs separate; no new A cost incurred.'", "'cost':'Compare C Actor with archived A Actor and B Actor+Provider on complete usage pairs; include all trials for time/completion; grading separate.'")
s=repl(s,"    adapter.ROOT=ROOT;adapter.PACKAGE=PACKAGE;adapter.EVALUATION=EVALUATION;adapter.evaluate.ROOT=EVALUATION", "    adapter.ROOT=ROOT;adapter.PACKAGE=PACKAGE;adapter.EVALUATION=EVALUATION;adapter.evaluate.ROOT=EVALUATION;adapter.HARNESS=HARNESS")
s=repl(s,"'stage':'sealed','cases':12,'new_deliveries':24,'model':MODEL,'prompt_sha256':PROMPT_HASH", "'stage':'sealed','cases':12,'new_deliveries':24,'model':MODEL,'actor_reasoning':'xhigh','hooks':False")
(ROOT/'run.py').write_text(s,encoding='utf-8')
for name in ['review.py','blind.py']:
 shutil.copy2(B/name,ROOT/name)
finish=(B/'finish.py').read_text(encoding='utf-8').split('def summarize(plan):')[0]
finish=finish.replace("'time_limit_seconds':1800,", "'time_limit_seconds':1800,'actor_reasoning':'xhigh','hooks_enabled':False,")
finish=finish.replace("'Masters Nudge及其Provider是本實驗授權的工具；hook-trust提示與Provider故障需分開記錄,'", "'本臂直接實作，未啟用Masters Nudge、hooks或Provider。'")
(ROOT/'finish.py').write_text(finish,encoding='utf-8')
for path in ROOT.glob('*.py'):compile(path.read_text(encoding='utf-8'),str(path),'exec')
print('Created C execution core; copied Actor runner only changes effort and C labels; frozen evaluation unchanged.')
