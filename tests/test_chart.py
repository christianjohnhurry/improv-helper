import pytest

from flower import Scene, SceneTable
from flower.chart import main


@pytest.fixture
def table_path(tmp_path):
    path = tmp_path / "show.json"
    SceneTable(
        scenes=[Scene("Opening", 0, 0, ""), Scene("Deeper", 75, 1, "single")]
    ).save_json(path)
    return path


def test_default_output_next_to_table(table_path, capsys):
    assert main([str(table_path)]) == 0
    html = table_path.with_suffix(".html")
    assert "Opening" in html.read_text()
    assert capsys.readouterr().out.strip() == str(html)


def test_explicit_output(table_path, tmp_path):
    out = tmp_path / "out.html"
    assert main([str(table_path), "-o", str(out)]) == 0
    assert out.exists()


def test_missing_file(tmp_path, capsys):
    assert main([str(tmp_path / "nope.json")]) == 1
    assert "cannot load" in capsys.readouterr().err


def test_invalid_table(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text('{"scenes": [{"description": "A", "timestamp": 5, "level": -1, "tag_type": ""}]}')
    assert main([str(bad)]) == 1
    assert "level" in capsys.readouterr().err
