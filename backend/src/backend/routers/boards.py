from fastapi import APIRouter, Depends, HTTPException, status
from backend.auth import get_current_user
from backend.models import (
    BoardJoinResponse,
    BoardOwnershipResponse,
    BoardSessionSummary,
    PushOpsRequest,
    SuccessResponse,
    UserProfile,
)
from backend.store import store

router = APIRouter(prefix="/api/boards", tags=["Board"])

@router.get("/{token}", response_model=BoardJoinResponse)
def join_board(token: str):
    session_id = store.sessions_by_token.get(token)
    if not session_id or session_id not in store.sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    session = store.sessions[session_id]
    if session.link_revoked:
        return BoardJoinResponse(
            found=True,
            revoked=True,
            session=BoardSessionSummary(
                id=session.id,
                title=session.title,
                role_title=session.role_title,
                candidate_name=session.candidate_name,
                status=session.status,
                link_revoked=True,
            ),
            elements=[],
        )

    elements_dict = store.board_elements.get(session.id, {})
    elements = list(elements_dict.values())

    return BoardJoinResponse(
        found=True,
        revoked=False,
        session=BoardSessionSummary(
            id=session.id,
            title=session.title,
            role_title=session.role_title,
            candidate_name=session.candidate_name,
            status=session.status,
            link_revoked=False,
        ),
        elements=elements,
    )

@router.post("/{token}/ops", response_model=SuccessResponse)
def push_ops(token: str, payload: PushOpsRequest):
    session_id = store.sessions_by_token.get(token)
    if not session_id or session_id not in store.sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    session = store.sessions[session_id]
    if session.link_revoked or session.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session link is revoked or session is completed",
        )

    if session.id not in store.board_elements:
        store.board_elements[session.id] = {}

    for op in payload.ops:
        if op.type == "upsert" and op.el:
            el_id = op.el.get("id")
            if el_id:
                store.board_elements[session.id][el_id] = op.el
        elif op.type == "delete" and op.id:
            store.board_elements[session.id].pop(op.id, None)

    return SuccessResponse(ok=True)

@router.get("/{token}/owned", response_model=BoardOwnershipResponse)
def get_owned_board(token: str, user: UserProfile = Depends(get_current_user)):
    session_id = store.sessions_by_token.get(token)
    if not session_id or session_id not in store.sessions:
        return BoardOwnershipResponse(owned=False, session=None)

    session = store.sessions[session_id]
    if session.owner_id == user.id:
        return BoardOwnershipResponse(owned=True, session=session)

    return BoardOwnershipResponse(owned=False, session=None)
