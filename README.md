# MP3 Movie API

This is a FastAPI application that stores one movie collection in a SQLite table and filters records using SQL, and each successful upload replaces the current collection.
Uploaded CSV files are checked for the exact 4 columns and at least 1 data row and then saved to a SQLite database, so the data is preserved across server restarts.
The `src/storage.py` module uses SQL to save, retrieve, count and search movies, and `src/database.py` creates the database connection and the movies table.
The `/movies/process` endpoint reuses my MP1 pipeline modules in `data_pipeline/` to validate and clean the movies, and then saves the results back to the database.
`GET /movies` responses are cached with FakeRedis in `src/cache.py`, so repeated requests are answered from the cache without querying the database.
After an upload or processing, the cache is cleared so that old cached responses aren’t served after the data changes.
Middleware logs every request with a request ID, status code, and duration.

## Running the API

```bash
python -m uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs

## Running the Tests

```bash
python -m pytest tests -v
```

## Sample Processing Request

`POST /movies/process` with:

```json
    {
        "validation": {
            "required_columns": ["title", "release_year", "rating", "genre"],
            "numeric_columns": ["release_year", "rating"]
        },
        "processing": {
            "remove_duplicates": true,
            "missing": {"enabled": true, "axis": "rows"},
            "outliers": {
                "enabled": true,
                "columns": ["rating"],
                "method": "iqr",
                "threshold": 1.5
            }
        }
    }


```

Expected result for the 20-row sample:

```json
{
  "validation_rows_removed": 0,
  "cleaning_report": {
    "rows_before": 20,
    "rows_after": 16,
    "rows_removed": 4,
    "columns_before": 4,
    "columns_after": 4,
    "columns_removed": 0
  }
}


```