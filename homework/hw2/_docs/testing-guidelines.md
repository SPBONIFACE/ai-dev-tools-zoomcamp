# Testing Guidelines

## General Principles
- **Test-Driven Development (TDD):** Write tests before implementing business or endpoint logic.
- **Independent & Isolated:** Tests must never depend on the execution order or shared mutable global state.
- **Fast & Deterministic:** Tests should run quickly in memory without external network calls.

## Backend Guidelines (FastAPI & Pytest)
- **Framework:** Pytest using `httpx.AsyncClient` or FastAPI `TestClient`.
- **Location:** All backend tests live in `backend/tests/`.
- **Naming Conventions:**
  - Files: `test_*.py` (e.g., `test_api.py`, `test_waitlist.py`)
  - Functions: `test_<feature>_<expected_behavior>()`
- **Structure (AAA Pattern):**
  - **Arrange:** Set up input data, models, or state.
  - **Act:** Execute the API call or function under test.
  - **Assert:** Validate HTTP status codes, response payloads, and database side-effects.
- **Execution:**
  - Run full suite: `cd backend && uv run pytest`
  - Run single test file: `cd backend && uv run pytest tests/test_api.py`
