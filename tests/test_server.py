import pytest
from fastapi.testclient import TestClient

from flower.server import create_app

TABLE = {
    "metadata": {"title": "Show", "date": "2026-10-10", "video_source": "http://v"},
    "scenes": [
        {"description": "Opening", "timestamp": 0, "level": 0, "tag_type": ""},
        {"description": "Deeper", "timestamp": 75, "level": 1, "tag_type": "single"},
    ],
}


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(tmp_path / "data"))


def test_index_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_list_empty_when_data_dir_missing(client):
    assert client.get("/api/tables").json() == []


def test_put_get_round_trip(client, tmp_path):
    assert client.put("/api/tables/show-1", json=TABLE).status_code == 200
    assert (tmp_path / "data" / "show-1.json").is_file()
    assert client.get("/api/tables/show-1").json() == TABLE
    assert client.get("/api/tables").json() == ["show-1"]


def test_get_missing_is_404(client):
    assert client.get("/api/tables/nope").status_code == 404


def test_put_invalid_table_is_422_and_not_saved(client, tmp_path):
    bad = {**TABLE, "scenes": [{**TABLE["scenes"][0], "level": -1}]}
    response = client.put("/api/tables/bad", json=bad)
    assert response.status_code == 422
    assert "level" in response.json()["detail"]
    assert client.get("/api/tables").json() == []


def test_put_non_increasing_timestamps_is_422(client):
    bad = {**TABLE, "scenes": [TABLE["scenes"][1], TABLE["scenes"][1]]}
    assert client.put("/api/tables/bad", json=bad).status_code == 422


def test_put_malformed_body_is_422(client):
    assert client.put("/api/tables/bad", json={"scenes": [{"nope": 1}]}).status_code == 422


@pytest.mark.parametrize("name", ["..%2Fescape", "a.b", "a b"])
def test_bad_names_rejected(client, name):
    assert client.put(f"/api/tables/{name}", json=TABLE).status_code in (404, 422)


def test_csv_export(client):
    client.put("/api/tables/show-1", json=TABLE)
    response = client.get("/api/tables/show-1/csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    lines = response.text.splitlines()
    assert lines[0] == "description,timestamp,level,tag_type"
    assert lines[2] == "Deeper,01:15,1,single"


def test_csv_export_missing_is_404(client):
    assert client.get("/api/tables/nope/csv").status_code == 404
