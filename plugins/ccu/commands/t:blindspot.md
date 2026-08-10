---
description: Surface your unknown unknowns about a domain or module before starting work in it
argument-hint: [domain, feature, or module you feel unfamiliar with]
---

Blind-spot pass before entering unfamiliar territory — a domain the user hasn't worked in, a module they didn't write, a technology the project uses that they only half know. The deliverable is a briefing that surfaces the questions the user didn't know to ask, so the follow-up discussion, plan, or prompt starts from a real map instead of a partial one.

**Topic: `$ARGUMENTS`**

## Steps

1. **Calibrate** — One question, multiple choice: what does the user already know about this topic?
   - Nothing — never touched it
   - Familiar — used it, never built with it
   - Experienced — built with it, but not in this codebase

   The answer sets the briefing's depth: a beginner gets vocabulary and mental models; an experienced user gets only this-repo specifics and potholes.

2. **Investigate** — Build the map before briefing:
   - The in-repo surface: which modules/files the topic touches, how they are structured, 2–3 representative files read in full
   - Historical work: `git log --oneline -20 -- <relevant paths>`, `docs/adr/` entries touching the area, a targeted grep of `.ccu/DECISIONS.md` (its entries are dated claims — apply the epistemics rule in [[session-state]]), prior beads (`br list --json 2>/dev/null` filtered by keyword)
   - Domain knowledge beyond the repo: what "good" looks like in this domain, standard approaches, common failure modes — use web search when the domain is outside your confident knowledge
   - The quality bar: what distinguishes a passable result from a good one in this domain (the article-class unknown "do I know how good something can be?")

3. **Brief** — Deliver in conversation, calibrated to step 1, organized as:
   - **Mental model** — the 3–5 concepts that make the domain legible (skip for experienced users)
   - **This repo's version** — how the codebase already does it: patterns to imitate with exact paths, prior decisions that constrain new work, infrastructure that already exists
   - **Potholes** — the mistakes newcomers to this domain/module make, and the past incidents or reverts `git log` reveals
   - **The quality bar** — what a good result looks like here, with a concrete example when one exists in-repo
   - **Questions you didn't know to ask** — 5–8 questions the user should now be able to answer or investigate before starting work

4. **Improve the next prompt** — End the briefing with 3–5 concrete additions for the user's follow-up prompt or `/t:discuss` session: constraints to state, references to point at, decisions to pre-make. These are the payoff — the pass exists to make the next instruction better.

5. **Record** — Write the briefing to `.ccu/artifacts/<yyyy-mm-dd>-blindspot-<slug>/briefing.md` so `/t:discuss` and `/plan-beads` sessions can consume it. Skip the file when `.ccu/` doesn't exist and the user declines to create it.

## Rules

- **Teach, don't implement** — no code changes, no beads filed. The briefing is the deliverable; end on it.
- **Repo evidence over general knowledge** — every "this repo does X" claim carries a path; general domain claims are labeled as such.
- **Calibrate ruthlessly** — repeating what the user already knows buries the actual blind spots. When in doubt, ask one more calibration question rather than pad the briefing.
- **Name the unknowns honestly** — when the domain is outside your confident knowledge and search doesn't settle it, say so; a briefing that hides its own blind spots defeats the purpose.
