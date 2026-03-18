Guided requirements gathering for a new feature or change. Produces structured artifacts in `.ccu/` that feed directly into `/planning`.

**Topic: `$ARGUMENTS`**

## Steps

1. **Initialize .ccu/** — Ensure `.ccu/` exists. If not, create it.

2. **Capture the vision** — If a topic was provided above, confirm your understanding. If not, ask: "What problem are you trying to solve?" Get a clear 1-2 sentence goal.

3. **Estimate scope** — Based on the vision, give a rough size estimate:
   - **Small** — single file, <1 hour, no architectural decisions
   - **Medium** — multiple files, 1-4 hours, some design choices
   - **Large** — cross-cutting, 4+ hours, architectural decisions needed
   - **Epic** — multi-session, needs decomposition into beads

4. **Investigate the codebase** — Before asking questions, look at the code:
   - Find similar patterns or features already implemented
   - Identify files and modules that would be affected
   - Check for existing infrastructure that can be reused
   Summarize your findings to the user.

5. **Ask targeted questions** — Based on what you found, ask specific questions about:
   - Edge cases the codebase investigation revealed
   - Ambiguous scope boundaries (what's in vs. out)
   - Technical constraints or tradeoffs discovered
   - UX decisions that need human judgment
   **One question at a time. Multiple choice when possible.**

6. **Write artifacts** — Save to `.ccu/`:
   - Append to `REQUIREMENTS.md`: requirements gathered from this discussion, with states (active/validated/deferred/out-of-scope)
   - Append to `DECISIONS.md`: any decisions made during the discussion (and WHY)

7. **Offer next steps** — Ask:
   - "Run `/planning` to decompose into beads?"
   - "Run `/brainstorming` for deeper design exploration?"
   - "Just start implementing?"

## Rules

- **One question at a time** — never ask multiple questions in a single message
- **Multiple choice preferred** — when you can enumerate options, present them as choices
- **Investigate before asking** — don't ask questions the codebase can answer
- **Short discussions** — aim for 3-6 questions total, not 20
- **No implementation** — this command produces requirements and decisions, not code
- **Graceful without .ccu/** — if .ccu/ can't be created, output requirements to conversation instead
