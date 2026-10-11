"""Command-line entry point: write a sunburst page for a saved scene table."""

from __future__ import annotations

import sys

from flower.chart import render_cli


def main(argv: list[str] | None = None) -> int:
    """Render a scene table as a sunburst page (timeline and scenes table too)."""
    return render_cli(
        argv, "sunburst", "sunburst", "-sunburst", "Render a scene table as a sunburst chart (HTML)."
    )


if __name__ == "__main__":
    sys.exit(main())
