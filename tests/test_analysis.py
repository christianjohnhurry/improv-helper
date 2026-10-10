from pathlib import Path

import pytest

from flower import Scene, SceneTable, ValidationError, analyse, scene_lengths

FIXTURE = Path(__file__).parent / "fixtures" / "the-scamps-show-3.json"


def table(*rows):
    return SceneTable(scenes=[Scene(*r) for r in rows])


def small():
    return table(
        ("Opening", 0, 0, ""),
        ("Base", 10, 0, ""),
        ("A", 20, 1, "single"),
        ("B", 35, 2, "double"),
        ("C", 40, 1, "double"),
        ("Base", 60, 0, ""),
        ("End", 100, 0, ""),
    )


def test_scene_lengths():
    assert scene_lengths(small()) == [10, 10, 15, 5, 20, 40, 0]


@pytest.mark.parametrize("n", [0, 1])
def test_too_few_rows(n):
    t = table(*[("Opening", 0, 0, "")][:n])
    with pytest.raises(ValidationError):
        scene_lengths(t)
    with pytest.raises(ValidationError):
        analyse(t)


def test_runs_and_tree():
    a = analyse(small())
    assert a.opening.scene.description == "Opening"
    assert [[n.scene.description for n in r.scenes] for r in a.runs] == [
        ["Base", "A", "B", "C"],
        ["Base"],
    ]
    base, node_a, node_b, node_c = a.runs[0].scenes
    assert node_a.parent is base and node_b.parent is node_a
    assert node_c.parent is base  # latest earlier level-0 scene, not B
    assert base.children == [node_a, node_c]
    assert (node_b.length, node_b.branch_length) == (5, 5)
    assert (node_a.length, node_a.branch_length) == (15, 20)
    assert (base.length, base.branch_length) == (10, 50)
    assert a.runs[0].length == 50


def test_stats():
    s = analyse(small()).stats
    assert s.total_time == 100
    assert s.run_count == 2
    assert s.max_depth == 2
    assert s.base_percent == 50  # 10 + 40 of 100
    assert s.mean_scene_length == pytest.approx(90 / 5)
    assert s.longest_scene.scene.description == "Base"
    assert s.longest_scene.index == 5
    assert (s.single_tags, s.double_tags) == (1, 2)


def test_no_runs():
    a = analyse(table(("Opening", 0, 0, ""), ("End", 30, 0, "")))
    assert a.runs == []
    assert a.stats.total_time == 30
    assert a.stats.base_percent == 0
    assert a.stats.mean_scene_length == 0
    assert a.stats.longest_scene is None


def test_scene_before_any_base_visit():
    t = table(("Opening", 0, 0, ""), ("A", 10, 1, "single"), ("End", 20, 0, ""))
    with pytest.raises(ValidationError, match="no parent"):
        analyse(t)


def test_level_skip_has_no_parent():
    t = table(
        ("Opening", 0, 0, ""),
        ("Base", 10, 0, ""),
        ("A", 20, 1, "single"),
        ("Base", 30, 0, ""),
        ("B", 40, 2, "single"),  # level 1 exists, but in an earlier run
        ("End", 50, 0, ""),
    )
    with pytest.raises(ValidationError, match="no parent"):
        analyse(t)


def test_end_marker_level_ignored():
    t = table(("Opening", 0, 0, ""), ("Base", 10, 0, ""), ("End", 20, 3, "single"))
    a = analyse(t)
    assert a.stats.max_depth == 0
    assert a.stats.single_tags == 0


def test_scamps_show_3():
    a = analyse(SceneTable.load_json(FIXTURE))
    s = a.stats
    assert s.total_time == 3183 - 1933
    assert a.opening.length == 2085 - 1933
    assert s.run_count == 4
    assert s.max_depth == 3
    assert [len(r.scenes) for r in a.runs] == [4, 2, 3, 1]
    assert [r.length for r in a.runs] == [389, 366, 311, 32]
    assert sum(r.length for r in a.runs) + a.opening.length == s.total_time
    assert s.base_percent == pytest.approx(100 * (65 + 116 + 83 + 32) / 1250)
    assert (s.single_tags, s.double_tags) == (3, 3)
    assert s.longest_scene.scene.description == "European Latte Art Championship"
    assert s.longest_scene.length == 250
