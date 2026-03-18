---
name: triage
description: >-
  Classify captured ideas from .ccu/CAPTURES.md into actionable categories.
  Converts captures to beads, quick-fixes, or deferred items. Use when you
  have pending captures to process, between tasks, or when /t:next suggests
  triaging. Triggers on triage, captures, classify, process ideas, sort backlog.
domain: project-management
role: specialist
triggers:
  - triage
  - captures
  - classify ideas
  - process captures
  - sort backlog
---

# Capture Triage Pipeline

Converts the messy idea queue in `.ccu/CAPTURES.md` into structured, actionable work items. This is where random thoughts become beads, quick-fixes, or conscious deferrals.

## Prerequisites

- `.ccu/CAPTURES.md` must exist with at least one unchecked item (`- [ ]`)
- Beads (`br` CLI) should be available for creating new work items

If CAPTURES.md doesn't exist or has no unchecked items, report "Nothing to triage" and stop.

## Triage Flow

For each unchecked capture in `.ccu/CAPTURES.md`:

### 1. Read and Understand

Read the capture text. If the meaning is ambiguous, briefly investigate the codebase for context (check the referenced file/module/feature). Keep investigation under 30 seconds per capture.

### 2. Classify

| Classification | Criteria | Action |
|---------------|----------|--------|
| **quick-fix** | Can be done in <5 minutes, no design decisions | Do it now, commit, mark capture |
| **new-bead** | Substantial work requiring tracking | Create bead via `br create`, mark capture with bead ID |
| **inject** | Belongs in an existing open bead | `br comments add <existing-bead>`, mark capture |
| **defer** | Valid but not urgent, no active epic for it | Leave unchecked, append `[deferred]` |
| **out-of-scope** | Not relevant to current project goals | Mark checked with `(out-of-scope: reason)` |

### 3. Execute

**quick-fix**: Implement the fix immediately, commit, then update the capture line:
```
- [x] 2026-03-19 10:15 — fix typo in error message (quick-fix, commit abc123)
```

**new-bead**: Create a tracked work item:
```bash
ACTOR="${BR_ACTOR:-assistant}"
br create --actor "$ACTOR" "<title from capture>" --priority <assessed> --type <task|bug|feature> --labels from-capture
```
Update capture: `- [x] 2026-03-19 10:15 — {text} (-> bead {ID})`

**inject**: Add to existing bead and mark:
```bash
br comments add --actor "$ACTOR" <existing-bead-id> --message "From capture: {text}"
```
Update capture: `- [x] 2026-03-19 10:15 — {text} (injected into {bead-id})`

**defer**: Append tag, don't check the box:
```
- [ ] 2026-03-19 10:15 — {text} [deferred]
```

**out-of-scope**: Check and explain:
```
- [x] 2026-03-19 10:15 — {text} (out-of-scope: not aligned with current goals)
```

### 4. Summary

After processing all captures, report:
```
Triage complete:
- N quick-fixes applied
- N new beads created
- N injected into existing beads
- N deferred
- N out-of-scope
```

## Graceful Degradation

If `br` is not available: skip bead creation and injection. Instead, write actionable items as a TODO section at the bottom of CAPTURES.md. Quick-fixes and out-of-scope classification still work without `br`.

## Rules

- **Process ALL unchecked captures** — don't skip any (except `[deferred]` items, re-assess those only if context has changed)
- **Be decisive** — classify quickly, don't over-analyze. 30 seconds max per capture.
- **Prefer inject over new-bead** — if an existing bead covers 80% of the capture, inject rather than creating a duplicate
- **Quick-fixes earn their name** — if it takes more than 5 minutes, reclassify as new-bead
