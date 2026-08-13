#!/bin/sh

for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 \
    && "$candidate" -c 'import sys; raise SystemExit(not (sys.version_info.major == 3 and sys.version_info.minor in range(10, 100)))' \
      >/dev/null 2>&1; then
    exec "$candidate" "$@"
  fi
done

echo "masters-nudge: Python 3.10+ not found" >&2
exit 0
