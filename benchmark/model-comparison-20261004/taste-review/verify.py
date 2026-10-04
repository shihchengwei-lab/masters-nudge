"""Verify recorded code-review results and archived source identities without model calls.

This verifies the evidence ledger, not the correctness of semantic taste decisions.
"""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import zipfile


ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT.parent


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    review = read(ROOT / 'reassessment.json')
    initial = read(PACKAGE / 'results-summary.json')
    index = read(ROOT / 'sources-index.json')
    assert sha(PACKAGE / 'evidence.zip') == review['source_evidence_sha256']
    assert sha(PACKAGE / 'results-summary.json') == review['source_initial_summary_sha256']
    assert sha(ROOT / 'sources.zip') == review['source_archive_sha256']
    original = {(p['case'], pair, p['trial']): p['winner']
                for pair, comparison in initial['pairs'].items()
                for p in comparison['eligible_pairs']}
    completed = {(d['case'], d['arm']) for d in initial['deliveries'] if d['completed']}
    source_lookup = {entry['archive_path']: entry for entry in index}
    assert len(source_lookup) == len(index)
    seen = set()
    counts = defaultdict(lambda: {'left': 0, 'right': 0, 'tie': 0})
    old_counts = defaultdict(lambda: {'left': 0, 'right': 0, 'tie': 0})
    changed = 0
    for row in review['decisions']:
        key = row['case'], row['pair'], row['trial']
        assert key not in seen
        seen.add(key)
        assert row['original_winner'] == original[key]
        assert (row['case'], row['a']) in completed and (row['case'], row['b']) in completed
        left, right = row['pair'].split('-')
        for field, totals in (('original_winner', old_counts), ('reassessed_winner', counts)):
            winner = row[field]
            assert winner in (left, right, 'tie')
            totals[row['pair']]['tie' if winner == 'tie' else 'left' if winner == left else 'right'] += 1
        did_change = row['original_winner'] != row['reassessed_winner']
        assert did_change == row['changed']
        if did_change:
            assert row['original_winner'] != 'tie' and row['reassessed_winner'] == 'tie'
            changed += 1
        assert row['reason'] and row['sources']
        for source in row['sources']:
            assert source_lookup[source['archive_path']]['sha256'] == source['sha256']
    assert seen == set(original) and len(seen) == 71
    assert len(completed) == 69
    assert changed == review['wins_revised_to_ties'] == 6
    assert len(seen) - changed == review['preserved_original_pairs'] == 65
    assert dict(counts) == review['reassessed_counts_left_right_tie']
    assert dict(old_counts) == review['original_counts_left_right_tie']
    completion = dict(sorted(Counter(arm[0] for _, arm in completed).items()))
    assert completion == review['completion_unchanged']
    with zipfile.ZipFile(ROOT / 'sources.zip') as sources, zipfile.ZipFile(PACKAGE / 'evidence.zip') as evidence:
        assert set(sources.namelist()) == set(source_lookup)
        patches = {}
        for delivery in initial['deliveries']:
            if not delivery['completed']:
                continue
            patch = evidence.read(delivery['evidence_prefix'] + 'final.patch').decode('utf-8').replace('\r', '')
            for block in re.split(r'(?=^diff --git )', patch, flags=re.M):
                header = re.match(r'diff --git a/(.*?) b/(.*)', block)
                git_index = re.search(r'^index \w+\.\.(\w+)', block, re.M)
                if header:
                    patches[(delivery['case'], delivery['arm'], header[2])] = git_index[1] if git_index else None
        restored = 0
        for entry in index:
            raw = sources.read(entry['archive_path'])
            assert hashlib.sha256(raw).hexdigest() == entry['sha256']
            git_blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            assert git_blob == entry['git_blob']
            if entry['kind'] == 'delivery':
                key = entry['case'], entry['delivery'], entry['path']
                assert key in patches
                if patches[key]:
                    assert git_blob.startswith(patches[key]), key
                restored += 1
        assert restored == 442
    print(json.dumps({'verified': True, 'initial_pairs_preserved': len(original),
                      'final_pair_decisions': len(seen), 'retained': 65, 'revised_to_ties': changed,
                      'restored_file_versions': restored, 'archived_source_files': len(index),
                      'final_counts_left_right_tie': dict(counts),
                      'completion_unchanged': completion}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
