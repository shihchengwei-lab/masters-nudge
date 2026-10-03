"""Verify actual D settings, archived references and restored calibration state."""
import json,os,subprocess,tempfile,shutil
from collections import Counter
from pathlib import Path
import run
ROOT=run.ROOT
plan=run.prepare();summary=run.read(ROOT/'results-summary.json')
execution=run.read(ROOT/'execution-summary.json');restoration=run.read(ROOT/'restoration-confirmed.json')
assert execution['completed']==24 and execution['errors']==[]
assert restoration['archived_A_unchanged'] and restoration['case_states_match']
assert set(restoration['restored_cases'])==set(plan['cases'])
helper=run.load_harness('final_verification')
states={};indexes={};execution_status=Counter()
for case in plan['cases']:
 backup=ROOT/'worktree-backups'/case;original=run.read(backup/'original-state.json')
 assert run.read(backup/'restored-state.json')==original
 work=helper.safe_work(case)
 states[case]=run.case_state(helper,case)==original
 with tempfile.TemporaryDirectory(prefix='verify-index-',dir=ROOT) as temporary:
  copy=Path(temporary)/'index';shutil.copy2(backup/'index',copy)
  old=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=work,env=dict(os.environ,GIT_INDEX_FILE=str(copy)))
  live=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=work)
  indexes[case]=old==live
 assert states[case] and indexes[case]
 for arm in ('D1','D2'):
  folder=run.artifact(case,arm);result=run.read(folder/'result.json');launch=run.read(folder/'launch.json');score=run.read(folder/'score-v3.json')
  assert result['actor_model']=='gpt-6.1-sol' and result['actor_reasoning']=='medium'
  assert launch['reasoning']=='medium' and launch['hooks'] is True
  assert 'model_reasoning_effort="medium"' in launch['command']
  assert '--enable' in launch['command'] and '--dangerously-bypass-hook-trust' in launch['command']
  assert 'hooks' in launch['command'] and 'plugins' in launch['command']
  assert Path(launch['provider_binary']).resolve()==Path(plan['codex_binary']).resolve()
  assert launch['provider_binary_sha256']==plan['codex_binary_sha256']
  assert result['provider_model']=='gpt-6-astra' and result['provider_reasoning']=='medium'
  assert run.read(folder/'masters-nudge-data/config.json')=={'provider':'openai','model':'gpt-6-astra'}
  attempts=run.read(folder/'provider-attempts.json')
  assert result['provider_attempt_count']==len(attempts)
  assert result['provider_delivered_count']==sum(bool(x.get('delivered')) for x in attempts)
  assert result['provider_silence_count']==sum(x['outcome']=='silence' for x in attempts)
  assert result['provider_fault_count']==sum(x['outcome'] not in ('feedback','silence') for x in attempts)
  assert result['provider_delivered_count']<=3 and result['provider_silence_count']<=2
  assert result['prompt_sha256']==plan['cases'][case]['A_prompt_sha256']==plan['cases'][case]['D_prompt_sha256']
  assert result['patch_sha256']==score['patch_sha256']==run.sha(folder/'final.patch')
  assert score['evaluator_sha256']==plan['evaluator_sha256'] and isinstance(score['task_completed'],bool)
  execution_status[score['execution_contract_status']]+=1
lookup={(r['case'],r['arm']):r for r in summary['deliveries']}
assert len(lookup)==72 and len(summary['pairs'])==48
for arm in ('A','B','D'):
 rows=[r for r in lookup.values() if r['arm'].startswith(arm)]
 assert len(rows)==24 and summary['arms'][arm]['unresolved']==0
 assert sum(r['completed'] is True for r in rows)==summary['arms'][arm]['completed']
 for row in rows:
  assert row['completed']==run.read(run.artifact(row['case'],row['arm'])/'score-v3.json')['task_completed']
for reference in ('A','B'):
 comparison=summary['comparisons'][reference+'-D'];eligible=[p for p in summary['pairs'] if p['pair']==reference+'-D' and p['status']=='blind_complete']
 expected=sum(lookup[case,reference+str(trial)]['completed'] and lookup[case,'D'+str(trial)]['completed'] for case in plan['cases'] for trial in (1,2))
 assert len(eligible)==comparison['taste_pairs']==expected
 assert dict(Counter(p['winner'] for p in eligible))==comparison['taste']
 assert sum(comparison['contract_counts'].values())==24
 complete_usage=sum(lookup[case,reference+str(trial)]['actor_usage_available'] and lookup[case,'D'+str(trial)]['actor_usage_available'] for case in plan['cases'] for trial in (1,2))
 assert comparison['matched_usage']['pair_count']==complete_usage
for source in run.read(ROOT/'harness-source-manifest.json'):
 assert run.sha(ROOT/source['snapshot'])==source['sha256']==run.sha(source['source'])
run.verify_archive(plan)
receipt={'new_D_deliveries':24,'archived_A_unchanged':True,'sealed_B_unchanged':True,'frozen_inputs_unchanged':True,'case_states_match':states,'index_entries_match':indexes,'D_execution_status':dict(execution_status),'actual_model':'gpt-6.1-sol','actual_reasoning':'medium','hooks':True,'provider_model':'gpt-6-astra','provider_reasoning':'medium','provider_feedback':summary['arms']['D']['provider_feedback'],'provider_faults':summary['arms']['D']['provider_faults'],'summary_sha256':run.sha(ROOT/'results-summary.json'),'report_sha256':run.sha(ROOT/'REPORT.zh-TW.md')}
run.save(ROOT/'final-integrity.json',receipt)
print(json.dumps(receipt,ensure_ascii=False))
