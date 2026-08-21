# SF Movies Explorer - Backend API

FastAPI backend abstraction over the DataSF Film Locations API (`yitu-d5am`).

## Setup & Running

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```
