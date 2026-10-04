"""Verify the portable six-answer export without model calls or original drives."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    trials = files = 0
    for slug in ('regexp', 'metaflow', 'tracing'):
        folder = ROOT / slug
        index = json.loads((folder / 'source-index.json').read_text(encoding='utf-8'))
        assert digest((folder / 'evidence.zip').read_bytes()) == index['evidence_sha256']
        with zipfile.ZipFile(folder / 'evidence.zip') as z:
            assert set(z.namelist()) == {r['path'] for r in index['files']}
            for entry in index['files']:
                data = z.read(entry['path'])
                assert digest(data) == entry['public_sha256'], entry['path']
                direct = folder / entry['path']
                if direct.exists():
                    assert direct.read_bytes() == data, direct
                if entry['path'].endswith('/final.patch'):
                    assert not entry['changed_for_publication']
                    assert digest(data) == entry['original_sha256']
                files += 1
            read = lambda name: json.loads(z.read(name))
            plan = read('plan.json')
            case = plan['case']
            assert plan['actor_wall_timeout_seconds'] is None
            assert plan['actor_model'] == plan['provider_model'] == 'gpt-6-astra'
            assert plan['actor_reasoning'] == plan['provider_reasoning'] == 'max'
            assert plan['provider_timeout_seconds'] == 1200 and plan['hook_timeout_seconds'] == 1320
            assert read('results-summary.json')['completed'] == 0
            assert read('code-review.json')['new_model_judge_calls'] == 0
            launches = read('actual-model-launches.json')
            assert sum(r['role'] == 'Actor' for r in launches) == 2
            for arm in plan['new_arms']:
                prefix = f'runs/{case}/{arm}/'
                result = read(prefix + 'result.json')
                patch_sha = digest(z.read(prefix + 'final.patch'))
                assert result['patch_sha256'] == read(prefix + 'fixed-checks.json')['patch_sha256'] == patch_sha
                assert read(prefix + 'execution-review.json')['patch_sha256'] == patch_sha
                assert read(prefix + 'launch.json')['timeout_seconds'] is None
                # Original audit hashes intentionally refer to unredacted source bytes.
                for source_name, key in [('actor-events.jsonl', 'transcript_sha256'), ('final.patch', 'patch_sha256')]:
                    original = next(r for r in index['files'] if r['path'] == prefix + source_name)
                    assert read(prefix + 'execution-evidence.json')[key] == original['original_sha256']
                assert not result['tests_modified']
                trials += 1
    assert trials == 6
    print(json.dumps({'verified': True, 'trials': trials, 'files': files, 'new_model_calls': 0}))


if __name__ == '__main__':
    main()
