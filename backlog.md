# AI Household Chore Manager - Task Backlog

A prioritized backlog for developing the application in Django, derived from the technical specifications in `_docs/plan.md`.

---

## Sprint 1: Data Models & Django Admin
- [x] **TASK-01: Implement Core ORM Models**
  - Define `Member` (`name`, `created_at`).
  - Define `Chore` (`title`, `description`, `frequency`, `effort_level`, `is_active`).
  - Define `Assignment` (`chore`, `member`, `assigned_date`, `due_date`, `status`, `completed_at`, `ai_reasoning`).
  - Generate and run initial database migrations (`makemigrations`, `migrate`).

- [x] **TASK-02: Register Models in Django Admin**
  - Register `Member`, `Chore`, and `Assignment` in `chores/admin.py`.
  - Add search fields, list filters (by status, frequency), and customized list displays.
  - CRUD operations enabled via `/admin/`.

- [x] **TASK-03: Seed Initial Sample Data**
  - Create a management command (`python manage.py seed_chores`) to populate default household members (Alice, Bob, Charlie) and common chores.

---

## Sprint 2: AI Allocation Engine (Mock & LLM)
- [x] **TASK-04: Implement Allocation Service Interface**
  - Define standard inputs (active chores, members, recent workload, user natural language notes).
  - Define structured output schema (Pydantic / dataclasses: list of assignments with explanation).

- [x] **TASK-05: Build Deterministic Mock Allocation Engine**
  - Implement rule-based assignment balancer (effort points + availability heuristics).
  - Ensures tests and local development run reliably offline with zero API costs.

- [x] **TASK-06: Integrate LLM Client (OpenAI / Gemini / Groq)**
  - Implement prompt template incorporating natural language availability notes.
  - Request structured JSON output conforming to the assignment schema.
  - Add fallback to mock engine when API key is missing or calls fail.

---

## Sprint 3: Views & API Endpoints
- [x] **TASK-07: Chore & Member Endpoints**
  - `GET /api/chores/`: List active chores.
  - `GET /api/members/`: List household members with current assignment counts.
  - `GET /api/assignments/`: List current week's assignments with status.

- [x] **TASK-08: Complete & Allocate Actions**
  - `POST /api/assignments/<id>/complete/`: Mark assignment completed with timestamp.
  - `POST /api/allocate/`: Accept natural language prompt, execute allocation engine, and persist new assignments.

---

## Sprint 4: Web Dashboard Interface
- [x] **TASK-09: Build Dashboard Template**
  - Create `templates/chores/dashboard.html` styled with Tailwind CSS.
  - Header with household overview and quick metrics.

- [ ] **TASK-10: Interactive Chore Board & Smart Allocator UI**
  - Section 1: Active assignments categorized into *Pending*, *In Progress*, and *Completed* with a single-click "Mark Done" toggle.
  - Section 2: AI Smart Allocator form (natural language text area + "Run AI Allocation" button + reasoning display).

---

## Sprint 5: Testing & DevOps Pipeline
- [ ] **TASK-11: Automated Test Suite**
  - Unit tests for model methods and validation in `chores/tests.py`.
  - Integration tests for API endpoints and the mock AI allocator.
  - Verify complete test pass via `python manage.py test`.

- [ ] **TASK-12: Containerization & Automation**
  - Create multi-stage `Dockerfile` and `docker-compose.yml` with SQLite volume mount.
  - Create `Makefile` with standard developer targets (`run`, `test`, `migrate`, `lint`).

- [ ] **TASK-13: GitHub Actions CI Workflow**
  - Configure `.github/workflows/ci.yml` to run linter (`ruff`), test suite, and Docker build on push/PR.
