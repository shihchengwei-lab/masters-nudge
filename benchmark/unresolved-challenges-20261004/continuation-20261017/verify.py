"""Verify three informed continuations offline; no model calls or regrading."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parent
CASES = {
    'regexp': ('regexp-404', 'J2', 'actor-evaluation-1', 4, 4, 77),
    'metaflow': ('fb-metaflow-stubs', 'K1', 'actor-evaluation-1', 9, 18, 45),
    'tracing': ('tracing-1523', 'L2', 'actor-evaluation-2', 4, 10, 148),
}
TOKEN_KEYS = ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def passed_flags(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == 'passed' and isinstance(child, bool):
                yield child
            yield from passed_flags(child)
    elif isinstance(value, list):
        for child in value:
            yield from passed_flags(child)


def verify_case(slug):
    case, arm, evaluation, check_count, probe_count, reserved_count = CASES[slug]
    folder = ROOT / slug
    index = read(folder / 'source-index.json')
    assert index['case'] == case
    assert digest((folder / 'evidence.zip').read_bytes()) == index['evidence_sha256']
    entries = {r['path']: r for r in index['files']}
    assert len(entries) == len(index['files'])
    with zipfile.ZipFile(folder / 'evidence.zip') as archive:
        assert len(archive.namelist()) == len(entries)
        assert set(archive.namelist()) == set(entries)
        for name, entry in entries.items():
            data = archive.read(name)
            assert digest(data) == entry['public_sha256'], (slug, name)
            direct = folder / name
            if direct.exists():
                assert direct.read_bytes() == data, direct
            if name.endswith('.patch'):
                assert not entry['changed_for_publication'], name
                assert digest(data) == entry['original_sha256'], name
        load = lambda name: json.loads(archive.read(name))
        plan = load('plan.json')
        launch = load('run/launch.json')
        result = load('run/result.json')
        audit = load('audit-summary.json')
        evidence = load(evaluation + '/evidence.json')
        baseline = load('baseline-evaluation/evidence.json')
        patch_sha = digest(archive.read('final.patch'))
        assert patch_sha == evidence['patch_sha256'] == audit['full_patch_sha256']
        assert digest(archive.read('continuation-only.patch')) == audit['continuation_patch_sha256']
        delivery = load('delivery-integrity.json')
        if slug == 'tracing':
            originals = {r.get('original_path', name): r for name, r in entries.items()}
            for name, expected in delivery['sha256'].items():
                assert originals[name]['original_sha256'] == expected, name
            assert delivery['patch_matches_evaluated_candidate'] and delivery['all_fixed_probes_pass']
        else:
            assert delivery['final_patch_sha256'] == patch_sha
            assert delivery['continuation_patch_sha256'] == audit['continuation_patch_sha256']
            assert delivery['exact_evaluated_delivery'] and delivery['all_probe_passed_flags_true']
            assert delivery['delta_apply_check'] == 'pass'
        assert plan['base_commit'] == launch['base_commit'] == audit['base_commit']
        assert result['exit_code'] == 0
        assert result['elapsed_seconds'] == audit['actor_elapsed_seconds']
        assert not audit['existing_test_changes'] and not audit['frozen_input_changes']
        assert audit['source_head_and_status_unchanged']
        assert plan['actor_timeout_seconds'] is None and launch['timeout_seconds'] is None
        assert plan['actor_model'] == plan['provider_model'] == 'gpt-6.1-sol'
        assert plan['actor_reasoning'] == plan['provider_reasoning'] == 'xhigh'
        assert launch.get('actor_model', launch.get('model')) == 'gpt-6.1-sol'
        assert launch.get('actor_reasoning', launch.get('reasoning')) == 'xhigh'
        assert launch['provider_model'] == 'gpt-6.1-sol' and launch['provider_reasoning'] == 'xhigh'
        assert 'PROVIDER_REASONING_EFFORT = "xhigh"' in archive.read('frozen-plugin/masters_nudge/runtime.py').decode()
        models = load('actual-models.json')
        assert all(r['expected_model_present'] and r['expected_effort_present'] for r in models)
        assert all('gpt-6.1-sol' in r['command_line'] and 'xhigh' in r['command_line'] for r in models)
        assert sum(r['role'] == 'actor' for r in models) == audit['actual_actor_count'] == 1
        assert sum(r['role'] == 'provider' for r in models) == audit['actual_provider_count']

        # The original six-answer package remains the authority for the starting patch
        # and the fixed task/evaluator bytes. Publication redaction has separate hashes.
        old_folder = ROOT.parent / slug
        old_index = {r['path']: r for r in read(old_folder / 'source-index.json')['files']}
        old_patch = old_folder / 'runs' / case / arm / 'final.patch'
        assert digest(old_patch.read_bytes()) == plan['initial_patch_sha256'] == baseline['patch_sha256']
        assert archive.read(f'historical-materials/{arm}/final.patch') == old_patch.read_bytes()
        manifest = load('frozen-evaluation/manifest.json')
        for name, expected in manifest['files'].items():
            assert entries['frozen-evaluation/' + name]['original_sha256'] == expected, name
        unchanged_inputs = 0
        for name, old in old_index.items():
            if name.startswith('frozen-evaluation/'):
                assert entries[name]['original_sha256'] == old['original_sha256'], name
                unchanged_inputs += 1
        assert unchanged_inputs > 0
        assert evidence['evaluator_sha256'] == entries['frozen-evaluation/manifest.json']['original_sha256']
        assert any(name.startswith(f'frozen-evaluation/cases/{case}/upstream-licenses/') for name in entries)

        assert len(evidence['checks']) == check_count
        assert evidence['case'] == baseline['case'] == case
        assert evidence['checks'].keys() == baseline['checks'].keys()
        assert all(v == 'pass' for v in evidence['checks'].values())
        assert not evidence.get('environment_error')
        flags = []
        for log in evidence['logs']:
            name = evaluation + '/' + log['file']
            assert log['exit_code'] == 0, name
            assert entries[name]['original_sha256'] == log['sha256'], name
            for line in archive.read(name).decode('utf-8').splitlines():
                if 'PROBE_RESULT ' in line:
                    flags.extend(passed_flags(json.loads(line.split('PROBE_RESULT ', 1)[1])))
        assert len(flags) == probe_count and all(flags), (slug, flags)

        attempts = load('nudge-attempts.json')
        assert len(attempts) == audit['actual_provider_count']
        assert all(r['outcome'] in ('feedback', 'silence') for r in attempts)
        counts = {key: sum(r['outcome'] == key for r in attempts) for key in ('feedback', 'silence')}
        counts['delivered'] = sum(r['delivered'] for r in attempts)
        counts['faults'] = 0
        for row in attempts:
            assert bool(json.loads(row['detail']['raw_output'])['feedback']) == (row['outcome'] == 'feedback')
        actor_usage = {k: result['actor_usage'][k] for k in TOKEN_KEYS}
        assert actor_usage == {k: audit['actor_usage'][k] for k in TOKEN_KEYS}
        provider_usage = {k: sum(r['detail']['usage'][k] for r in attempts) for k in TOKEN_KEYS}
        combined = {k: actor_usage[k] + provider_usage[k] for k in TOKEN_KEYS}
        assert combined == audit['actor_plus_provider_usage']
        assert provider_usage == {k: audit['provider_usage'][k] for k in TOKEN_KEYS}
        combined['uncached_input_tokens'] = combined['input_tokens'] - combined['cached_input_tokens']
        if slug == 'tracing':
            tests = load('continuation-verification.json')
            for name, row in tests.items():
                if 'sha256' in row:
                    assert entries[name]['original_sha256'] == row['sha256']
            additional = {'passed': tests['full-tests-final.txt']['passed'],
                          'failed': tests['full-tests-final.txt']['failed'],
                          'ignored': tests['full-tests-final.txt']['ignored']}
            assert evidence['reserved_detail'] == {'passed': reserved_count, 'failed': 0}
        else:
            log = 'continuation-all-rules-final.log' if slug == 'regexp' else 'continuation-tests-after-1.txt'
            matches = re.findall(r'(\d+) (?:passing|passed)', archive.read(log).decode())
            assert len(matches) == 1
            additional = {'passed': int(matches[0])}
            reserved = archive.read(evaluation + '/reserved.txt').decode()
            assert re.search(rf'\b{reserved_count} (?:passing|passed)\b', reserved)
        return {
            'case': case, 'initial_arm': arm, 'base_commit': plan['base_commit'],
            'completion': 'pass', 'final_patch_sha256': patch_sha,
            'continuation_patch_sha256': audit['continuation_patch_sha256'],
            'evaluation': f'{slug}/{evaluation}/evidence.json',
            'fixed_checks': evidence['checks'], 'baseline_checks_passed': sum(v == 'pass' for v in baseline['checks'].values()),
            'fixed_check_count': check_count, 'probe_passed_flags': len(flags), 'reserved_tests_passed': reserved_count,
            'additional_test_summary': additional,
            'actor_model': plan['actor_model'], 'provider_model': plan['provider_model'],
            'actor_reasoning': plan['actor_reasoning'], 'provider_reasoning': plan['provider_reasoning'],
            'actor_timeout_seconds': None, 'actor_seconds_including_provider': audit['actor_elapsed_seconds'],
            'provider_seconds_subset': round(audit['provider_elapsed_seconds'], 3),
            'actor_plus_provider_tokens': combined, 'nudges': counts,
            'actual_actors': 1, 'actual_providers': len(attempts),
            'existing_tests_unchanged': audit.get('existing_test_count', audit.get('existing_test_file_count')),
            'historical_fixed_inputs_verified': unchanged_inputs, 'archived_files_verified': len(entries),
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-summary', action='store_true', help='Rebuild only the derived continuation summary.')
    args = parser.parse_args()
    cases = {slug: verify_case(slug) for slug in CASES}
    summary = {'date': '2026-10-17', 'scope': 'Informed continuations using historical failures and implementations; separate from original independent comparisons.',
               'cases': cases, 'completed_cases': len(cases),
               'actor_seconds_including_provider': round(sum(r['actor_seconds_including_provider'] for r in cases.values()), 3),
               'actor_plus_provider_tokens': {k: sum(r['actor_plus_provider_tokens'][k] for r in cases.values()) for k in (*TOKEN_KEYS, 'uncached_input_tokens')},
               'actual_actors': sum(r['actual_actors'] for r in cases.values()),
               'actual_providers': sum(r['actual_providers'] for r in cases.values()),
               'new_model_calls_during_verification': 0}
    target = ROOT / 'results-summary.json'
    if args.write_summary:
        target.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    else:
        assert read(target) == summary, 'Continuation summary differs from archived evidence'
    print(json.dumps({'verified': True, 'completed_cases': len(cases),
                      'archived_files': sum(r['archived_files_verified'] for r in cases.values()),
                      'new_model_calls': 0}))


if __name__ == '__main__':
    main()
