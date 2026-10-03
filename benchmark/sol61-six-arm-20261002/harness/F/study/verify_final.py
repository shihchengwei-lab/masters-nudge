"""Check actual F settings, immutable C/E, quotas, restoration and all source snapshots."""
import os, subprocess, tempfile, shutil, json
from pathlib import Path
from collections import Counter
import run
ROOT=run.ROOT;plan=run.prepare();summary=run.read(ROOT/'results-summary.json');helper=run.load_harness('final_verification')
assert run.read(ROOT/'execution-summary.json')['completed']==24
states={};indexes={};execution=Counter()
for cid in plan['cases']:
 backup=ROOT/'worktree-backups'/cid;original=run.read(backup/'original-state.json');work=helper.safe_work(cid)
 states[cid]=run.case_state(helper,cid)==original==run.read(backup/'restored-state.json')
 with tempfile.TemporaryDirectory(prefix='verify-index-',dir=ROOT) as tmp:
  copy=Path(tmp)/'index';shutil.copy2(backup/'index',copy)
  old=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=work,env=dict(os.environ,GIT_INDEX_FILE=str(copy)))
  live=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=work);indexes[cid]=old==live
 assert states[cid] and indexes[cid]
 for arm in ('F1','F2'):
  folder=run.artifact(cid,arm);r=run.read(folder/'result.json');launch=run.read(folder/'launch.json');score=run.read(folder/'score-v3.json')
  assert r['actor_model']=='gpt-6.1-sol' and r['actor_reasoning']==launch['reasoning']=='xhigh'
  assert 'model_reasoning_effort="xhigh"' in launch['command'] and launch['hooks'] is True
  assert r['provider_model']=='gpt-6.1-sol' and r['provider_reasoning']=='medium'
  assert run.read(folder/'masters-nudge-data/config.json')=={'provider':'openai','model':'gpt-6.1-sol'}
  assert Path(launch['provider_binary']).resolve()==Path(plan['codex_binary']).resolve()
  assert launch['provider_binary_sha256']==plan['codex_binary_sha256']
  assert r['prompt_sha256']==plan['cases'][cid]['E_prompt_sha256']==plan['cases'][cid]['F_prompt_sha256']
  assert r['patch_sha256']==score['patch_sha256']==run.sha(folder/'final.patch')
  assert score['evaluator_sha256']==plan['evaluator_sha256']
  attempts=run.read(folder/'provider-attempts.json')
  assert r['provider_attempt_count']==len(attempts)
  assert r['provider_delivered_count']==sum(bool(x.get('delivered')) for x in attempts)<=3
  assert r['provider_silence_count']==sum(x['outcome']=='silence' for x in attempts)<=2
  assert r['provider_fault_count']==sum(x['outcome'] not in ('feedback','silence') for x in attempts)
  execution[score['execution_contract_status']]+=1
lookup={(r['case'],r['arm']):r for r in summary['deliveries']};assert len(lookup)==72 and len(summary['pairs'])==48
for a in 'CEF':
 rows=[r for r in lookup.values() if r['arm'].startswith(a)];assert len(rows)==24
 assert sum(r['completed'] is True for r in rows)==summary['arms'][a]['completed']
 for r in rows:assert r['completed']==run.completed_score(r['case'],r['arm'])['task_completed']
for name,comp in summary['comparisons'].items():
 a,b=name.split('-');eligible=[p for p in summary['pairs'] if p['pair']==name and p['status']=='blind_complete']
 assert len(eligible)==comp['taste_pairs']==sum(lookup[cid,a+str(i)]['completed'] and lookup[cid,b+str(i)]['completed'] for cid in plan['cases'] for i in (1,2))
 assert dict(Counter(p['winner'] for p in eligible))==comp['taste']
 assert sum(comp['contract_counts'].values())==24
for source in run.read(ROOT/'harness-source-manifest.json'):
 assert run.sha(ROOT/source['snapshot'])==source['sha256']==run.sha(source['source'])
assert run.sha(ROOT/'diagnostics/flipt-segments/rollout_legacy_shape_audit_test.go')==run.sha(run.E_REFERENCE/'diagnostics/flipt-segments/rollout_legacy_shape_audit_test.go')
assert run.sha(ROOT/'diagnostics/clap-2297/diagnostic_occurrences.rs')==run.sha(run.E_REFERENCE/'diagnostics/clap-2297/diagnostic_occurrences.rs')
run.verify_archive(plan)
assert plan['codex_binary_sha256']==run.read(run.E_REFERENCE/'plan.json')['codex_binary_sha256']
receipt={'new_F_deliveries':24,'references_C_E_unchanged':True,'same_frozen_cli_as_E':True,'CLI_difference_C':plan['CLI_difference_C'],
 'case_states_match':states,'index_entries_match':indexes,'actual_actor_model':'gpt-6.1-sol','actor_reasoning':'xhigh',
 'provider_model':'gpt-6.1-sol','provider_reasoning':'medium','F_execution_status':dict(execution),
 'source_snapshots':len(run.read(ROOT/'harness-source-manifest.json')),'summary_sha256':run.sha(ROOT/'results-summary.json'),'report_sha256':run.sha(ROOT/'REPORT.zh-TW.md')}
run.save(ROOT/'final-integrity.json',receipt);print(json.dumps(receipt,ensure_ascii=False))
