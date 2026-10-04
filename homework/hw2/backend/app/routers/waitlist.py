from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.models.schemas import PartyCreate, PartyResponse, PartyStatus, PartyStatusUpdate, NotifyPartyResponse
from app.services.store import store

router = APIRouter(prefix="/api/waitlist", tags=["Waitlist"])

@router.get("", response_model=List[PartyResponse])
def get_waitlist(status: Optional[PartyStatus] = Query(None, description="Filter by party status")):
    return store.get_parties(status=status)

@router.post("", response_model=PartyResponse, status_code=status.HTTP_201_CREATED)
def create_party(party_in: PartyCreate):
    return store.add_party(party_in)

@router.get("/{party_id}", response_model=PartyResponse)
def get_party(party_id: str):
    party = store.get_party(party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return party

@router.patch("/{party_id}/status", response_model=PartyResponse)
def update_party_status(party_id: str, update_in: PartyStatusUpdate):
    party = store.update_party_status(party_id, update_in.status)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return party

@router.post("/{party_id}/notify", response_model=NotifyPartyResponse)
def notify_party(party_id: str):
    try:
        return store.notify_party(party_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{party_id}/cancel", response_model=PartyResponse)
def cancel_party(party_id: str):
    party = store.cancel_party(party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return party

