# AI Household Chore Manager

A smart shared household chore management tool that balances workloads, schedules recurring tasks, and uses an AI assistant to allocate chores fairly based on natural language availability and member preferences.

---

## 1. Problem
Living in a shared household (with roommates or family) often leads to friction over household chores:
- **Unequal Workloads**: Without clear visibility, some members end up doing far more than others.
- **Static Schedules Fail**: Rigid chore rosters break down when people travel, have exams, or work late.
- **Preference Clashes**: People dislike different chores (e.g., someone hates doing dishes but doesn't mind vacuuming).
- **Communication Overhead**: Coordinating swaps and reminders manually across chat apps is awkward and tedious.

**AI Household Chore Manager** solves this by providing a unified chore dashboard coupled with an intelligent allocation engine. Members can submit everyday status notes in plain language (e.g., *"Alice is out of town Friday-Sunday; Bob prefers cooking over cleaning bathrooms"*), and the AI calculates a fair, transparent assignment schedule.

---

## 2. Demo & Walkthrough
*(Screenshots and demo GIF will be added as the web UI components are rendered).*

### Sample Allocation Flow
1. **Household Status**: 3 members (Alice, Bob, Charlie) and 5 pending chores (Kitchen, Bathrooms, Trash, Groceries, Vacuuming).
2. **Natural Language Input**:
   > *"Alice has an exam Wednesday and is away this weekend. Charlie cleaned bathrooms last week and prefers grocery shopping. Bob is free all week."*
3. **AI Assignment Output**:
   - **Bob**: Clean Kitchen & Bathrooms (High availability this week, balances previous workload)
   - **Charlie**: Grocery Shopping & Vacuuming (Matches preference, alternates away from bathrooms)
   - **Alice**: Take out Trash (Light, quick task fitting her limited study schedule)
   - **Transparent Reasoning**: Included alongside each assignment for fairness.

---

## 3. Evaluation
- **Allocation Quality**: Evaluated against constraint satisfaction benchmarks (ensuring unavailable members are never assigned conflicting chores).
- **Fairness Balance**: Tracks weekly effort points assigned per member to prevent workload disparity.
- **Offline / CI Determinism**: Includes a deterministic rule-based mock engine ensuring reproducible allocations during testing without API calls.

---

## 4. Testing
Automated tests verify data models, business logic, and chore allocation.

Run the test suite locally:
```bash
python manage.py test
# or if using pytest:
pytest
```

---

## 5. Monitoring & Observability
- **Health Checks**: Endpoint providing service status and database connectivity.
- **Audit Log**: Every AI allocation run records the input prompt, model used, reasoning, and member task distribution for review.

---

## 6. Quickstart

### Prerequisites
- Python 3.11+
- Virtual environment tool (`venv`)
- Git

### Local Setup
1. **Clone the repository**:
   ```bash
   git clone git@github.com:SPBONIFACE/ai-dev-tools-zoomcamp.git
   cd ai-dev-tools-zoomcamp
   ```

2. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install django
   ```

4. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start the development server**:
   ```bash
   python manage.py runserver
   ```
   Open your browser at [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to access the application.

---

## 7. Data & Configuration
The application uses environment variables for configuration. Create a `.env` file from the template:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DEBUG` | Enable debug mode | `True` |
| `SECRET_KEY` | Django secret key | Local development key |
| `AI_PROVIDER` | AI allocation engine (`mock`, `openai`, `gemini`) | `mock` |
| `OPENAI_API_KEY` | API key for OpenAI (optional if using mock) | None |

---

## 8. Deployment
The project is packaged for containerized deployment:
```bash
docker compose up --build
```
This runs the application with a persistent volume for the SQLite database.

---

## 9. Architecture

```
+-------------------------------------------------------------+
|                      Client Browser                         |
|             (Chore Dashboard & Management UI)               |
+------------------------------+------------------------------+
                               | HTTP / JSON REST APIs
+------------------------------v------------------------------+
|                    Django Web Backend                       |
|  - URL Router & Views (Admin / API Endpoints)               |
|  - Chores App Logic (Models, Allocation Manager)            |
+---------------+------------------------------+--------------+
                |                              |
+---------------v---------------+   +----------v--------------+
|    Database Layer (SQLite)    |   |     AI Allocation Engine|
|  - Django ORM Models          |   |  - LLM Provider Client  |
|  - Migrations & State         |   |  - Deterministic Mock   |
+-------------------------------+   +-------------------------+
```

---

## 10. Project Structure

```
.
├── README.md                 # Project landing page & documentation
├── PROJECT_SCOPE.md          # Scoping and feature requirements specification
├── _docs/
│   └── plan.md               # Detailed technical implementation roadmap
├── manage.py                 # Django management script
├── chore_manager/            # Django project configuration
│   ├── __init__.py
│   ├── settings.py           # Application settings & registered apps
│   ├── urls.py               # Main routing table
│   ├── asgi.py               # ASGI configuration
│   └── wsgi.py               # WSGI configuration
└── chores/                   # Core application
    ├── admin.py              # Django admin panel registrations
    ├── apps.py               # App configuration
    ├── models.py             # Data entities (Member, Chore, Assignment)
    ├── views.py              # Views & allocation endpoints
    └── tests.py              # Unit & integration tests
```

---

## 11. Decisions & Trade-Offs
- **Django over Micro-frameworks**: Chosen for its built-in admin dashboard and ORM migrations, allowing immediate data management without writing custom admin views.
- **SQLite over PostgreSQL**: For local use and homework submissions, SQLite requires zero setup and is portable in Docker volumes.
- **Mock Fallback Engine**: Enables CI/CD pipelines to run automated tests reliably without incurring API costs or failing when API keys are absent.

---

## 12. CI/CD Pipeline
- **GitHub Actions (`.github/workflows/ci.yml`)**:
  - Automatically runs on `push` and `pull_request` against `main`.
  - Runs code linting and formatting checks.
  - Executes unit and integration tests using the local mock provider.
  - Verifies Docker image build.

---

## 13. Limitations & Future Work

### Limitations
- Currently optimized for single-household usage (no multi-tenant authorization).
- Natural language parsing relies on structured prompting; highly ambiguous input may fall back to default round-robin rules.

### Future Work
- Push notifications / Telegram bot integration for daily chore reminders.
- Recurring chore rotation templates with automated cadence scheduling.
- Member satisfaction scoring based on historical task swaps.
