import pytest
from fastapi.testclient import TestClient
from main import app

def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_frontend_is_served():
    client = TestClient(app)
    r = client.get("/app/")
    assert r.status_code == 200
    assert "Agente WhatsApp SEPLAN" in r.text
