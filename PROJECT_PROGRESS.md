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

### Phase 7 — Autocomplete Search API

#### What We Did:
We built a fast, case-insensitive, deduplicated, and ranked autocomplete search API endpoint `GET /api/v1/search/suggestions`.

#### Key Highlights & Architecture:
1. **Endpoint Contract:** `GET /api/v1/search/suggestions?q=<query>&limit=<limit>`
   - `q`: Required query string (min length 2, max length 100). Whitespace trimmed automatically.
   - `limit`: Result count cap (default 8, min 1, max 15).
2. **Clean Discriminated Schema (`SearchSuggestion`):**
   ```json
   {
     "data": [
       { "value": "Vertigo", "type": "movie" },
       { "value": "Golden Gate Bridge", "type": "location" }
     ]
   }
   ```
3. **Upstream Filtering & Deterministic Ranking:**
   - Filters upstream in DataSF using SoQL `lower(title) like '%q%' or lower(locations) like '%q%'`.
   - Ranks prefix matches above contains matches.
   - Prioritizes movie titles over locations when match relevance score is equal.
4. **Case-Insensitive Deduplication:** Identical movie titles or filming location names are deduplicated efficiently using candidate sets while preserving original casing.
5. **Resilient Error Propagation:** Empty search results return `200 OK` with `{"data": []}`, while upstream DataSF network errors preserve exception details to return structured `502 Bad Gateway` error envelopes.

---

### Phase 8 — Frontend Foundation & API Integration

#### What We Did:
We created a clean React + TypeScript frontend architecture connected to the FastAPI backend using Axios and TanStack Query with strongly-typed API models and custom data fetching hooks.

#### Key Highlights & Architecture:
1. **Centralized API Client:** Created `src/api/client.ts` with base URL validation from `VITE_API_BASE_URL` and a 10s request timeout.
2. **Strongly Typed Models:** Created `src/types/movie.ts` and `src/types/search.ts` mirroring backend FastAPI response contracts (`MovieLocation`, `MovieListResponse`, `SearchSuggestion`).
3. **API Modules:** Implemented `getMovies(params)` and `getSearchSuggestions(query, limit)` in `src/api/movies.ts` and `src/api/search.ts`.
4. **TanStack Query Hooks:** Created `useMovies()` and `useSearchSuggestions()` with `enabled: query.length >= 2` guard logic.
5. **HomePage & State Verification:** Built `HomePage` component rendering loading, error, empty, and data preview (3-5 sample items) states to verify end-to-end connectivity (`React -> FastAPI -> DataSF`).

---

### Phase 9 — Interactive Leaflet Map

#### What We Did:
We replaced the temporary movie data preview with a fully interactive OpenStreetMap component using Leaflet and React Leaflet to map San Francisco film locations geographically.

#### Key Highlights & Architecture:
1. **Interactive Map Component (`MovieMap.tsx`):**
   - Configured `MapContainer` with OpenStreetMap tile layer (`url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"`).
   - Centered default view on San Francisco (`[37.7749, -122.4194]`, zoom level `12`).
2. **Vite + Leaflet Asset Fix:** Reconfigured Leaflet default marker icon paths (`marker-icon.png`, `marker-icon-2x.png`, `marker-shadow.png`) to avoid broken asset URL issues in Vite bundling.
3. **Marker & Popup Rendering:**
   - Rendered markers dynamically at `[movie.coordinates.latitude, movie.coordinates.longitude]`.
   - Popups display movie title, release year, location name, and director (hiding missing/null fields).
4. **HomePage Integration:** Connected `useMovies({ limit: 500 })` to fetch San Francisco locations, displaying a live location count badge ("Showing X filming locations") alongside responsive map bounds.

---

## 🧪 Testing & Quality Assurance Summary

We maintain **100% automated test suite pass rate** across backend and frontend:

### Backend Pytest Suite:
```bash
cd backend
.venv/bin/pytest -v
```
- **Coverage:** 56 tests across config, health, DataSF client, MovieService, movies API, and search API.
- **Result:** `56 passed in 0.23s`

### Frontend Vitest Suite:
```bash
cd frontend
npm test
```
- **Coverage:** 4 tests in `App.test.tsx` verifying map loading, location count badge, success, error, and empty states.
- **Result:** `4 passed in 0.62s`

### Production Build Verification:
```bash
cd frontend
npm run build
```
- **Result:** `✓ built in 130ms` (0 TypeScript / ESLint errors).

---

## 🚀 Next Steps

We are ready to move on to **Phase 10**!
