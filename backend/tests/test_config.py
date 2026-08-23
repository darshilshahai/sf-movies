from app.core.config import get_settings


def test_settings_load():
    settings = get_settings()
    assert settings.app_name == "SF Movies API"
    assert settings.api_prefix == "/api/v1"
    assert settings.frontend_url == "http://localhost:5173"
