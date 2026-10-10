import pytest

from flower import Scene, SceneTable, ShowMetadata, ValidationError
from flower.visualise import PASTEL_COLORS, bezier_arc, flower_chart, level_color


def make_table():
    return SceneTable(
        metadata=ShowMetadata(title="Show", date="2026-10-10"),
        scenes=[
            Scene("Opening", 0, 0, ""),
            Scene("Same level", 60, 0, ""),
            Scene("Deeper", 120, 1, "single"),
            Scene("Back", 200, 0, ""),
        ],
    )


def test_bezier_arc_endpoints_and_direction():
    x, y = bezier_arc(0, 0, 10, 2, arc_height=0.5, steps=20)
    assert (x[0], y[0]) == (0, 0)
    assert (x[-1], y[-1]) == (10, 2)
    assert len(x) == len(y) == 20
    # Control point is offset in the direction of travel, so the curve bows above the chord.
    assert y[10] > 1
    _, y_down = bezier_arc(0, 2, 10, 0)
    assert y_down[20] < 1


def test_level_color_cycles():
    assert level_color(0) == PASTEL_COLORS[0]
    assert level_color(len(PASTEL_COLORS)) == PASTEL_COLORS[0]


def test_flat_and_arc_traces():
    fig = flower_chart(make_table())
    # flat (1) + run-up and arc (2) for a transition + run-up and arc (2)
    assert len(fig.data) == 5
    flat = fig.data[0]
    assert list(flat.x) == [0, 60] and list(flat.y) == [0, 0]
    # The run-up is flat at the level being left; the arc ends at the next scene.
    run_up, arc = fig.data[1], fig.data[2]
    assert list(run_up.y) == [0, 0]
    assert (arc.x[-1], arc.y[-1]) == (120, 1)
    assert arc.line.color == level_color(0)
    assert fig.data[3].line.color == level_color(1)


def test_annotations_name_every_scene():
    fig = flower_chart(make_table())
    assert [a.text for a in fig.layout.annotations] == [
        "Opening",
        "Same level",
        "Deeper",
        "Back",
    ]
    deeper = fig.layout.annotations[2]
    assert (deeper.x, deeper.y) == (120, 1)


def test_axes_and_title():
    fig = flower_chart(make_table())
    assert fig.layout.title.text == "Show - 2026-10-10"
    assert fig.layout.xaxis.title.text == "Time (MM:SS)"
    assert fig.layout.xaxis.ticktext[0] == "00:00"
    assert len(fig.layout.xaxis.tickvals) == len(fig.layout.xaxis.ticktext)
    assert fig.layout.yaxis.dtick == 1


def test_empty_and_single_scene():
    assert len(flower_chart(SceneTable()).data) == 0
    single = SceneTable(scenes=[Scene("Only", 0, 0, "")])
    fig = flower_chart(single)
    assert len(fig.data) == 0 and len(fig.layout.annotations) == 1


def test_invalid_table_rejected():
    bad = SceneTable(scenes=[Scene("A", 10, 0, ""), Scene("B", 5, 1, "single")])
    with pytest.raises(ValidationError):
        flower_chart(bad)
