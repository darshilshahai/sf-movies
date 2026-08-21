# SF Movies Explorer - Completed Features & Architecture Overview

Welcome to the **SF Movies Explorer** progress summary! This document provides a beginner-friendly overview of everything built so far, explaining what each feature does, why it exists, and how all parts work together.

---

## 🎯 Project Overview

**SF Movies Explorer** is a full-stack web application designed to explore movie filming locations across San Francisco on an interactive map.

### Current Architecture Flow:

```
+------------------+         REST / JSON          +-------------------------+
|  React Frontend  | <--------------------------> |  FastAPI Web Backend    |
| (Setup Ready)    |   GET /api/v1/movies?search  |  (App Factory / CORS)   |
+------------------+                              +------------+------------+
                                                               |
                                                  MovieService Layer
                                                  - Validates Coordinates
                                                  - Aggregates Cast List
                                                  - Normalizes & Deduplicates
                                                               |
                                                  DataSF Client (HTTPX)
                                                  - Async HTTP Calls
                                                  - Explicit Timeouts
                                                  - Safe SoQL Escaping
                                                               |
                                                               v
                                                      DataSF Open API
                                                    (yitu-d5am.json)
```

---

## 📋 Completed Phases Breakdown

---

### Phase 1 — DataSF API Investigation

#### What We Did:
We thoroughly analyzed the official San Francisco Open Data dataset ("Film Locations in San Francisco", ID: `yitu-d5am`). We profiled all **2,214 records** in the live dataset.

#### Key Learnings & Findings:
1. **Raw Data Anatomy:** DataSF stores records as flat rows where each row represents **one filming location**. A single film like *Milk* or *Vertigo* appears in multiple rows for different locations.
2. **Missing Data Handling:** 
   - 86 records have no geographic coordinates (missing latitude/longitude).
   - 54 records have no specific location name.
3. **Data Type Anomalies:** Numbers like `latitude`, `longitude`, and `release_year` are returned as **text strings** (e.g. `"37.7857"`, `"2008"`).
4. **Cast Fields:** Cast members are split across three separate keys (`actor_1`, `actor_2`, `actor_3`).
5. **Backend Decision:** We decided that our **FastAPI backend** should fetch, clean, and normalize this raw data so our React frontend receives clean, predictable JSON objects.

---

### Phase 2 — Repository & Project Structure

#### What We Did:
We set up a clean, professional monorepo folder layout dividing frontend and backend logic.

#### Folder Structure:
- `frontend/`: React + TypeScript application initialized with Vite, Tailwind CSS v4, Lucide icons, and Leaflet map packages.
- `backend/`: FastAPI Python application with modular packages for routes (`api/`), client services (`clients/`), core configs (`core/`), middleware (`middleware/`), schemas (`schemas/`), business logic (`services/`), and tests (`tests/`).

---

### Phase 3 — Backend Foundation

#### What We Did:
We built a solid, production-grade FastAPI application foundation before writing any business logic.

#### Main Features Added:
1. **Application Factory Pattern (`app/main.py`):** Functions like `create_application()` build and configure the app dynamically. Uses modern Python lifespan event handlers for server startup and shutdown.
2. **Centralized Configuration (`app/core/config.py`):** Uses Pydantic `BaseSettings` to load environment variables from `.env` files into a strongly-typed object cached with `@lru_cache`. No scattered `os.getenv()` calls.
3. **Application Logging (`app/core/logging.py`):** Replaced `print()` with standard Python logging formatted cleanly with timestamps and log levels.
4. **Request Duration Middleware (`app/middleware/request_logging.py`):** Automatically measures and logs how long every HTTP request takes in milliseconds (`duration_ms`).
5. **Global Exception Handling (`app/core/exceptions.py`):** Custom `AppException` class captures internal errors and returns uniform JSON responses: `{"error": {"code": "...", "message": "..."}}`. Stack traces are kept in private logs and never leaked to users.
6. **API Versioning & Health Endpoint (`GET /api/v1/health`):** Mounted version 1 API routes under `/api/v1`. Includes a health check endpoint returning `{"status": "healthy", "service": "sf-movies-api"}`.
7. **CORS Security:** Configured Cross-Origin Resource Sharing so only our React frontend (`http://localhost:5173`) can communicate with the backend.

---

### Phase 4 — DataSF API Client Integration (`DataSFClient`)

#### What We Did:
We built `DataSFClient` inside `app/clients/datasf.py` to handle all outgoing HTTP network calls to DataSF.

#### Main Features Added:
1. **Asynchronous HTTP Requests:** Uses `httpx.AsyncClient` to make non-blocking HTTP requests so the backend can handle multiple users simultaneously.
2. **Explicit Timeouts:** Enforces a configurable 10-second timeout (`datasf_timeout_seconds`) so slow DataSF responses never hang our backend indefinitely.
3. **Query Parameter Support:** Supports SODA API query parameters (`$limit`, `$offset`, `$where`, `$order`, `$q`).
4. **Upstream Error Mapping:** Converts network failures (`httpx.RequestError`) and timeouts (`httpx.TimeoutException`) into custom exceptions (`UpstreamServiceException` -> HTTP 502 Bad Gateway, `UpstreamTimeoutException` -> HTTP 504 Gateway Timeout).
5. **Isolated Unit Testing:** Created a test suite (`tests/test_datasf_client.py`) using `httpx.MockTransport`. All unit tests run in memory without hitting the real internet.

---

### Phase 5 — Movie Domain & Service Layer (`MovieService`)

#### What We Did:
We built `MovieService` inside `app/services/movie_service.py` and domain schemas inside `app/schemas/movie.py` to transform raw DataSF data into clean internal models.

#### Main Features Added:
1. **Clean Pydantic Schemas (`Coordinates` & `MovieLocation`):** Standardized data model with float coordinates, integer release year, and clean text fields.
2. **Coordinate Validation:** Converts latitude/longitude text strings to `float` numbers and verifies they fall within valid geographic bounds (-90 to 90 latitude, -180 to 180 longitude).
3. **Unusable Record Filtering:** Records missing essential map attributes (title, location name, or valid coordinates) are skipped and logged as warnings.
4. **Cast Normalization:** Combines `actor_1`, `actor_2`, and `actor_3` into a single `actors: ["Actor A", "Actor B"]` list, removing empty entries and duplicate names.
5. **Text Cleaning:** Trims whitespace and turns empty text strings `""` into `None`.
6. **Batch Deduplication:** Deduplicates exact duplicate location rows using an in-memory set.
7. **Preserved Upstream Errors:** If DataSF is down, `MovieService` lets upstream exceptions propagate to show clear 502/504 errors instead of pretending 0 movies exist.

---

### Phase 6 — Movie Locations REST API (`GET /api/v1/movies`)

#### What We Did:
We exposed `MovieService` through a clean, RESTful API endpoint: `GET /api/v1/movies`.

#### Main Features Added:
1. **Thin API Route Handler (`app/api/v1/movies.py`):** Route handler validates parameters, calls `MovieService`, and returns the JSON response. Zero business logic in the route.
2. **Input Parameter Validation:**
   - `limit`: Integer between 1 and 500 (default: 100).
   - `offset`: Non-negative integer (default: 0).
   - `search`: String between 1 and 100 characters for searching titles or location names.
   - `year`: Integer between 1900 and 2100 for release year filtering.
3. **Response Envelope (`MovieListResponse`):** Returns data wrapped in a clean JSON envelope:
   ```json
   {
     "data": [
       {
         "title": "Vertigo",
         "release_year": 1958,
         "location": "Mission Dolores",
         "coordinates": {
           "latitude": 37.7643,
           "longitude": -122.4269
         },
         "director": "Alfred Hitchcock",
         "actors": ["James Stewart", "Kim Novak"],
         "neighborhood": "Mission"
       }
     ],
     "meta": {
       "count": 1,
       "limit": 100,
       "offset": 0
     }
   }
   ```
4. **Upstream SoQL Search & Quote Escaping:** Search queries build SoQL `$where` clauses for upstream filtering at the DataSF API level. Single quotes are escaped (`'` -> `''`) so queries like `"O'Brien"` run safely without syntax errors.
5. **Empty Results Return HTTP 200:** Searching for a non-existent title returns `200 OK` with `"data": []` and `"count": 0` (not a 404 error).
6. **Auto-Generated Swagger Documentation:** Fully documented with response schemas and query descriptions at `http://localhost:8000/docs`.

---

## 🧪 Testing & Quality Assurance Summary

We maintain **100% automated test suite pass rate**:

```bash
cd backend
uv run pytest -v
```

### Test Coverage:
- **`tests/test_config.py`**: Settings loading tests.
- **`tests/test_health.py`**: Health endpoint check tests.
- **`tests/test_datasf_client.py`**: 8 client transport tests (success, empty payload, 500 error, timeout, network failure, invalid JSON, unexpected shape, query params).
- **`tests/test_movie_service.py`**: 14 service normalization tests (valid mapping, optional fields, missing coords, invalid lat/lng, out-of-bounds coords, missing title/location, actor cleanup, exception propagation, mixed rows, deduplication, SoQL query builder).
- **`tests/test_movies_api.py`**: 10 route integration tests (200 OK envelope, pagination params, search param, year param, empty 200 OK, limit validation ge/le, offset validation, search max length, 502 error propagation).

**Result:** `34 passed in 0.33s`

---

## 🚀 Next Steps

We are ready to move on to **Phase 7**!
