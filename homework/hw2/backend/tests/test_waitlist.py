import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.store import store

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_store():
    store.reset()

def test_create_party_auto_wait_time():
    # Initially 3 active parties in seed data -> (3 + 1) * 10 = 40 mins
    res = client.post(
        "/api/waitlist",
        json={
            "guest_name": "David Kim",
            "party_size": 2,
            "phone_number": "+15550001111",
            "notes": "Quiet table please",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["guest_name"] == "David Kim"
    assert data["party_size"] == 2
    assert data["quoted_wait_min"] == 40
    assert data["status"] == "waiting"
    assert "id" in data
    assert "created_at" in data

def test_create_party_manual_wait_time_override():
    res = client.post(
        "/api/waitlist",
        json={
            "guest_name": "VIP Guest",
            "party_size": 4,
            "phone_number": "+15550002222",
            "quoted_wait_min": 15,
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["quoted_wait_min"] == 15

def test_get_waitlist_all_and_filtered():
    res_all = client.get("/api/waitlist")
    assert res_all.status_code == 200
    parties = res_all.json()
    assert len(parties) >= 3

    # Filter by waiting
    res_waiting = client.get("/api/waitlist?status=waiting")
    assert res_waiting.status_code == 200
    waiting_parties = res_waiting.json()
    for p in waiting_parties:
        assert p["status"] == "waiting"

def test_get_party_by_id_found_and_not_found():
    res = client.get("/api/waitlist/p-101")
    assert res.status_code == 200
    assert res.json()["guest_name"] == "Elena Rostova"

    res_404 = client.get("/api/waitlist/unknown-id")
    assert res_404.status_code == 404

def test_patch_party_status():
    res = client.patch("/api/waitlist/p-101/status", json={"status": "notified"})
    assert res.status_code == 200
    assert res.json()["status"] == "notified"
    assert res.json()["notified_at"] is not None

def test_cancel_party():
    res = client.post("/api/waitlist/p-101/cancel")
    assert res.status_code == 200
    assert res.json()["status"] == "cancelled"

    # Verify status is updated in get
    res_get = client.get("/api/waitlist/p-101")
    assert res_get.json()["status"] == "cancelled"
