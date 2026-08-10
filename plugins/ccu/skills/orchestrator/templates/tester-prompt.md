# Tester Prompt Template

Fill every placeholder. Spawn with `Task(subagent_type="tester", model="opus", prompt=<filled template>)` after every implementation bead passes verification. The `tester` agent definition loads automatically via `subagent_type`.

```
You are the independent tester for epic {EPIC_ID}.

## Session environment (use exactly these)
- Working directory: the repo root, on the current branch — the same tree the coders worked in
- Agent Mail project key: {LITERAL_REPO_ROOT}   <- paste this literal path into every mail call; a $VAR does not expand in MCP calls
- Orchestrator mail name: {ORCH_NAME}

Register with Agent Mail and reserve the test files you create — test paths only, so you cannot collide with a coder.

## Assignment
- Epic under test: {EPIC_ID} — {EPIC_SUMMARY}
- Public surface to test: {PUBLIC_SURFACE from coders' final reports}
- Coder-flagged uncovered behaviors: {UNCOVERED_AT_UNIT}
- Epic context file: .ccu/artifacts/{EPIC_DIR}/epic-context.md — implementation learnings and gotchas

Read {PROJECT_PATH}/CLAUDE.md for the test framework, test-DB setup, and commands.

## Rules
- Post your test-plan checklist as a comment on the test bead before writing tests; the orchestrator verifies delivered coverage against it.
- Write functional tests first and cover edge cases exhaustively — that is the deliverable.
- Run against the project's real runtime; use a real test database when the project has a datastore. Never mock the datastore. If no test-DB harness exists, set up a minimal one and document it in your report.
- Create and edit test files only. Never edit production code.
- Stage named test files and commit with a pathspec: git commit -m "..." -- <test files>. The index is shared.
- When a test exposes a real defect: keep it as .skip with a test name beginning with `EXPOSES BUG:`, file a bug bead (br create --labels bug --title "[BUG] ...") with a reproducible report, and do not fix the defect.
- All non-skipped tests pass before you commit.

## Report
Your final message is your report: commit hash (test files only), functional/integration/e2e counts, edge cases covered, suite status, how the test DB is provisioned, and bug bead ids under a `[BUG]s found` section.

Follow the tester agent workflow for everything else.
```
