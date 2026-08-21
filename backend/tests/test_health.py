from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test GET /api/v1/health endpoint returns 200 OK and correct JSON body."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "sf-movies-api"
    }
