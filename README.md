# Loopback — Collaborative System Design Interview Platform

A full-stack, real-time collaborative system design interview platform built with **React**, **FastAPI**, **WebSockets**, and **SQLite/SQLAlchemy**.

Developed as part of the **[AI Dev Tools Zoomcamp](https://datatalks.club)** (*Part 2: Build and Ship a Full-Stack App with AI Coding Assistants*) by Alexey Grigorev.

---

## 1. Project Overview

**Loopback** enables interviewers and candidates to conduct live system architecture interviews on a shared infinite canvas:
* **Interviewer**: Signs in, creates an interview session, gets a shareable join link, follows candidate cursors in real time, and keeps private interview notes.
* **Candidate**: Joins via link token with just a display name (no account required), and immediately collaborates with drawing tools, components, and arrows.
* **Real-time Sync**: Synchronous live cursors and shape updates broadcast via WebSockets.
* **Persistent Storage**: All sessions, board components, and notes are saved to disk using SQLite and SQLAlchemy, ready for PostgreSQL in Module 3.

---

## 2. Architecture & Tech Stack

```
                                 ┌────────────────────────┐
                                 │   openapi.yaml Spec    │
                                 │ (Single API Agreement) │
                                 └───────────┬────────────┘
                                             │
               ┌─────────────────────────────┴─────────────────────────────┐
               ▼                                                           ▼
┌──────────────────────────────┐                           ┌──────────────────────────────┐
│       React Frontend         │                           │       FastAPI Backend        │
│    (Port 8080 / Vite)        │                           │     (Port 8091 / Uvicorn)    │
├──────────────────────────────┤                           ├──────────────────────────────┤
│ • React 19 + TanStack Start  │ ─── REST (fetch API) ───► │ • FastAPI 0.141              │
│ • TanStack Router & Query    │                           │ • Pydantic v2 validation     │
│ • Tailwind CSS v4 + Radix UI │ ◄── WebSockets (/ws) ───► │ • Bidirectional WS Broadcast │
│ • SVG Canvas & Shapes Engine │                           │ • PBKDF2 Password Hashing    │
└──────────────────────────────┘                           │ • Bearer Token Auth          │
                                                           └──────────────┬───────────────┘
                                                                          │
                                                           ┌──────────────▼───────────────┐
                                                           │     SQLAlchemy Persistence   │
                                                           │ (SQLite: interview_boards.db)│
                                                           └──────────────────────────────┘
```

### Technology Highlights:
* **Frontend**: React 19, TanStack Start, TanStack Router, TanStack Query, Tailwind CSS, Lucide React, Vite.
* **Backend**: Python 3.13, FastAPI, Uvicorn, WebSockets, Pydantic, managed with **`uv`**.
* **Database**: SQLite (via SQLAlchemy ORM), configured to be **database-agnostic** via the `DATABASE_URL` environment variable.
* **API Specification**: Formal OpenAPI 3.0.3 contract in `openapi.yaml`.

---

## 3. Directory Layout

```text
ai-devops-m2/
├── Makefile                      # Convenient shortcuts (make run, make test, make frontend)
├── AGENTS.md                     # Directives for AI coding assistants (uv, git rules)
├── openapi.yaml                  # Shared REST & WebSocket API specification
├── README.md                     # Project documentation
│
├── docs/
│   └── specs.md                  # Functional specification for the interview platform
│
├── backend/
│   ├── pyproject.toml            # Backend dependencies managed by uv
│   ├── uv.lock                   # Deterministic lockfile
│   ├── main.py                   # Server wrapper
│   ├── interview_boards.db       # SQLite database (auto-created on start)
│   ├── src/backend/
│   │   ├── main.py               # FastAPI application with CORS middleware
│   │   ├── database.py           # SQLAlchemy engine & session factory (database-agnostic)
│   │   ├── db_models.py          # ORM models (users, auth_tokens, sessions, board_elements)
│   │   ├── models.py             # Pydantic request/response schemas
│   │   ├── auth.py               # Password hashing & HTTPBearer token authentication
│   │   ├── store.py              # Persistence layer with automatic database seeding
│   │   └── routers/
│   │       ├── auth.py           # /api/auth (signup, login, me, logout)
│   │       ├── sessions.py       # /api/sessions (interview session CRUD)
│   │       ├── boards.py         # /api/boards (public join, batch ops, ownership)
│   │       └── realtime.py       # /ws/board/{token} (multi-client WebSocket sync)
│   └── tests/
│       ├── test_auth.py          # Auth & token validation tests
│       ├── test_sessions.py      # Session CRUD tests
│       ├── test_boards.py        # Token join & batch ops persistence tests
│       └── test_websocket.py     # Real-time WebSocket connection & broadcast tests
│
└── frontend/
    ├── package.json              # Frontend dependencies
    ├── vite.config.ts            # Vite configuration
    ├── .env                      # Points to VITE_API_URL and VITE_WS_URL
    └── src/
        ├── lib/
        │   ├── api.ts            # Typed client for FastAPI REST & WebSocket endpoints
        │   └── board-types.ts    # Board element schemas (Node, Edge, Draw, Text)
        ├── components/board/
        │   ├── BoardCanvas.tsx   # SVG whiteboard engine with live WebSocket collaboration
        │   └── shapes.tsx        # System architecture shape glyphs & renderers
        └── routes/
            ├── index.tsx         # Landing page
            ├── auth.tsx          # Interviewer sign in / sign up
            ├── b/$token.tsx      # Candidate & interviewer collaborative board screen
            └── _authenticated/
                └── dashboard.tsx # Interviewer sessions dashboard
```

---

## 4. Key Features

### Interviewer Dashboard
* View all interview sessions sorted by date.
* Create new interview sessions with candidate name and role title.
* Copy shareable candidate join links.
* Toggle session state: `live` vs `completed`.
* Revoke or restore candidate access links at any time.

### Board & Canvas System
* **Infinite Canvas**: Smooth panning, zooming, and fit-to-view controls.
* **Architecture Components**:
  * Client (Web / Mobile)
  * Services & Microservices
  * Load Balancers & API Gateways
  * Databases (SQL / NoSQL) & Caches (Redis)
  * Message Queues & Event Streams (Kafka / SQS)
  * Cloud Object Storage (S3) & CDNs
  * LLM / Model Calls
  * Boundary / VPC groupings & Sticky Notes
* **Connections**: Auto-anchoring directional arrows with solid or dashed styles and editable labels (e.g. "gRPC", "HTTPS", "10k rps").
* **Freehand & Text**: Pen tool with customizable stroke widths and colors, eraser, and free text labels.
* **Private Notes**: Dockable interviewer notepad auto-saved to the database.

### Real-Time Multi-User Collaboration
* **Live Cursors**: See each participant's mouse movement and name badge in real time.
* **Presence**: Join/leave events track active users in the room.
* **Instant Shape Propagation**: Moving, creating, resizing, or deleting components instantly streams to all other peers via WebSockets.
* **Reconnection & Persistence**: Edits are periodically batch-persisted to SQLite so sessions survive network drops and reloads.

---

## 5. Getting Started

### Prerequisites
* [uv](https://docs.astral.sh/uv/) (Python package manager)
* [Node.js](https://nodejs.org/) & [pnpm](https://pnpm.io/)
* Python 3.13+

### Quick Start

1. **Install Dependencies**:
   ```bash
   # Backend
   make install
   
   # Frontend
   cd frontend && pnpm install && cd ..
   ```

2. **Start the Backend** (Terminal 1):
   ```bash
   make run
   ```
   * The FastAPI server starts at **http://localhost:8091**.
   * Interactive API documentation is available at **http://localhost:8091/docs**.

3. **Start the Frontend** (Terminal 2):
   ```bash
   make frontend
   ```
   * The web application opens at **http://localhost:8080**.

---

## 6. Default Credentials & Seed Data

The database is pre-seeded on first run for immediate testing:

| Role | Email | Password |
|---|---|---|
| **Interviewer** | `interviewer@example.com` | `password123` |

### Pre-Seeded Board Demo:
* **Title**: *"Distributed Rate Limiter Design"* (Candidate: *Alexey Grigorev*)
* **Join Token**: `demo-token`
* **Direct URL**: [http://localhost:8080/b/demo-token](http://localhost:8080/b/demo-token)
* Comes pre-populated with a client, API Gateway, Redis sliding-window cache, backend core service, and architectural requirements.

---

## 7. Running Tests

Run the full backend test suite:
```bash
make test
```
All 16 unit and integration tests verify:
* Hashed password authentication & bearer token lifecycles
* Session creation, update, and revocation
* Public board token queries and batch element mutations
* Live WebSocket connection, presence updates, and board persistence

---

## 8. Two-Browser Collaboration Test

To verify real-time collaboration:

1. **Window 1 (Interviewer)**:
   - Log in at `http://localhost:8080/auth`.
   - On `/dashboard`, click **"New session"** or open an existing session.
   - Click **"Open board"** or **"Copy link"**.

2. **Window 2 (Candidate)**:
   - Open a **Private / Incognito window** (to separate user sessions).
   - Paste the link (e.g. `http://localhost:8080/b/{token}`).
   - Type a candidate name and click **"Enter Board"**.

3. **Interact**:
   - Move your mouse in Window 2 and watch the live cursor appear in Window 1.
   - Drag a database or draw a line in Window 2 and see it update in Window 1 instantly.

---

## 9. Next Steps (Modules 3 & 4 Preview)

* **Module 3: Containerization & Cloud Database**:
  - Run PostgreSQL with Docker Compose.
  - Switch `DATABASE_URL` from SQLite to PostgreSQL with zero code changes.
  - Set up Alembic database migrations.
* **Module 4: CI/CD & Production Deployment**:
  - Automated test runs in GitHub Actions.
  - Containerized production build and cloud deployment.
