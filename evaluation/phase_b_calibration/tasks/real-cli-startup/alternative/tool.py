import sys


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["--version"]:
        print("tool 1.0")
        return
    if len(args) == 2 and args[0] == "--details":
        from catalog import lookup

        print(f"{args[1]}:{lookup(args[1])}")
        return
    raise SystemExit("usage: tool.py [--version | --details NAME]")


if __name__ == "__main__":
    main()
