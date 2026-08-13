import json
import sys
from pathlib import Path


def greeting_for(name):
    config_path = Path(__file__).with_name("defaults.json")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    return f"{config['greeting']}, {name}!"


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) == 2 and args[0] == "greet":
        print(greeting_for(args[1]))
        return 0
    print("usage: mn_cli.py greet NAME", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
