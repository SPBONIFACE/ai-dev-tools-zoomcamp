from typing import List
from fastapi import APIRouter
from app.models.schemas import NotificationLogResponse
from app.services.store import store

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationLogResponse])
def get_notifications():
    return store.get_notifications()
