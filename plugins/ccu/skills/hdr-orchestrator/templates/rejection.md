# REJECTION-\<n\>.md Template

Written by the coordinator to `.ccu/delegations/<id>/REJECTION-<n>.md` — **before** any keystroke is injected. The file is the durable order; the injected message only points at it. If the pane died, a fresh same-host peer at the repo root is pointed to this file and the original brief — the rejection never depends on a keystroke having landed.

`<n>` starts at 1 and increments per rejection of the same delegation (ledger tracks the count). Three rejections → the coordinator stops and escalates to the user.

```markdown
# Rejection <n>: <YYYYMMDD>-<kebab-slug>

Rejected: <ISO timestamp>
Bead: <bead-id>

## What failed
<!-- One line per failed verification check, by name:
     result-incomplete | missing-commit | missing-trailer | scope-drift |
     smell | foreign-edit-hold | full-suite-red | bead-not-closed |
     assertion-line-edit | reviewer-finding -->
- <check>: <one-line statement of the failure>

## Evidence
<!-- Exact, reproducible: SHAs, file paths, grep output lines, failing test names
     with the command that shows them. The peer must be able to see exactly what
     you saw without asking. -->

## What to redo
<!-- Concrete instructions, ordered. Reference the bead for the spec — do NOT
     restate its content here. End with: re-run your scoped gates, commit with
     trailers, rewrite RESULT.md, close the bead. -->
1. <step>
2. Re-run your scoped gates, commit (pathspec + trailers), rewrite RESULT.md<bead repos: , then `br close <bead-id>`>.
```
