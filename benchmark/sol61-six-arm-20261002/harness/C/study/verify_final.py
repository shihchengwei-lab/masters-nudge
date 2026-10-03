"""Verify actual C settings, archived references and restored calibration state."""
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
 for arm in ('C1','C2'):
  folder=run.artifact(case,arm);result=run.read(folder/'result.json');launch=run.read(folder/'launch.json');score=run.read(folder/'score-v3.json')
  assert result['actor_model']=='gpt-6.1-sol' and result['actor_reasoning']=='xhigh'
  assert launch['reasoning']=='xhigh' and launch['hooks'] is False
  assert 'model_reasoning_effort="xhigh"' in launch['command']
  assert '--enable' not in launch['command'] and '--dangerously-bypass-hook-trust' not in launch['command']
  assert result['provider_model'] is None and result['provider_reasoning'] is None
  assert all(result[k]==0 for k in ('provider_attempt_count','provider_delivered_count','provider_fault_count','provider_silence_count'))
  assert not run.read(folder/'provider-attempts.json')
  assert result['prompt_sha256']==plan['cases'][case]['A_prompt_sha256']==plan['cases'][case]['C_prompt_sha256']
  assert result['patch_sha256']==score['patch_sha256']==run.sha(folder/'final.patch')
  assert score['evaluator_sha256']==plan['evaluator_sha256'] and isinstance(score['task_completed'],bool)
  execution_status[score['execution_contract_status']]+=1
lookup={(r['case'],r['arm']):r for r in summary['deliveries']}
assert len(lookup)==72 and len(summary['pairs'])==48
for arm in ('A','B','C'):
 rows=[r for r in lookup.values() if r['arm'].startswith(arm)]
 assert len(rows)==24 and summary['arms'][arm]['unresolved']==0
 assert sum(r['completed'] is True for r in rows)==summary['arms'][arm]['completed']
 for row in rows:
  assert row['completed']==run.read(run.artifact(row['case'],row['arm'])/'score-v3.json')['task_completed']
for reference in ('A','B'):
 comparison=summary['comparisons'][reference+'-C'];eligible=[p for p in summary['pairs'] if p['pair']==reference+'-C' and p['status']=='blind_complete']
 expected=sum(lookup[case,reference+str(trial)]['completed'] and lookup[case,'C'+str(trial)]['completed'] for case in plan['cases'] for trial in (1,2))
 assert len(eligible)==comparison['taste_pairs']==expected
 assert dict(Counter(p['winner'] for p in eligible))==comparison['taste']
 assert sum(comparison['contract_counts'].values())==24
 complete_usage=sum(lookup[case,reference+str(trial)]['actor_usage_available'] and lookup[case,'C'+str(trial)]['actor_usage_available'] for case in plan['cases'] for trial in (1,2))
 assert comparison['matched_usage']['pair_count']==complete_usage
for source in run.read(ROOT/'harness-source-manifest.json'):
 assert run.sha(ROOT/source['snapshot'])==source['sha256']==run.sha(source['source'])
run.verify_archive(plan)
receipt={'new_C_deliveries':24,'archived_A_unchanged':True,'sealed_B_unchanged':True,'frozen_inputs_unchanged':True,'case_states_match':states,'index_entries_match':indexes,'C_execution_status':dict(execution_status),'actual_model':'gpt-6.1-sol','actual_reasoning':'xhigh','hooks':False,'provider_attempts':0,'summary_sha256':run.sha(ROOT/'results-summary.json'),'report_sha256':run.sha(ROOT/'REPORT.zh-TW.md')}
run.save(ROOT/'final-integrity.json',receipt)
print(json.dumps(receipt,ensure_ascii=False))
