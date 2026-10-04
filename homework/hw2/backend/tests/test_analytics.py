import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.store import store

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_store():
    store.reset()

def test_analytics_summary_default_state():
    res = client.get("/api/analytics/summary")
    assert res.status_code == 200
    data = res.json()
    # 3 active parties in seed data: 15, 30, 40 min waits -> avg is (15+30+40)/3 = 28.33 -> 28
    assert data["active_waiting"] == 3
    assert data["avg_wait_min"] == 28
    assert data["total_seated_today"] == 0

def test_analytics_summary_updates_on_seating():
    # Seat one party
    client.post("/api/tables/T1/seat", json={"party_id": "p-101"})

    res = client.get("/api/analytics/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["active_waiting"] == 2
    assert data["total_seated_today"] == 1
