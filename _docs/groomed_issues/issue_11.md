# [Sprint 5] TASK-11: Automated Test Suite

## 1. Description / Goal
Consolidate, expand, and verify full test coverage across all application layers—including data models, allocation engines, REST API endpoints, management commands, and web dashboard views. Ensure that the entire test suite executes deterministically, keylessly, and passes 100% offline using the canonical project test runner (`uv run python manage.py test`).

## 2. Specification & Edge Cases

**Target File Location**: `chores/tests/` (modular test suite package)

### Test Suite Architecture & Modular Coverage:
1. **Data Models & Admin** (`chores/tests/test_models.py`):
   - `Member`: Model creation, unique name constraint, string representation, alphabetical ordering.
   - `Chore`: Model defaults (`is_active=True`, `frequency='weekly'`), valid effort levels (1, 2, 3), string representation.
   - `Assignment`: Foreign key relations to `Member` and `Chore`, status choices (`pending`, `completed`, `skipped`), string representation, and `mark_completed()` method updating status and `completed_at` timestamp.
   - Admin registration: Verify `MemberAdmin`, `ChoreAdmin`, and `AssignmentAdmin` are registered with configured search fields and list filters.
   - Seed command: Test `python manage.py seed_chores` populating default household members (Alice, Bob, Charlie) and default chores idempotently.
2. **Allocation Service Layer**:
   - Schemas & Interface (`chores/tests/test_allocation_interface.py`): Validate Pydantic data schemas (`MemberData`, `ChoreData`, `WorkloadHistory`, `ProposedAssignment`, `AllocationRequest`, `AllocationResponse`) and rejection of invalid effort levels (< 1 or > 3).
   - Mock Allocation Engine (`chores/tests/test_mock_engine.py`): Rule-based round-robin allocation, effort point balancing heuristics, and deterministic assignment generation without external dependencies.
   - LLM Allocation Engine & Fallback (`chores/tests/test_llm_engine.py`): Structured prompt construction, natural language preference parsing, and automatic fallback to `MockAllocationEngine` when API keys are missing or provider calls fail.
3. **REST API Endpoints & Actions**:
   - Resource Endpoints (`chores/tests/test_api_endpoints.py`): CRUD and query listing for `GET`/`POST /api/members/`, `GET`/`POST /api/chores/`, and `GET /api/assignments/` (including `status` and `member_id` filters).
   - Action Endpoints (`chores/tests/test_api_actions.py`): `POST /api/assignments/<id>/complete/` (completion toggle and timestamp verification) and `POST /api/allocate/` (triggering allocation engine and persisting new assignments).
4. **Dashboard Views & UI Integration**:
   - View Rendering (`chores/tests/test_dashboard_views.py`): HTTP 200 responses for `/` and named route `chores:dashboard`, `chores/dashboard.html` template rendering, and metric card counts.
   - Interactive DOM & Static Assets (`chores/tests/test_dashboard_interactive.py`): Static asset resolution for `static/chores/dashboard.js`, DOM column containers (`#pending-column`, `#in-progress-column`, `#completed-column`), and AJAX contract structures.

### Constraints, Edge Cases & Validation Rules:
- **Canonical Test Runner**: All tests must run via `uv run python manage.py test`. Per `_docs/process.md`, Django's test runner is the project standard. `pytest` is not a project dependency in `pyproject.toml` and must not be required.
- **Zero API Dependencies / 100% Offline**: All tests must execute offline without requiring internet connectivity or active third-party API credentials (`OPENAI_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`). LLM tests must use mocks or fallback paths.
- **Database Isolation**: Tests must execute against Django's isolated test database environment. The root database `db.sqlite3` must remain unmodified and unpolluted.
- **Fast Execution**: The complete test suite must execute in under 5 seconds.
- **Allocation Edge Cases**:
  - Allocating when zero members or zero active chores exist must handle gracefully (no unhandled 500 server errors).
  - Notes field with empty string, whitespace only, or unicode characters must be accepted cleanly.
- **API Error Handling**:
  - Invalid JSON payloads or missing required fields return HTTP 400 with structured JSON errors.
  - Non-existent assignment ID for completion returns HTTP 404.
  - Invalid HTTP methods (e.g. GET on completion/allocate) return HTTP 405.
- **Model Idempotency**:
  - Calling `mark_completed()` on an already completed assignment does not corrupt or erase previous completion data.

## 3. Acceptance Criteria
- [ ] Test suite is organized under `chores/tests/` with modular test files covering models, allocation engines, API endpoints, and dashboard views.
- [ ] 100% of test cases pass with zero failures and zero errors when running `uv run python manage.py test`.
- [ ] All tests execute completely offline without requiring internet access or active third-party API keys (`OPENAI_API_KEY`, `GEMINI_API_KEY`, etc.).
- [ ] Running the test suite leaves the root `db.sqlite3` database file unmodified (unaltered file content and no test records persisted).
- [ ] Full test suite execution (`uv run python manage.py test`) completes in under 5 seconds.

## 4. Out of Scope
- [TASK-13 / Issue #13](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/13) — Configuring GitHub Actions CI workflow to run tests automatically on pull requests and pushes.
- [TASK-14 / Issue #14](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/14) — Pytest runner migration & `pytest-django` tooling integration (deferred: `uv run python manage.py test` is the project's canonical test suite runner per `_docs/process.md`; adding `pytest` requires separate dependency evaluation).
