# [Sprint 5] TASK-11: Automated Test Suite

## 1. Description / Goal
Consolidate, expand, and ensure full test coverage for all backend models, allocation service engines, and REST API endpoints. Verify that the entire test suite executes keylessly, deterministically, and passes 100% offline.

## 2. Specification & Edge Cases

**Target File Location**: `chores/tests/` (modular test directory containing model, service, view, and API tests)

### Test Coverage Requirements:
1. **Model Tests** (`test_models.py`):
   - Member, Chore, Assignment model creation, string representation, methods (`mark_completed`), validation rules.
2. **Allocation Service Tests** (`test_allocation.py`):
   - Schema validation, `MockAllocationEngine` round-robin & heuristic logic, `LLMAllocationEngine` fallback to mock engine.
3. **API Endpoint Tests** (`test_api.py`):
   - CRUD operations for `/api/members/`, `/api/chores/`, `/api/assignments/`, completion action, allocation action.
4. **Dashboard View Tests** (`test_views.py`):
   - HTTP 200 responses, correct template rendering.

### Edge Cases & Validation Rules:
- **Zero API Dependencies**: All tests must run offline without requiring external API keys or active internet connections.
- **Database Isolation**: Tests must run against isolated test SQLite databases without polluting `db.sqlite3`.

## 3. Acceptance Criteria
- [ ] Test suite organized under `chores/tests/` with tests for models, engines, APIs, and views.
- [ ] 100% of test cases pass when executing `uv run python manage.py test`.
- [ ] 100% of test cases pass when executing `uv run pytest`.
- [ ] Test suite completes in under 5 seconds.

## 4. Out of Scope
- [TASK-13 / Issue #13](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/13) — Configuring GitHub Actions CI workflow to run tests automatically.
