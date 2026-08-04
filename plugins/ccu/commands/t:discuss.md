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
   - `.ccu/DECISIONS.md` — prior architectural decisions (so you don't re-litigate them)
   - `.ccu/REQUIREMENTS.md` — existing requirements (so you don't duplicate)
   - `.ccu/EVIDENCE.md` — recent completions (what was just built)
   - `git log --oneline -15` — recent activity and direction
   This context shapes every question you ask. Without it, your advice will be generic and miss the project's specific situation.

3. **Capture the vision** — If a topic was provided above, confirm your understanding in light of the project context you just loaded. If not, ask: "What problem are you trying to solve?" Get a clear 1-2 sentence goal.

4. **Estimate scope** — Based on the vision AND project context:
   - **Small** — single file, <1 hour, no architectural decisions
   - **Medium** — multiple files, 1-4 hours, some design choices
   - **Large** — cross-cutting, 4+ hours, architectural decisions needed
   - **Epic** — multi-session, needs decomposition into beads

5. **Investigate the codebase** — Go deeper into the code relevant to the topic:
   - Find similar patterns or features already implemented
   - Identify files and modules that would be affected
   - Check for existing infrastructure that can be reused
   - Cross-reference with prior decisions in `.ccu/DECISIONS.md` — don't propose something that contradicts an existing decision without acknowledging the conflict
   Summarize your findings to the user.

6. **Ask targeted questions** — Based on what you found, ask specific questions about:
   - Edge cases the codebase investigation revealed
   - Ambiguous scope boundaries (what's in vs. out)
   - Technical constraints or tradeoffs discovered
   - Conflicts with prior decisions that need resolution
   - UX decisions that need human judgment
   **One question at a time. Multiple choice when possible.**

7. **Write artifacts** — Save to `.ccu/`:
   - Append to `REQUIREMENTS.md`: requirements gathered from this discussion, with states (active/validated/deferred/out-of-scope)
   - Append to `DECISIONS.md`: any decisions made during the discussion (and WHY)

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
- **Graceful without .ccu/** — if .ccu/ can't be created, output requirements to conversation instead
