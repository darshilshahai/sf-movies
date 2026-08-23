# SF Movies Explorer - Backend API

FastAPI backend abstraction over the DataSF Film Locations API (`yitu-d5am`).

## Setup & Running with `uv`

```bash
# Sync dependencies & create virtual environment
uv sync

# Run development server
uv run uvicorn app.main:app --reload --port 8000
```

## Running Tests

```bash
uv run pytest
```

## Deployment (Render)

- **Root Directory**: `backend`
- **Build Command**: `uv sync`
- **Start Command**: `.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port $PORT`

