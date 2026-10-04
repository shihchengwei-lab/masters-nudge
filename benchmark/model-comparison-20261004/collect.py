"""Bundle immutable local experiment records; no models or tests are run."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile
import argparse

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
STUDIES = {
    'A': 'sol61-ab-12case-20260930',
    'B': 'sol61-b-finalized-12case-20261001',
    'C': 'sol61-c-xhigh-direct-12case-20261001',
    'D': 'sol61-astra-provider-12case-20261001-desktop',
    'E': 'sol61-xhigh-astra-provider-12case-20261002',
    'F': 'sol61-f-xhigh-sol-provider-12case-20261002',
}
DIAGNOSTICS = {
    'D_flipt': ('D', 'diagnostics/rollout-shape'),
    'D_clap': ('D', 'diagnostics/clap-occurrences-valid'),
    'C_flipt': ('all', 'diagnostics/flipt-segments'),
    'C_clap': ('all', 'diagnostics/clap-2297'),
    'E_flipt': ('E', 'diagnostics/flipt-segments'),
    'E_clap': ('E', 'diagnostics/clap-2297'),
    'F_flipt': ('F', 'diagnostics/flipt-segments'),
    'F_clap': ('F', 'diagnostics/clap-2297'),
}


def add_i(source_root):
    """Append a completed study while preserving every existing source byte."""
    collection = read(ROOT / 'collection.json')
    assert 'I' not in collection['studies'], 'I is already collected'
    index = read(ROOT / 'source-index.json')
    old_count = len(index)
    destination = ROOT / 'evidence.zip'
    assert sha(destination) == collection['evidence_zip_sha256']
    root = Path(source_root).resolve()
    plan = read(root / 'plan.json')
    assert read(root / 'pipeline-status.json')['status'] == 'complete'
    assert read(root / 'final-integrity.json')['new_I_deliveries'] == 24
    cases = list(read(ROOT / 'data/plans/F.json')['cases'])
    assert list(plan['cases']) == cases
    receipt = {'previous_evidence_sha256': sha(destination),
               'previous_source_index_sha256': sha(ROOT / 'source-index.json'),
               'previous_source_files': old_count, 'added_arm': 'I',
               'source_study': str(root), 'new_actors': 0, 'new_judges': 0}

    def files(folder):
        return sorted(p for p in folder.rglob('*') if p.is_file()
                      and '__pycache__' not in p.parts and p.suffix != '.pyc')

    def record(source, target, location):
        index.append({'source': str(source), 'sha256': sha(source), location: target})

    def copy(source, target):
        target_path = ROOT / target
        assert not target_path.exists(), target
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target_path)
        assert sha(source) == sha(target_path)
        record(source, target, 'bundle_path')

    copy(root / 'plan.json', 'data/plans/I.json')
    copy(root / 'results-summary.json', 'data/summaries/I.json')
    for name in ('final-integrity.json', 'grading-protocol.json', 'pipeline-status.json',
                 'restoration-confirmed.json', 'execution-summary.json', 'reference-manifest.json',
                 'infrastructure-recovery.json', 'timeout-recovery.json', 'timeout-cleanup.json',
                 'verification-recovery.json', 'continuation-plan.json',
                 'continuation-preserved-results.json', 'grading-resume-preserved-results.json',
                 'actual-launch-observation.json', 'actual-provider-launch.json'):
        copy(root / name, 'data/provenance/I/' + name)
    manifest = root / 'harness-source-manifest.json'
    copy(manifest, 'harness/I/source-manifest.json')
    for entry in read(manifest):
        source = root / entry['snapshot']
        assert sha(source) == entry['sha256']
        copy(source, 'harness/I/' + entry['snapshot'].removeprefix('harness-sources/'))
    for relative, expected in plan['package_hashes'].items():
        source = root / 'frozen-plugin' / relative
        assert sha(source) == expected
        copy(source, 'protocol/nudge-plugin-I/' + relative)
    for suffix, folder in (('flipt', 'flipt-segments'), ('clap', 'clap-2297')):
        copy(root / 'diagnostics' / folder / 'comparison.json', f'data/diagnostics/I_{suffix}.json')
    indexed = {entry['source'] for entry in index}
    for source, expected in plan['reference_manifest'].items():
        if source not in indexed:
            path = Path(source)
            assert sha(path) == expected
            copy(path, 'data/provenance/I/references/' + path.parent.name + '/' + path.name)

    temporary = ROOT / 'evidence.extending.zip'
    shutil.copyfile(destination, temporary)
    with zipfile.ZipFile(temporary, 'a', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        existing = set(archive.namelist())

        def pack(source, target):
            assert target not in existing, target
            archive.write(source, target)
            existing.add(target)
            record(source, target, 'zip_member')

        def pack_folder(folder, prefix):
            assert folder.is_dir(), str(folder)
            for source in files(folder):
                pack(source, prefix + '/' + source.relative_to(folder).as_posix())

        for cid in cases:
            for trial in (1, 2):
                slot = 'I' + str(trial)
                folder = root / 'runs' / cid / slot
                assert all((folder / n).is_file() for n in
                           ('result.json', 'score-v3.json', 'final.patch', 'launch.json', 'prompt.txt'))
                pack_folder(folder, f'runs/I/{cid}/{slot}')
                pack_folder(root / 'evaluation-v3' / cid / slot, f'evaluation/I/{cid}/{slot}')
        pack_folder(root / 'blind-v3/judges', 'judges/I')
        pack_folder(root / 'execution-judges', 'execution-judges/I')
        pack_folder(root / 'diagnostics', 'diagnostics/I')
        pack_folder(root / 'harness-amendments', 'infrastructure/I/harness-amendments')
        pack_folder(root / 'infrastructure-attempts', 'infrastructure/I/attempts')
        pack_folder(root / 'errors', 'infrastructure/I/errors')
        for source in sorted(root.glob('*.txt')):
            pack(source, 'infrastructure/I/logs/' + source.name)
        for name in ('REPORT.zh-TW.md', 'MATERIALS.zh-TW.md', 'blind-contract-concerns.json'):
            pack(root / name, 'study/I/' + name)
    with zipfile.ZipFile(temporary) as archive:
        for entry in index:
            actual = hashlib.sha256(archive.read(entry['zip_member'])).hexdigest() if 'zip_member' in entry else sha(ROOT / entry['bundle_path'])
            assert actual == entry['sha256'], entry
    assert all(sha(Path(e['source'])) == e['sha256'] for e in index[old_count:])
    temporary.replace(destination)
    receipt['all_previous_source_bytes_preserved'] = True
    receipt['added_source_files'] = len(index) - old_count
    save(ROOT / 'data/provenance/I/collection-extension.json', receipt)
    save(ROOT / 'source-index.json', index)
    collection['studies']['I'] = root.name
    collection.update(records=168, original_sources_unchanged=len(index),
                      evidence_zip_sha256=sha(destination), evidence_zip_bytes=destination.stat().st_size,
                      note='A available source collected at closure; B-F and I verified against study snapshots. I appended with all existing source bytes preserved.')
    save(ROOT / 'collection.json', collection)
    print(json.dumps(receipt, ensure_ascii=False))


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    destination = ROOT / 'evidence.zip'
    if destination.exists():
        raise RuntimeError('Evidence already sealed; use aggregate.py --verify, not recollection.')
    roots = {arm: BASE / name for arm, name in STUDIES.items()}
    roots['all'] = BASE / 'sol61-all-arms-benefit-20261002'
    plans = {arm: read(roots[arm] / 'plan.json') for arm in STUDIES}
    cases = list(plans['F']['cases'])
    assert len(cases) == 12
    assert all(list(plan['cases']) == cases for plan in plans.values())
    assert len({plan['evaluator_sha256'] for plan in plans.values()}) == 1
    assert len({plans[arm]['prompt_semantic_sha256'] for arm in 'BDEF'}) == 1
    for cid in cases:
        assert len({plan['cases'][cid]['base_commit'] for plan in plans.values()}) == 1
    provenance = []

    def record(source, target, location):
        provenance.append({'source': str(source), 'sha256': sha(source), location: target})

    def copy(source, target):
        target_path = ROOT / target
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target_path)
        assert sha(source) == sha(target_path)
        record(source, target, 'bundle_path')

    def files(folder):
        return sorted(p for p in folder.rglob('*') if p.is_file()
                      and '__pycache__' not in p.parts and p.suffix != '.pyc')

    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        def pack(source, target):
            archive.write(source, target)
            record(source, target, 'zip_member')

        def pack_folder(folder, prefix):
            for source in files(folder):
                pack(source, prefix + '/' + source.relative_to(folder).as_posix())

        for arm in STUDIES:
            root = roots[arm]
            copy(root / 'plan.json', f'data/plans/{arm}.json')
            if arm != 'A':
                copy(root / 'results-summary.json', f'data/summaries/{arm}.json')
            for name in ('final-integrity.json', 'grading-protocol.json', 'pipeline-status.json',
                         'restoration-confirmed.json', 'diagnostic-integrity.json',
                         'binary-recovery.json', 'fixture-recovery-complete.json',
                         'defender-fixture-events.json'):
                if (root / name).exists():
                    copy(root / name, f'data/provenance/{arm}/{name}')
            manifest = root / 'harness-source-manifest.json'
            if manifest.exists():
                copy(manifest, f'harness/{arm}/source-manifest.json')
                for entry in read(manifest):
                    source = root / entry['snapshot']
                    assert sha(source) == entry['sha256'], str(source)
                    copy(source, f'harness/{arm}/' + entry['snapshot'].removeprefix('harness-sources/'))
            else:
                # A had no per-study source-snapshot directory. Preserve its available
                # source now; actual launch/events remain the evidence of execution.
                for source in sorted(root.glob('*.py')):
                    copy(source, 'harness/A/collected-at-close/' + source.name)
            for cid in cases:
                for trial in (1, 2):
                    slot = arm + str(trial)
                    folder = root / 'runs' / cid / slot
                    required = ('result.json', 'score-v3.json', 'final.patch', 'actor-events.jsonl',
                                'execution-review.json', 'execution-evidence.json', 'prompt.txt', 'launch.json')
                    assert all((folder / name).is_file() for name in required), str(folder)
                    # Entire run directories: original outputs, Provider packets, trace
                    # and code change; no transient repository or dependency tree.
                    pack_folder(folder, f'runs/{arm}/{cid}/{slot}')
                    evaluation = root / 'evaluation-v3' / cid / slot
                    assert evaluation.is_dir(), str(evaluation)
                    pack_folder(evaluation, f'evaluation/{arm}/{cid}/{slot}')
            if arm != 'A':
                pack_folder(root / 'blind-v3' / 'judges', f'judges/{arm}')
            for source in files(root / 'execution-judges'):
                relative = source.relative_to(root / 'execution-judges')
                prefix = ('history/A-study-earlier-B-execution-judges'
                          if arm == 'A' and any(part in ('B1', 'B2') for part in relative.parts)
                          else f'execution-judges/{arm}')
                pack(source, prefix + '/' + relative.as_posix())
            for name in ('infrastructure-recovery', 'errors'):
                if (root / name).exists():
                    pack_folder(root / name, f'infrastructure/{arm}/{name}')
        for name, (arm, directory) in DIAGNOSTICS.items():
            folder = roots[arm] / directory
            copy(folder / 'comparison.json', f'data/diagnostics/{name}.json')
            pack_folder(folder, 'diagnostics/' + name)
        pack_folder(roots['D'] / 'diagnostics/clap-occurrences', 'diagnostics/D_clap_invalid_control')
        startup = BASE / 'sol61-astra-provider-12case-20261001'
        for name in ('STARTUP-FAILURE.json', 'STARTUP-FAILURE.zh-TW.md'):
            copy(startup / name, 'data/provenance/D/' + name)

    frozen = roots['F'] / 'frozen-evaluation'
    for source in files(frozen):
        copy(source, 'protocol/evaluation/' + source.relative_to(frozen).as_posix())
    plugin = roots['F'] / 'frozen-plugin'
    for relative, expected in plans['F']['package_hashes'].items():
        source = plugin / relative
        assert sha(source) == expected
        copy(source, 'protocol/nudge-plugin/' + relative)
    copy(roots['all'] / 'results-summary.json', 'data/prior-five-arm-summary.json')
    assert all(sha(Path(entry['source'])) == entry['sha256'] for entry in provenance)
    save(ROOT / 'source-index.json', provenance)
    save(ROOT / 'collection.json', {
        'studies': STUDIES, 'records': 144, 'case_count': 12,
        'new_actors': 0, 'new_judges': 0, 'original_sources_unchanged': len(provenance),
        'evidence_zip_sha256': sha(destination), 'evidence_zip_bytes': destination.stat().st_size,
        'note': 'A available harness source collected at closure; B-F sources verified against existing study snapshots.',
    })
    print(json.dumps({'source_files': len(provenance), 'evidence_MiB': round(destination.stat().st_size / 2**20, 1)}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--add-i', metavar='COMPLETED_STUDY_ROOT')
    args = parser.parse_args()
    add_i(args.add_i) if args.add_i else main()
