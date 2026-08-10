# Verification

Verify a bead when its worker reports completion. Read the bead, the worker's report, and the commit diff before accepting.

## Report contract

The report (the worker's final message, mirrored in mail and a bead comment) must contain the commit hash, test counts, the bead status confirmed via `br show`, and the actual scope with a reason for any path beyond the `## Files` forecast. Reject an incomplete report.

## Commit and bead state

```bash
git log --grep="Bead: <bead-id>" --oneline    # at least one commit exists
git show <hash> --stat                        # changed paths
br show <bead-id> --json                      # status "done"
```

## Scope and causality

Compare the diff with the bead's `## Files` forecast and the reported actual scope. Do not reject a path only because the forecast omitted it. For each unplanned path, verify the change is:

- necessary for an acceptance criterion or an affected gate;
- minimal for that need;
- explained in the report;
- free of a reservation held by another active worker.

Reject unrelated edits, unexplained expansion, and another worker's swept-up staged files. The pathspec commit rule (`git commit -m "..." -- <paths>`) exists to prevent sweeping; a commit containing foreign staged work fails regardless of intent.

Assign a failing gate by causality, not by path: a failure caused by the worker's change belongs to the worker even when the failing file is outside `## Files`; an independent failure is recorded, not charged to the bead.

## Smell check

```bash
git show <hash> -p -- . ':(exclude)*test*' ':(exclude)*spec*' \
  | grep -inE '(mock|stub|placeholder|not.implemented|TODO|FIXME|test\.skip|it\.skip)' \
  | head -20
```

Read every hit in context; reject behavior, not substrings in unrelated identifiers. Mock or stub behavior in production files fails `production` work; it is allowed in test files and in `demo`/`mockup` work. One skip is legitimate: a tester-owned test whose name begins with `EXPOSES BUG:` and whose bug bead exists (`br list --labels bug --json`). A coder commit never contains skips.

## Rejection

Write the rejection as mail on the epic thread (what failed, what a passing resubmission contains), then resume the live worker with `SendMessage` or respawn a fix-scoped worker pointing at the thread, per [agent-mail.md](agent-mail.md). Stop after three rejections on one bead and report the evidence to the user.

## Tester phase

The tester commit may change only test paths. Verify:

```bash
git log --grep="Bead: <test-bead-id>" --oneline
git show <hash> --stat                        # test files only
br show <test-bead-id> --json
```

Compare the delivered tests with the test-plan checklist the tester posted as a bead comment; every item is delivered or explicitly explained. Happy-path-only coverage is incomplete — send it back. The tester runs against the project's real runtime, and against a real test database when the project has a datastore; it never mocks the datastore and never edits production code. A missing test-DB harness is legitimate new infrastructure, not a violation.

## Bug routing

Each `[BUG]` bead goes to a fresh fix-scoped worker whose prompt carries the bug bead id, the failing test location (`{TEST_FILE}::{TEST_NAME}`), and the original bead id. The fixer reproduces via the skipped test, fixes production code at root cause without weakening the test, un-skips the test in the same fix commit, re-runs the gates, and closes the bug bead with the fix hash. Verify the fix commit like any bead and confirm the previously skipped test runs green. Proceed to review only when `br list --labels bug --json` shows no open bug bead for the epic, or the user has explicitly deferred the remainder.

## Reviewer phase

The reviewer reports Critical / Recommended / Nits with a verdict, then writes documentation once the verdict is PASS or the criticals are acknowledged out of scope. On NEEDS_FIXES with criticals, ask the user whether to fix critical only, fix all, or accept as-is; spawn a fix-scoped worker for the chosen set and re-verify its commit.
