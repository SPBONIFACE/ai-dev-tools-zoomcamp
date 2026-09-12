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
- [ ] `LLMAllocationEngine` inherits from `BaseAllocationEngine` in `chores/allocation/llm_engine.py`.
- [ ] Structured prompt generator formats request into JSON schema format for LLM inference.
- [ ] Robust fallback to `MockAllocationEngine` occurs automatically when API key is missing or API call fails.
- [ ] Return object clearly identifies `engine_used` (`"llm"` when successful, `"mock (fallback)"` on API failure).
- [ ] Unit tests in `chores/tests/test_llm_engine.py` using mock/patching verify:
  - Successful LLM structured JSON response parsing.
  - Automatic fallback when API key is missing.
  - Automatic fallback when API call raises an exception or returns invalid JSON.
- [ ] All unit tests pass cleanly offline via `uv run python manage.py test`.

## 4. Out of Scope
- [TASK-07 / Issue #7](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/7) — Member and Chore REST endpoints.
- [TASK-08 / Issue #8](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/8) — API endpoint `POST /api/allocate/`.
