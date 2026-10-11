"""Chart pages: an embeddable HTML page (D3 timeline, sunburst and scenes table) for scene tables.

The markup, CSS and D3 code live in templates/shows_page.html; this module turns
flower.analysis output into the JSON the page draws from. One show gives a
single-show page, several give a page with a show picker.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from importlib import resources
from pathlib import Path

from flower.analysis import analyse
from flower.scene_table import SceneTable

VIEWS = ("timeline", "sunburst", "table", "compare")


def pretty(slug: str) -> str:
    """Turn a slug like 'the-scamps-show-3' into 'The Scamps Show 3'."""
    return " ".join(w.capitalize() for w in slug.replace("_", "-").split("-"))


def show_data(table: SceneTable, fallback_name: str = "") -> dict:
    """The page's JSON for one show: scenes, runs and stats.

    Args:
        table: The scene table, with the end-of-show marker as its last row.
        fallback_name: Name to use when the table has no title (e.g. the file stem).

    Returns:
        A JSON-serialisable dict; scene starts are seconds from the Opening.

    Raises:
        ValidationError: If the table cannot be analysed.
    """
    a = analyse(table)
    origin = a.opening.scene.timestamp
    run_of = {id(n): ri for ri, r in enumerate(a.runs) for n in r.scenes}
    nodes = sorted([a.opening] + [n for r in a.runs for n in r.scenes], key=lambda n: n.index)
    scenes = [
        dict(
            i=n.index, name=n.scene.description, start=n.scene.timestamp - origin,
            video=n.scene.timestamp, len=n.length, level=n.scene.level, tag=n.scene.tag_type,
            run=run_of.get(id(n)), parent=n.parent.index if n.parent else None,
            branch=n.branch_length,
        )
        for n in nodes
    ]
    runs = []
    for r in a.runs:
        first = next((n.scene.description for n in r.scenes if n.scene.level > 0), None)
        runs.append(dict(name=first or "Closing base", len=r.length, scenes=len(r.scenes)))
    s = a.stats
    longest = s.longest_scene
    return dict(
        name=pretty(table.metadata.title or fallback_name),
        date=table.metadata.date,
        video=table.metadata.video_source,
        total=s.total_time,
        maxDepth=s.max_depth,
        scenes=scenes,
        runs=runs,
        stats=dict(
            total=s.total_time, runs=s.run_count, maxDepth=s.max_depth,
            count=len(scenes) - 1,
            basePct=s.base_percent, meanScene=s.mean_scene_length,
            longestName=longest.scene.description if longest else "",
            longestLen=longest.length if longest else 0,
            single=s.single_tags, double=s.double_tags,
        ),
    )


def shows_page(shows: Iterable[dict], view: str = "timeline") -> str:
    """Render the page for show dicts from show_data, newest first.

    Args:
        shows: Show dicts from show_data.
        view: The view open on load: 'timeline', 'sunburst', 'table', or 'compare'
            (all shows side by side; each is timed from its Opening).

    Returns:
        A standalone HTML document (D3 is loaded from cdnjs).

    Raises:
        ValueError: If the view is not one of VIEWS. "compare" needs two or more shows.
    """
    if view not in VIEWS:
        raise ValueError(f"view must be one of {', '.join(VIEWS)}; got {view!r}")
    shows = list(shows)
    if view == "compare" and len(shows) < 2:
        raise ValueError("the compare view needs two or more shows")
    ordered = sorted(shows, key=lambda s: s["date"] or "", reverse=True)
    template = resources.files("flower").joinpath("templates/shows_page.html").read_text("utf-8")
    data = json.dumps(ordered).replace("</", "<\\/")
    return template.replace("__SHOWS__", data).replace("__VIEW__", json.dumps(view))


def show_page(table: SceneTable, view: str = "timeline", fallback_name: str = "") -> str:
    """Render the page for a single scene table (see shows_page)."""
    return shows_page([show_data(table, fallback_name)], view)


def site_page(data_dir: Path, view: str = "timeline") -> tuple[str, list[str]]:
    """Render the multi-show page from every scene table JSON in a directory.

    Files that are not valid scene tables are skipped.

    Args:
        data_dir: Directory of scene table JSON files.
        view: The view open on load (see shows_page).

    Returns:
        The HTML and the names of the shows included, newest first.
    """
    shows = []
    for path in sorted(data_dir.glob("*.json")):
        try:
            shows.append(show_data(SceneTable.load_json(path), path.stem))
        except (OSError, ValueError, TypeError, KeyError):
            continue
    shows.sort(key=lambda s: s["date"] or "", reverse=True)
    return shows_page(shows, view), [s["name"] for s in shows]
