# [Sprint 5] TASK-13: GitHub Actions CI Workflow

## 1. Description / Goal
Configure an automated GitHub Actions CI workflow (`.github/workflows/ci.yml`) that runs on every push and pull request to `main`. The pipeline automatically lints the codebase, executes the offline test suite, and verifies Docker image compilation.

## 2. Specification & Edge Cases

**Target File Location**: `.github/workflows/ci.yml`

### Workflow Pipeline Steps:
1. **Trigger Events**:
   - `push: branches: [ main ]`
   - `pull_request: branches: [ main ]`
2. **Jobs**:
   - `job: test-and-build` running on `ubuntu-latest`.
   - **Step 1**: `actions/checkout@v4`
   - **Step 2**: Install `uv` (`astral-sh/setup-uv@v3`).
   - **Step 3**: Set up Python (`actions/setup-python@v5` with `python-version: "3.11"`).
   - **Step 4**: Install dependencies (`uv sync`).
   - **Step 5**: Run linter (`uv run ruff check .`).
   - **Step 6**: Run automated tests (`uv run python manage.py test`).
   - **Step 7**: Build Docker image (`docker build -t chore-manager:ci .`).

### Edge Cases & Validation Rules:
- **No Secret Tokens Required**: Workflow must complete 100% successfully without relying on external secret API tokens (`OPENAI_API_KEY`, etc.).
- **Fast Execution**: Entire CI run must complete within 2 minutes.

## 3. Acceptance Criteria
- [ ] Workflow file `.github/workflows/ci.yml` exists and is valid YAML syntax.
- [ ] Configured to run on pushes and pull requests targeting `main`.
- [ ] Includes steps for linting (`ruff`), testing (`python manage.py test`), and Docker image build verification.
- [ ] CI pipeline passes cleanly on GitHub when pushed.

## 4. Out of Scope
- Production deployment / CD pipelines (e.g. AWS / Heroku / GCP App Engine).
