import json
import sys
from pathlib import Path


def load_templates():
    return json.loads((Path.cwd() / "templates.json").read_text(encoding="utf-8"))


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2 or args[0] != "greet":
        raise SystemExit("usage: note_cli.py greet NAME")
    print(load_templates()["greet"].format(name=args[1]))


if __name__ == "__main__":
    main()
