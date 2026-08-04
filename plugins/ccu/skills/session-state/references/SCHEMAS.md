# .ccu/ File Schemas

Exact formats for each artifact file. Commands and skills should follow these formats when writing to `.ccu/`.

## SESSION.md

```markdown
# Session State

## Current Phase
- **phase:** {priming | planning | working | reviewing | wrapping-up}
- **command:** {the active command, e.g., t:auto}
- **started:** {ISO timestamp}

## Active Beads
- {bead-id} ({status}) — {title}

## Last Action
- **action:** {bead_claimed | bead_completed | verification_failed | ...}
- **bead:** {bead-id}
- **timestamp:** {ISO timestamp}
```

## CHECKPOINT.md

```markdown
# Checkpoint

## Context
- **command:** {the command that was running}
- **iteration:** {loop count, if applicable}
- **timestamp:** {ISO timestamp}

## Completed This Session
- [x] {bead-id} — {title} (commit {hash})

## In Progress
- {bead-id} — {title}
  - status: {what step the work was on}
  - files_touched: [{list of files}]

## Pending
- {bead-id} — {title}

## Recovery Instructions
{Free-text guidance for the next session on how to resume.}

## Recipe State (if a recipe is active)
- **recipe:** {name, e.g., new-feature}
- **step:** {current step number}
- **completed:** [{list of completed step numbers}]
- **context:** {$ARGUMENTS passed to the recipe}
```

## HANDOFF.md

All .ccu/ artifact writes MUST include the staleness header so consumers can detect outdated content.

```markdown
---
last_updated: {ISO timestamp, e.g., 2026-03-24T08:00:00Z}
session_id: {session UUID}
---

# Session Handoff

## Decisions Made
- {decision and why — e.g., "Chose retry over skip because blocked beads get human review"}

## Next Action
{Explicit single recommendation for what the next session should do first.}

## Open Questions
- {anything unresolved that needs human input}

## In-Progress Beads
- {bead-id} — {title}: {current state and what remains}
```

**Note:** "What Was Done" and "Dead Ends" sections are no longer included — CASS auto-indexes session history, and CM captures anti-patterns via `cm mark --harmful`.

## EVIDENCE.md

Each entry is a structured record appended after a bead is completed. Entries are separated by `---`.

```markdown
# Evidence Log

---
## {bead-id} — {title}
- **commit:** {hash}
- **files_changed:** {comma-separated list from git diff --name-only HEAD~1}
- **lines:** +{added} / -{removed}
- **verification:**
  - tests: {N passed / M total}
  - lint: {pass | fail | N/A}
  - typecheck: {pass | fail | N/A}
  - build: {pass | fail | N/A}
  - ubs: {pass | fail | N/A}
- **completed:** {ISO timestamp}
- **actor:** {agent name or "user"}
```

## REQUIREMENTS.md

Requirements gathered from `/t:discuss` sessions. Each requirement has a state. Append new requirements, update states in place.

```markdown
# Requirements

---
## R001 — {short title}
- **date:** {YYYY-MM-DD}
- **state:** {active | validated | deferred | out-of-scope}
- **description:** {what is needed}
- **acceptance:** {how to verify it's done}
- **source:** {which /t:discuss session or conversation}
```

## DECISIONS.md

Each entry is an architectural or design decision with context. Entries are separated by `---`. Number decisions sequentially.

```markdown
# Architectural Decisions

---
## D001 — {short title}
- **date:** {YYYY-MM-DD}
- **context:** {what prompted this decision}
- **decision:** {what was decided}
- **rationale:** {why this over alternatives}
- **alternatives:** {what else was considered}
```

## CAPTURES.md

Simple checklist format. Unchecked = untriaged. Checked = processed.

```markdown
# Captures

- [ ] C{NN} | {YYYY-MM-DD HH:MM} — {idea text}
- [ ] C{NN} | {YYYY-MM-DD HH:MM} — {idea text} [attachment: .ccu/captures/{filename}]
- [x] C{NN} | {YYYY-MM-DD HH:MM} — {idea text} (-> bead {id})
- [x] C{NN} | {YYYY-MM-DD HH:MM} — {idea text} (out-of-scope: {reason})
```

