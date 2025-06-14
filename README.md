# Metrics API

This project is a technical test build with **Django**, which consists ingesting and restoring metric data through a REST API.

## Tech Stack

- Python 3.12
- Django 5.2
- Django REST Framework
- SQLite 
- Docker + Docker Compose
- Uvicorn
- uv (project and dependency manager)
- Ruff (linting PEP8)
- Pytest (unit tests)

## Main directories and files

- `config/` — Django project (settings, urls, asgi)
- `metrics/` — Django application containing the `Metric` model, views and unit tests
- `docker-entrypoint.sh` — Docker startup script 
- `Dockerfile` — Docker image definition 
- `compose.yml` — Docker compose configuration 
- `pyproject.toml` — Dependencies managed with `uv`
- `README.md`

## Running the app with Docker

The following commands should be run from the project root folder `weenat_test`.   

### Environment variables file

Before launching the app, you must create an environment variable file named `.env` at the root of the project (i.e `weenat_test`) and include the following 3 variables: 

```bash
SECRET_KEY = "you-generated-key" 
DEBUG = False 
ALLOWED_HOSTS=localhost,127.0.0.1
```
If needed, you can generate the key using:
```bash
python generate_secret_key.py
``` 

### Build and start the app

```bash
docker compose build --no-cache
docker compose up -d
```
This will:
- Install dependencies using `uv` 
- Apply database migrations
- Start the server using `uvicorn`

The application will be available at `localhost:8000`

## API endpoints

The API exposes three endpoints:

### 1. Ingests metrics data
Request:

```bash
POST /api/ingest
```
```json
{
  "at": "2021-01-02T05:26:27Z",
  "datalogger": "c2a61e2e-068d-4670-a97c-72bfa5e2a58a",
  "location": {
    "lat": 47.56321,
    "lng": 1.524568
  },
  "measurements": [
    {
      "label": "temp",
      "value": 10.52
    },
    {
      "label": "rain",
      "value": 0
    },
    {
      "label": "hum",
      "value": 79.5
    }
  ]
}
```

Response:

```json
{
    "message": "Record is inserted successfully"
}
```

### 2. Returns the data stored. The output is the raw data stored.

Request:
```bash
GET /api/data?datalogger=c2a61e2e-068d-4670-a97c-72bfa5e2a58a
```
Response:

```json
[
    {
        "label": "temp",
        "measured_at": "2021-01-02T05:26:27Z",
        "value": 10.52
    },
    {
        "label": "rain",
        "measured_at": "2021-01-02T05:26:27Z",
        "value": 0.0
    },
    {
        "label": "hum",
        "measured_at": "2021-01-02T05:26:27Z",
        "value": 79.5
    }
]
```

### 3. Returns the data stored. The output will be either raw data or aggregates. The behaviour is driven by the query parameter span.

Request:
```bash
GET /api/summary?span=day&datalogger=c2a61e2e-068d-4670-a97c-72bfa5e2a58a
```
Response:

```json
[
    {
        "label": "temp",
        "time_slot": "2021-01-02T00:00:00Z",
        "value": 10.52
    },
    {
        "label": "rain",
        "time_slot": "2021-01-02T00:00:00Z",
        "value": 0.0
    },
    {
        "label": "hum",
        "time_slot": "2021-01-02T00:00:00Z",
        "value": 79.5
    }
]
```
## Tests and coverage 

Unit tests are available in `metrics/tests/`:

```bash
docker exec metric_api uv run pytest --cov=./ --cov-config=coverage.ini 
```

## Linting with default rules

This project uses **Ruff** for code linting:

```bash
docker exec metric_api uv run ruff check .
```