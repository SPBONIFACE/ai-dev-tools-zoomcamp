# [Sprint 5] TASK-13: GitHub Actions CI Workflow

## 1. Description / Goal
Configure an automated Continuous Integration (CI) workflow (`.github/workflows/ci.yml`) triggered on all pushes and pull requests to `main`. The workflow verifies code formatting/linting, executes the offline test suite, and builds the container image to prevent regressions before code is merged.

## 2. Specification & Edge Cases

**Target File Location**: `.github/workflows/ci.yml`

### Workflow Pipeline Specification:
1. **Name**: `CI Pipeline`
2. **Trigger Events**:
   - `push`: branches `[ main ]`
   - `pull_request`: branches `[ main ]`
3. **Environment Variables** (Workflow or Job level):
   - `AI_PROVIDER: mock`
   - `PYTHONUNBUFFERED: "1"`
4. **Jobs & Steps (`test-and-build`)**:
   - **Runner**: `ubuntu-latest`
   - **Step 1: Checkout Code**:
     - `uses: actions/checkout@v4`
   - **Step 2: Install uv**:
     - `uses: astral-sh/setup-uv@v5`
     - `with: enable-cache: true`
   - **Step 3: Set up Python**:
     - `uses: actions/setup-python@v5`
     - `with: python-version: "3.11"`
   - **Step 4: Install Dependencies**:
     - `run: uv sync --frozen` (or `make install` / `uv sync`)
   - **Step 5: Code Quality & Lint Check**:
     - `run: uv run ruff check .` (or `uvx ruff check .` / `make lint`)
   - **Step 6: Automated Test Suite**:
     - `run: uv run python manage.py test` (or `make test`)
   - **Step 7: Docker Image Build Verification**:
     - `run: docker build -t chore-manager:ci .` (or `make docker-build`)

### Constraints, Edge Cases & Validation Rules:
- **Zero Secrets / Offline Determinism**: CI must run completely offline without configuring or requiring GitHub repository secret tokens (`OPENAI_API_KEY`, `GEMINI_API_KEY`, etc.). `AI_PROVIDER=mock` ensures allocation services fallback cleanly.
- **Workflow YAML Validity**: File must be valid YAML syntax parseable by GitHub Actions schema parsers without syntax or indentation errors.
- **Fast Execution**: Entire CI run should leverage uv caching and multi-stage Docker build caching to complete within 2 minutes.
- **Failure Short-Circuit**: If linting or tests fail, subsequent build steps must not execute and the pull request status check must report a failure.

## 3. Acceptance Criteria
- [x] Workflow file `.github/workflows/ci.yml` exists with valid YAML syntax.
- [x] Workflow triggers on both `push` and `pull_request` targeting the `main` branch.
- [x] Uses `actions/checkout@v4`, `astral-sh/setup-uv@v5`, and `actions/setup-python@v5` (Python 3.11).
- [x] Executes dependency installation (`uv sync`), linting (`ruff check .`), automated tests (`python manage.py test`), and Docker image build (`docker build -t chore-manager:ci .`).
- [x] Sets environment variable `AI_PROVIDER=mock` so the pipeline runs keylessly without requiring GitHub repository secrets.
- [x] All CI steps complete successfully with zero errors on standard pushes/PRs.

## 4. Out of Scope
- Automated CD deployment to cloud hosting (AWS, GCP, Heroku, Fly.io).
- Image registry publishing (pushing Docker images to Docker Hub or GitHub Container Registry `ghcr.io`).
- [TASK-14 / Issue #14](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/14) — Pytest runner migration.

---

## 5. Engineer Comment (Status: Implemented & Open for Review)
- Implemented GitHub Actions CI Pipeline in `.github/workflows/ci.yml`:
  - Configured pipeline name `CI Pipeline`.
  - Configured event triggers on `push` and `pull_request` targeting branch `main`.
  - Defined global pipeline environment variables `AI_PROVIDER: mock` and `PYTHONUNBUFFERED: "1"` enabling offline, keyless execution without requiring repository secrets.
  - Configured job `test-and-build` on `ubuntu-latest` with standard sequential steps:
    1. Code checkout via `actions/checkout@v4`.
    2. uv installation and caching via `astral-sh/setup-uv@v5` with `enable-cache: true`.
    3. Python 3.11 setup via `actions/setup-python@v5`.
    4. Dependency sync via `uv sync --frozen`.
    5. Code quality lint check via `uvx ruff check .`.
    6. Automated test suite execution via `uv run python manage.py test`.
    7. Container image build verification via `docker build -t chore-manager:ci .`.
- Authored integration test suite in `chores/tests/test_database_isolation.py` (`CIWorkflowTests`) validating workflow file existence, YAML formatting and tab validation, triggers, environment variables, job runners, action versions, and execution step commands.
- Verified:
  - `make lint` passes cleanly with zero errors ("All checks passed!").
  - `make test` executes 155 tests with 100% pass rate in ~0.18s.
- Issue remains open for QA review.

