# Loopback — Collaborative System Design Interview Platform

> A specialized, real-time collaborative whiteboard designed for technical system design interviews.

Built as part of the **[AI Dev Tools Zoomcamp](https://datatalks.club)** (Module 2: *Build and Ship a Full-Stack App with AI Coding Assistants*).

---

## The Problem

Conducting technical system design interviews is often clunky for both interviewers and candidates:

* **General whiteboards waste time**: Tools like Miro or generic drawing apps force candidates to manually draw boxes and labels from scratch instead of focusing on high-level architecture and trade-offs.
* **Account friction**: Most collaboration tools require both participants to create accounts or install software before entering a room.
* **Split attention**: Interviewers often juggle multiple windows—one for the shared drawing, one for the candidate's CV, and another for private evaluation notes and rubrics.

## The Solution

**Loopback** is a dedicated interview platform designed to make system architecture discussions seamless:

* **Frictionless Candidate Join**: Candidates join with a single click via an invite link and enter their name—no account or login required.
* **Pre-built Architecture Primitives**: One-click components for databases, caches, message queues, microservices, and labeled connection arrows.
* **Live Multi-User Collaboration**: Low-latency WebSocket synchronization showing real-time cursor positions, shape movements, and edits.
* **Private Interviewer Workspace**: A built-in scratchpad for private interviewer notes that candidates cannot see, stored alongside the session.

---

## How It Works

```
1. Interviewer logs in ──► Creates interview session ──► Copies invite link
                                                              │
2. Candidate opens link ──► Enters name ──► Joins shared canvas (no account)
                                                              │
3. Live Collaboration ◄── WebSockets broadcast shapes & cursors ──► Both draw & discuss
                                                              │
4. Private Evaluation ──► Interviewer notes auto-saved to database
```

1. **Schedule**: The interviewer logs in, creates an interview session (e.g., *“Senior Backend Engineer — Rate Limiter Design”*), and generates an invite link.
2. **Join**: The candidate opens the link in their browser, types their display name, and enters the board immediately.
3. **Collaborate**: Both parties design the system together on an infinite canvas with live cursors and architecture components.
4. **Evaluate**: The interviewer writes assessment notes in a private panel saved directly to the database.

---

## Architecture & Tech Stack

```
   ┌────────────────────────┐             ┌────────────────────────┐
   │     React Frontend     │             │    FastAPI Backend     │
   │  (Port 8080 via Vite)  │             │ (Port 8091 via Uvicorn)│
   ├────────────────────────┤   REST API  ├────────────────────────┤
   │ • React 19             │ ──────────► │ • Python 3.13 / FastAPI│
   │ • TanStack Router      │             │ • Pydantic validation  │
   │ • Interactive SVG      │  WebSocket  │ • Multi-client broadcast│
   │ • Tailwind CSS         │ ◄─────────► │ • PBKDF2 Token Auth    │
   └────────────────────────┘             └───────────┬────────────┘
                                                      │ SQLAlchemy
                                          ┌───────────▼────────────┐
                                          │  Database-Agnostic DB  │
                                          │ (SQLite / PostgreSQL)  │
                                          └────────────────────────┘
```

* **Frontend**: **React 19** with **TanStack Router** and **Tailwind CSS**. Provides an interactive SVG canvas with smooth panning, zooming, and zero drawing latency.
* **Backend**: **FastAPI** running on Python 3.13, managed with **`uv`**. Implements standard REST endpoints documented via `openapi.yaml`, alongside a WebSocket hub that broadcasts room events in real time.
* **Storage**: **SQLAlchemy** ORM configured with **SQLite** for zero-configuration local development. The database layer is database-agnostic (`DATABASE_URL`), ready for PostgreSQL in Module 3.

---

## Quickstart

### Prerequisites

* [uv](https://docs.astral.sh/uv/) (Python package manager)
* [Node.js](https://nodejs.org/) (v20+) and [pnpm](https://pnpm.io/)

### 1. Start the Backend

```bash
# Install backend dependencies and start the server
make run
```
* Backend runs at **http://localhost:8091**
* Interactive API documentation is available at **http://localhost:8091/docs**

### 2. Start the Frontend

In a second terminal window:

```bash
# Install frontend dependencies and start Vite dev server
make frontend
```
* Web app runs at **http://localhost:8080**

---

## Trying It Out

### Demo Credentials

A seed interviewer account is automatically created on startup:

* **URL**: [http://localhost:8080/auth](http://localhost:8080/auth)
* **Email**: `interviewer@example.com`
* **Password**: `password123`

### Testing Two-Player Live Collaboration

1. **Interviewer Window**: Open [http://localhost:8080/auth](http://localhost:8080/auth), sign in, and click **New session** or open the pre-seeded *"Distributed Rate Limiter Design"* session.
2. **Candidate Window**: Open a **Private / Incognito window**, paste the invite link (e.g. `http://localhost:8080/b/<token>`), type a candidate name, and click **Enter Board**.
3. **Live Sync**: Move your mouse or drag a shape in the candidate window—the changes and cursor appear instantly in the interviewer window.

---

## Running Tests

Run the backend test suite with a single command:

```bash
make test
```

Runs all 16 automated tests covering authentication, session management, board token access, and real-time WebSocket communication.

---

## Roadmap

* **Module 3**: Docker Compose setup with PostgreSQL and Alembic database migrations.
* **Module 4**: Continuous Integration (CI) and automated production deployment pipelines.
