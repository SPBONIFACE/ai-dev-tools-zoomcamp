# [Sprint 3] TASK-07: Chore & Member Endpoints

## 1. Description / Goal
Implement Django REST API view endpoints for managing household members, chore definitions, and viewing active chore assignments. These endpoints provide JSON formatted data for consumption by the web dashboard frontend.

## 2. Specification & Edge Cases

**Target File Location**: `chores/views.py` & `chores/urls.py` (or `chore_manager/urls.py`)

### Endpoints Specification:
1. `GET /api/members/`
   - **Response**: `200 OK`
   - **Body**: JSON array of members including `id`, `name`, `created_at`, `pending_assignments_count`, `completed_assignments_count`.
2. `POST /api/members/`
   - **Request**: `{"name": "David"}`
   - **Response**: `201 Created` with created member object, or `400 Bad Request` if `name` is missing or duplicate.
3. `GET /api/chores/`
   - **Query Params**: `is_active` (optional boolean, default `true`).
   - **Response**: `200 OK` JSON array of chores (`id`, `title`, `description`, `frequency`, `effort_level`, `is_active`).
4. `POST /api/chores/`
   - **Request**: `{"title": "Mop Floor", "effort_level": 2, "frequency": "weekly"}`
   - **Response**: `201 Created` with created chore object, or `400 Bad Request` on invalid choice or missing title.
5. `GET /api/assignments/`
   - **Query Params**: `status` (optional: `pending`, `in_progress`, `completed`), `member_id` (optional).
   - **Response**: `200 OK` JSON array of assignments with nested chore summary, member summary, `assigned_date`, `due_date`, `status`, `completed_at`, `ai_reasoning`.

### Edge Cases & Validation Rules:
- **Duplicate Member Name**: Reject duplicate `name` with `400 Bad Request` (`{"error": "Member with this name already exists."}`).
- **Invalid Effort Level or Frequency**: Return `400 Bad Request` if `effort_level` is not 1, 2, or 3, or if `frequency` is not in allowed choices.
- **Empty Lists**: Return `200 OK` with an empty JSON array `[]` when no members/chores exist.

## 3. Acceptance Criteria
- [x] Endpoint `GET /api/members/` returns HTTP 200 with JSON list of members and assignment stats.
- [x] Endpoint `POST /api/members/` creates a new member and returns HTTP 201.
- [x] Endpoint `GET /api/chores/` returns HTTP 200 with JSON list of active chores.
- [x] Endpoint `POST /api/chores/` creates a new chore definition and returns HTTP 201.
- [x] Endpoint `GET /api/assignments/` returns HTTP 200 with JSON list of assignments filterable by status.
- [x] Integration tests in `chores/tests/test_api_endpoints.py` verify all CRUD operations, status codes, and error payloads.
- [x] All unit and integration tests pass cleanly via `uv run python manage.py test`.

## 4. Out of Scope
- [TASK-08 / Issue #8](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/8) — `POST /api/assignments/<id>/complete/` and `POST /api/allocate/` actions.
- [TASK-09 / Issue #9](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/9) — HTML dashboard UI templates.

---

## 5. Engineer Comment (Status: Implemented & Open for Review)
- Implemented REST API endpoints in `chores/views.py`:
  - `GET /api/members/`: returns JSON array of members with computed `pending_assignments_count` and `completed_assignments_count`.
  - `POST /api/members/`: creates member and returns 201 Created, with 400 Bad Request validations for duplicate member names and missing names.
  - `GET /api/chores/`: lists chores filtered by `is_active` (defaults to active chores only).
  - `POST /api/chores/`: creates chore definition and returns 201 Created, with 400 Bad Request validations for missing title, invalid effort level (must be 1, 2, or 3), and invalid frequency choice.
  - `GET /api/assignments/`: returns JSON array with nested chore and member summaries, filterable by `status` and `member_id`.
- Connected routes in `chores/urls.py` and included in `chore_manager/urls.py`.
- Authored 20 integration tests in `chores/tests/test_api_endpoints.py` verifying status codes (200, 201, 400, 405), payload content, query filters, and validation edge cases.
- All 92 tests pass cleanly via `uv run python manage.py test`.

---

## 6. QA Verdict: PASS
- [x] Endpoint `GET /api/members/` returns HTTP 200 with JSON list of members and assignment stats. - PASS
- [x] Endpoint `POST /api/members/` creates a new member and returns HTTP 201. - PASS
- [x] Endpoint `GET /api/chores/` returns HTTP 200 with JSON list of active chores. - PASS
- [x] Endpoint `POST /api/chores/` creates a new chore definition and returns HTTP 201. - PASS
- [x] Endpoint `GET /api/assignments/` returns HTTP 200 with JSON list of assignments filterable by status. - PASS
- [x] Integration tests in `chores/tests/test_api_endpoints.py` verify all CRUD operations, status codes, and error payloads. - PASS
- [x] All unit and integration tests pass cleanly via `uv run python manage.py test`. - PASS

Tests: `uv run python manage.py test`, 92 passed, 0 failed

---

## 7. Orchestrator Status: CLOSED
Issue #7 verified and officially closed. Backlog updated.
