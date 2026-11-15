# Given # When # Then
import httpx
from fastapi.testclient import TestClient

from src.main import app


class TestHealth:
    def test_should_return_ok_when_health_endpoint_called(self) -> None:
        # Given
        client = TestClient(app)

        # When
        response: httpx.Response = client.request("GET", "/health")

        # Then
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
