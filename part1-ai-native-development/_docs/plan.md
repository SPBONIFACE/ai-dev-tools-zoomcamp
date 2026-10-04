# AI Household Chore Manager - Implementation Plan

## 1. Project Overview & Objectives
The goal of this project is to build an intelligent, lightweight shared household chore management web tool. The tool allows household members to maintain chore lists, submit natural language updates regarding their availability or task preferences, and leverage an AI engine to allocate chores fairly and transparently.

---

## 2. System Architecture & Tech Stack

### Architecture Diagram (High-Level)
```
+-------------------------------------------------------------+
|                      Client Browser                         |
|   (HTML5 / Tailwind CSS / Vanilla JS Responsive Dashboard)   |
+------------------------------+------------------------------+
                               | HTTP / JSON REST APIs
+------------------------------v------------------------------+
|                     FastAPI Backend                         |
|  - API Endpoints (/api/members, /api/chores, /api/allocate) |
|  - Static & Template File Server                            |
+---------------+------------------------------+--------------+
                |                              |
+---------------v---------------+   +----------v--------------+
|    Database Layer (SQLite)    |   |     AI Allocation Engine|
|  - SQLModel / SQLAlchemy ORM  |   |  - Pluggable LLM Client |
|  - Data Persistence           |   |  - Offline Mock Engine  |
+-------------------------------+   +-------------------------+
```

### Component Details
- **Backend**: Python 3.11+ with **FastAPI** for clean REST APIs and async performance.
- **Data Persistence**: **SQLite** managed via **SQLModel / SQLAlchemy** for zero-setup, file-backed reliability.
- **Frontend**: Single-page modern dashboard using semantic **HTML5**, **Tailwind CSS** (via CDN or bundled), and lightweight **JavaScript** (no heavy frontend framework build steps).
- **AI Service Layer**:
  - Structured output prompt engineering (JSON Schema).
  - Pluggable provider architecture supporting OpenAI / Gemini / Groq.
  - Deterministic **Mock AI Fallback** for CI/CD runs and local offline development without requiring paid API keys.
- **DevOps & Delivery**:
  - `Dockerfile` (multi-stage build for minimal image size).
  - `docker-compose.yml` for single-command startup.
  - `Makefile` for developer ergonomics (`run`, `test`, `lint`, `docker-build`).
  - GitHub Actions workflow (`.github/workflows/ci.yml`) for automated linting, testing, and container build checks.

---

## 3. Data Model Design

### Entities & Schemas

1. **`Member`**
   - `id`: `int` (Primary Key, auto-increment)
   - `name`: `str` (Display name, e.g., "Alice", "Bob")
   - `created_at`: `datetime`

2. **`Chore`**
   - `id`: `int` (Primary Key, auto-increment)
   - `title`: `str` (e.g., "Clean Kitchen", "Take out Trash")
   - `description`: `Optional[str]`
   - `frequency`: `str` (Daily, Weekly, Bi-weekly, As-needed)
   - `effort_level`: `int` (1 = Quick/Low, 2 = Medium, 3 = Heavy)
   - `is_active`: `bool` (Default: `True`)

3. **`Assignment`**
   - `id`: `int` (Primary Key, auto-increment)
   - `chore_id`: `int` (Foreign Key to `Chore.id`)
   - `member_id`: `int` (Foreign Key to `Member.id`)
   - `assigned_date`: `date`
   - `due_date`: `date`
   - `status`: `str` (`pending`, `completed`, `skipped`)
   - `completed_at`: `Optional[datetime]`
   - `ai_reasoning`: `Optional[str]` (Explanation of why this member was assigned)

---

## 4. Step-by-Step Implementation Roadmap

### Phase 1: Environment & Project Foundation
- [ ] Initialize project directory structure (`app/`, `tests/`, `static/`, `_docs/`).
- [ ] Configure dependency management (`pyproject.toml` or `requirements.txt` with FastAPI, Uvicorn, SQLModel, Pydantic, pytest, ruff).
- [ ] Create base configuration system (`app/config.py`) supporting environment variables (`DATABASE_URL`, `AI_PROVIDER`, `OPENAI_API_KEY`, etc.).

### Phase 2: Database & Data Models
- [ ] Implement database session handling (`app/database.py`).
- [ ] Define SQLModel classes for `Member`, `Chore`, and `Assignment` (`app/models.py`).
- [ ] Implement seed data script to populate initial household members and default chores for testing.

### Phase 3: Core API Endpoints
- [ ] `GET /api/members` and `POST /api/members`: Manage household members.
- [ ] `GET /api/chores` and `POST /api/chores`: Manage chore definitions.
- [ ] `GET /api/assignments`: Fetch current active and past assignments.
- [ ] `PATCH /api/assignments/{id}/complete`: Mark chore as completed.

### Phase 4: AI Smart Assignment Engine
- [ ] Define structured allocation schema (Pydantic models for allocations and reasoning).
- [ ] Implement `MockAIEngine`: Deterministic, rule-based round-robin balancing with simulated constraint checks (ensures CI passes without external network calls).
- [ ] Implement `LLMAIEngine`: Prompts LLM with current chores, member roster, historical workloads, and user-provided natural language constraints.
- [ ] Endpoint `POST /api/allocate`: Accepts natural language notes (e.g., *"Alice is away Friday-Sunday, Bob wants to do cooking"*), runs the engine, and saves or previews generated assignments.

### Phase 5: Interactive Web Dashboard
- [ ] Build clean, responsive UI (`static/index.html` and `static/app.js`):
  - **Chore Board**: Current assignments categorized by status (Today, Upcoming, Completed).
  - **Quick Action**: Single-click "Mark Done" toggle.
  - **AI Smart Allocator Panel**: Natural language input box + "Run Smart Allocation" trigger with live preview of AI reasoning.
  - **Household Settings**: Modal or tab to add/remove chores and members.

### Phase 6: Automated Testing & Verification
- [ ] Unit tests for data models and CRUD operations (`tests/test_api.py`).
- [ ] Unit tests for AI allocation logic and mock fallback (`tests/test_allocation.py`).
- [ ] Test coverage verification with `pytest`.

### Phase 7: DevOps, Containerization & CI/CD
- [ ] Multi-stage `Dockerfile` optimizing container size and caching dependencies.
- [ ] `docker-compose.yml` configured for local port forwarding and SQLite volume persistence.
- [ ] `Makefile` automating common developer commands:
  - `make install`
  - `make run`
  - `make test`
  - `make lint`
  - `make docker-build`
- [ ] GitHub Actions workflow (`.github/workflows/ci.yml`) triggering on pushes to `main` and Pull Requests:
  - Python linting check (`ruff check .`)
  - Automated test execution (`pytest`)
  - Docker container build verification (`docker build -t chore-manager:ci .`)

---

## 5. Verification & Acceptance Criteria
1. **Local Run**: The app starts with a single command (`uvicorn` or `docker compose up`) and serves the UI at `http://localhost:8000`.
2. **AI Allocation Flow**: Submitting a natural language constraint returns a fair allocation accompanied by clear reasoning.
3. **CI Pipeline Pass**: Automated tests and linting run cleanly in GitHub Actions without needing third-party API tokens.
4. **Persistence**: Completed chore statuses and assignments persist across server restarts in SQLite.
