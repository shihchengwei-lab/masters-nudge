"""Repair bookkeeping for the existing timeout, then run only missing trials.

All recorded solution outcomes remain immutable. Model, prompts and time budgets
remain fixed. Raw post-deadline material is retained but is not a delivery.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import run

ROOT = run.ROOT


def finalize_existing_timeout(plan, runner):
    folder = ROOT / 'runs/tracing-1523/I1'
    if (folder / 'result.json').exists():
        return
    launch = run.read(folder / 'launch.json')
    running = run.read(folder / 'running.json')
    cleanup = run.read(ROOT / 'timeout-cleanup.json')
    started = datetime.fromisoformat(running['started_utc'])
    stopped = datetime.fromisoformat(cleanup['utc'])
    deadline = started.timestamp() + plan['actor_wall_timeout_seconds']
    attempts, skipped = runner.attempts(folder / 'masters-nudge-data')
    assert all(row['started'] <= deadline and row['finished'] <= deadline for row in attempts)
    events = []
    for line in (folder / 'actor-events.jsonl').read_text(encoding='utf-8').splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            pass
    (folder / 'final.patch').write_bytes(b'')
    run.save(folder / 'provider-attempts.json', attempts)
    provider_usage = {key: sum(int(row.get('detail', {}).get('usage', {}).get(key) or 0)
                              for row in attempts)
                      for key in ['input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens']}
    faults = [row for row in attempts if row['outcome'] not in ('feedback', 'silence')]
    # This is the first fixed verification of this scheduled outcome, never a new Actor run.
    checks = runner.verification('tracing-1523', 'I1', plan['cases']['tracing-1523'], folder, [])
    result = {
        'case': 'tracing-1523', 'arm': 'I1', 'actor_model': run.MODEL,
        'actor_reasoning': 'xhigh', 'provider_model': plan['provider_model'],
        'provider_reasoning': 'xhigh', 'base_commit': launch['base_commit'],
        'prompt_sha256': launch['prompt_sha256'], 'patch_sha256': run.sha(folder / 'final.patch'),
        'actor_exit': None, 'actor_elapsed_seconds': 1800.0,
        'total_elapsed_seconds': (stopped - started).total_seconds() + sum(c['elapsed_seconds'] for c in checks),
        'verification_elapsed_seconds': sum(c['elapsed_seconds'] for c in checks),
        'actor_usage': {}, 'provider_usage': provider_usage,
        'file_change_events': sum(e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'file_change' for e in events),
        'provider_attempt_count': len(attempts),
        'provider_feedback_count': sum(r['outcome'] == 'feedback' for r in attempts),
        'provider_silence_count': sum(r['outcome'] == 'silence' for r in attempts),
        'provider_fault_count': len(faults),
        'provider_delivered_count': sum(bool(r.get('delivered')) for r in attempts),
        'provider_skipped_test_patches': skipped, 'tests_modified': [], 'actor_added_tests': [],
        'verification': checks, 'verification_error': '',
        'execution_fault': 'Actor exceeded 1800 second wall budget', 'contract_passed': False,
        'artifact_dir': str(folder),
        'timeout_bookkeeping': {
            'actor_rerun': False, 'deadline_seconds': 1800, 'exit_code_unavailable': True,
            'post_deadline_overrun_seconds': max(0, (stopped - started).total_seconds() - 1800),
            'deadline_patch_unavailable': True, 'final_patch_handling': 'No accepted delivery; empty patch for fixed verification.',
            'retained_material': 'after-deadline.patch and unmodified actor-events.jsonl',
            'actor_usage_handling': 'Incomplete terminal usage; exclude Token pairs.',
            'file_change_events_scope': 'Full preserved raw transcript, including post-deadline events; not an accepted delivery.',
            'test_path_inventory_unavailable_at_deadline': True,
        },
    }
    run.save(folder / 'result.json', result)
    (folder / 'running.json').unlink(missing_ok=True)
    run.save(ROOT / 'timeout-recovery.json', {
        **result['timeout_bookkeeping'], 'case': 'tracing-1523', 'arm': 'I1',
        'prior_recorded_deliveries': 17, 'remaining_new_actor_deliveries': 6,
        'harness_amendment': 'harness-amendments/timeout-termination-20261004/amendment.json',
    })
    run.emit({'stage': 'preserved_timeout_finalized', 'case': 'tracing-1523', 'arm': 'I1', 'contract_passed': False})


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    plan = run.prepare()
    run.verify_archive(plan)
    runner = run.load_harness('timeout_continuation')
    before = {str(p.relative_to(ROOT)): run.sha(p) for p in ROOT.glob('runs/*/*/result.json')}
    assert len(before) == 17 or (ROOT / 'timeout-recovery.json').exists()
    run.save(ROOT / 'continuation-preserved-results.json', before)
    run.save(ROOT / 'orchestrator.json', {'pid': os.getpid(), 'started_utc': datetime.now(timezone.utc).isoformat(), 'recovery': 'timeout-termination-repair'})
    run.save(ROOT / 'pipeline-status.json', {'status': 'running', 'stage': 'timeout-bookkeeping'})
    finalize_existing_timeout(plan, runner)
    pending_cases = [cid for cid in plan['cases'] if not all((ROOT / 'runs' / cid / arm / 'result.json').exists() for arm in plan['new_arms'])]
    missing = [(cid, arm) for cid in pending_cases for arm in plan['new_arms'] if not (ROOT / 'runs' / cid / arm / 'result.json').exists()]
    run.save(ROOT / 'continuation-plan.json', {'missing_trials': missing, 'preserved_result_sha256': before, 'timeout_is_failed_outcome': True})
    run.save(ROOT / 'pipeline-status.json', {'status': 'running', 'stage': 'actors-continuation', 'new_actor_trials': len(missing)})
    errors = []
    with ThreadPoolExecutor(max_workers=plan['workers']) as pool:
        futures = {pool.submit(run.run_case, cid, plan, runner): cid for cid in pending_cases}
        for future in as_completed(futures):
            cid = futures[future]
            try:
                future.result()
            except Exception as exc:
                run.STOP.set()
                error = {'case': cid, 'error': str(exc)}
                errors.append(error)
                run.save(ROOT / 'errors' / (cid + '.json'), error)
                run.emit(error)
    assert all(run.sha(ROOT / p) == digest for p, digest in before.items())
    run.save(ROOT / 'execution-summary.json', {**run.status(plan), 'errors': errors})
    states = {cid: run.case_state(runner, cid) == run.read(ROOT / 'worktree-backups' / cid / 'original-state.json') for cid in plan['cases']}
    assert all(states.values())
    run.verify_archive(plan)
    run.save(ROOT / 'restoration-confirmed.json', {'case_states_match': True, 'references_C_F_unchanged': True, 'restored_cases': list(states)})
    if errors:
        run.save(ROOT / 'pipeline-status.json', {'status': 'needs_repair', 'stage': 'actors-continuation', 'errors': errors})
        return 1
    assert run.status(plan)['completed'] == 24
    env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
    linux = '/mnt/e/masters-nudge-benchmark/' + ROOT.name + '/diagnostics/flipt-segments/run.py'
    stages = [
        ('flipt-original-clause', ['wsl.exe', '-u', 'root', '--exec', 'python3', linux]),
        ('clap-original-clause', [sys.executable, '-X', 'utf8', str(ROOT / 'diagnostic_clap_occurrences.py')]),
        ('execution-and-taste-grading', [sys.executable, '-X', 'utf8', str(ROOT / 'finish.py')]),
        ('integrity', [sys.executable, '-X', 'utf8', str(ROOT / 'verify_final.py')]),
    ]
    diagnostics = {}
    for stage, command in stages:
        run.save(ROOT / 'pipeline-status.json', {'status': 'running', 'stage': stage})
        run.emit({'pipeline_stage': stage})
        started = time.monotonic()
        proc = subprocess.run(command, cwd=ROOT, env=env, stdout=sys.stdout, stderr=sys.stderr, creationflags=subprocess.CREATE_NO_WINDOW)
        if proc.returncode:
            run.save(ROOT / 'pipeline-status.json', {'status': 'needs_repair', 'stage': stage, 'exit_code': proc.returncode})
            return proc.returncode
        if 'original-clause' in stage:
            diagnostics[stage] = {'seconds': time.monotonic() - started}
            run.save(ROOT / 'diagnostics-status.json', {'status': 'complete' if len(diagnostics) == 2 else 'in_progress', 'stages': diagnostics})
    run.save(ROOT / 'pipeline-status.json', {'status': 'complete', 'new_I_deliveries': 24, 'infrastructure_recovery': True, 'timeout_outcome_preserved': True})
    run.emit({'pipeline_stage': 'complete', 'new_I_deliveries': 24})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
