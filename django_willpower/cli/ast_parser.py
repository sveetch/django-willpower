import argparse
import ast
import sys
from pathlib import Path


def argumentparser_init(parser_class):
    """
    Initialize Parser and define all arguments.
    """
    parser = parser_class(
        description=(
            "Open a Python module to parse it with 'ast' module and output its parsed "
            "tree. This is an experimental tool that currently add no feature to the "
            "Willpower command."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "source",
        metavar="<source_filepath>",
        type=Path,
        help=(
            "Path to a Python module file."
        ),
    )
    parser.add_argument(
        "--destination",
        type=Path,
        metavar="<destination_path>",
        help=(
            "An existing path of a directory where to write a "
            "'[SOURCE FILENAME].ast.py' file containing the parsed tree "
            "representation. If destination is not given, the parsed tree is printed "
            "to standard output."
        )
    )

    return parser


def main(argv=sys.argv):
    """
    Command interface
    """
    print("🚀 Starting")
    parser = argumentparser_init(argparse.ArgumentParser)
    args = parser.parse_args(argv[1:])

    # Check destination if given
    if args.destination and not args.destination.exists():
        print("🚨 Given destination directory does not exist: {}".format(
            args.destination
        ))
        print("💥 Aborted.")
        sys.exit(1)

    # Parse code to a tree
    tree = ast.parse(args.source.read_text())
    # Dump tree
    content = ast.dump(tree, indent=4)

    # Print tree representation
    if not args.destination:
        print(content)
    else:
        destination = (
            args.destination / Path(args.source.stem + ".ast" + args.source.suffix)
        )
        destination.write_text(content)
        print("📝 Tree was written to:", destination)

    print("🎉 Done.")


if __name__ == "__main__":
    main()
