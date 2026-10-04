# [Sprint 3] TASK-08: Complete & Allocate Actions

## 1. Description / Goal
Implement state mutation and allocation action endpoints: marking an assignment completed (`POST /api/assignments/<id>/complete/`) and triggering smart chore allocation (`POST /api/allocate/`).

## 2. Specification & Edge Cases

**Target File Location**: `chores/views.py` & `chores/urls.py`

### Action Endpoints Specification:
1. `POST /api/assignments/<id>/complete/`
   - **Request**: Empty body or `{"status": "completed"}`.
   - **Response**: `200 OK` with updated assignment JSON (`id`, `status="completed"`, `completed_at` timestamp).
   - **Error Handling**: `404 Not Found` if assignment ID does not exist.
2. `POST /api/allocate/`
   - **Request Payload**:
     ```json
     {
       "user_notes": "Alice is away Friday to Sunday.",
       "dry_run": false
     }
     ```
   - **Workflow**:
     - Fetch active members and active chores from SQLite database.
     - Calculate recent workload history per member (past 14 days).
     - Instantiate allocation engine (`LLMAllocationEngine` or `MockAllocationEngine`).
     - Execute allocation engine with request.
     - If `dry_run == false`: persist created `Assignment` instances to database with `status="pending"` and store `ai_reasoning`.
   - **Response Payload**: `200 OK`
     ```json
     {
       "success": true,
       "engine_used": "mock",
       "assignments_created": 5,
       "raw_reasoning_summary": "...",
       "assignments": [...]
     }
     ```

### Edge Cases & Validation Rules:
- **Already Completed Assignment**: Calling `/complete/` on an already completed assignment is idempotent; update timestamp and return `200 OK`.
- **No Members or No Chores**: If DB has no active members or chores, return `400 Bad Request` with message: *"Cannot run allocation without active members and chores."*.
- **Dry Run Mode**: If `dry_run == true`, execute engine and return proposed assignments without writing records to `db.sqlite3`.

## 3. Acceptance Criteria
- [x] Endpoint `POST /api/assignments/<id>/complete/` marks assignment completed, sets `completed_at`, and returns HTTP 200.
- [x] Endpoint `POST /api/assignments/<invalid_id>/complete/` returns HTTP 404.
- [x] Endpoint `POST /api/allocate/` runs allocation engine with natural language notes and returns HTTP 200 with generated assignments.
- [x] Persisted assignments are saved in SQLite database when `dry_run=false`.
- [x] Integration tests in `chores/tests/test_api_actions.py` verify completion workflow and allocation persistence.
- [x] All unit and integration tests pass cleanly via `uv run python manage.py test`.

## 4. Out of Scope
- [TASK-10 / Issue #10](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/10) — Dashboard UI buttons for completing chores and triggering AI allocation.

---

## 5. Engineer Comment (Status: Implemented & Open for Review)
- Implemented `complete_assignment_api` in `chores/views.py`: handles `POST /api/assignments/<id>/complete/`, idempotently calls `mark_completed()`, sets `completed_at`, and returns 200 OK or 404 Not Found.
- Implemented `allocate_api` in `chores/views.py`: handles `POST /api/allocate/`, computes 14-day workload history per member, invokes `LLMAllocationEngine` (with mock fallback), persists assignments in DB when `dry_run=false`, and returns proposed assignments when `dry_run=true`.
- Added URL routes in `chores/urls.py`.
- Authored 17 integration tests in `chores/tests/test_api_actions.py` verifying completion (200, 404, idempotency), allocation (dry_run true/false, empty member/chore 400 validation, workload history calculation, and user notes adherence).
- All 109 tests pass cleanly via `uv run python manage.py test`.

---

## 6. QA Verdict: PASS
- [x] Endpoint `POST /api/assignments/<id>/complete/` marks assignment completed, sets `completed_at`, and returns HTTP 200. - PASS
- [x] Endpoint `POST /api/assignments/<invalid_id>/complete/` returns HTTP 404. - PASS
- [x] Endpoint `POST /api/allocate/` runs allocation engine with natural language notes and returns HTTP 200 with generated assignments. - PASS
- [x] Persisted assignments are saved in SQLite database when `dry_run=false`. - PASS
- [x] Integration tests in `chores/tests/test_api_actions.py` verify completion workflow and allocation persistence. - PASS
- [x] All unit and integration tests pass cleanly via `uv run python manage.py test`. - PASS

Tests: `uv run python manage.py test`, 109 passed, 0 failed

---

## 7. Orchestrator Status: CLOSED
Issue #8 verified and officially closed. Backlog updated.
