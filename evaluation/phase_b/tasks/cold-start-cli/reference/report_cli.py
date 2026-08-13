import sys


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["--version"]:
        print("report-cli 1.0")
        return 0
    if len(args) == 2 and args[0] == "--details":
        from lookup import LOOKUP

        name = args[1]
        print(f"{name}:{LOOKUP[name]}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
