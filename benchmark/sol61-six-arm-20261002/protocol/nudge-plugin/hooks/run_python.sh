#!/bin/sh

export PYTHONIOENCODING=utf-8

for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 \
    && "$candidate" -c 'import sys; raise SystemExit(not (sys.version_info.major == 3 and sys.version_info.minor in range(10, 100)))' \
      >/dev/null 2>&1; then
    "$candidate" "$@"
    exit $?
  fi
done

echo "masters-nudge: Python 3.10+ not found" >&2
printf '%s\n' '{"systemMessage":"\u672c\u8f2a\u53cd\u994b\u672a\u57f7\u884c (Python 3.10+ not found)"}'
if [ "$MASTERS_NUDGE_TEST_MODE" = "1" ]; then
  exit 1
fi
exit 0
