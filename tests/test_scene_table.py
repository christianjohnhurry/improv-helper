import csv

import pytest

from flower import (
    Scene,
    SceneTable,
    ShowMetadata,
    ValidationError,
    format_timestamp,
    parse_timestamp,
)


def make_table():
    return SceneTable(
        metadata=ShowMetadata(title="Show", date="2026-10-10", video_source="http://v"),
        scenes=[
            Scene("Opening", 0, 0, ""),
            Scene("Deeper", 75, 1, "single"),
            Scene("Even deeper", 130, 2, "double"),
            Scene("Back to base", 200, 0, ""),
        ],
    )


def test_timestamp_helpers():
    assert parse_timestamp("01:15") == 75
    assert parse_timestamp("100:05") == 6005
    assert format_timestamp(75) == "01:15"
    assert format_timestamp(6005) == "100:05"
    for bad in ["", "1", "aa:bb", "01:60", "-1:00"]:
        with pytest.raises(ValueError):
            parse_timestamp(bad)
    with pytest.raises(ValueError):
        format_timestamp(-1)


def test_valid_table_passes():
    make_table().validate()


def test_timestamps_must_increase():
    t = make_table()
    t.scenes[2].timestamp = 75
    with pytest.raises(ValidationError, match="timestamp"):
        t.validate()


def test_negative_level_rejected():
    t = make_table()
    t.scenes[1].level = -1
    with pytest.raises(ValidationError, match="level"):
        t.validate()


def test_bad_tag_type_rejected():
    t = make_table()
    t.scenes[1].tag_type = "triple"
    with pytest.raises(ValidationError, match="tag_type"):
        t.validate()


def test_base_scene_requires_empty_tag_type():
    t = make_table()
    t.scenes[3].tag_type = "single"
    with pytest.raises(ValidationError, match="base scene"):
        t.validate()


def test_json_round_trip(tmp_path):
    path = tmp_path / "table.json"
    t = make_table()
    t.save_json(path)
    assert SceneTable.load_json(path) == t


def test_load_json_validates(tmp_path):
    t = make_table()
    d = t.to_dict()
    d["scenes"][1]["level"] = -3
    with pytest.raises(ValidationError):
        SceneTable.from_dict(d)


def test_csv_export(tmp_path):
    path = tmp_path / "table.csv"
    make_table().export_csv(path)
    rows = list(csv.reader(path.open()))
    assert rows[0] == ["description", "timestamp", "level", "tag_type"]
    assert rows[2] == ["Deeper", "01:15", "1", "single"]
    assert rows[4] == ["Back to base", "03:20", "0", ""]


def test_version_is_semver_and_in_changelog():
    import re
    from pathlib import Path

    import flower

    assert re.fullmatch(r"\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?", flower.__version__)
    changelog = Path(__file__).parent.parent / "CHANGELOG.md"
    assert f"## [{flower.__version__}]" in changelog.read_text()
