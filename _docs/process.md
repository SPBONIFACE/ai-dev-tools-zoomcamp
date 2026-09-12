# Process & Multi-Agent Lifecycle

## Orchestrator

The main session is strictly the **Orchestrator**. 
- It does **not** groom, implement, or test code itself.
- When given a command (whether a full backlog run or a single step like "Implement issue #X"), it always dispatches the appropriate subagent.
- Its responsibilities are: selecting tasks, dispatching subagents with the required context, routing feedback, and closing issues upon QA approval.

## Roles

- **Product Manager (PM)**: Grooms tasks before implementation using `_docs/task-template.md`. Saves/updates specifications in `_docs/groomed_issues/`. Follows `_docs/team/pm.md`.
- **Software Engineer**: Implements one groomed task against its acceptance criteria, writes tests, and commits the implementation. Follows `_docs/team/software-engineer.md`.
- **QA Engineer**: Validates the code against acceptance criteria using `uv run python manage.py test`. Does not modify code; outputs `PASS` or `FAIL`. Follows `_docs/team/qa-engineer.md`.

## Lifecycle

1. **Pick**: Select the next open task from `backlog.md`.
2. **Groom**: Dispatch the PM subagent to groom it (or review/verify existing criteria in `_docs/groomed_issues/`).
3. **Implement**: Dispatch the Software Engineer subagent to implement the task and pass its test suite.
4. **Verify**: Dispatch the QA Engineer subagent to independently check the result against the acceptance criteria.
5. **Route Feedback**:
   - **On FAIL (Defect/Bug)**: Route back to Step 3 with the QA report as input.
   - **On FAIL (Flawed/Contradictory Criteria)**: Route back to Step 2 for PM re-grooming.
   - **On PASS**: Proceed to Step 6.
6. **Close**: The Orchestrator marks the task complete (`- [x]`) in `backlog.md`, updates the issue record, and commits the lifecycle status.
7. **Repeat**: Continue until all backlog tasks are completed.

## Rules

- The orchestrator never writes code or runs tests directly; it always dispatches subagents.
- Never implement an ungroomed task.
- The software engineer does not close the issue.
- QA does not modify code, only outputs `PASS` or `FAIL`.
- The orchestrator closes the issue only after QA outputs `PASS`.
- Use `uv run python manage.py test` as the standard project test suite runner.
- Commit regularly.
