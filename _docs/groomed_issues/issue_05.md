# [Sprint 2] TASK-05: Build Deterministic Mock Allocation Engine

## 1. Description / Goal
Implement a concrete allocation engine `MockAllocationEngine` that inherits from `BaseAllocationEngine`. The mock engine uses a deterministic, rule-based algorithm to fairly balance chore effort points and respect availability constraints specified in user natural language notes. This enables keyless, reliable offline testing and local development.

## 2. Specification & Edge Cases

**Target File Location**: `chores/allocation/mock_engine.py`

### Algorithmic Strategy:
1. **Current Workload Calculation**:
   - Compute each member's starting workload: `workload[member_id] = recent_effort_sum` (from `WorkloadHistory`).
2. **Availability & Constraint Parsing (Heuristic)**:
   - Parse `user_notes` (case-insensitive string matching):
     - If a member's name appears with negative indicators (e.g., "away", "busy", "vacation", "out of town", "traveling", "sick", "unavailable"), mark member as `unavailable`.
     - If all members are marked unavailable by heuristics, ignore availability constraints and log a warning/summary message.
3. **Deterministic Chore Sorting & Assignment**:
   - Sort chores by `effort_level` descending (heaviest chores first).
   - For each chore, assign to the available member with the lowest accumulated effort points (`workload[member_id]`).
   - If tied in workload, break ties deterministically by alphabetical order of `member.name`.
   - Update member's accumulated workload: `workload[member_id] += chore.effort_level`.
   - Generate clear, human-readable `reasoning` for each assignment (e.g., *"Assigned to Alice based on lowest current workload score (2 pts) and availability."*).

### Edge Cases & Validation Rules:
- **All Members Unavailable**: If `user_notes` marks everyone unavailable (e.g. *"Alice is away, Bob is away, Charlie is sick"*), fall back to balancing among all members and include in `raw_reasoning_summary`: *"All members were marked unavailable in notes; falling back to full roster allocation."*.
- **Member Name Partial Matches**: Match full member names (case-insensitive) to avoid false positives (e.g., name "Al" matching "Also").
- **Zero Workload History**: If `workload_history` is omitted or empty, initialize all members with starting workload of 0.
- **Engine Identifier**: Return `engine_used="mock"` in `AllocationResponse`.

## 3. Acceptance Criteria
- [ ] `MockAllocationEngine` class inherits from `BaseAllocationEngine` in `chores/allocation/mock_engine.py`.
- [ ] `MockAllocationEngine.allocate(request)` returns a valid `AllocationResponse` containing `assignments`, `raw_reasoning_summary`, and `engine_used="mock"`.
- [ ] Member effort points are balanced across chores deterministically.
- [ ] Members detected as unavailable in `user_notes` are excluded from assignments unless all members are unavailable.
- [ ] Ties in workload score are broken deterministically by member name (alphabetical order).
- [ ] Unit tests in `chores/tests/test_mock_engine.py` verify:
  - Equal effort distribution on balanced rosters.
  - Correct exclusion of unavailable members based on natural language keywords.
  - Fallback behavior when all members are unavailable.
  - Deterministic repeatability (same input produces identical output).
- [ ] All unit tests pass cleanly via `uv run python manage.py test`.

## 4. Out of Scope
- [TASK-06 / Issue #6](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/6) — LLM client integration (OpenAI / Gemini / Groq).
- [TASK-08 / Issue #8](https://github.com/SPBONIFACE/ai-dev-tools-zoomcamp/issues/8) — API endpoint `POST /api/allocate/`.
