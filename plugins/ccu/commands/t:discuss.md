---
description: Guided requirements gathering for a feature; produces .ccu/ artifacts that feed /plan-beads
argument-hint: [topic]
---

Guided requirements gathering for a new feature or change. Produces structured artifacts in `.ccu/` that feed directly into `/plan-beads`.

**Topic: `$ARGUMENTS`**

## Steps

1. **Initialize .ccu/** — Ensure `.ccu/` exists. If not, create it.

2. **Load project context** — Before doing anything else, build situational awareness by reading (skip any that don't exist):
   - `CLAUDE.md` or `AGENTS.md` — project conventions, rules, architecture
   - `README.md` — what the project is and how it works
   - `CONTEXT.md` + a scan of `docs/adr/` — the curated current truth (terms, standing decisions)
   - `br list --json 2>/dev/null` — open beads (so you don't duplicate planned work)
   - `git log --oneline -15` — recent activity and direction
   This context shapes every question you ask. Without it, your advice will be generic and miss the project's specific situation.

3. **Capture the vision** — If a topic was provided above, confirm your understanding in light of the project context you just loaded. If not, ask: "What problem are you trying to solve?" Get a clear 1-2 sentence goal.

   If the user signals low familiarity with the topic's domain or module ("chưa rõ", "chưa từng làm", "I don't know this area"), run a blind-spot pass first — the `/t:blindspot` flow: calibrate their level, investigate the domain and the in-repo surface, brief them on the unknowns they didn't know to ask about — then continue here. Interviewing someone about a domain they can't see wastes both sides' questions.

4. **Estimate scope** — Based on the vision AND project context:
   - **Small** — single file, <1 hour, no architectural decisions
   - **Medium** — multiple files, 1-4 hours, some design choices
   - **Large** — cross-cutting, 4+ hours, architectural decisions needed
   - **Epic** — multi-session, needs decomposition into beads

5. **Investigate the codebase** — Go deeper into the code relevant to the topic:
   - Find similar patterns or features already implemented
   - Identify files and modules that would be affected
   - Check for existing infrastructure that can be reused
   - Cross-reference standing decisions: `docs/adr/` and, for the "why" behind them, a targeted grep of `.ccu/DECISIONS.md` (its entries are dated claims — apply the epistemics rule in [[session-state]]). Don't propose something that contradicts a standing decision without acknowledging the conflict
   Summarize your findings to the user.

6. **Ask targeted questions** — Based on what you found, ask specific questions about:
   - Edge cases the codebase investigation revealed
   - Ambiguous scope boundaries (what's in vs. out)
   - Technical constraints or tradeoffs discovered
   - Conflicts with prior decisions that need resolution
   - UX decisions that need human judgment
   **One question at a time. Multiple choice when possible.**

   **Order by architectural impact:** ask first the questions whose answer would change the data model, an interface, or a user-facing flow; mechanical details come last or not at all — implementation can absorb those without a decision.

   **For visual/UX-heavy topics:** offer to mock 2–4 divergent design directions (a quick React + shadcn/Tailwind demo, per the repo's demo convention) for the user to react to before locking requirements. Reacting to a prototype is cheaper than discovering misaligned expectations during implementation.

7. **Record outcomes** — Requirements become beads, not a log: file must-do requirements via `/file-beads` (small, clear) or carry them into `/plan-beads` (epic-sized) — beads are the only requirement store with a real lifecycle. Decisions made during the discussion follow the promote rule in [[session-state]]: ADR-gate decisions get `docs/adr/NNNN-slug.md` + a one-line `.ccu/DECISIONS.md` pointer; below-gate decisions get a journal entry in the shared schema.

8. **Offer next steps** — Ask:
   - "Run `/file-beads` to create the bead?" - in case the issue is small and clear
   - "Run `/plan-beads` to decompose into beads?" - in case the issue is large and should be consider as an Epic
   - "Run `/brainstorming` for deeper design exploration?"
   - "Just start implementing?"

## Rules

- **One question at a time** — never ask multiple questions in a single message
- **Multiple choice preferred** — when you can enumerate options, present them as choices
- **Investigate before asking** — don't ask questions the codebase can answer
- **Short discussions** — aim for 3-6 questions total, not 20
- **No implementation** — this command produces requirements and decisions, not code
- **Graceful without .ccu/ or beads** — if neither is available, output requirements and decisions to the conversation instead
