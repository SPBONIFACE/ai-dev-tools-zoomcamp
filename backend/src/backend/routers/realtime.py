import json
from typing import Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.store import store

router = APIRouter(tags=["Realtime"])

@router.websocket("/ws/board/{token}")
async def websocket_board_endpoint(
    websocket: WebSocket,
    token: str,
    name: Optional[str] = "Anonymous",
    role: Optional[str] = "candidate",
):
    await websocket.accept()

    if token not in store.room_connections:
        store.room_connections[token] = set()
    store.room_connections[token].add(websocket)

    # Broadcast join event to all peers in room
    join_notice = {
        "type": "presence",
        "action": "join",
        "participant": {"name": name, "role": role},
        "count": len(store.room_connections[token]),
    }
    for peer in list(store.room_connections[token]):
        if peer != websocket:
            try:
                await peer.send_json(join_notice)
            except Exception:
                pass

    try:
        while True:
            text = await websocket.receive_text()
            try:
                data = json.loads(text)
            except Exception:
                continue

            # If message contains board operations, persist them in the store
            if data.get("type") == "board_ops" and "ops" in data:
                session_id = store.sessions_by_token.get(token)
                if session_id and session_id in store.sessions:
                    session = store.sessions[session_id]
                    if not session.link_revoked and session.status != "completed":
                        if session_id not in store.board_elements:
                            store.board_elements[session_id] = {}
                        for op in data["ops"]:
                            if op.get("type") == "upsert" and op.get("el"):
                                el_id = op["el"].get("id")
                                if el_id:
                                    store.board_elements[session_id][el_id] = op["el"]
                            elif op.get("type") == "delete" and op.get("id"):
                                store.board_elements[session_id].pop(op["id"], None)
                        await websocket.send_json({"type": "ops_ack", "status": "ok"})

            # Broadcast to all other peers in the room
            for peer in list(store.room_connections.get(token, [])):
                if peer != websocket:
                    try:
                        await peer.send_text(text)
                    except Exception:
                        pass

    except WebSocketDisconnect:
        pass
    finally:
        if token in store.room_connections:
            store.room_connections[token].discard(websocket)
            leave_notice = {
                "type": "presence",
                "action": "leave",
                "participant": {"name": name, "role": role},
                "count": len(store.room_connections[token]),
            }
            for peer in list(store.room_connections[token]):
                try:
                    await peer.send_json(leave_notice)
                except Exception:
                    pass
