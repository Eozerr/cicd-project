import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_system_metrics(client):
    response = client.get("/system")
    assert response.status_code == 200

def test_system_metrics_returns_json(client):
    response = client.get("/system")
    data = response.get_json()
    assert data["status"] == "ok"
    assert "cpu" in data
    assert "memory" in data
    assert "disk" in data