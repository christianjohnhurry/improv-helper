"""Command-line entry point: write a flower chart page for a saved scene table."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from flower.page import show_page
from flower.scene_table import SceneTable, ValidationError


def render_cli(argv: list[str] | None, prog: str, view: str, suffix: str, what: str) -> int:
    """Render a scene table JSON file to a standalone HTML page opened on one view.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).
        prog: Program name for --help.
        view: The view open on load ('timeline' or 'sunburst').
        suffix: Appended to the table's stem for the default output name.
        what: Description for --help.

    Returns:
        Process exit code: 0 on success, 1 if the table could not be read or analysed.
    """
    parser = argparse.ArgumentParser(prog=prog, description=what)
    parser.add_argument("table", type=Path, help="scene table JSON file")
    parser.add_argument(
        "-o", "--output", type=Path,
        help=f"output HTML file (default: <table>{suffix}.html next to the table)",
    )
    args = parser.parse_args(argv)

    try:
        table = SceneTable.load_json(args.table)
        html = show_page(table, view, args.table.stem)
    except (OSError, json.JSONDecodeError, ValidationError, TypeError) as e:
        print(f"error: cannot render {args.table}: {e}", file=sys.stderr)
        return 1

    output = args.output or args.table.with_name(f"{args.table.stem}{suffix}.html")
    output.write_text(html, encoding="utf-8")
    print(output)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Render a scene table as a timeline page (stats tiles, sunburst and scenes table too)."""
    return render_cli(argv, "chart", "timeline", "", "Render a scene table as a timeline chart (HTML).")


if __name__ == "__main__":
    sys.exit(main())
