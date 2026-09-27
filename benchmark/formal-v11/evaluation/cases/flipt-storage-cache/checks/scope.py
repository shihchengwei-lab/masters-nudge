"""The task explicitly forbids compensating edits to old call sites.

Inspect the original delivery, not the evaluator's updated test files. This
does not restrict unrelated filenames or require a particular wiring shape.
"""
import json
from pathlib import Path
import re

text=Path('/tmp/delivery.patch').read_text() if Path('/tmp/delivery.patch').exists() else ''
violations=[]
for block in re.split(r'(?=^diff --git )',text,flags=re.M):
    m=re.match(r'diff --git a/(.*?) b/',block)
    if not m:continue
    name=m.group(1)
    if name in ('internal/cmd/grpc.go','internal/server/middleware/grpc/middleware.go','internal/storage/cache/cache.go'):
        continue
    removed='\n'.join(line[1:] for line in block.splitlines() if line.startswith('-') and not line.startswith('---'))
    added='\n'.join(line[1:] for line in block.splitlines() if line.startswith('+') and not line.startswith('+++'))
    renamed_interceptor='CacheUnaryInterceptor(' in removed and 'EvaluationCacheUnaryInterceptor(' in added
    renamed_helper=bool(re.search(r'\.\s*(set|get)\(',removed) and re.search(r'\.\s*(setJSON|getJSON|setProto|getProto)\(',added))
    if renamed_interceptor or renamed_helper:violations.append(name)
print('PROBE_RESULT '+json.dumps({'passed':not violations,'compensating_callsite_edits':violations}))
