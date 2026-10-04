from app.database import SessionLocal
from app.models.db import DBParty, DBTable, DBNotificationLog
from app.models.schemas import PartyCreate
from app.services.store import store

def test_database_persistence_across_sessions():
    store.reset()

    # Add a party through the store
    party = store.add_party(
        PartyCreate(
            guest_name="Persistence Test Guest",
            party_size=3,
            phone_number="+15559998888",
            notes="Testing SQLite persistence",
        )
    )

    # Open a fresh independent database session to assert persistence
    db = SessionLocal()
    try:
        row = db.query(DBParty).filter(DBParty.id == party.id).first()
        assert row is not None
        assert row.guest_name == "Persistence Test Guest"
        assert row.party_size == 3
        assert row.status == "waiting"
    finally:
        db.close()

def test_seeded_tables_exist_in_db():
    store.reset()
    db = SessionLocal()
    try:
        count = db.query(DBTable).count()
        assert count == 6
        table_ids = [t.id for t in db.query(DBTable).all()]
        assert set(table_ids) == {"T1", "T2", "T3", "T4", "T5", "T6"}
    finally:
        db.close()
