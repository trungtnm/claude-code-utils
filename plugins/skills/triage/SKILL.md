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

Read the capture text. Briefly investigate the codebase for context — check the referenced file/module/feature, read `.ccu/DECISIONS.md` for prior decisions, and `git log --oneline -10` for recent activity.

### 2. Classify

| Classification | Criteria | Action |
|---------------|----------|--------|
| **quick-fix** | Can be done in <5 minutes, no design decisions | Do it now, commit, mark capture |
| **new-bead** | Substantial work requiring tracking | Discuss with user, then create rich bead |
| **inject** | Belongs in an existing open bead | `br comments add <existing-bead>`, mark capture |
| **defer** | Valid but not urgent, no active epic for it | Leave unchecked, append `[deferred]` |
| **out-of-scope** | Not relevant to current project goals | Mark checked with `(out-of-scope: reason)` |

### 3. Execute

**quick-fix**: Implement the fix immediately, commit, then update the capture line:
```
- [x] 2026-03-19 10:15 — fix typo in error message (quick-fix, commit abc123)
```

**new-bead**: A one-liner capture is NOT enough for an agent to work on. Before creating the bead, run a mini-discussion to enrich it:

1. **Investigate the codebase** — find relevant files, existing patterns, constraints
2. **Ask the user 1-3 targeted questions** — one at a time, multiple choice preferred:
   - What exactly should change? (scope)
   - What does success look like? (acceptance criteria)
   - Any constraints or preferences? (approach)
   Skip questions you can answer from the codebase investigation.
3. **Create a rich bead** with enough context for an agent to work autonomously:
   ```bash
   ACTOR="${BR_ACTOR:-assistant}"
   br create --actor "$ACTOR" "<clear title>" \
     --priority <assessed> \
     --type <task|bug|feature> \
     --labels from-capture \
     --description "$(cat <<'BEAD'
   ## Context
   <Why this matters. What prompted it.>

   ## What to Change
   <Specific files, modules, or behaviors to modify.>

   ## Acceptance Criteria
   - [ ] <verifiable criterion 1>
   - [ ] <verifiable criterion 2>

   ## Technical Notes
   <Existing patterns to follow, constraints, relevant files found during investigation.>
   BEAD
   )"
   ```
4. Update capture: `- [x] 2026-03-19 10:15 — {text} (-> bead {ID})`

The bead description must be self-contained — a worker agent with zero prior context should be able to read it and start implementing without asking questions.

**inject**: Add enriched context (not just the raw capture text) to existing bead:
```bash
br comments add --actor "$ACTOR" <existing-bead-id> --message "From capture: {text}. Investigation: {what you found in the codebase}. Suggestion: {recommended approach}."
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
- **Classify quickly, enrich thoroughly** — classification is fast (seconds), but new-bead enrichment takes time (1-3 questions per bead). This is intentional: cheap captures in, rich beads out.
- **Beads must be agent-ready** — a worker agent reading the bead description should be able to start implementing without asking questions. If the bead doesn't have context, acceptance criteria, and technical notes, it's not ready.
- **Prefer inject over new-bead** — if an existing bead covers 80% of the capture, inject rather than creating a duplicate
- **Quick-fixes earn their name** — if it takes more than 5 minutes, reclassify as new-bead
- **One question at a time** — when enriching new-beads, ask the user one question at a time, multiple choice preferred. Don't batch 5 questions into one message.
