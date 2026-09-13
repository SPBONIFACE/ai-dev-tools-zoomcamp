import os
from datetime import datetime, timezone
from typing import List
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from backend.auth import get_current_user
from backend.models import (
    CreateSessionRequest,
    Session,
    SuccessResponse,
    UpdateSessionRequest,
    UserProfile,
)
from backend.store import store

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])

def generate_join_token() -> str:
    # 14-char alphanumeric token matching frontend generator
    return os.urandom(8).hex()[:14]

@router.get("", response_model=List[Session])
def list_sessions(user: UserProfile = Depends(get_current_user)):
    user_sessions = [
        s for s in store.sessions.values() if s.owner_id == user.id
    ]
    user_sessions.sort(key=lambda s: s.created_at, reverse=True)
    return user_sessions

@router.post("", response_model=Session, status_code=status.HTTP_201_CREATED)
def create_session(data: CreateSessionRequest, user: UserProfile = Depends(get_current_user)):
    session_id = str(uuid4())
    join_token = generate_join_token()
    now = datetime.now(timezone.utc)

    session = Session(
        id=session_id,
        owner_id=user.id,
        title=data.title,
        candidate_name=data.candidate_name,
        role_title=data.role_title,
        status="live",
        join_token=join_token,
        notes="",
        link_revoked=False,
        created_at=now,
        updated_at=now,
        ended_at=None,
    )
    store.sessions[session_id] = session
    store.sessions_by_token[join_token] = session_id
    store.board_elements[session_id] = {}
    return session

@router.get("/{id}", response_model=Session)
def get_session(id: str, user: UserProfile = Depends(get_current_user)):
    session = store.sessions.get(id)
    if not session or session.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session

@router.patch("/{id}", response_model=Session)
def update_session(id: str, patch: UpdateSessionRequest, user: UserProfile = Depends(get_current_user)):
    session = store.sessions.get(id)
    if not session or session.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    now = datetime.now(timezone.utc)
    updated_dict = session.model_dump()
    patch_dict = patch.model_dump(exclude_unset=True)

    for k, v in patch_dict.items():
        if v is not None:
            updated_dict[k] = v

    if patch.status == "completed" and session.status != "completed":
        updated_dict["ended_at"] = now
    elif patch.status in ("draft", "live"):
        updated_dict["ended_at"] = None

    updated_dict["updated_at"] = now
    new_session = Session(**updated_dict)
    store.sessions[id] = new_session
    return new_session

@router.delete("/{id}", response_model=SuccessResponse)
def delete_session(id: str, user: UserProfile = Depends(get_current_user)):
    session = store.sessions.get(id)
    if not session or session.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if session.join_token in store.sessions_by_token:
        del store.sessions_by_token[session.join_token]
    if id in store.board_elements:
        del store.board_elements[id]
    del store.sessions[id]

    return SuccessResponse(ok=True)
