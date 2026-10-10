"""Command-line entry point: write a sunburst chart for a saved scene table."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from flower.scene_table import SceneTable, ValidationError
from flower.sunburst import sunburst_chart


def main(argv: list[str] | None = None) -> int:
    """Render a scene table JSON file to a standalone HTML sunburst.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Process exit code: 0 on success, 1 if the table could not be read or analysed.
    """
    parser = argparse.ArgumentParser(
        prog="sunburst", description="Render a scene table as a sunburst chart (HTML)."
    )
    parser.add_argument("table", type=Path, help="scene table JSON file")
    parser.add_argument(
        "-o", "--output", type=Path,
        help="output HTML file (default: <table>-sunburst.html next to the table)",
    )
    args = parser.parse_args(argv)

    try:
        table = SceneTable.load_json(args.table)
        fig = sunburst_chart(table)
    except (OSError, json.JSONDecodeError, ValidationError, TypeError) as e:
        print(f"error: cannot render {args.table}: {e}", file=sys.stderr)
        return 1

    output = args.output or args.table.with_name(f"{args.table.stem}-sunburst.html")
    fig.write_html(output)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
