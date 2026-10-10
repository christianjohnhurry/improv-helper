"""Flower chart: render a scene table as a Plotly figure of the set's structure."""

from __future__ import annotations

import numpy as np
import plotly.colors as pc
import plotly.graph_objects as go

from flower.scene_table import SceneTable, format_timestamp

PASTEL_COLORS = pc.qualitative.Pastel1
LINE_WIDTH = 4
RUN_UP_FRACTION = 0.2  # share of a transition's duration spent on the arc
ARC_HEIGHT = 0.7  # bezier control point offset, in levels
ARC_STEPS = 40


def level_color(level: int) -> str:
    """Return the pastel colour for a level, cycling if there are more levels than colours."""
    return PASTEL_COLORS[level % len(PASTEL_COLORS)]


def bezier_arc(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    arc_height: float = ARC_HEIGHT,
    steps: int = ARC_STEPS,
) -> tuple[np.ndarray, np.ndarray]:
    """Sample a quadratic bezier curve between two points.

    The control point sits at the midpoint, offset by arc_height in the
    direction of travel (up when y1 > y0, otherwise down).

    Args:
        x0: Start x.
        y0: Start y.
        x1: End x.
        y1: End y.
        arc_height: Vertical offset of the control point.
        steps: Number of sample points, including both ends.

    Returns:
        Arrays of x and y values along the curve.
    """
    xm = (x0 + x1) / 2
    ym = (y0 + y1) / 2 + arc_height * (1 if y1 > y0 else -1)
    t = np.linspace(0, 1, steps)
    x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * xm + t**2 * x1
    y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * ym + t**2 * y1
    return x, y


def _line(x: list[float], y: list[float], level: int) -> go.Scatter:
    return go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(color=level_color(level), width=LINE_WIDTH),
        hoverinfo="none",
        showlegend=False,
    )


def flower_chart(table: SceneTable) -> go.Figure:
    """Build the flower chart for a scene table.

    Time (seconds, labelled MM:SS) runs along x and scene level along y. Each
    scene is drawn from its start to the next scene's start: a flat line at its
    level, finishing with a bezier arc when the next scene is at a different
    level. Lines are coloured by the level they leave, and each scene's name is
    annotated where it starts.

    Args:
        table: The scene table to draw.

    Returns:
        The Plotly figure (empty apart from the title if the table has no scenes).

    Raises:
        ValidationError: If the table is invalid.
    """
    table.validate()
    scenes = table.scenes
    fig = go.Figure()

    for current, following in zip(scenes, scenes[1:]):
        x0, x1 = current.timestamp, following.timestamp
        y0, y1 = current.level, following.level
        if y0 == y1:
            fig.add_trace(_line([x0, x1], [y0, y1], y0))
            continue
        arc_start = x1 - (x1 - x0) * RUN_UP_FRACTION
        fig.add_trace(_line([x0, arc_start], [y0, y0], y0))
        arc_x, arc_y = bezier_arc(arc_start, y0, x1, y1)
        fig.add_trace(_line(arc_x.tolist(), arc_y.tolist(), y0))

    # Annotations are added after the lines so they sit on top.
    for scene in scenes:
        fig.add_annotation(
            x=scene.timestamp,
            y=scene.level,
            xref="x",
            yref="y",
            text=scene.description,
            showarrow=False,
            font=dict(color="black", size=14),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(0,0,0,0)",
            yshift=10,
        )

    ticks = _time_ticks(scenes[-1].timestamp) if scenes else []
    meta = table.metadata
    title = " - ".join(part for part in (meta.title, meta.date) if part)
    fig.update_layout(
        title=title,
        xaxis=dict(
            title="Time (MM:SS)",
            tickmode="array",
            tickvals=ticks,
            ticktext=[format_timestamp(t) for t in ticks],
        ),
        yaxis=dict(title="Level", dtick=1),
        showlegend=False,
        plot_bgcolor="white",
    )
    return fig


def _time_ticks(end: int, target_count: int = 10) -> list[int]:
    """Choose evenly spaced tick times (seconds) on round intervals up to end."""
    steps = (5, 10, 15, 30, 60, 120, 300, 600, 900, 1800, 3600)
    step = next((s for s in steps if end / s <= target_count), steps[-1])
    return list(range(0, end + step, step))
