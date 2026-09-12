# [Sprint 5] TASK-12: Containerization & Automation

## 1. Description / Goal
Configure containerization (`Dockerfile`, `.dockerignore`, `docker-compose.yml`) and developer automation tooling (`Makefile`) to enable fast, single-command development, testing, linting, and offline containerized deployment.

## 2. Specification & Edge Cases

**Target File Locations**:
- `Dockerfile`
- `.dockerignore`
- `docker-compose.yml`
- `Makefile`

### Component Specifications:

1. **`Dockerfile` (Multi-Stage Build)**:
   - **Base Image**: `python:3.11-slim` or `python:3.12-slim`.
   - **uv Tooling**: Copy official `uv` and `uvx` binaries from `ghcr.io/astral-sh/uv:latest` (e.g., `COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/`).
   - **Multi-Stage Caching**:
     - Builder stage: Copy `pyproject.toml` and `uv.lock` first, install project dependencies using `uv sync --frozen --no-install-project` into a virtual environment (`/app/.venv`).
     - Runtime stage: Copy virtualenv from builder stage, copy application code, set `ENV PATH="/app/.venv/bin:$PATH"`.
   - **Configuration**:
     - Working directory: `/app`.
     - Environment variables: `PYTHONUNBUFFERED=1`, `PYTHONDONTWRITEBYTECODE=1`, `AI_PROVIDER=mock`.
     - Expose port `8000`.
     - Entrypoint / CMD: Execute Django server via `python manage.py runserver 0.0.0.0:8000`.

2. **`.dockerignore`**:
   - Exclude unnecessary directories and build artifacts from Docker context:
     - Virtual environments: `.venv/`, `venv/`, `env/`
     - Python cache files: `__pycache__/`, `*.py[cod]`
     - Git artifacts: `.git/`, `.github/`
     - Local database & state: `db.sqlite3` (prevents baking local state into Docker images)
     - IDE & tool caches: `.ruff_cache/`, `.pytest_cache/`, `.DS_Store`

3. **`docker-compose.yml`**:
   - Service name: `web`
   - Build definition: Context `.`, dockerfile `Dockerfile`.
   - Port mapping: `8000:8000` (or configurable via `"${PORT:-8000}:8000"`).
   - Volume mount: `./db.sqlite3:/app/db.sqlite3` for persistent SQLite storage across container teardowns and restarts.
   - Environment variables:
     - `PYTHONUNBUFFERED=1`
     - `AI_PROVIDER=mock`
   - Restart policy: `unless-stopped` (or default).

4. **`Makefile`**:
   - Declare `.PHONY` for all non-file targets.
   - Targets:
     - `install`: Install/sync project dependencies (`uv sync`).
     - `run`: Start local Django development server (`uv run python manage.py runserver`).
     - `test`: Run the canonical test suite (`uv run python manage.py test`).
     - `migrate`: Apply Django database migrations (`uv run python manage.py migrate`).
     - `lint`: Run code quality linter (`uv run ruff check .` or `uvx ruff check .`).
     - `docker-build`: Build Docker container image (`docker build -t chore-manager .` or `docker compose build`).
     - `docker-up`: Start containerized application in detached mode (`docker compose up -d`).
     - `docker-down`: Stop and remove active containers (`docker compose down`).

### Constraints, Edge Cases & Validation Rules:
- **SQLite Volume Mount Host File Edge Case**: On Linux and macOS Docker daemons, mounting `./db.sqlite3:/app/db.sqlite3` will create `db.sqlite3` as a directory on the host if the file does not already exist. The specification and Makefile/compose workflows should ensure `touch db.sqlite3` occurs if missing before mounting, or document this requirement clearly.
- **Docker Cache Invalidation**: Source code file changes must NOT invalidate cached dependency layers. `pyproject.toml` and `uv.lock` must be copied and installed prior to copying application source files.
- **Zero API Dependency in Container**: Default environment variable `AI_PROVIDER=mock` ensures the container operates immediately without external API keys or network access.
- **Cross-Platform Compatibility**: Makefile commands must execute cleanly in standard POSIX shells (`bash`/`zsh`).

## 3. Acceptance Criteria
- [ ] `Dockerfile` builds a working image cleanly via `docker build -t chore-manager .` using a multi-stage build, `ghcr.io/astral-sh/uv:latest` binary copy, and `python:3.11-slim` or `3.12-slim`.
- [ ] `.dockerignore` exists and excludes `.venv/`, `__pycache__/`, `.git/`, `db.sqlite3`, and tool caches from build context.
- [ ] `docker-compose.yml` configures service `web`, maps port `8000:8000`, mounts `./db.sqlite3:/app/db.sqlite3`, and sets `PYTHONUNBUFFERED=1` and `AI_PROVIDER=mock`.
- [ ] `Makefile` contains valid `.PHONY` targets: `install`, `run`, `test`, `migrate`, `lint`, `docker-build`, `docker-up`, `docker-down`.
- [ ] Executing `make lint` runs `ruff check .` with zero errors.
- [ ] Executing `make test` executes `uv run python manage.py test` and passes 100%.
- [ ] Executing `make docker-up` (or `docker compose up -d`) starts the web container, and `http://localhost:8000/` returns HTTP 200.
- [ ] Data created inside the container (e.g. creating a chore or completing an assignment) persists to host `./db.sqlite3` across `docker compose down` and restart.

## 4. Out of Scope
- [TASK-13 / Issue #13](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/13) — Automating Docker image build and lint/test verification within GitHub Actions CI.
- Production orchestration & cloud deployment (e.g. Kubernetes, AWS ECS, GCP Cloud Run).
