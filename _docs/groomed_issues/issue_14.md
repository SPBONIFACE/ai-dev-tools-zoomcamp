# [Sprint 5] TASK-14: Pytest Runner Integration & Test Tooling Enhancement (Optional)

## 1. Description / Goal
Evaluate and optionally configure `pytest` and `pytest-django` as an alternative or parallel test runner alongside Django's native `manage.py test` runner.

## 2. Specification & Edge Cases

**Target File Locations**: `pyproject.toml`, `pytest.ini`

### Specification:
1. **Dependencies**:
   - Add `pytest` and `pytest-django` to `pyproject.toml` under development dependencies.
2. **Configuration**:
   - Create `pytest.ini` or configure `pyproject.toml` `[tool.pytest.ini_options]` with `DJANGO_SETTINGS_MODULE = "chore_manager.settings"`.
3. **Compatibility**:
   - Ensure compatibility with all existing `unittest.TestCase` / `django.test.TestCase` classes in `chores/tests/`.

### Constraints & Edge Cases:
- Must not break the canonical runner `uv run python manage.py test`.
- Must support offline execution with zero external network access.

## 3. Acceptance Criteria
- [ ] `pytest` and `pytest-django` are added to project dependencies.
- [ ] `uv run pytest` executes all test cases in `chores/tests/` and passes 100%.
- [ ] Canonical runner `uv run python manage.py test` continues to pass without conflict.

## 4. Out of Scope
- [TASK-11 / Issue #11](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/11) — Baseline automated test suite execution via canonical runner `manage.py test`.
- [TASK-13 / Issue #13](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/13) — CI workflow configuration.
