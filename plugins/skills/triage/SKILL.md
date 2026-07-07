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
| **reopen** | Feedback on a closed bead that reveals incomplete/broken work | Reopen bead with new acceptance criteria |
| **defer** | Valid but not urgent, no active epic for it | Leave unchecked, append `[deferred]` |
| **out-of-scope** | Not relevant to current project goals | Mark checked with `(out-of-scope: reason)` |

### 3. Execute

**quick-fix**: Implement the fix immediately, commit, then update the capture line:
```
- [x] 2026-03-19 10:15 — fix typo in error message (quick-fix, commit abc123)
```

**new-bead**: A one-liner capture is NOT enough for an agent to work on. Before creating the bead, run a mini-discussion to enrich it, then delegate the actual filing to the [[file-beads]] skill (single-bead mode):

1. **Investigate the codebase** — find relevant files, existing patterns, constraints. Note any high-risk surface (novel infra, security, billing, data-loss).
2. **Ask the user 1-3 targeted questions** — one at a time, multiple choice preferred:
   - What exactly should change? (scope)
   - What does success look like? (acceptance criteria)
   - Any constraints or preferences? (approach)
   Skip questions you can answer from the codebase investigation.
3. **Pick a template tier** (see [[file-beads]] Step 4):
   - **Tier 1 (minimal)** — small, well-trodden, no design decisions
   - **Tier 2 (standard)** — most beads land here (default)
   - **Tier 3 (high-risk)** — novel/external infra, security, billing, anything where being wrong is expensive
4. **Delegate to [[file-beads]]** in single-bead mode, passing the enriched payload:
   - Title (action-oriented)
   - Type, priority, labels (include `from-capture`)
   - Project context, what to change, acceptance criteria
   - For Tier 2+: reasoning, considerations, technical notes
   - For Tier 3: `⚠ HIGH RISK` reason + "investigate before coding" items

   file-beads owns the canonical `br create` invocation and template — do not embed your own template here.

5. Update capture: `- [x] 2026-03-19 10:15 — {text} (-> bead {ID})`

The bead description must be self-contained — a worker agent with zero prior context should be able to read it and start implementing without asking questions.

**inject**: Add enriched context (not just the raw capture text) to existing bead:
```bash
br comments add --actor "$ACTOR" <existing-bead-id> --message "From capture: {text}. Investigation: {what you found in the codebase}. Suggestion: {recommended approach}."
```
Update capture: `- [x] 2026-03-19 10:15 — {text} (injected into {bead-id})`

**reopen**: When a capture references work that was already done (a closed bead), investigate whether the closed bead actually addressed the concern. Check the bead's acceptance criteria, the commit that closed it, and the current code state.

- If the original fix is **incomplete or broken** — reopen the bead with the new feedback:
  ```bash
  br reopen --actor "$ACTOR" <bead-id>
  br comments add --actor "$ACTOR" <bead-id> --message "Reopened: {feedback from capture}. Original fix did not address: {what's still wrong}."
  br update --actor "$ACTOR" <bead-id> --description "$(cat <<'BEAD'
  ## Context
  <Original context + why it's being reopened>

  ## What Still Needs to Change
  <Specific gaps or regressions found>

  ## Acceptance Criteria
  - [ ] <new/updated verifiable criteria based on feedback>
  - [ ] <original criteria that were not met>

  ## Technical Notes
  <What the original fix did, what it missed, relevant files>
  BEAD
  )"
  ```
  Update capture: `- [x] 2026-03-19 10:15 — {text} (reopened bead {bead-id})`

- If the original fix is **actually correct** and the capture is a misunderstanding or a new/separate concern — classify as **new-bead** or **out-of-scope** instead. Don't reopen beads unnecessarily.

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
- N beads reopened
- N deferred
- N out-of-scope
```

## Graceful Degradation

If `br` is not available: skip bead creation and injection. Instead, write actionable items as a TODO section at the bottom of CAPTURES.md. Quick-fixes and out-of-scope classification still work without `br`.

## Rules

- **Process ALL unchecked captures** — don't skip any (except `[deferred]` items, re-assess those only if context has changed)
- **Classify quickly, enrich thoroughly** — classification is fast (seconds), but new-bead enrichment takes time (1-3 questions per bead). This is intentional: cheap captures in, rich beads out.
- **Delegate bead structure to [[file-beads]]** — never embed your own bead template here. Pass an enriched payload + chosen template tier to file-beads and let it own the `br create` call. This keeps triage and plan-driven filing consistent.
- **Match template tier to risk** — small obvious work gets Tier 1; default to Tier 2; escalate to Tier 3 for anything novel/external/security/billing. When in doubt, escalate one tier.
- **Beads must be agent-ready** — a worker agent reading the bead description should be able to start implementing without asking questions. The chosen tier's required sections are the minimum.
- **Prefer inject over new-bead** — if an existing bead covers 80% of the capture, inject rather than creating a duplicate
- **Quick-fixes earn their name** — if it takes more than 5 minutes, reclassify as new-bead
- **One question at a time** — when enriching new-beads, ask the user one question at a time, multiple choice preferred. Don't batch 5 questions into one message.
