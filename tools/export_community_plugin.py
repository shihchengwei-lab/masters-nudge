"""Export committed plugin and existing tests for the Community Plugins layout.

Only the plugin, test sources and a source receipt are exported. Local session
logs, credentials, benchmark trees and user settings are never included.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from masters_nudge.plugin_inventory import package_files


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def export(output):
    output = output.resolve()
    if output == ROOT or output.is_relative_to(ROOT):
        raise ValueError('Export to a separate checkout or staging directory')
    # Publish committed bytes: Git checkout newline conversions cannot change receipts.
    commit = git('rev-parse', 'HEAD').decode().strip()
    paths = [f'plugins/masters-nudge/{name}' for name in package_files()]
    tests = git('ls-files', 'tests/spec').decode().splitlines()
    tests = [name for name in tests if name.endswith('.py')]
    dirty = git('status', '--porcelain', '--', *paths, 'tests/spec')
    if dirty:
        raise ValueError('Commit the plugin and test sources before exporting')
    receipt = {'repository': 'https://github.com/shihchengwei-lab/masters-nudge',
               'commit': commit, 'method': 'Exact committed plugin/test blobs; no private data or model calls.',
               'files': {}}
    for source in paths + tests:
        destination = source if source in paths else 'tests/masters-nudge/support/upstream-tests/' + source.removeprefix('tests/')
        raw = git('show', f'{commit}:{source}')
        target = output / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        receipt['files'][destination] = {'source': source, 'sha256': hashlib.sha256(raw).hexdigest()}
    target = output / 'tests/masters-nudge/source-receipt.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'Exported {len(receipt["files"])} committed files from {commit}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    export(parser.parse_args().output)
