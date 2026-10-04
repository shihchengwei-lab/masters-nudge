"""Verify the completed cohort and preservation receipts without rerunning outcomes."""
import json
import os
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
import run

ROOT = Path(__file__).resolve().parent
plan = run.prepare()
summary = run.read(ROOT / 'results-summary.json')
execution = run.read(ROOT / 'execution-summary.json')
restoration = run.read(ROOT / 'restoration-confirmed.json')
assert execution['completed'] == 24 and execution['errors'] == []
assert len(plan['cases']) == 12
assert set(restoration['restored_cases']) == set(plan['cases'])
assert restoration['case_states_match'] and restoration['archived_A_unchanged']
runner = run.load_harness('final_verification')
states = {}
index_matches = {}
index_byte_matches = {}
execution_statuses = Counter()
for case in plan['cases']:
    backup = ROOT / 'worktree-backups' / case
    original = run.read(backup / 'original-state.json')
    assert run.read(backup / 'restored-state.json') == original
    work = runner.safe_work(case)
    index = Path(runner.git(work, 'rev-parse', '--path-format=absolute', '--git-path', 'index').strip())
    index_byte_matches[case] = run.sha(index) == run.sha(backup / 'index')
    # Git may refresh file timestamps in an otherwise identical index.
    with tempfile.TemporaryDirectory(prefix='verify-index-', dir=ROOT) as temporary:
        index_copy = Path(temporary) / 'index'
        shutil.copy2(backup / 'index', index_copy)
        environment = dict(os.environ, GIT_INDEX_FILE=str(index_copy))
        prior_entries = subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=work, env=environment)
        live_entries = subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=work)
        index_matches[case] = prior_entries == live_entries
    states[case] = run.case_state(runner, case) == original
    assert states[case] and index_matches[case], case
    for arm in ('B1', 'B2'):
        folder = run.artifact(case, arm)
        result = run.read(folder / 'result.json')
        score = run.read(folder / 'score-v3.json')
        assert isinstance(score['task_completed'], bool)
        assert score['patch_sha256'] == result['patch_sha256'] == run.sha(folder / 'final.patch')
        assert result['prompt_sha256'] == plan['cases'][case]['B_prompt_sha256']
        assert result['actor_model'] == result['provider_model'] == 'gpt-6.1-sol'
        assert result['actor_reasoning'] == result['provider_reasoning'] == 'medium'
        assert result['provider_delivered_count'] <= 3 and result['provider_silence_count'] <= 2
        assert score['evaluator_sha256'] == plan['evaluator_sha256']
        execution_statuses[score['execution_contract_status']] += 1
for arm in ('A', 'B'):
    rows = [r for r in summary['deliveries'] if r['arm'].startswith(arm)]
    assert len(rows) == summary['arms'][arm]['recorded'] == 24
    assert sum(r['completed'] is True for r in rows) == summary['arms'][arm]['completed']
    assert summary['arms'][arm]['unresolved'] == 0
blind = [p for p in summary['pairs'] if p['status'] == 'blind_complete']
assert len(summary['pairs']) == 24
assert len(blind) == summary['taste_jointly_completed_pairs'] == sum(a['completed'] is True and b['completed'] is True for a in summary['deliveries'] if a['arm'].startswith('A') for b in summary['deliveries'] if b['case']==a['case'] and b['arm']=='B'+a['arm'][1:])
assert dict(Counter(p['winner'] for p in blind)) == summary['taste']
assert summary['matched_usage_comparison']['pair_count'] == sum(a['actor_usage_available'] and b['actor_usage_available'] for a in summary['deliveries'] if a['arm'].startswith('A') for b in summary['deliveries'] if b['case']==a['case'] and b['arm']=='B'+a['arm'][1:])
assert sum(summary['paired_contract_results'].values()) == 24
assert summary['paired_contract_results']['unresolved'] == 0
assert summary['paired_contract_results']['both_completed'] == len(blind)
run.verify_archive(plan)
receipt = {'fresh_B_deliveries': 24, 'archived_A_deliveries': 24, 'archived_A_unchanged': True,
           'frozen_inputs_unchanged': True, 'case_states_match_live': states, 'index_entries_match': index_matches,
           'index_bytes_match': index_byte_matches,
           'B_execution_review_statuses': dict(execution_statuses), 'jointly_completed_taste_pairs': len(blind),
           'matched_usage_pairs': summary['matched_usage_comparison']['pair_count'], 'report_sha256': run.sha(ROOT / 'REPORT.zh-TW.md'),
           'summary_sha256': run.sha(ROOT / 'results-summary.json')}
run.save(ROOT / 'final-integrity.json', receipt)
print(json.dumps(receipt, ensure_ascii=False))
