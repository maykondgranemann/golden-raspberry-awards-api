from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAPI:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["api_status"] == "running"
        assert "last_tests_run" in json_response
        assert isinstance(json_response["last_tests_run"], str)

    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "Golden Raspberry Awards API is running!"
