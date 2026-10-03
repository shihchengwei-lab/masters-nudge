"""Extract execution evidence for human-readable review; never auto-approve it."""
import argparse
import json
from pathlib import Path
import re
import sys
import run


def export(cid, arm):
    folder = run.artifact(cid, arm)
    if not (folder / 'result.json').exists():
        return None
    events_path = folder / 'actor-events.jsonl'
    if not events_path.exists():
        raise RuntimeError('Missing execution transcript: ' + str(folder))
    commands, changes, other_tools = [], [], []
    errors = []
    for number, line in enumerate(events_path.read_text(encoding='utf-8').splitlines(), 1):
        try:
            event = json.loads(line)
        except ValueError:
            errors.append({'line': number, 'problem': 'invalid JSON'})
            continue
        if event.get('type') in ('error', 'turn.failed'):
            errors.append({'line': number, 'event': event})
        if event.get('type') != 'item.completed':
            continue
        item = event.get('item', {})
        kind = item.get('type')
        if kind == 'command_execution':
            commands.append({'line': number, 'command': item['command'], 'exit_code': item.get('exit_code')})
        elif kind == 'file_change':
            changes.append({'line': number, 'status': item.get('status'),
                            'changes': [{k: c.get(k) for k in ['path', 'kind']} for c in item.get('changes', [])]})
        elif kind not in ['agent_message', 'reasoning', None]:
            other_tools.append({'line': number, 'item': item})
    result = run.read(folder / 'result.json')
    launch = run.read(folder / 'launch.json')
    manifest = run.read(run.ROOT / 'plan.json')
    meta = manifest['cases'][cid]
    patch_paths = re.findall(r'^\+\+\+ b/(.*)$', (folder / 'final.patch').read_text(encoding='utf-8'), re.M)
    output = {'case': cid, 'arm': arm, 'transcript': str(events_path), 'transcript_sha256': run.sha(events_path),
              'patch_sha256': run.sha(folder / 'final.patch'), 'launch': launch,
              'base_matches': launch['base_commit'] == meta['base_commit'],
              'prompt_matches': run.textsha((folder / 'prompt.txt').read_text(encoding='utf-8')) == meta[arm[0] + '_prompt_sha256'],
              'actor_exit': result['actor_exit'], 'actor_seconds': result['actor_elapsed_seconds'],
              'existing_tests_changed': result.get('tests_modified', []), 'patch_paths': patch_paths,
              'commands': commands, 'file_changes': changes, 'other_tools': other_tools, 'errors': errors}
    run.save(folder / 'execution-evidence.json', output)
    text = [f"# {cid}/{arm}",
            f"base_matches={output['base_matches']} prompt_matches={output['prompt_matches']} actor_exit={output['actor_exit']} seconds={output['actor_seconds']}",
            'existing_tests_changed=' + json.dumps(output['existing_tests_changed']),
            'patch_paths=' + json.dumps(patch_paths), '\n## Completed commands']
    text += ['L' + str(c['line']) + ' exit=' + str(c['exit_code']) + ' ' + c['command'] for c in commands]
    text += ['\n## File changes', json.dumps(changes, ensure_ascii=False), '\n## Other tools',
             json.dumps(other_tools, ensure_ascii=False), '\n## Errors', json.dumps(errors, ensure_ascii=False)]
    (folder / 'execution-evidence.txt').write_text('\n'.join(text) + '\n', encoding='utf-8')
    return folder / 'execution-evidence.txt'


def score(cid, arm):
    folder = run.artifact(cid, arm)
    decision_path = folder / 'execution-review.json'
    if not decision_path.exists():
        return None
    review = run.read(decision_path)
    audit = run.read(folder / 'execution-evidence.json')
    assert review['execution_evidence_sha256'] == run.sha(folder / 'execution-evidence.json')
    assert audit['transcript_sha256'] == run.sha(folder / 'actor-events.jsonl')
    assert audit['patch_sha256'] == run.sha(folder / 'final.patch') == review['patch_sha256']
    assert review['status'] in ('pass', 'fail', 'environment_error') and review['evidence'] and review['reason']
    evidence = run.read(run.evaluation_directory(folder) / 'evidence.json')
    evidence['execution_review'] = review
    result = run.evaluate.score(cid, folder / 'final.patch', evidence)
    output = run.score_path(folder)
    if output.exists():
        assert run.read(output) == result
    else:
        run.evaluate.write_new(output, result)
    return {'case': cid, 'arm': arm, 'task_completed': result['task_completed'],
            'status': result['status'], 'execution_contract_status': result['execution_contract_status'],
            'failed_checks': result['failed_checks']}


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['export', 'score'])
    parser.add_argument('--cases', nargs='*')
    args = parser.parse_args()
    plan = run.initialize()
    for cid in args.cases or plan['cases']:
        for arm in plan['new_arms']:
            result = export(cid, arm) if args.action == 'export' else score(cid, arm)
            if result is not None:
                run.emit(str(result) if isinstance(result, Path) else result)
