"""Check local README links independently of runtime behavior tests."""
from pathlib import Path
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def main():
    missing = []
    for name in ("README.md", "README.zh-TW.md"):
        document = ROOT / name
        for target in re.findall(r"\[[^]]*\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            local = unquote(target.split("#", 1)[0])
            if not (document.parent / local).is_file():
                missing.append(f"{name}: missing {target}")
    print("\n".join(missing) if missing else "README local links resolve")
    return int(bool(missing))


if __name__ == "__main__":
    raise SystemExit(main())
