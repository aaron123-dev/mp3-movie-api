import pandas as pd
import pytest

from src import MovieStorage
import main


def test_movies_persist(client, test_storage, uploaded_movies):
    other_storage = MovieStorage(test_storage.db_path)
    df = other_storage.get()
    assert len(df) == 20
    assert other_storage.count_movies() == 20
    assert list(df.columns) == ["title", "release_year", "rating", "genre"]

    expected_titles = pd.read_csv("fixtures/sample_movies.csv")["title"].tolist()
    assert df["title"].tolist() == expected_titles

    storage_ids = [row["id"] for row in other_storage.select_columns(["title"], limit=100)]
    response = client.get("/movies", params={"limit": 100})
    assert response.status_code == 200
    api_ids = [row["id"] for row in response.json()["data"]]
    assert storage_ids == list(range(1, 21))
    assert api_ids == list(range(1, 21))


def test_cache_and_processing(client, uploaded_movies, processing_body):
    response_100 = client.get("/movies", params={"limit": 100})
    assert response_100.status_code == 200
    assert main.cache.get(100) == response_100.json()

    response_1 = client.get("/movies", params={"limit": 1})
    assert response_1.status_code == 200
    assert main.cache.get(1) == response_1.json()

    repeat = client.get("/movies", params={"limit": 100})
    assert repeat.status_code == 200
    assert repeat.json() == response_100.json()

    process = client.post("/movies/process", json=processing_body)
    assert process.status_code == 200
    report = process.json()
    assert report["validation_rows_removed"] == 0
    assert report["cleaning_report"]["rows_before"] == 20
    assert report["cleaning_report"]["rows_after"] == 16
    assert report["cleaning_report"]["rows_removed"] == 4
    assert main.cache.get(100) is None
    assert main.cache.get(1) is None

    updated = client.get("/movies", params={"limit": 100})
    assert updated.status_code == 200
    body = updated.json()
    assert body["total_rows"] == 16
    titles = [row["title"] for row in body["data"]]
    assert titles == [f"Movie {letter}" for letter in "ABCDEFGHIJKLMNOP"]
    assert [row["id"] for row in body["data"]] == list(range(1, 17))
    assert main.cache.get(100) == body


def test_cache_hit_skips_database(client, uploaded_movies, monkeypatch):
    first = client.get("/movies", params={"limit": 100})
    assert first.status_code == 200

    def fail_if_called(*args, **kwargs):
        pytest.fail("The database should not be queried on a cache hit")

    monkeypatch.setattr(main.storage, "select_columns", fail_if_called)
    monkeypatch.setattr(main.storage, "count_movies", fail_if_called)

    second = client.get("/movies", params={"limit": 100})
    assert second.status_code == 200
    assert second.json() == first.json()