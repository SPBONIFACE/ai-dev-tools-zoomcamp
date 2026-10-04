# AGENTS.md

## Commands

### Quick Shortcuts (Makefile)
- `make run` - start backend server (`http://localhost:8000`)
- `make test` - run full backend test suite (`uv run pytest`)
- `make run-frontend` - start frontend development server (`http://localhost:5173`)
- `make install` - install both backend and frontend dependencies

### Backend
- `cd backend && make run` (or `uv run uvicorn app.main:app --reload --port 8000`) - start backend server
- `cd backend && make test` (or `uv run pytest`) - run test suite
- `cd backend && uv run pytest tests/test_api.py` - run single test file
- `cd backend && make install` (or `uv sync`) - install dependencies

### Frontend
- `cd frontend && npm install` - install dependencies
- `cd frontend && npm run dev` - start frontend development server
- `cd frontend && npm run build` - verify frontend build and typecheck


## Rules

- Consult `_docs/specs.md` before making any schema, endpoint, or business logic changes.
- Consult `openapi.yaml` as the source of truth for the API contract (paths, request/response models, status codes).
- Write tests first before implementing backend endpoint logic (TDD).
- Dependencies are added in `pyproject.toml` or `package.json`. Do not add new ones without asking.
- Keep commits atomic and reference the task/issue number (e.g. `feat(backend): ... (closes #1)`).

## Documents

- `_docs/process.md` - how work is organized
- `openapi.yaml` - backend-frontend API contract
- Before writing tests, read `_docs/testing-guidelines.md` if applicable
- For anything touching the UI, read `_docs/design-system.md` if applicable

