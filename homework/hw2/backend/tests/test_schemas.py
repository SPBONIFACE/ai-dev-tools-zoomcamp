import pytest
from pydantic import ValidationError
from app.models.schemas import (
    PartyCreate,
    PartyStatus,
    PartyStatusUpdate,
    PartyResponse,
    TableStatus,
    TableResponse,
    SeatPartyRequest,
    NotificationLogResponse,
    AnalyticsSummaryResponse,
)

def test_party_create_valid():
    data = {
        "guest_name": "Elena Rostova",
        "party_size": 4,
        "phone_number": "+15551234567",
        "notes": "Window seat preferred",
        "quoted_wait_min": 25,
    }
    party_in = PartyCreate(**data)
    assert party_in.guest_name == "Elena Rostova"
    assert party_in.party_size == 4
    assert party_in.phone_number == "+15551234567"
    assert party_in.quoted_wait_min == 25

def test_party_create_optional_wait_time():
    data = {
        "guest_name": "Marcus Vance",
        "party_size": 2,
        "phone_number": "+15559876543",
    }
    party_in = PartyCreate(**data)
    assert party_in.quoted_wait_min is None

def test_party_create_invalid_party_size():
    with pytest.raises(ValidationError):
        PartyCreate(guest_name="Invalid Party", party_size=0, phone_number="123")

    with pytest.raises(ValidationError):
        PartyCreate(guest_name="Invalid Party", party_size=15, phone_number="123")

def test_party_status_enum():
    assert PartyStatus.WAITING == "waiting"
    assert PartyStatus.NOTIFIED == "notified"
    assert PartyStatus.SEATED == "seated"
    assert PartyStatus.CANCELLED == "cancelled"
    assert PartyStatus.NO_SHOW == "no_show"

    with pytest.raises(ValidationError):
        PartyStatusUpdate(status="unknown_status")

def test_seat_party_request():
    req = SeatPartyRequest(party_id="party-123")
    assert req.party_id == "party-123"

def test_table_response_schema():
    table = TableResponse(
        id="T1",
        name="Table 1",
        capacity=4,
        status=TableStatus.AVAILABLE,
        current_party_id=None,
    )
    assert table.id == "T1"
    assert table.capacity == 4
    assert table.status == "available"

def test_analytics_summary_schema():
    analytics = AnalyticsSummaryResponse(
        active_waiting=5,
        avg_wait_min=20,
        total_seated_today=12,
    )
    assert analytics.active_waiting == 5
    assert analytics.avg_wait_min == 20
    assert analytics.total_seated_today == 12
