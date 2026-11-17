# MP3 Movie API

This is a FastAPI application that ___.
Uploaded CSV files are checked for ___ and then saved to ___, so the data ___.
The `src/storage.py` module uses SQL to ___, and `src/database.py` ___.
The `/movies/process` endpoint reuses my MP1 pipeline modules in `data_pipeline/` to ___.
`GET /movies` responses are cached with FakeRedis in `src/cache.py`, so ___.
After an upload or processing, the cache is ___ so that ___.
Middleware logs every request with ___.

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
(paste the processing_body JSON from the Part 2 instructions here)
```

Expected result for the 20-row sample:

```json
(paste the expected processing response from the Part 2 instructions here)

```