"""Command-line interface for scratch2py."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .emit import emit_project
from .parser import parse_project
from .unpack import unpack


def convert(sb3_path: str, out_dir: str) -> int:
    sb3 = Path(sb3_path)
    if not sb3.exists():
        print(f"error: no such file: {sb3}", file=sys.stderr)
        return 1

    unpacked = unpack(sb3)
    project = parse_project(unpacked.project_json)
    report = emit_project(project, unpacked, out_dir)

    print(f"Converted {sb3.name} -> {out_dir}")
    print(f"  targets: {len(project.targets)} "
          f"(1 stage, {len(project.sprites)} sprites)")
    print(report.summary())
    print(f"\nRun it with:\n  cd {out_dir}\n  pip install -r requirements.txt\n  python main.py")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scratch2py",
        description="Convert a Scratch .sb3 project into a runnable pygame Python project.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    convert_parser = sub.add_parser("convert", help="Convert a .sb3 file to a Python project.")
    convert_parser.add_argument("sb3", help="Path to the input .sb3 file.")
    convert_parser.add_argument(
        "-o", "--output", default="out", help="Output directory (default: ./out)."
    )

    args = parser.parse_args(argv)
    if args.command == "convert":
        return convert(args.sb3, args.output)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
