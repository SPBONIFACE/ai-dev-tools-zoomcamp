import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models.db import DBParty, DBTable, DBNotificationLog
from app.models.schemas import (
    PartyResponse,
    PartyStatus,
    TableResponse,
    TableStatus,
    NotificationLogResponse,
    PartyCreate,
    AnalyticsSummaryResponse,
    NotifyPartyResponse,
)

# Initialize tables
Base.metadata.create_all(bind=engine)

SEED_PARTIES = [
    {
        "id": "p-101",
        "guest_name": "Elena Rostova",
        "party_size": 2,
        "phone_number": "+1 (555) 014-2201",
        "notes": "Window booth preferred. Quiet table.",
        "quoted_wait_min": 15,
        "status": "waiting",
    },
    {
        "id": "p-102",
        "guest_name": "Marcus Vance",
        "party_size": 4,
        "phone_number": "+1 (555) 018-8832",
        "notes": "Needs 1 high chair.",
        "quoted_wait_min": 30,
        "status": "waiting",
    },
    {
        "id": "p-103",
        "guest_name": "Sarah Jenkins",
        "party_size": 6,
        "phone_number": "+1 (555) 019-9941",
        "notes": "Birthday celebration.",
        "quoted_wait_min": 40,
        "status": "notified",
    },
]

SEED_TABLES = [
    {"id": "T1", "name": "Table 1", "capacity": 2, "status": "available"},
    {"id": "T2", "name": "Table 2", "capacity": 2, "status": "available"},
    {"id": "T3", "name": "Table 3", "capacity": 4, "status": "available"},
    {"id": "T4", "name": "Table 4", "capacity": 4, "status": "available"},
    {"id": "T5", "name": "Table 5", "capacity": 6, "status": "available"},
    {"id": "T6", "name": "Table 6", "capacity": 6, "status": "available"},
]

class SQLAlchemyStore:
    def __init__(self):
        self.init_db()

    def init_db(self):
        db: Session = SessionLocal()
        try:
            # Check if tables seeded
            if db.query(DBTable).count() == 0:
                for t in SEED_TABLES:
                    db.add(DBTable(**t))
                now = datetime.now(timezone.utc)
                for p in SEED_PARTIES:
                    notified_at = now if p["status"] == "notified" else None
                    db.add(DBParty(**p, created_at=now, notified_at=notified_at))
                db.add(
                    DBNotificationLog(
                        id="notif-1",
                        party_id="p-103",
                        phone_number="+1 (555) 019-9941",
                        message="TableHop: Your table is ready! Please report to the host stand within 5 minutes.",
                        sent_at=now,
                    )
                )
                db.commit()
        finally:
            db.close()

    def reset(self):
        db: Session = SessionLocal()
        try:
            db.query(DBNotificationLog).delete()
            db.query(DBParty).delete()
            db.query(DBTable).delete()
            db.commit()

            # Re-seed
            for t in SEED_TABLES:
                db.add(DBTable(**t))
            now = datetime.now(timezone.utc)
            for p in SEED_PARTIES:
                notified_at = now if p["status"] == "notified" else None
                db.add(DBParty(**p, created_at=now, notified_at=notified_at))
            db.add(
                DBNotificationLog(
                    id="notif-1",
                    party_id="p-103",
                    phone_number="+1 (555) 019-9941",
                    message="TableHop: Your table is ready! Please report to the host stand within 5 minutes.",
                    sent_at=now,
                )
            )
            db.commit()
        finally:
            db.close()

    def _to_party_response(self, row: DBParty) -> PartyResponse:
        return PartyResponse(
            id=row.id,
            guest_name=row.guest_name,
            party_size=row.party_size,
            phone_number=row.phone_number,
            notes=row.notes,
            quoted_wait_min=row.quoted_wait_min,
            status=PartyStatus(row.status),
            table_id=row.table_id,
            created_at=row.created_at,
            notified_at=row.notified_at,
            seated_at=row.seated_at,
        )

    def _to_table_response(self, row: DBTable) -> TableResponse:
        return TableResponse(
            id=row.id,
            name=row.name,
            capacity=row.capacity,
            status=TableStatus(row.status),
            current_party_id=row.current_party_id,
        )

    def _to_notification_response(self, row: DBNotificationLog) -> NotificationLogResponse:
        return NotificationLogResponse(
            id=row.id,
            party_id=row.party_id,
            phone_number=row.phone_number,
            message=row.message,
            sent_at=row.sent_at,
        )

    # --- Waitlist Methods ---
    def get_parties(self, status: Optional[PartyStatus] = None) -> List[PartyResponse]:
        db: Session = SessionLocal()
        try:
            query = db.query(DBParty)
            if status:
                query = query.filter(DBParty.status == status.value)
            rows = query.order_by(DBParty.created_at.asc()).all()
            return [self._to_party_response(r) for r in rows]
        finally:
            db.close()

    def get_party(self, party_id: str) -> Optional[PartyResponse]:
        db: Session = SessionLocal()
        try:
            row = db.query(DBParty).filter(DBParty.id == party_id).first()
            return self._to_party_response(row) if row else None
        finally:
            db.close()

    def add_party(self, data: PartyCreate) -> PartyResponse:
        db: Session = SessionLocal()
        try:
            active_count = db.query(DBParty).filter(
                DBParty.status.in_([PartyStatus.WAITING.value, PartyStatus.NOTIFIED.value])
            ).count()
            auto_wait = (active_count + 1) * 10
            quoted_wait = data.quoted_wait_min if data.quoted_wait_min is not None else auto_wait

            now = datetime.now(timezone.utc)
            party_id = f"p-{uuid.uuid4().hex[:8]}"
            db_party = DBParty(
                id=party_id,
                guest_name=data.guest_name,
                party_size=data.party_size,
                phone_number=data.phone_number,
                notes=data.notes,
                quoted_wait_min=quoted_wait,
                status=PartyStatus.WAITING.value,
                table_id=None,
                created_at=now,
            )
            db.add(db_party)
            db.commit()
            db.refresh(db_party)
            return self._to_party_response(db_party)
        finally:
            db.close()

    def update_party_status(self, party_id: str, status: PartyStatus) -> Optional[PartyResponse]:
        db: Session = SessionLocal()
        try:
            row = db.query(DBParty).filter(DBParty.id == party_id).first()
            if not row:
                return None
            row.status = status.value
            now = datetime.now(timezone.utc)
            if status == PartyStatus.NOTIFIED:
                row.notified_at = now
            elif status == PartyStatus.SEATED:
                row.seated_at = now
            db.commit()
            db.refresh(row)
            return self._to_party_response(row)
        finally:
            db.close()

    def cancel_party(self, party_id: str) -> Optional[PartyResponse]:
        db: Session = SessionLocal()
        try:
            row = db.query(DBParty).filter(DBParty.id == party_id).first()
            if not row:
                return None
            if row.table_id:
                table_row = db.query(DBTable).filter(DBTable.id == row.table_id).first()
                if table_row:
                    table_row.status = TableStatus.AVAILABLE.value
                    table_row.current_party_id = None
            row.status = PartyStatus.CANCELLED.value
            row.table_id = None
            db.commit()
            db.refresh(row)
            return self._to_party_response(row)
        finally:
            db.close()

    # --- Table Methods ---
    def get_tables(self) -> List[TableResponse]:
        db: Session = SessionLocal()
        try:
            rows = db.query(DBTable).order_by(DBTable.id.asc()).all()
            return [self._to_table_response(r) for r in rows]
        finally:
            db.close()

    def seat_party(self, table_id: str, party_id: str) -> TableResponse:
        db: Session = SessionLocal()
        try:
            table = db.query(DBTable).filter(DBTable.id == table_id).first()
            if not table:
                raise KeyError("Table not found")
            if table.status == TableStatus.OCCUPIED.value:
                raise ValueError("Table is already occupied")

            party = db.query(DBParty).filter(DBParty.id == party_id).first()
            if not party:
                raise KeyError("Party not found")

            now = datetime.now(timezone.utc)
            table.status = TableStatus.OCCUPIED.value
            table.current_party_id = party.id

            party.status = PartyStatus.SEATED.value
            party.table_id = table.id
            party.seated_at = now

            db.commit()
            db.refresh(table)
            return self._to_table_response(table)
        finally:
            db.close()

    def clear_table(self, table_id: str) -> TableResponse:
        db: Session = SessionLocal()
        try:
            table = db.query(DBTable).filter(DBTable.id == table_id).first()
            if not table:
                raise KeyError("Table not found")

            table.status = TableStatus.AVAILABLE.value
            table.current_party_id = None
            db.commit()
            db.refresh(table)
            return self._to_table_response(table)
        finally:
            db.close()

    # --- Notification & Analytics Methods ---
    def notify_party(self, party_id: str) -> NotifyPartyResponse:
        db: Session = SessionLocal()
        try:
            party = db.query(DBParty).filter(DBParty.id == party_id).first()
            if not party:
                raise KeyError("Party not found")

            now = datetime.now(timezone.utc)
            party.status = PartyStatus.NOTIFIED.value
            party.notified_at = now

            notif_id = f"notif-{uuid.uuid4().hex[:8]}"
            notif = DBNotificationLog(
                id=notif_id,
                party_id=party.id,
                phone_number=party.phone_number,
                message=f"TableHop: Your table is ready for {party.guest_name}! Please proceed to the host stand.",
                sent_at=now,
            )
            db.add(notif)
            db.commit()
            db.refresh(party)
            db.refresh(notif)
            return NotifyPartyResponse(
                party=self._to_party_response(party),
                notification=self._to_notification_response(notif),
            )
        finally:
            db.close()

    def get_notifications(self) -> List[NotificationLogResponse]:
        db: Session = SessionLocal()
        try:
            rows = db.query(DBNotificationLog).order_by(DBNotificationLog.sent_at.desc()).all()
            return [self._to_notification_response(r) for r in rows]
        finally:
            db.close()

    def get_analytics_summary(self) -> AnalyticsSummaryResponse:
        db: Session = SessionLocal()
        try:
            active_parties = db.query(DBParty).filter(
                DBParty.status.in_([PartyStatus.WAITING.value, PartyStatus.NOTIFIED.value])
            ).all()
            total_seated = db.query(DBParty).filter(
                DBParty.status == PartyStatus.SEATED.value
            ).count()
            avg_wait = (
                round(sum(p.quoted_wait_min for p in active_parties) / len(active_parties))
                if active_parties
                else 0
            )
            return AnalyticsSummaryResponse(
                active_waiting=len(active_parties),
                avg_wait_min=avg_wait,
                total_seated_today=total_seated,
            )
        finally:
            db.close()

store = SQLAlchemyStore()
