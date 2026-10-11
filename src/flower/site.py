"""Command-line entry point: build the multi-show embed page from a directory of scene tables."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from flower.page import site_page


def main(argv: list[str] | None = None) -> int:
    """Write one HTML page with a picker for every scene table JSON in a directory.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Process exit code: 0 on success, 1 if no valid scene tables were found.
    """
    parser = argparse.ArgumentParser(
        prog="site", description="Build the multi-show chart page from a directory of scene tables."
    )
    parser.add_argument("data_dir", type=Path, nargs="?", default=Path("data"),
                        help="directory of scene table JSON files (default: data)")
    parser.add_argument("-o", "--output", type=Path,
                        help="output HTML file (default: <data_dir>/scamps-shows.html)")
    args = parser.parse_args(argv)

    html, names = site_page(args.data_dir)
    if not names:
        print(f"error: no scene tables found in {args.data_dir}", file=sys.stderr)
        return 1
    output = args.output or args.data_dir / "scamps-shows.html"
    output.write_text(html, encoding="utf-8")
    print(f"{output} ({len(html) // 1024} KB, {len(names)} shows: {', '.join(names)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
