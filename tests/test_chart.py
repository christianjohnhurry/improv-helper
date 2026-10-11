import json
import re
from pathlib import Path

import pytest

from flower import Scene, SceneTable, analyse, show_data, show_page, shows_page
from flower.chart import main
from flower.page import site_page
from flower.site import main as site_main
from flower.sunburst_cli import main as sunburst_main

FIXTURE = Path(__file__).parent / "fixtures" / "the-scamps-show-3.json"


def embedded(html):
    """The SHOWS JSON embedded in a page."""
    return json.loads(re.search(r"var SHOWS = (.*?);\n", html).group(1).replace("<\\/", "</"))


@pytest.fixture
def table_path(tmp_path):
    path = tmp_path / "show.json"
    SceneTable(
        scenes=[Scene("Opening", 0, 0, ""), Scene("Base", 20, 0, ""),
                Scene("Deeper", 75, 1, "single"), Scene("End", 90, 0, "")]
    ).save_json(path)
    return path


def test_show_data_matches_analysis():
    table = SceneTable.load_json(FIXTURE)
    a = analyse(table)
    d = show_data(table)
    assert d["total"] == a.stats.total_time and d["stats"]["runs"] == len(d["runs"]) == len(a.runs)
    assert d["scenes"][0]["start"] == 0 and d["scenes"][0]["run"] is None
    nodes = [a.opening] + [n for r in a.runs for n in r.scenes]
    assert [s["i"] for s in d["scenes"]] == sorted(n.index for n in nodes)
    assert {s["i"]: s["branch"] for s in d["scenes"]} == {n.index: n.branch_length for n in nodes}


def test_name_falls_back_to_file_stem():
    table = SceneTable(scenes=[Scene("Opening", 0, 0, ""), Scene("End", 30, 0, "")])
    assert show_data(table, "my-show_two")["name"] == "My Show Two"


def test_page_embeds_shows_newest_first_and_view():
    table = SceneTable.load_json(FIXTURE)
    old, new = show_data(table), show_data(table)
    old["date"], old["name"], new["date"], new["name"] = "2026-01-01", "Old", "2026-02-01", "New"
    html = shows_page([old, new], "sunburst")
    assert [s["name"] for s in embedded(html)] == ["New", "Old"]
    assert 'view: "sunburst"' in html and "__" not in re.search(r"view: .*", html).group(0)


def test_page_escapes_script_close_in_names():
    table = SceneTable(scenes=[Scene("</script>", 0, 0, ""), Scene("End", 30, 0, "")])
    html = show_page(table)
    assert html.count("</script>") == 2  # d3 + the page script
    assert embedded(html)[0]["scenes"][0]["name"] == "</script>"


def test_unknown_view_rejected():
    with pytest.raises(ValueError, match="view"):
        shows_page([], "pie")


def test_default_output_next_to_table(table_path, capsys):
    assert main([str(table_path)]) == 0
    html = table_path.with_suffix(".html")
    assert 'view: "timeline"' in html.read_text()
    assert capsys.readouterr().out.strip() == str(html)


def test_sunburst_cli_default_output(table_path):
    assert sunburst_main([str(table_path)]) == 0
    assert 'view: "sunburst"' in table_path.with_name("show-sunburst.html").read_text()


def test_explicit_output(table_path, tmp_path):
    out = tmp_path / "out.html"
    assert main([str(table_path), "-o", str(out)]) == 0
    assert out.exists()


def test_missing_file(tmp_path, capsys):
    assert main([str(tmp_path / "nope.json")]) == 1
    assert "cannot render" in capsys.readouterr().err


def test_invalid_table(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text('{"scenes": [{"description": "A", "timestamp": 5, "level": -1, "tag_type": ""}]}')
    assert main([str(bad)]) == 1
    assert "level" in capsys.readouterr().err


def test_site_builds_every_valid_table_and_skips_others(tmp_path, capsys):
    (tmp_path / "a.json").write_text(FIXTURE.read_text())
    (tmp_path / "junk.json").write_text("not json")
    assert site_main([str(tmp_path)]) == 0
    out = tmp_path / "scamps-shows.html"
    assert len(embedded(out.read_text())) == 1
    assert site_page(tmp_path)[1] == ["The Scamps Show 3"]


def test_site_with_no_tables(tmp_path, capsys):
    assert site_main([str(tmp_path)]) == 1
    assert "no scene tables" in capsys.readouterr().err


def shifted(table, offset):
    """The table with every timestamp moved later by offset seconds."""
    return SceneTable(
        metadata=table.metadata,
        scenes=[Scene(s.description, s.timestamp + offset, s.level, s.tag_type) for s in table.scenes],
    )


def test_show_data_is_timed_from_the_opening():
    table = SceneTable.load_json(FIXTURE)
    late = show_data(shifted(table, 1500))
    assert late["scenes"][0]["start"] == 0
    assert {k: v for k, v in late.items() if k != "scenes"} == {k: v for k, v in show_data(table).items() if k != "scenes"}
    assert [s["start"] for s in late["scenes"]] == [s["start"] for s in show_data(table)["scenes"]]
    assert [s["video"] for s in late["scenes"]][0] == table.scenes[0].timestamp + 1500


def test_show_data_scene_count_excludes_opening():
    d = show_data(SceneTable.load_json(FIXTURE))
    assert d["stats"]["count"] == len(d["scenes"]) - 1


def test_compare_view_needs_two_shows():
    one = show_data(SceneTable.load_json(FIXTURE))
    with pytest.raises(ValueError, match="two or more"):
        shows_page([one], "compare")
    html = shows_page([one, {**one, "name": "Other", "date": "2026-10-01"}], "compare")
    assert "var state = { show: 0, view: \"compare\"" in html


def test_site_compare_view(tmp_path, capsys):
    (tmp_path / "a.json").write_text(FIXTURE.read_text())
    assert site_main([str(tmp_path), "--view", "compare"]) == 1
    assert "two or more" in capsys.readouterr().err
    (tmp_path / "b.json").write_text(FIXTURE.read_text())
    assert site_main([str(tmp_path), "--view", "compare"]) == 0
