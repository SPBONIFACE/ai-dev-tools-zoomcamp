from typing import List
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import TableResponse, SeatPartyRequest
from app.services.store import store

router = APIRouter(prefix="/api/tables", tags=["Tables"])

@router.get("", response_model=List[TableResponse])
def get_tables():
    return store.get_tables()

@router.post("/{table_id}/seat", response_model=TableResponse)
def seat_party(table_id: str, payload: SeatPartyRequest):
    try:
        return store.seat_party(table_id, payload.party_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{table_id}/clear", response_model=TableResponse)
def clear_table(table_id: str):
    try:
        return store.clear_table(table_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
