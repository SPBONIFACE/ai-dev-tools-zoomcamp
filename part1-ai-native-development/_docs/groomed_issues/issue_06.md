# [Sprint 2] TASK-06: Integrate LLM Client (OpenAI / Gemini / Groq)

## 1. Description / Goal
Implement `LLMAllocationEngine` inheriting from `BaseAllocationEngine`. The LLM engine constructs a structured prompt incorporating household member roster, active chores, workload history, and user natural language notes. It requests a structured JSON response matching `AllocationResponse` and gracefully falls back to `MockAllocationEngine` whenever API keys are missing or LLM API calls fail.

## 2. Specification & Edge Cases

**Target File Location**: `chores/allocation/llm_engine.py`

### Key Design & Implementation:
1. **Configurable Providers & API Key Handling**:
   - Read `AI_PROVIDER` (e.g., `openai`, `gemini`, `groq`, `mock`) and corresponding API keys (`OPENAI_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`) from Django settings / environment variables (`app/config` or `settings.py`).
2. **Structured Prompt Construction**:
   - Format prompt with JSON schema expectations:
     ```json
     {
       "assignments": [{"chore_id": 1, "member_id": 2, "reasoning": "..."}],
       "raw_reasoning_summary": "..."
     }
     ```
   - Inject roster details, chore titles & effort levels, past workloads, and `user_notes`.
3. **Fallback Logic**:
   - If no API key is configured or `AI_PROVIDER=="mock"`, log info and instantiate `MockAllocationEngine` directly.
   - If API call times out, raises network error, or returns unparseable JSON, log error, fall back to `MockAllocationEngine`, and return `engine_used="mock (fallback)"`.

### Edge Cases & Validation Rules:
- **Missing API Key**: Immediately triggers fallback to `MockAllocationEngine` without attempting network connection.
- **Mismatched IDs**: If LLM returns a `chore_id` or `member_id` that does not exist in the request, validate with Pydantic and trigger fallback to mock engine.
- **LLM Rate Limits / Timeouts**: Catch `Exception`, log warning, and complete allocation via mock engine without throwing a 500 error to the client.

## 3. Acceptance Criteria
- [x] `LLMAllocationEngine` inherits from `BaseAllocationEngine` in `chores/allocation/llm_engine.py`.
- [x] Structured prompt generator formats request into JSON schema format for LLM inference.
- [x] Robust fallback to `MockAllocationEngine` occurs automatically when API key is missing or API call fails.
- [x] Return object clearly identifies `engine_used` (`"llm"` when successful, `"mock (fallback)"` on API failure).
- [x] Unit tests in `chores/tests/test_llm_engine.py` using mock/patching verify:
  - Successful LLM structured JSON response parsing.
  - Automatic fallback when API key is missing.
  - Automatic fallback when API call raises an exception or returns invalid JSON.
- [x] All unit tests pass cleanly offline via `uv run python manage.py test`.

## 4. Out of Scope
- [TASK-07 / Issue #7](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/7) — Member and Chore REST endpoints.
- [TASK-08 / Issue #8](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/8) — API endpoint `POST /api/allocate/`.

---

## 5. Engineer Comment (Status: Implemented & Open for Review)
- Implemented `LLMAllocationEngine` in `chores/allocation/llm_engine.py` inheriting from `BaseAllocationEngine`.
- Configurable AI providers supported (`openai`, `gemini`, `groq`, `mock`) with API key resolution from Django settings (`OPENAI_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `AI_API_KEY`) and environment variables.
- Structured prompt generation injecting household roster, active chores, workload history, and user natural language notes with JSON schema expectations.
- Automatic fallback to `MockAllocationEngine` returning `engine_used="mock (fallback)"` on missing API key, network timeout, HTTP error, malformed JSON, mismatched member/chore IDs, or duplicate/omitted chore assignments.
- Exported `LLMAllocationEngine` in `chores/allocation/__init__.py`.
- Authored 28 comprehensive unit tests in `chores/tests/test_llm_engine.py` using `unittest.mock` to verify prompt generation, provider REST calls, JSON parsing with and without markdown fences, and all fallback triggers.
- All 72 tests pass cleanly via `uv run python manage.py test`.

---

## 6. QA Verdict: PASS
- [x] `LLMAllocationEngine` inherits from `BaseAllocationEngine` in `chores/allocation/llm_engine.py`. - PASS
- [x] Structured prompt generator formats request into JSON schema format for LLM inference. - PASS
- [x] Robust fallback to `MockAllocationEngine` occurs automatically when API key is missing or API call fails. - PASS
- [x] Return object clearly identifies `engine_used` (`"llm"` when successful, `"mock (fallback)"` on API failure). - PASS
- [x] Unit tests in `chores/tests/test_llm_engine.py` using mock/patching verify:
  - Successful LLM structured JSON response parsing.
  - Automatic fallback when API key is missing.
  - Automatic fallback when API call raises an exception or returns invalid JSON. - PASS
- [x] All unit tests pass cleanly offline via `uv run python manage.py test`. - PASS

Tests: `uv run python manage.py test`, 72 passed, 0 failed

---

## 7. Orchestrator Status: CLOSED
Issue #6 verified and officially closed. Backlog updated.

