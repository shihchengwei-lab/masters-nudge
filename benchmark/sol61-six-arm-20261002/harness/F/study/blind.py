"""Fixed-rubric, independent anonymous pairwise judgments for the three arms."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import run

ROOT = run.ROOT / ('blind-v3' if run.AMENDMENT else 'blind')
MODEL = 'gpt-6-astra'
RUBRIC = (run.EVALUATION / 'blind-rubric.txt').read_text(encoding='utf-8')
SCHEMA = {
    'type': 'object',
    'properties': {
        'winner': {'type': 'string', 'enum': ['X', 'Y', 'tie']},
        'reason': {'type': 'string'},
        'evidence': {'type': 'array', 'items': {
            'type': 'object', 'properties': {k: {'type': 'string'} for k in
                                            ['criterion', 'x_location', 'y_location', 'observation']},
            'required': ['criterion', 'x_location', 'y_location', 'observation'], 'additionalProperties': False}},
        'contract_concerns': {'type': 'array', 'items': {
            'type': 'object', 'properties': {
                'candidate': {'type': 'string', 'enum': ['X', 'Y']},
                **{k: {'type': 'string'} for k in ['exact_clause', 'location', 'observation']}},
            'required': ['candidate', 'exact_clause', 'location', 'observation'], 'additionalProperties': False}}},
    'required': ['winner', 'reason', 'evidence', 'contract_concerns'], 'additionalProperties': False}


def prepare_source(cid, arm, plan):
    helper = run.load_harness('source_helper')
    label = hashlib.sha256(('round11|' + cid + '|' + arm).encode()).hexdigest()[:16]
    path = ROOT / 'sources' / label
    receipt = ROOT / 'source-receipts' / (label + '.json')
    patch = run.artifact(cid, arm) / 'final.patch'
    expected = {'case': cid, 'arm': arm, 'base': plan['cases'][cid]['base_commit'], 'patch_sha256': run.sha(patch)}
    if receipt.exists():
        assert run.read(receipt) == expected
        if path.exists():
            return path
    elif path.exists():
        raise RuntimeError('Unreceipted anonymous checkout: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    helper.calibration.checked(['git', '-c', 'core.longpaths=true', '-c', 'core.autocrlf=false',
                                'worktree', 'add', '--detach', str(path), expected['base']],
                               helper.safe_work(cid), 600)
    helper.apply(path, patch)
    run.save(receipt, expected)
    return path


def run_judge(cid, trial, pair, number, plan):
    directory = ROOT / 'judges' / cid / ('trial-' + str(trial)) / pair / ('judge-' + str(number))
    record_path = directory / 'result.json'
    if record_path.exists():
        return run.read(record_path)
    if (directory / 'events.jsonl').exists():
        raise RuntimeError('Preserved incomplete judgment requires explicit infrastructure recovery: ' + str(directory))
    left, right = [arm + str(trial) for arm in pair.split('-')]
    swap = (int(hashlib.sha256((cid + '|' + str(trial) + '|' + pair).encode()).hexdigest(), 16) % 2 == 1) ^ (number == 2)
    mapping = {'X': right if swap else left, 'Y': left if swap else right}
    directory.mkdir(parents=True, exist_ok=True)
    trees = {label: prepare_source(cid, arm, plan) for label, arm in mapping.items()}
    patches = {label: (run.artifact(cid, arm) / 'final.patch').read_text(encoding='utf-8')
               for label, arm in mapping.items()}
    task = (run.EVALUATION / 'cases' / cid / 'task.md').read_text(encoding='utf-8')
    prompt = (RUBRIC + '\n\n你可以使用 X_source、Y_source 唯讀工具查看兩份完整程式的必要關係。'
              '本次兩份交付均通過同版封存驗收、執行契約及相同原條款補查。請用繁體中文回傳指定 JSON。\n\n'
              'TASK\n' + task + '\n\nIMPLEMENTATION X PATCH\n' + patches['X'] +
              '\n\nIMPLEMENTATION Y PATCH\n' + patches['Y'])
    (directory / 'prompt.txt').write_text(prompt, encoding='utf-8', newline='\n')
    run.save(directory / 'schema.json', SCHEMA)
    helper = run.load_harness('judge_helper')
    configs = []
    for label in ['X', 'Y']:
        config = {'command': sys.executable, 'args': [str(run.PACKAGE / 'masters_nudge/read_only_repo_mcp.py'),
                  '--root', str(trees[label]), '--budget', '400000', '--audit', str(directory / (label + '-reads.jsonl'))],
                  'enabled': True, 'startup_timeout_sec': 30, 'tool_timeout_sec': 60,
                  'default_tools_approval_mode': 'approve', 'env': {'PYTHONIOENCODING': 'utf-8'}}
        configs += ['-c', 'mcp_servers.' + label + '_source=' + helper.toml(config)]
    command = [plan['codex_binary'], '-c', 'project_doc_max_bytes=0', '-c', 'features.multi_agent=false',
               '-c', 'model_reasoning_effort="medium"', '-c', 'web_search="disabled"', '-c', 'features.shell_tool=false',
               '--disable', 'hooks', '--disable', 'plugins', *configs, 'exec', '--ignore-user-config', '--ignore-rules',
               '--skip-git-repo-check', '--ephemeral', '--json', '-s', 'read-only', '-m', MODEL,
               '-C', str(directory), '--output-schema', str(directory / 'schema.json'), '-o', str(directory / 'output.json'), '-']
    run.save(directory / 'launch.json', {'command': command, 'mapping': mapping,
             'prompt_sha256': run.textsha(prompt), 'rubric_sha256': run.textsha(RUBRIC),
             'patches': {label: run.sha(run.artifact(cid, arm) / 'final.patch') for label, arm in mapping.items()}})
    env = os.environ.copy()
    env.update(PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1', MASTERS_NUDGE_ACTIVE='0',
               TEMP=str(run.CAL / 'tmp'), TMP=str(run.CAL / 'tmp'))
    start = time.monotonic()
    run.emit({'stage': 'judge_started', 'case': cid, 'trial': trial, 'pair': pair, 'judge': number})
    with (directory / 'events.jsonl').open('w', encoding='utf-8') as stdout, (directory / 'stderr.txt').open('w', encoding='utf-8') as stderr:
        process = subprocess.Popen(command, cwd=directory, env=env, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                   text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            process.communicate(prompt, timeout=900)
        except subprocess.TimeoutExpired:
            subprocess.run(['taskkill.exe', '/PID', str(process.pid), '/T', '/F'], capture_output=True, timeout=30)
            process.wait(timeout=30)
            run.save(directory / 'fault.json', {'type': 'timeout', 'seconds': 900})
            raise
    if process.returncode or not (directory / 'output.json').exists():
        run.save(directory / 'fault.json', {'exit': process.returncode})
        raise RuntimeError('Judge infrastructure failure: ' + str(directory))
    judgment = run.read(directory / 'output.json')
    assert judgment['winner'] in ['X', 'Y', 'tie']
    assert judgment['reason'] and (judgment['winner'] == 'tie' or judgment['evidence'])
    events = []
    for line in (directory / 'events.jsonl').read_text(encoding='utf-8').splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            pass
    usage = next((e['usage'] for e in reversed(events) if e.get('type') == 'turn.completed'), {})
    record = {**judgment, 'case': cid, 'trial': trial, 'pair': pair, 'judge': number, 'mapping': mapping,
              'winner_arm': mapping[judgment['winner']][0] if judgment['winner'] != 'tie' else 'tie',
              'usage': usage, 'elapsed_seconds': round(time.monotonic() - start, 3),
              'model': MODEL, 'reasoning': 'medium', 'prompt_sha256': run.textsha(prompt),
              'mapped_concerns': [{**c, 'arm': mapping[c['candidate']]} for c in judgment['contract_concerns']]}
    run.save(record_path, record)
    run.emit({'stage': 'judge_complete', 'case': cid, 'trial': trial, 'pair': pair, 'judge': number,
              'winner': record['winner_arm'], 'concerns': len(record['contract_concerns'])})
    return record


def run_pair(cid, trial, pair, plan):
    output = ROOT / 'judges' / cid / ('trial-' + str(trial)) / pair / 'pair.json'
    if output.exists():
        return run.read(output)
    left, right = pair.split('-')
    paths = {arm: run.score_path(run.artifact(cid, arm + str(trial))) for arm in [left, right]}
    if not all(p.exists() for p in paths.values()):
        return None
    scores = {arm: run.completed_score(cid, arm + str(trial)) for arm in paths}
    if any(score['execution_contract_status'] == 'unreviewed' or score['task_completed'] is None for score in scores.values()):
        return None
    passed = {arm: score['task_completed'] for arm, score in scores.items()}
    if not all(passed.values()):
        record = {'case': cid, 'trial': trial, 'pair': pair, 'status': 'contract_result',
                  'winner': left if passed[left] else right if passed[right] else 'both_failed',
                  'task_completed': passed, 'judges': []}
    else:
        judges = [run_judge(cid, trial, pair, n, plan) for n in [1, 2]]
        if judges[0]['winner_arm'] != judges[1]['winner_arm']:
            judges.append(run_judge(cid, trial, pair, 3, plan))
        counts = Counter(j['winner_arm'] for j in judges)
        winner = next((arm for arm in [left, right, 'tie'] if counts[arm] >= 2), 'tie')
        record = {'case': cid, 'trial': trial, 'pair': pair, 'status': 'blind_complete',
                  'winner': winner, 'task_completed': passed, 'judges': judges,
                  'concerns': [c for j in judges for c in j['mapped_concerns']]}
    run.save(output, record)
    run.emit({k: record[k] for k in ['case', 'trial', 'pair', 'status', 'winner']})
    return record


def remove_sources(cid):
    helper = run.load_harness('cleanup_helper')
    root = (ROOT / 'sources').resolve()
    for receipt in (ROOT / 'source-receipts').glob('*.json'):
        if run.read(receipt)['case'] != cid:
            continue
        source = (root / receipt.stem).resolve()
        assert source.parent == root
        if source.exists():
            helper.git(helper.safe_work(cid), 'worktree', 'remove', '--force', str(source))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--watch', action='store_true')
    parser.add_argument('--cases', nargs='*')
    args = parser.parse_args()
    plan = run.initialize()
    ROOT.mkdir(exist_ok=True)
    protocol = {'model': MODEL, 'reasoning': 'medium', 'rubric_sha256': run.textsha(RUBRIC), 'schema': SCHEMA,
                'pairs': plan['pairwise_comparisons'], 'trials': [1, 2],
                'rule': 'Two independent reversed orders; third if different; majority; three different votes => tie.',
                'source_access': 'Full source through read-only MCP; no arm labels, Provider nudges, execution traces, references or other judgments.'}
    if (ROOT / 'protocol.json').exists():
        assert run.read(ROOT / 'protocol.json') == protocol
    else:
        run.save(ROOT / 'protocol.json', protocol)
    cases = args.cases or list(plan['cases'])
    while True:
        finished = 0
        for cid in cases:
            complete = 0
            for trial in [1, 2]:
                for pair in plan['pairwise_comparisons']:
                    if run_pair(cid, trial, pair, plan) is not None:
                        complete += 1
            if complete == 2 * len(plan['pairwise_comparisons']):
                remove_sources(cid)
                finished += 1
        if finished == len(cases) or not args.watch:
            break
        time.sleep(15)
