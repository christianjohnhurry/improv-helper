"""Sunburst chart: a time-proportional view of a show's structure, with a stats card."""

from __future__ import annotations

import plotly.graph_objects as go

from flower.analysis import SceneNode, ShowAnalysis, analyse
from flower.scene_table import SceneTable, format_timestamp

ROOT_ID = "show"
NEUTRAL_COLOR = "#cccccc"  # Opening and base scenes
TAG_COLORS = {"single": "#8ecae6", "double": "#ffb703"}
LEGEND = [("Opening / base", NEUTRAL_COLOR), *((t.capitalize(), c) for t, c in TAG_COLORS.items())]
SUNBURST_DOMAIN = [0.0, 0.68]
CARD_X = 0.72


def node_id(node: SceneNode) -> str:
    return f"s{node.index}"


def _kind(node: SceneNode, analysis: ShowAnalysis) -> str:
    """Tag type label for hover: the tag, or 'opening' / 'base'."""
    if node is analysis.opening:
        return "opening"
    return node.scene.tag_type or "base"


def sunburst_rows(analysis: ShowAnalysis, title: str) -> list[dict]:
    """Flatten the analysis into one dict per sunburst sector, root first.

    Args:
        analysis: The show analysis.
        title: The show title, used for the centre.

    Returns:
        Rows with id, parent, label, value (branch length), start (seconds from
        the Opening), own length, kind and colour. The end marker is not included.
    """
    origin = analysis.opening.scene.timestamp
    rows = [
        dict(
            id=ROOT_ID, parent="", label=title, value=analysis.stats.total_time,
            start=0, own=0, kind="show", color=NEUTRAL_COLOR,
        )
    ]
    nodes = [analysis.opening] + [n for r in analysis.runs for n in r.scenes]
    for node in sorted(nodes, key=lambda n: n.index):
        parent = node_id(node.parent) if node.parent else ROOT_ID
        kind = _kind(node, analysis)
        rows.append(
            dict(
                id=node_id(node), parent=parent, label=node.scene.description,
                value=node.branch_length, start=node.scene.timestamp - origin,
                own=node.length, kind=kind, color=TAG_COLORS.get(kind, NEUTRAL_COLOR),
            )
        )
    return rows


def stats_card_text(analysis: ShowAnalysis) -> str:
    """HTML text for the stats card."""
    s = analysis.stats
    longest = s.longest_scene
    longest_text = (
        f"{format_timestamp(longest.length)} ({longest.scene.description})" if longest else "-"
    )
    lines = [
        "<b>Show stats</b>",
        f"Total time: {format_timestamp(s.total_time)}",
        f"Runs: {s.run_count}",
        f"Max depth: {s.max_depth}",
        f"At base: {s.base_percent:.1f}%",
        f"Mean scene: {format_timestamp(round(s.mean_scene_length))}",
        f"Longest scene: {longest_text}",
        f"Single tags: {s.single_tags}",
        f"Double tags: {s.double_tags}",
    ]
    return "<br>".join(lines)


def sunburst_chart(table: SceneTable) -> go.Figure:
    """Render a scene table as a time-proportional sunburst with a stats card.

    The centre is the show title. Ring 1 is the Opening and each base visit in
    show order; each run's scenes grow out of its base visit. Arc angle is
    whole-branch time. The end-of-show marker is not drawn.

    Args:
        table: The scene table, with the end-of-show marker as its last row.

    Returns:
        A Plotly figure.

    Raises:
        ValidationError: If the table cannot be analysed.
    """
    analysis = analyse(table)
    title = table.metadata.title or "Show"
    rows = sunburst_rows(analysis, title)

    fig = go.Figure(
        go.Sunburst(
            ids=[r["id"] for r in rows],
            parents=[r["parent"] for r in rows],
            labels=[r["label"] for r in rows],
            values=[r["value"] for r in rows],
            branchvalues="total",
            marker=dict(colors=[r["color"] for r in rows]),
            customdata=[
                [format_timestamp(r["start"]), format_timestamp(r["own"]),
                 format_timestamp(r["value"]), r["kind"]]
                for r in rows
            ],
            hovertemplate=(
                "<b>%{label}</b><br>Start: %{customdata[0]}<br>Own length: %{customdata[1]}"
                "<br>Branch length: %{customdata[2]}<br>Tag type: %{customdata[3]}"
                "<extra></extra>"
            ),
            sort=False,
            rotation=0,
            domain=dict(x=SUNBURST_DOMAIN),
        )
    )
    # Sunbursts have no legend, so add empty scatter traces to carry the entries.
    for name, color in LEGEND:
        fig.add_trace(
            go.Scatter(
                x=[None], y=[None], mode="markers", name=name,
                marker=dict(color=color, size=12, symbol="square"),
            )
        )
    fig.add_annotation(
        text=stats_card_text(analysis), xref="paper", yref="paper", x=CARD_X, y=0.5,
        xanchor="left", yanchor="middle", align="left", showarrow=False,
        bordercolor="#999999", borderwidth=1, borderpad=10, bgcolor="#fafafa",
    )
    fig.update_layout(
        title=title,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        legend=dict(x=CARD_X, y=0.05, xanchor="left", yanchor="bottom"),
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig
