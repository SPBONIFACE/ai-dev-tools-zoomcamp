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
- [ ] Workflow file `.github/workflows/ci.yml` exists with valid YAML syntax.
- [ ] Workflow triggers on both `push` and `pull_request` targeting the `main` branch.
- [ ] Uses `actions/checkout@v4`, `astral-sh/setup-uv@v5`, and `actions/setup-python@v5` (Python 3.11).
- [ ] Executes dependency installation (`uv sync`), linting (`ruff check .`), automated tests (`python manage.py test`), and Docker image build (`docker build -t chore-manager:ci .`).
- [ ] Sets environment variable `AI_PROVIDER=mock` so the pipeline runs keylessly without requiring GitHub repository secrets.
- [ ] All CI steps complete successfully with zero errors on standard pushes/PRs.

## 4. Out of Scope
- Automated CD deployment to cloud hosting (AWS, GCP, Heroku, Fly.io).
- Image registry publishing (pushing Docker images to Docker Hub or GitHub Container Registry `ghcr.io`).
- [TASK-14 / Issue #14](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/14) — Pytest runner migration.
