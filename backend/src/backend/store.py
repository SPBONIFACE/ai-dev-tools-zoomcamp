import hashlib
import os
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4
from fastapi import WebSocket
from backend.models import Session, UserProfile

def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()
    return f"{salt}${pwd_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, pwd_hash = stored_hash.split("$", 1)
        test_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()
        return test_hash == pwd_hash
    except Exception:
        return False

class InMemoryStore:
    def __init__(self) -> None:
        self.users: dict[str, dict[str, Any]] = {}
        self.users_by_email: dict[str, str] = {}
        self.tokens: dict[str, str] = {}  # token -> user_id
        self.sessions: dict[str, Session] = {}  # session_id -> Session
        self.sessions_by_token: dict[str, str] = {}  # join_token -> session_id
        self.board_elements: dict[str, dict[str, dict[str, Any]]] = {}  # session_id -> {el_id -> el}
        self.room_connections: dict[str, set[WebSocket]] = {}  # token -> set of WebSockets
        self.seed_data()

    def seed_data(self) -> None:
        # Seed Interviewer
        user_id = "00000000-0000-0000-0000-000000000001"
        now = datetime.now(timezone.utc)
        self.users[user_id] = {
            "id": user_id,
            "email": "interviewer@example.com",
            "password_hash": hash_password("password123"),
            "created_at": now,
        }
        self.users_by_email["interviewer@example.com"] = user_id
        self.tokens["demo-token-123"] = user_id

        # Seed Interview Session
        session_id = "11111111-1111-1111-1111-111111111111"
        join_token = "demo-token"
        seed_session = Session(
            id=session_id,
            owner_id=user_id,
            title="Distributed Rate Limiter Design",
            candidate_name="Alexey Grigorev",
            role_title="Staff Software Engineer",
            status="live",
            join_token=join_token,
            notes="Discuss sliding window log vs token bucket. Great system depth.",
            link_revoked=False,
            created_at=now,
            updated_at=now,
            ended_at=None,
        )
        self.sessions[session_id] = seed_session
        self.sessions_by_token[join_token] = session_id

        # Seed Board Elements for this session
        self.board_elements[session_id] = {
            "node-client": {
                "id": "node-client",
                "kind": "node",
                "shape": "client",
                "x": 100,
                "y": 240,
                "w": 150,
                "h": 74,
                "label": "Client App",
                "sub": "web / mobile",
                "color": "node-service",
            },
            "node-gateway": {
                "id": "node-gateway",
                "kind": "node",
                "shape": "gateway",
                "x": 360,
                "y": 240,
                "w": 160,
                "h": 74,
                "label": "API Gateway",
                "sub": "Envoy / Kong",
                "color": "node-edge-net",
            },
            "node-redis": {
                "id": "node-redis",
                "kind": "node",
                "shape": "cache",
                "x": 620,
                "y": 140,
                "w": 140,
                "h": 92,
                "label": "Redis Cluster",
                "sub": "Sliding Window",
                "color": "node-data",
            },
            "node-service": {
                "id": "node-service",
                "kind": "node",
                "shape": "service",
                "x": 620,
                "y": 320,
                "w": 160,
                "h": 80,
                "label": "Backend Service",
                "sub": "FastAPI Core",
                "color": "node-service",
            },
            "edge-client-gw": {
                "id": "edge-client-gw",
                "kind": "edge",
                "from": "node-client",
                "to": "node-gateway",
                "style": "solid",
                "arrow": "end",
                "label": "HTTPS",
                "color": "node-edge-net",
            },
            "edge-gw-redis": {
                "id": "edge-gw-redis",
                "kind": "edge",
                "from": "node-gateway",
                "to": "node-redis",
                "style": "dashed",
                "arrow": "end",
                "label": "Check Quota",
                "color": "node-data",
            },
            "edge-gw-svc": {
                "id": "edge-gw-svc",
                "kind": "edge",
                "from": "node-gateway",
                "to": "node-service",
                "style": "solid",
                "arrow": "end",
                "label": "Forward req",
                "color": "node-service",
            },
            "note-reqs": {
                "id": "note-reqs",
                "kind": "node",
                "shape": "note",
                "x": 840,
                "y": 180,
                "w": 180,
                "h": 140,
                "label": "Requirements",
                "sub": "100k rps, <10ms overhead, multi-region",
                "color": "node-note",
            },
        }

    # User & Auth helpers
    def create_user(self, email: str, password: str) -> UserProfile:
        user_id = str(uuid4())
        now = datetime.now(timezone.utc)
        user_dict = {
            "id": user_id,
            "email": email.lower().strip(),
            "password_hash": hash_password(password),
            "created_at": now,
        }
        self.users[user_id] = user_dict
        self.users_by_email[email.lower().strip()] = user_id
        return UserProfile(id=user_id, email=email, created_at=now)

    def get_user_by_email(self, email: str) -> Optional[dict[str, Any]]:
        user_id = self.users_by_email.get(email.lower().strip())
        return self.users.get(user_id) if user_id else None

    def get_user_by_id(self, user_id: str) -> Optional[UserProfile]:
        user_dict = self.users.get(user_id)
        if not user_dict:
            return None
        return UserProfile(
            id=user_dict["id"],
            email=user_dict["email"],
            created_at=user_dict["created_at"],
        )

    def create_token_for_user(self, user_id: str) -> str:
        token = os.urandom(24).hex()
        self.tokens[token] = user_id
        return token

    def get_user_id_by_token(self, token: str) -> Optional[str]:
        return self.tokens.get(token)

    def revoke_token(self, token: str) -> bool:
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False

# Global singleton store
store = InMemoryStore()
