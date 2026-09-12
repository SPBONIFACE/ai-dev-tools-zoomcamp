# [Sprint 5] TASK-12: Containerization & Automation

## 1. Description / Goal
Create containerization configuration (`Dockerfile` & `docker-compose.yml`) and developer automation scripts (`Makefile`) to enable simple, single-command execution and deployment.

## 2. Specification & Edge Cases

**Target File Locations**: `Dockerfile`, `docker-compose.yml`, `Makefile`

### Component Specification:
1. **`Dockerfile`**:
   - Multi-stage build based on `python:3.11-slim` or `python:3.12-slim`.
   - Install dependencies using `uv`.
   - Expose port 8000.
   - Entrypoint running Gunicorn or Uvicorn / Django development server: `python manage.py runserver 0.0.0.0:8000`.
2. **`docker-compose.yml`**:
   - Service name: `web`.
   - Port mapping: `8000:8000`.
   - Volume mount: `./db.sqlite3:/app/db.sqlite3` for persistent SQLite storage across container restarts.
   - Environment variables: `PYTHONUNBUFFERED=1`, `AI_PROVIDER=mock`.
3. **`Makefile`**:
   - `make install`: Run `uv sync`.
   - `make run`: Run `uv run python manage.py runserver`.
   - `make test`: Run `uv run python manage.py test`.
   - `make migrate`: Run `uv run python manage.py migrate`.
   - `make lint`: Run `uv run ruff check .`.
   - `make docker-build`: Run `docker build -t chore-manager .`.
   - `make docker-up`: Run `docker compose up -d`.

### Edge Cases & Validation Rules:
- **Container File Permissions**: SQLite volume mount must have appropriate read/write permissions inside the container.
- **Port Conflicts**: Port 8000 configurable via environment variable `PORT`.

## 3. Acceptance Criteria
- [ ] `Dockerfile` builds a working container image cleanly without build errors.
- [ ] `docker-compose.yml` starts the web app and connects to SQLite volume persistence.
- [ ] `Makefile` contains targets `install`, `run`, `test`, `migrate`, `lint`, `docker-build`.
- [ ] Running `make test` executes full test suite and passes.
- [ ] App is accessible inside Docker at `http://localhost:8000`.

## 4. Out of Scope
- [TASK-13 / Issue #13](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/13) — GitHub Actions CI pipeline execution of Docker build.
