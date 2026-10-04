import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.store import store

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_store():
    store.reset()

def test_notify_party_success():
    res = client.post("/api/waitlist/p-101/notify")
    assert res.status_code == 200
    data = res.json()
    assert "party" in data
    assert "notification" in data
    assert data["party"]["status"] == "notified"
    assert data["party"]["notified_at"] is not None
    assert "TableHop" in data["notification"]["message"]
    assert data["notification"]["phone_number"] == data["party"]["phone_number"]

    # Verify notification log list has this notification
    logs_res = client.get("/api/notifications")
    assert logs_res.status_code == 200
    logs = logs_res.json()
    assert any(log["party_id"] == "p-101" for log in logs)

def test_notify_unknown_party_404():
    res = client.post("/api/waitlist/unknown-id/notify")
    assert res.status_code == 404
