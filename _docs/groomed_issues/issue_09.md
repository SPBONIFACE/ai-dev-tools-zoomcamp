# [Sprint 4] TASK-09: Build Dashboard Template

## 1. Description / Goal
Build the web dashboard HTML template structure (`templates/chores/dashboard.html`) styled with Tailwind CSS. The template provides a modern header, household metrics overview cards, responsive layout grid, and container sections for the chore board and AI allocator.

## 2. Specification & Edge Cases

**Target File Location**: `chores/templates/chores/dashboard.html` (and Django template view in `chores/views.py`)

### Template Components & Layout:
1. **Header Navigation**:
   - Title: "AI Household Chore Manager"
   - Subtitle / Household status pill.
2. **Metrics Bar (Top Row)**:
   - Card 1: Total Active Chores
   - Card 2: Pending Assignments
   - Card 3: Completed This Week
   - Card 4: Active Household Members
3. **Main Content Grid (2 Columns on Desktop, 1 Column on Mobile)**:
   - Left Column (2/3 width): Chore Board Container (`#chore-board-container`)
   - Right Column (1/3 width): AI Allocator Panel (`#ai-allocator-container`)
4. **Styling & Assets**:
   - Tailwind CSS via CDN link in `<head>`.
   - Inter / Roboto Google Font for modern typography.
   - Clean color palette (dark mode / slate / indigo accents).

### Edge Cases & Validation Rules:
- **Responsive Breakpoints**: Layout must stack vertically cleanly on mobile screens (`< 768px`) without horizontal overflow.
- **Empty States**: Cards and containers must display fallback text (e.g. "No pending assignments") gracefully when data is 0.

## 3. Acceptance Criteria
- [x] Django view `dashboard_view` renders `chores/dashboard.html` at route `/`.
- [x] Template contains header, 4 metric cards, and containers for the chore board and AI allocator panel.
- [x] Styled with Tailwind CSS without broken layouts or raw unstyled HTML elements.
- [x] Template unit test in `chores/tests/test_dashboard_views.py` verifies HTTP 200 response and presence of main containers.
- [x] All tests pass cleanly via `uv run python manage.py test`.

## 4. Out of Scope
- [TASK-10 / Issue #10](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/10) — Client-side JavaScript (`static/chores/dashboard.js`) fetching API data and handling interactive clicks.

---

## 5. Engineer Comment (Status: Implemented & Open for Review)
- Implemented `dashboard_view` in `chores/views.py`: computes `total_active_chores`, `pending_assignments_count`, `completed_this_week_count`, and `active_members_count` context metrics and renders `chores/dashboard.html`.
- Created Tailwind CSS dashboard template in `chores/templates/chores/dashboard.html`:
  - Modern, responsive Tailwind CSS styling using CDN and Google Fonts (Inter).
  - Header with title "AI Household Chore Manager" and "Household Active" status pill.
  - Metrics bar featuring 4 cards: Total Active Chores, Pending Assignments, Completed This Week, and Active Household Members, with empty state fallbacks.
  - 2-column responsive layout (desktop 2/3 and 1/3, mobile single-column stacked) featuring `#chore-board-container` with status columns and `#ai-allocator-container` with allocation notes input, button, spinner, error alert, and reasoning results preview.
- Wired route `path('', views.dashboard_view, name='dashboard')` in `chores/urls.py`.
- Authored 10 comprehensive unit/integration tests in `chores/tests/test_dashboard_views.py` testing HTTP 200, template rendering, header, status pill, metric cards, main container IDs, styling assets, responsive breakpoints, empty states, and populated metrics.
- All 119 tests pass cleanly via `uv run python manage.py test`.

