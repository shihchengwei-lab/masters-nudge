"""Preserve the original callers the task excludes from this change.

Read delivered source through a temporary Git index because the runtime suite
replaces test files. A Go parser distinguishes calls from comments and strings.
These are all original callers outside the exempt wiring and definitions,
verified against the pinned base, including the owning Store test package.
"""
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import tempfile

CALLERS = {
    'internal/server/middleware/grpc/middleware_test.go': ['CacheUnaryInterceptor'],
    'internal/storage/cache/cache_test.go': ['set', 'get'],
}


def inspect_delivery(patch):
    if not patch.exists() or not patch.stat().st_size:
        return []
    changed = subprocess.check_output(['git', 'apply', '--numstat', str(patch)], text=True).splitlines()
    paths = {line.split('\t')[-1] for line in changed}
    selected = paths & CALLERS.keys()
    if not selected:
        return []
    with tempfile.TemporaryDirectory(prefix='contract-scope-') as temp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp)/'index'), GOFLAGS='')
        subprocess.run(['git', 'read-tree', 'HEAD'], env=env, check=True, capture_output=True)
        subprocess.run(['git', 'apply', '--cached', '--whitespace=nowarn', str(patch)], env=env, check=True, capture_output=True)
        documents = []
        for path in sorted(selected):
            before = subprocess.check_output(['git', 'show', 'HEAD:'+path], env=env, text=True)
            after = subprocess.run(['git', 'show', ':'+path], env=env, capture_output=True, text=True)
            documents.append({'path': path, 'before': before, 'after': after.stdout, 'names': CALLERS[path]})
        parser = Path(temp)/'scope_calls.go'
        parser.write_bytes(Path(__file__).with_name('scope_calls.go.txt').read_bytes())
        proc = subprocess.run(['go', 'run', str(parser)],
                              input=json.dumps(documents), text=True, capture_output=True, env=env, check=True)
        comparisons = json.loads(proc.stdout)
    return [row['path'] for row in comparisons
            if Counter(row['before'] or []) - Counter(row['after'] or [])]


if __name__ == '__main__':
    violations = inspect_delivery(Path('/tmp/delivery.patch'))
    print('PROBE_RESULT '+json.dumps({'passed': not violations, 'compensating_callsite_edits': violations}))
