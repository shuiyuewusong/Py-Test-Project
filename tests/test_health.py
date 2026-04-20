from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "degraded")
    assert "db_type" in data
    assert "db" in data


def test_health_contains_env(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert "app_env" in response.json()
