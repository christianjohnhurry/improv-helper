from pathlib import Path

from flower import Scene, SceneTable, analyse, sunburst_chart

FIXTURE = Path(__file__).parent / "fixtures" / "the-scamps-show-3.json"


def scamps():
    return SceneTable.load_json(FIXTURE)


def trace(fig):
    return fig.data[0]


def test_structure_matches_analysis():
    table = scamps()
    a = analyse(table)
    t = trace(sunburst_chart(table))
    by_id = dict(zip(t.ids, zip(t.parents, t.values, t.labels)))

    nodes = [a.opening] + [n for r in a.runs for n in r.scenes]
    assert len(t.ids) == len(nodes) + 1  # plus the root; end marker not drawn
    assert by_id["show"] == ("", a.stats.total_time, table.metadata.title)
    for n in nodes:
        parent = f"s{n.parent.index}" if n.parent else "show"
        assert by_id[f"s{n.index}"] == (parent, n.branch_length, n.scene.description)
    assert f"s{len(table.scenes) - 1}" not in by_id


def test_ring_one_is_opening_and_base_visits_in_order():
    table = scamps()
    a = analyse(table)
    t = trace(sunburst_chart(table))
    ring_one = [i for i, p in zip(t.ids, t.parents) if p == "show"]
    assert ring_one == [f"s{a.opening.index}"] + [f"s{r.base.index}" for r in a.runs]


def test_branch_values_total_and_children_fit():
    t = trace(sunburst_chart(scamps()))
    assert t.branchvalues == "total"
    values = dict(zip(t.ids, t.values))
    for parent in t.ids:
        kids = [values[i] for i, p in zip(t.ids, t.parents) if p == parent]
        assert sum(kids) <= values[parent]
    assert values["show"] == sum(v for i, p, v in zip(t.ids, t.parents, t.values) if p == "show")


def test_colours_by_tag_type():
    table = scamps()
    t = trace(sunburst_chart(table))
    colors = dict(zip(t.ids, t.marker.colors))
    grey = colors["show"]
    singles = {c for i, c in colors.items() if i != "show" and table.scenes[int(i[1:])].tag_type == "single"}
    doubles = {c for i, c in colors.items() if i != "show" and table.scenes[int(i[1:])].tag_type == "double"}
    assert len(singles) == len(doubles) == 1 and singles != doubles
    assert not ({grey} & (singles | doubles))
    assert colors["s0"] == grey and colors["s1"] == grey  # Opening and a base scene


def test_hover_fields():
    t = trace(sunburst_chart(scamps()))
    row = dict(zip(t.ids, t.customdata))
    assert list(row["s0"]) == ["00:00", "02:32", "02:32", "opening"]
    assert row["s2"][0] == "03:37" and row["s2"][3] == "single"


def test_legend_and_stats_card():
    fig = sunburst_chart(scamps())
    assert [t.name for t in fig.data[1:]] == ["Opening / base", "Single", "Double"]
    card = fig.layout.annotations[0].text
    for label in ("Total time", "Runs", "Max depth", "At base", "Mean scene",
                  "Longest scene", "Single tags", "Double tags"):
        assert label in card


def test_minimal_show():
    table = SceneTable(scenes=[Scene("Opening", 0, 0, ""), Scene("End", 30, 0, "")])
    t = trace(sunburst_chart(table))
    assert list(t.ids) == ["show", "s0"] and list(t.values) == [30, 30]
