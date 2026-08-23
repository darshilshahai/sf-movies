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

### Phase 10 — Movie Markers & Detailed Popups

#### What We Did:
We extracted a dedicated, presentational `MoviePopup` component to display structured, rich movie metadata (title, release year, filming location, neighborhood, director, cast list, studio, and fun facts) with conditional null-hiding and polished dark theme CSS styling.

#### Key Highlights & Architecture:
1. **Extracted `MoviePopup.tsx` Component:**
   - Isolated popup presentation into `src/components/map/MoviePopup.tsx`.
   - Displays clear typography hierarchy (Amber title, badges, metadata labels, bullet-separated cast list).
2. **Conditional Metadata Rendering:**
   - Hides absent optional metadata cleanly without rendering `null` text or empty placeholders (no `"Director: null"` or `"N/A"`).
3. **Custom Leaflet Dark Theme Styling (`index.css`):**
   - Applied CSS overrides for `.leaflet-popup-content-wrapper`, `.leaflet-popup-content`, `.leaflet-popup-tip`, and `.leaflet-popup-close-button` matching the application's slate/amber theme.
4. **Zero Network Call Overhead:** Popup consumes pre-normalized `MovieLocation` props without triggering extra API requests on marker click.

---

### Phase 11 — Search & Autocomplete UI

#### What We Did:
We built an accessible, keyboard-navigable search autocomplete component (`SearchAutocomplete.tsx`) powered by a custom 300ms input debouncing hook (`useDebounce.ts`) and TanStack Query suggestions hook (`useSearchSuggestions.ts`).

#### Key Highlights & Architecture:
1. **300ms Input Debouncing (`useDebounce.ts`):** Prevents rapid keystrokes from firing unnecessary network queries. API calls trigger only when debounced query length >= 2 characters.
2. **Search Autocomplete Component (`SearchAutocomplete.tsx`):**
   - Prominent search input with `Search` icon and clear button (`X`).
   - Discriminated suggestions list displaying movie (`Clapperboard` icon) and location (`MapPin` icon) items.
   - Outside click dismissal via `useRef` and `useEffect` event listener.
   - High `z-50` z-index context ensuring dropdown renders smoothly above Leaflet map.
3. **Full Keyboard Navigation:**
   - `ArrowDown` & `ArrowUp` for option highlighting.
   - `Enter` key to confirm selection.
   - `Escape` key to close dropdown.
4. **WAI-ARIA Accessibility:** Implemented `role="combobox"`, `aria-autocomplete="list"`, `aria-expanded`, `role="listbox"`, and `role="option"` with `aria-selected` attributes.

---

### Phase 12 — Connect Search to Map Filtering

#### What We Did:
We connected search autocomplete selection to server-side movie location filtering (`GET /api/v1/movies?title=` for movie suggestions, `GET /api/v1/movies?location=` for location suggestions) and built an automatic Leaflet viewport bounds controller (`MapBoundsController.tsx`).

#### Key Highlights & Architecture:
1. **Backend Exact Filters (`movie_service.py` & `movies.py`):** Added `title` and `location` query parameters to `GET /api/v1/movies`, generating exact SoQL equality clauses (`lower(title) = 'escaped_title'` / `lower(locations) = 'escaped_location'`) with single-quote escaping.
2. **State Ownership & Query Invalidation (`HomePage.tsx`):**
   - Managed `selectedSuggestion` state in `HomePage.tsx`.
   - Derived `GetMoviesParams` (`{ title: value }` vs `{ location: value }`), automatically triggering TanStack Query refetches when selection updates.
   - Displayed active filter callout badge (`Filtering by movie: "Vertigo"`) with instant Reset button.
3. **Automatic Map Viewport Controller (`MapBoundsController.tsx`):**
   - Single marker: Centers map around location (`map.setView`) with zoom `15`.
   - Multiple markers: Fits bounds (`map.fitBounds`) around all location coordinates with padding `[40, 40]`.
   - Reset: Returns map to San Francisco default center (`[37.7749, -122.4194]`, zoom `12`) when search is cleared.

266: ---

### Phase 13 — Loading, Error, Empty States & Responsive UI Polish

#### What We Did:
We polished the application into a production-grade, interview-ready UI with extracted presentational components (`ResultStatus.tsx`, `ErrorState.tsx`), count pluralization, WAI-ARIA live region updates, background refetch status badges, and responsive map container heights.

#### Key Highlights & Architecture:
1. **Result Status & Accessibility (`ResultStatus.tsx`):**
   - Formats location count grammar ("1 filming location" vs "2 filming locations").
   - Includes `role="status"` and `aria-live="polite"` for screen-reader notifications.
   - Displays active filter badge (`Filtering by movie: "Vertigo"`) with an inline Reset button.
2. **Recoverable Error Feedback (`ErrorState.tsx`):**
   - Renders clear, friendly error messages with an explicit `Try Again` action (`refetch()`).
   - Disables retry button while refetching to prevent duplicate requests.
3. **Background Updating Overlay:**
   - Displays a non-blocking `"Updating map..."` pill in the top-right corner over the map while refetching filtered queries (`isFetching && !isLoading`).
4. **Responsive Ergonomics:**
   - Responsive container padding (`px-4 sm:px-6 lg:px-8`) and search input font size (`16px` on mobile preventing unwanted browser zoom).
   - Responsive map height (`h-[450px] md:h-[550px] lg:h-[650px]`).

287: ---

### Phase 14 — Full Testing & Reliability Pass

#### What We Did:
We conducted a comprehensive reliability, test coverage, and security audit across the full-stack repository, expanding test cases for upstream HTTP 403/404 handling, coordinate boundary constraints (-90.0, 90.0, -180.0, 180.0), and outside-click dropdown dismissal while verifying zero debug logs and zero committed secrets.

#### Key Highlights & Architecture:
1. **Backend Edge-Case Test Expansion (`test_datasf_client.py` & `test_movie_service.py`):**
   - Added HTTP 403/404 forbidden/not found upstream failure test assertions.
   - Added exact WGS84 boundary coordinate validation tests.
2. **Frontend Outside-Click Dismissal Test (`SearchAutocomplete.test.tsx`):**
   - Added test verifying container ref outside-click event handler dismisses dropdown suggestions cleanly.
3. **Full-Stack Reliability & Security Audit:**
   - 0 debug `console.log` or `print` statements in production source files.
   - Verified `.gitignore` prevents tracking `.env`, `.venv`, `node_modules`, `dist`, or `__pycache__`.

---

## 🧪 Testing & Quality Assurance Summary

We maintain **100% automated test suite pass rate** across backend and frontend:

### Backend Pytest Suite:
```bash
cd backend
.venv/bin/pytest -v
```
- **Coverage:** 62 tests across config, health, openapi/docs availability, DataSF client, MovieService, movies API, and search API.
- **Result:** `62 passed in 0.22s`

### Frontend Vitest Suite:
```bash
cd frontend
npm test
```
- **Coverage:** 18 tests across `App.test.tsx`, `MoviePopup.test.tsx`, and `SearchAutocomplete.test.tsx` (verifying outside-click dismissal, debouncing, keyboard navigation, server-side filtering, and error retry).
- **Result:** `18 passed in 3.09s`

### Production Build Verification:
```bash
cd frontend
npm run build
```
- **Result:** `✓ built in 178ms` (0 TypeScript / ESLint errors).

---

## 🚀 Next Steps

We are ready to move on to **Phase 15**!


