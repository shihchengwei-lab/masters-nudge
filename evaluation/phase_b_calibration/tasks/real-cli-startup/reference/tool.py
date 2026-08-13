import argparse


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--details")
    args = parser.parse_args(argv)
    if args.version:
        print("tool 1.0")
        return
    if args.details:
        from catalog import lookup

        print(f"{args.details}:{lookup(args.details)}")


if __name__ == "__main__":
    main()
