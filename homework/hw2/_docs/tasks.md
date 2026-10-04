# TableHop Backlog & Groomed Issues

This backlog contains the fully groomed tasks for TableHop, aligned with `_docs/specs.md`, `_docs/process.md`, `_docs/testing-guidelines.md`, and the requirements of Homework 2.

---

## Issue #1: Setup empty backend project with a passing test
* **Status:** ✅ Closed / Done (Commit `9c4c291`)
* **Role:** Quality Engineer & Software Engineer
* **User Story:**
  As a developer, I want an initialized FastAPI backend environment with automated testing so that all subsequent feature development can follow strict TDD practices.
* **Technical Scope:**
  - Workspace: `backend/` initialized with `uv init --app backend`.
  - Dependencies: `fastapi`, `uvicorn[standard]`, `pydantic`, `pytest`, `httpx`.
  - Minimal root route: `GET /health` returning `{"status": "ok", "service": "TableHop API"}`.
  - Test suite: `backend/tests/test_api.py`.
* **Acceptance Criteria:**
  - [x] `backend/pyproject.toml` contains `fastapi`, `uvicorn`, `pydantic`, `pytest`, and `httpx`.
  - [x] `GET /health` returns HTTP 200 with JSON payload `{"status": "ok", "service": "TableHop API"}`.
  - [x] Running `cd backend && uv run pytest` exits with code 0.
* **Definition of Done:**
  - Test passes cleanly.
  - Atomic git commit references issue: `feat(backend): setup empty project with passing health test (closes #1)`.

---

## Issue #2: Define Pydantic schemas for Waitlist, Tables, and Notifications
* **Status:** 📋 Ready for Dev
* **Role:** Product Manager & Backend Architect
* **User Story:**
  As a backend service, I want strongly typed data validation models matching the product specification so that client payloads are sanitized, invalid states are rejected, and OpenAPI documentation is automatically generated.
* **Technical Scope:**
  - Location: `backend/app/models/schemas.py`.
  - Enums:
    - `PartyStatus`: `waiting`, `notified`, `seated`, `cancelled`, `no_show`.
    - `TableStatus`: `available`, `occupied`.
  - Schemas:
    - `PartyCreate`: `guest_name` (str, min 1), `party_size` (int, 1–12), `phone_number` (str), `notes` (optional str), `quoted_wait_min` (optional int).
    - `PartyStatusUpdate`: `status` (`PartyStatus`).
    - `PartyResponse`: All party fields including `id`, `status`, `created_at`, `notified_at`, `seated_at`, `table_id`.
    - `TableResponse`: `id`, `name`, `capacity`, `status`, `current_party_id`.
    - `SeatPartyRequest`: `party_id` (str).
    - `NotificationLogResponse`: `id`, `party_id`, `phone_number`, `message`, `sent_at`.
    - `AnalyticsSummaryResponse`: `active_waiting` (int), `avg_wait_min` (int), `total_seated_today` (int).
* **Acceptance Criteria:**
  - [ ] All models defined in `app/models/schemas.py` match `_docs/specs.md` section 4.
  - [ ] Valid inputs deserialize correctly; invalid party sizes (< 1 or > 12) raise `ValidationError`.
  - [ ] Enums restrict `PartyStatus` and `TableStatus` to approved specification values.
  - [ ] Schema unit tests in `backend/tests/test_schemas.py` pass with `uv run pytest`.
* **TDD Test Plan:**
  - `test_party_create_valid()`: verifies valid payload serialization.
  - `test_party_create_invalid_size()`: asserts validation error when `party_size=0` or `party_size=15`.
  - `test_party_status_enum()`: asserts validation error for unknown status strings.
* **Definition of Done:**
  - `uv run pytest` runs green on `tests/test_schemas.py`.
  - Commit message: `feat(backend): define Pydantic schemas for entities and requests (closes #2)`.

---

## Issue #3: Test and implement Waitlist endpoints with in-memory store
* **Status:** 📋 Ready for Dev
* **Role:** Quality Engineer & Software Engineer
* **User Story:**
  As a restaurant host, I want API endpoints to add walk-in parties, list active waitlist entries, retrieve individual guest status, and cancel entries so that front-of-house intake is fully functional.
* **Technical Scope:**
  - Store: In-memory dictionary/list in `backend/app/services/store.py` (to be replaced by SQLite in Issue #7).
  - Router: `backend/app/routers/waitlist.py`.
  - Endpoints:
    - `GET /api/waitlist`: Returns list of parties, optional query filter `?status=...`.
    - `POST /api/waitlist`: Creates party; auto-calculates `quoted_wait_min = (active_waiting + 1) * 10` if not provided.
    - `GET /api/waitlist/{party_id}`: Returns party details (used by guest tracker). 404 if not found.
    - `PATCH /api/waitlist/{party_id}/status`: Updates lifecycle status.
    - `POST /api/waitlist/{party_id}/cancel`: Sets status to `cancelled` and frees table if assigned.
* **Acceptance Criteria:**
  - [ ] Adding a party without wait time auto-calculates based on queue depth (~10 min per active waiting party).
  - [ ] Adding a party with explicit wait time respects manual override.
  - [ ] `GET /api/waitlist/{party_id}` returns 200 for existing party, 404 for unknown ID.
  - [ ] Canceling an entry updates status to `cancelled`.
  - [ ] All tests in `backend/tests/test_waitlist.py` pass with `uv run pytest`.
* **TDD Test Plan:**
  - `test_create_party_auto_wait_time()`
  - `test_create_party_manual_override()`
  - `test_list_waitlist_and_filter()`
  - `test_get_party_by_id_found_and_not_found()`
  - `test_cancel_party()`
* **Definition of Done:**
  - All waitlist tests pass.
  - Commit message: `feat(backend): implement waitlist CRUD endpoints with in-memory store (closes #3)`.

---

## Issue #4: Test and implement Table management and seating endpoints
* **Status:** 📋 Ready for Dev
* **Role:** Quality Engineer & Software Engineer
* **User Story:**
  As a host, I want API endpoints to view available tables, seat waiting parties at appropriately sized tables, and clear occupied tables so that restaurant seating capacity is maintained in real time.
* **Technical Scope:**
  - Pre-seeded tables: T1 (2 seats), T2 (2 seats), T3 (4 seats), T4 (4 seats), T5 (6 seats), T6 (6 seats).
  - Router: `backend/app/routers/tables.py`.
  - Endpoints:
    - `GET /api/tables`: Lists all tables with capacity, status (`available`/`occupied`), and `current_party_id`.
    - `POST /api/tables/{table_id}/seat`: Accepts `{ "party_id": "..." }`. Sets table to `occupied`, party to `seated`, links `table_id`, records `seated_at`. Returns 400 if table is already occupied.
    - `POST /api/tables/{table_id}/clear`: Sets table status to `available` and clears `current_party_id`.
* **Acceptance Criteria:**
  - [ ] Default store seeds 6 tables matching specified capacities.
  - [ ] Seating an active party sets table status to `occupied` and party status to `seated`.
  - [ ] Seating at an already occupied table returns HTTP 400 Bad Request.
  - [ ] Clearing an occupied table marks it `available` and unlinks the party.
  - [ ] All tests in `backend/tests/test_tables.py` pass with `uv run pytest`.
* **TDD Test Plan:**
  - `test_list_seeded_tables()`
  - `test_seat_party_success()`
  - `test_seat_party_table_already_occupied_error()`
  - `test_clear_table()`
* **Definition of Done:**
  - All table and seating tests pass.
  - Commit message: `feat(backend): implement table matching and seating endpoints (closes #4)`.

---

## Issue #5: Test and implement Notification and Analytics endpoints
* **Status:** 📋 Ready for Dev
* **Role:** Quality Engineer & Software Engineer
* **User Story:**
  As a host, I want to trigger simulated SMS alerts when a table is ready and view real-time KPI metrics so that operations can track performance and notify guests promptly.
* **Technical Scope:**
  - Router: `backend/app/routers/notifications.py` and `backend/app/routers/analytics.py`.
  - Endpoints:
    - `POST /api/waitlist/{party_id}/notify`: Sets party status to `notified`, records timestamp `notified_at`, and appends an entry to the notification log.
    - `GET /api/notifications`: Returns chronological list of simulated SMS dispatch logs.
    - `GET /api/analytics/summary`: Computes and returns `{ "active_waiting": int, "avg_wait_min": int, "total_seated_today": int }`.
* **Acceptance Criteria:**
  - [ ] Notifying a party changes status to `notified` and returns notification log entry.
  - [ ] `GET /api/notifications` returns all logged simulated SMS events.
  - [ ] `GET /api/analytics/summary` accurately calculates active queue count, average wait time, and seated total.
  - [ ] Full backend test suite passes: `uv run pytest`.
* **TDD Test Plan:**
  - `test_notify_party_creates_log_and_updates_status()`
  - `test_list_notifications()`
  - `test_analytics_summary_calculation()`
* **Definition of Done:**
  - Tests pass with zero regressions across waitlist, tables, notifications, and analytics.
  - Commit message: `feat(backend): implement notification dispatch and KPI analytics endpoints (closes #5)`.

---

## Issue #6: Connect Frontend and Backend with CORS (HW2 Question 6)
* **Status:** 📋 Ready for Dev
* **Role:** Full-Stack Integration Engineer
* **User Story:**
  As a user of the TableHop web application, I want the React frontend to communicate with the live FastAPI backend over HTTP so that all guest and table updates persist across browser tabs and devices.
* **Technical Scope:**
  - Backend: Add `fastapi.middleware.cors.CORSMiddleware` in `backend/app/main.py` allowing origins `["http://localhost:5173", "http://127.0.0.1:5173"]`.
  - Frontend: Configure `frontend/.env.development` with `VITE_USE_MOCK=false` and `VITE_API_URL=http://localhost:8000`.
  - Verification:
    - Start backend: `cd backend && uv run uvicorn app.main:app --reload --port 8000`.
    - Start frontend: `cd frontend && npm run dev`.
    - End-to-end user actions in browser: add walk-in, notify, seat, and verify data reflects across browser reloads.
* **Acceptance Criteria:**
  - [ ] CORS middleware allows requests from `http://localhost:5173` without CORS policy errors.
  - [ ] Frontend successfully switches from mock store to HTTP API calls when `VITE_USE_MOCK=false`.
  - [ ] Parties created in the frontend appear in the backend's `GET /api/waitlist`.
  - [ ] Answers HW2 Question 6: URL used by frontend is `http://localhost:8000`.
* **Definition of Done:**
  - Integration verified with live API calls.
  - Commit message: `feat(integration): connect React frontend to FastAPI backend with CORS (closes #6)`.

---

## Issue #7: Integrate SQLite database with SQLAlchemy ORM (HW2 Question 7)
* **Status:** 📋 Ready for Dev
* **Role:** Database Engineer & Software Engineer
* **User Story:**
  As a restaurant operator, I want all waitlist entries, table assignments, and logs stored in a persistent SQLite database so that records survive backend server restarts.
* **Technical Scope:**
  - Add dependency: `cd backend && uv add sqlalchemy`.
  - Database layer: `backend/app/database.py` with `sqlite:///./tablehop.db` and scoped session dependency `get_db()`.
  - ORM Models: `backend/app/models/db.py` for `DBParty`, `DBTable`, and `DBNotificationLog`.
  - Startup event: Automatically create tables and seed default tables T1–T6 if empty.
  - Service migration: Refactor routers to query and mutate SQLite via SQLAlchemy sessions instead of in-memory dictionaries.
  - Tests: Verify SQLite database persistence and verify test suite passes cleanly with `uv run pytest`.
* **Acceptance Criteria:**
  - [ ] SQLite database file created and auto-migrated on startup.
  - [ ] Tables T1–T6 pre-seeded on initial startup.
  - [ ] Data added to waitlist remains intact after stopping and restarting the backend server.
  - [ ] All unit and integration tests continue to pass via `cd backend && uv run pytest`.
  - [ ] Answers HW2 Question 7: Test command is `uv run pytest` (or `cd backend && uv run pytest`).
* **Definition of Done:**
  - All tests green with SQLite database integration.
  - Commit message: `feat(database): integrate SQLAlchemy SQLite persistence (closes #7)`.
