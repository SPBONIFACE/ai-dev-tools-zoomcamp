import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.store import store

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_store():
    store.reset()

def test_list_tables_contains_six_seeded_tables():
    res = client.get("/api/tables")
    assert res.status_code == 200
    tables = res.json()
    assert len(tables) == 6
    capacities = {t["capacity"] for t in tables}
    assert capacities == {2, 4, 6}
    for t in tables:
        assert t["status"] == "available"
        assert t["current_party_id"] is None

def test_seat_party_success():
    res = client.post("/api/tables/T3/seat", json={"party_id": "p-102"})
    assert res.status_code == 200
    table_data = res.json()
    assert table_data["id"] == "T3"
    assert table_data["status"] == "occupied"
    assert table_data["current_party_id"] == "p-102"

    # Verify party is marked seated with table_id
    party_res = client.get("/api/waitlist/p-102")
    assert party_res.status_code == 200
    party_data = party_res.json()
    assert party_data["status"] == "seated"
    assert party_data["table_id"] == "T3"
    assert party_data["seated_at"] is not None

def test_seat_party_already_occupied_error():
    # Seat party at T1
    client.post("/api/tables/T1/seat", json={"party_id": "p-101"})

    # Try to seat another party at T1
    res_conflict = client.post("/api/tables/T1/seat", json={"party_id": "p-102"})
    assert res_conflict.status_code == 400
    assert "already occupied" in res_conflict.json()["detail"].lower()

def test_seat_party_not_found_errors():
    # Unknown table
    res_unknown_table = client.post("/api/tables/UNKNOWN/seat", json={"party_id": "p-101"})
    assert res_unknown_table.status_code == 404

    # Unknown party
    res_unknown_party = client.post("/api/tables/T1/seat", json={"party_id": "unknown-party"})
    assert res_unknown_party.status_code == 404

def test_clear_table_success():
    # Seat first
    client.post("/api/tables/T2/seat", json={"party_id": "p-101"})

    # Clear table
    res_clear = client.post("/api/tables/T2/clear")
    assert res_clear.status_code == 200
    assert res_clear.json()["status"] == "available"
    assert res_clear.json()["current_party_id"] is None

def test_clear_unknown_table_404():
    res = client.post("/api/tables/UNKNOWN/clear")
    assert res.status_code == 404
