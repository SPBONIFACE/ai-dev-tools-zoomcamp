from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class DBParty(Base):
    __tablename__ = "parties"

    id = Column(String, primary_key=True, index=True)
    guest_name = Column(String, nullable=False)
    party_size = Column(Integer, nullable=False)
    phone_number = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    quoted_wait_min = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="waiting")
    table_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    notified_at = Column(DateTime, nullable=True)
    seated_at = Column(DateTime, nullable=True)

class DBTable(Base):
    __tablename__ = "tables"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="available")
    current_party_id = Column(String, nullable=True)

class DBNotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(String, primary_key=True, index=True)
    party_id = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    message = Column(String, nullable=False)
    sent_at = Column(DateTime, default=utcnow, nullable=False)
