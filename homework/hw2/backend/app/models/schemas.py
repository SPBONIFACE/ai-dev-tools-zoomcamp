from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class PartyStatus(str, Enum):
    WAITING = "waiting"
    NOTIFIED = "notified"
    SEATED = "seated"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class TableStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"

class PartyCreate(BaseModel):
    guest_name: str = Field(..., min_length=1, description="Primary guest name")
    party_size: int = Field(..., ge=1, le=12, description="Number of guests (1-12)")
    phone_number: str = Field(..., min_length=1, description="Contact phone number")
    notes: Optional[str] = Field(None, description="Special requests or notes")
    quoted_wait_min: Optional[int] = Field(None, ge=0, description="Host manual wait time quote in minutes")

class PartyStatusUpdate(BaseModel):
    status: PartyStatus

class PartyResponse(BaseModel):
    id: str
    guest_name: str
    party_size: int
    phone_number: str
    notes: Optional[str] = None
    quoted_wait_min: int
    status: PartyStatus
    table_id: Optional[str] = None
    created_at: datetime
    notified_at: Optional[datetime] = None
    seated_at: Optional[datetime] = None

class TableResponse(BaseModel):
    id: str
    name: str
    capacity: int
    status: TableStatus
    current_party_id: Optional[str] = None

class SeatPartyRequest(BaseModel):
    party_id: str

class NotificationLogResponse(BaseModel):
    id: str
    party_id: str
    phone_number: str
    message: str
    sent_at: datetime

class AnalyticsSummaryResponse(BaseModel):
    active_waiting: int
    avg_wait_min: int
    total_seated_today: int

class NotifyPartyResponse(BaseModel):
    party: PartyResponse
    notification: NotificationLogResponse

