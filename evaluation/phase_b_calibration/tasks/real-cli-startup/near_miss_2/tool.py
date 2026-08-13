import argparse

import catalog


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--details")
    args = parser.parse_args(argv)
    if args.version:
        print("tool 1.0")
        return
    if args.details:
        print(f"{args.details}:{catalog.lookup(args.details)}")


if __name__ == "__main__":
    main()
