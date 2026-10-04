"""Replace stale infrastructure verification, preserve all Actor outcomes, finish grading."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone
import run

ROOT = run.ROOT


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    plan = run.prepare()
    before = {str(p.relative_to(ROOT)): run.sha(p) for p in ROOT.glob('runs/*/*/result.json')}
    assert len(before) == 24
    run.save(ROOT / 'grading-resume-preserved-results.json', before)
    run.save(ROOT / 'orchestrator.json', {'pid': os.getpid(), 'started_utc': datetime.now(timezone.utc).isoformat(), 'recovery': 'stale-verification'})
    evidence_folder = ROOT / 'evaluation-v3/nodebb-images/I1'
    folder = ROOT / 'runs/nodebb-images/I1'
    evidence = run.read(evidence_folder / 'evidence.json')
    actual_hash = run.sha(folder / 'final.patch')
    if evidence['patch_sha256'] != actual_hash:
        prior = ROOT / 'infrastructure-attempts/nodebb-images/I1/capacity-before-edit/final.patch'
        assert evidence['patch_sha256'] == run.sha(prior)
        destination = ROOT / 'infrastructure-attempts/nodebb-images/I1/stale-capacity-verification'
        assert evidence_folder.resolve().is_relative_to(ROOT.resolve())
        assert destination.resolve().is_relative_to(ROOT.resolve()) and not destination.exists()
        evidence_folder.rename(destination)
        run.save(ROOT / 'pipeline-status.json', {'status': 'running', 'stage': 'repair-stale-verification'})
        helper = run.load_harness('verification_recovery')
        started = time.monotonic()
        checks = helper.verification('nodebb-images', 'I1', plan['cases']['nodebb-images'], folder, [])
        corrected = run.read(evidence_folder / 'evidence.json')
        assert corrected['patch_sha256'] == actual_hash
        run.save(ROOT / 'verification-recovery.json', {
            'case': 'nodebb-images', 'arm': 'I1', 'reason': 'stale evidence references initial pre-edit capacity attempt',
            'preserved_evidence': str(destination), 'prior_patch_sha256': evidence['patch_sha256'],
            'actual_patch_sha256': actual_hash, 'new_evidence_sha256': run.sha(evidence_folder / 'evidence.json'),
            'verification_seconds': time.monotonic() - started, 'checks': checks,
            'actor_rerun': False, 'recorded_actor_results_unchanged': True,
        })
    run.verify_archive(plan)
    env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
    for stage, name in [('execution-and-taste-grading', 'finish.py'), ('integrity', 'verify_final.py')]:
        run.save(ROOT / 'pipeline-status.json', {'status': 'running', 'stage': stage})
        process = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / name)], cwd=ROOT,
                                 env=env, stdout=sys.stdout, stderr=sys.stderr, creationflags=subprocess.CREATE_NO_WINDOW)
        if process.returncode:
            run.save(ROOT / 'pipeline-status.json', {'status': 'needs_repair', 'stage': stage, 'exit_code': process.returncode})
            return process.returncode
    assert all(run.sha(ROOT / relative) == digest for relative, digest in before.items())
    run.save(ROOT / 'pipeline-status.json', {'status': 'complete', 'new_I_deliveries': 24,
                                           'infrastructure_recovery': True, 'timeout_outcome_preserved': True,
                                           'stale_verification_repaired': True})
    run.emit({'pipeline_stage': 'complete', 'new_I_deliveries': 24})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
