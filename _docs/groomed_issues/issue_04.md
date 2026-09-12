# [Sprint 2] TASK-04: Implement Allocation Service Interface

## 1. Description / Goal
Define the formal abstract Python interface and structured Pydantic schemas for the AI Chore Allocation Service. This interface will serve as the contract between the application (views/API) and the allocation engines (Mock Engine in TASK-05 and LLM Engine in TASK-06).

## 2. Specification & Edge Cases

**Target File Location**: `chores/allocation/schemas.py` and `chores/allocation/interface.py`

### Data Schemas (Pydantic / Dataclasses):
- `MemberData`:
  - `id`: `int`
  - `name`: `str`
- `ChoreData`:
  - `id`: `int`
  - `title`: `str`
  - `effort_level`: `int` (1 = Low, 2 = Medium, 3 = High)
  - `frequency`: `str`
- `WorkloadHistory`:
  - `member_id`: `int`
  - `recent_effort_sum`: `int` (total effort assigned/completed in past 7-14 days)
- `AllocationRequest`:
  - `members`: `List[MemberData]`
  - `chores`: `List[ChoreData]`
  - `workload_history`: `List[WorkloadHistory]` (optional, default empty list `[]`)
  - `user_notes`: `Optional[str]` (natural language constraints, default `""`)
- `ProposedAssignment`:
  - `chore_id`: `int`
  - `member_id`: `int`
  - `reasoning`: `str` (explanation of why this member was assigned)
- `AllocationResponse`:
  - `assignments`: `List[ProposedAssignment]`
  - `raw_reasoning_summary`: `str`
  - `engine_used`: `str` ("mock" or "llm")

### Abstract Interface:
- Abstract base class `BaseAllocationEngine(ABC)` with method:
  `@abstractmethod def allocate(self, request: AllocationRequest) -> AllocationResponse:`

### Edge Cases & Validation Rules:
- **Empty Members**: If `request.members` is empty, raise `InvalidAllocationRequestError("Cannot allocate chores with zero household members.")`.
- **Empty Chores**: If `request.chores` is empty, return an `AllocationResponse` with an empty `assignments` list and `raw_reasoning_summary="No active chores to allocate."`.
- **Empty / Whitespace User Notes**: `user_notes` should default to `""` without failing validation.
- **Invalid Effort Level**: `effort_level` must be an integer between 1 and 3.

## 3. Acceptance Criteria
- [x] Pydantic data schemas (`AllocationRequest`, `AllocationResponse`, `ProposedAssignment`, `MemberData`, `ChoreData`, `WorkloadHistory`) are defined in `chores/allocation/schemas.py`.
- [x] Abstract base class `BaseAllocationEngine` with `@abstractmethod def allocate(...)` is defined in `chores/allocation/interface.py`.
- [x] `InvalidAllocationRequestError` exception is defined for input validation errors.
- [x] Unit tests in `chores/tests/test_allocation_interface.py` verify schema instantiation, serialization/deserialization, and validation errors (e.g. zero members raises error).
- [x] All unit tests pass cleanly via `uv run python manage.py test`.

## 4. Out of Scope
- [TASK-05 / Issue #5](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/5) — Concrete implementation of the rule-based round-robin allocation algorithm.
- [TASK-06 / Issue #6](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/6) — Concrete implementation calling OpenAI / Gemini / Groq APIs.
- [TASK-08 / Issue #8](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/8) — Django REST API endpoint `POST /api/allocate/`.

---

## 5. Engineer Comment (Status: Implemented & Open for Review)
- Created `pyproject.toml` and installed `pydantic>=2.0` and `django>=5.0` via `uv sync` (with user approval).
- Defined Pydantic v2 schemas `MemberData`, `ChoreData` (with 1-3 effort level validation), `WorkloadHistory`, `ProposedAssignment`, `AllocationRequest` (with zero-member validation and user notes normalization), and `AllocationResponse` in `chores/allocation/schemas.py`.
- Defined `InvalidAllocationRequestError` in `chores/allocation/schemas.py`.
- Defined abstract base class `BaseAllocationEngine` with `@abstractmethod def allocate(...)` in `chores/allocation/interface.py`.
- Reorganized `chores/tests.py` into package `chores/tests/` (`test_models.py` and `test_allocation_interface.py`).
- Added 14 comprehensive unit tests in `chores/tests/test_allocation_interface.py` covering schema instantiation, JSON & dict serialization/deserialization, validation rules, and abstract interface contracts.
- Ran full test suite via `uv run python manage.py test`: 28 tests passing (0 failures, 0 errors).

---

## 6. QA Verdict: PASS
- [x] Pydantic data schemas (`AllocationRequest`, `AllocationResponse`, `ProposedAssignment`, `MemberData`, `ChoreData`, `WorkloadHistory`) are defined in `chores/allocation/schemas.py`. - PASS
- [x] Abstract base class `BaseAllocationEngine` with `@abstractmethod def allocate(...)` is defined in `chores/allocation/interface.py`. - PASS
- [x] `InvalidAllocationRequestError` exception is defined for input validation errors. - PASS
- [x] Unit tests in `chores/tests/test_allocation_interface.py` verify schema instantiation, serialization/deserialization, and validation errors (e.g. zero members raises error). - PASS
- [x] All unit tests pass cleanly via `uv run python manage.py test`. - PASS

Tests: `uv run python manage.py test`, 28 passed, 0 failed

---

## 7. Orchestrator Status: CLOSED
Issue #4 verified and officially closed. Backlog updated.
