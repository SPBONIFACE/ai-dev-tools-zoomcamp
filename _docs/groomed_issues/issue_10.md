# [Sprint 4] TASK-10: Interactive Chore Board & Smart Allocator UI

## 1. Description / Goal
Implement client-side JavaScript (`static/chores/dashboard.js`) to power the interactive Chore Board and AI Smart Allocator panel on the web dashboard.

## 2. Specification & Edge Cases

**Target File Location**: `chores/static/chores/dashboard.js` & `chores/templates/chores/dashboard.html`

### UI Features & Workflows:
1. **Interactive Chore Board**:
   - Categorize assignments into 3 status columns: **Pending**, **In Progress**, **Completed**.
   - Single-click **"Mark Done"** button on pending/in-progress assignment cards.
   - When clicked, sends AJAX `POST /api/assignments/<id>/complete/`, updates card status to Completed dynamically with a smooth visual transition, and updates the metrics bar.
2. **AI Smart Allocator Panel**:
   - Free-text `<textarea>` for natural language notes (e.g. *"Alice is traveling Thursday to Saturday"*).
   - **"Run AI Allocation"** button.
   - When clicked:
     - Disables button and displays loading spinner.
     - Sends AJAX `POST /api/allocate/` with notes payload.
     - On success: renders live preview of reasoning summary and newly generated assignments, then refreshes the Chore Board automatically.
     - On error: displays user-friendly error alert box.

### Edge Cases & Validation Rules:
- **Network / Server Error Handling**: Show inline alert badge if API call fails (`"Failed to run allocation. Please try again."`).
- **Empty Inputs**: Submitting allocation with empty notes text area runs normal round-robin allocation without throwing client errors.
- **Double Submission**: Disable "Run AI Allocation" button while request is in flight to prevent duplicate submissions.

## 3. Acceptance Criteria
- [x] Chore Board loads assignments from `GET /api/assignments/` and renders them into Pending, In Progress, and Completed columns.
- [x] Clicking "Mark Done" updates assignment status via `POST /api/assignments/<id>/complete/` without reloading the page.
- [x] Submitting natural language notes triggers `POST /api/allocate/` and displays reasoning summary and updated assignments.
- [x] Loading states (spinners / disabled buttons) are active during API calls.
- [x] Manual browser check: dashboard loads at `http://localhost:8000/` and interactive buttons function as expected.

## 4. Out of Scope
- [TASK-12 / Issue #12](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/12) — Docker container deployment.

---

## 5. Engineer Comment (Status: Implemented & Open for Review)
- Created `chores/static/chores/dashboard.js`:
  - Dynamically loads and renders assignments from `GET /api/assignments/` into the three board columns (`#pending-column`, `#in-progress-column`, `#completed-column`).
  - Implements single-click "Mark Done" button on pending/in-progress cards calling `POST /api/assignments/<id>/complete/` with visual transition, dynamic status badge updates, and updates to the metrics bar.
  - Implements AI Allocator panel submission calling `POST /api/allocate/` with CSRF handling, spinner/disabled loading states, live preview of reasoning summary and generated assignments, and automatic board refresh.
  - Includes user-friendly error alerts (`#allocation-error`, `#allocation-error-message`), empty state fallbacks, and double-submission protection.
- Updated `chores/templates/chores/dashboard.html` to include CSRF meta tag, live assignment preview container in `#allocation-results`, and deferred script tag loading `dashboard.js`.
- Configured static route in `chores/urls.py` ensuring static assets are served across test and local development environments.
- Authored 15 integration tests in `chores/tests/test_dashboard_interactive.py` covering static file finder resolution, HTTP static file serving, template script/meta tags, DOM column IDs and badges, empty states, form controls, error alerts, and backing API complete/allocate workflows.
- All 134 test suite tests pass cleanly via `uv run python manage.py test`.
- Issue remains open for QA review.

