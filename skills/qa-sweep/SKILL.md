---
name: qa-sweep
description: "Full quality sweep of the codebase: random code inspection, peer review of agent-written code, and UI/UX polish pass. Use when you want a thorough quality check before shipping, after a burst of agent work, or when the codebase needs a health check. Triggers on 'quality sweep', 'QA pass', 'review everything', 'check the codebase', 'polish everything'."
---

# QA Sweep

Three-phase quality assurance workflow that systematically finds and fixes issues across code correctness, agent-written code quality, and UI/UX polish.

<AUTONOMOUS>
Execute all phases immediately without asking questions or requesting confirmation. The user expects you to just do the work. Do not ask "should I proceed?", "which files should I check?", or "are you sure?". Start Phase 1 right away and work through all phases autonomously. Only stop to ask if you encounter a genuinely ambiguous situation where proceeding could cause damage.
</AUTONOMOUS>

## When to Use

- Before a release or merge to main
- After a burst of multi-agent work
- When you suspect accumulated quality debt
- When the user says "check everything", "quality pass", "sweep the codebase"

## Phases

Run these phases in order. Each phase builds on the previous — code correctness first, then deeper agent review, then user-facing polish.

### Phase 1: Random Code Inspection

Randomly explore code files, deeply investigate their functionality, trace execution flows, and fix any bugs or issues found. Use extended thinking.

1. **Sample broadly** — Pick code files semi-randomly across different parts of the project. Don't just look at the most obvious entry points — dig into utilities, helpers, middleware, workers, and less-visited corners of the codebase.

2. **Deep-read each file** — For each file you pick, read it completely. Understand what it does, why it exists, and how it fits into the larger system.

3. **Trace connections** — Follow the imports and exports. Read the files that this file imports from, and find the files that import from it. Understand the full execution flow — where data comes from, how it's transformed, where it goes.

4. **Inspect with fresh eyes** — Once you understand the purpose and context, do a careful, methodical, critical review looking for:
   - Obvious bugs, logic errors, off-by-one mistakes
   - Silly mistakes like typos, copy-paste errors, wrong variable names
   - Missing error handling at system boundaries
   - Race conditions or state management issues
   - Dead code, unreachable branches, impossible conditions
   - Inconsistencies with how similar patterns are handled elsewhere
   - Security issues (injection, unsanitized input, exposed secrets)

5. **Check against project standards** — Read AGENTS.md (if present) and any referenced best-practice guides. Verify the code conforms.

6. **Fix what you find** — For each issue, fix it directly. Keep fixes minimal and targeted.

7. **Move on and repeat** — Cover at least 3-4 different areas of the codebase.

**Rules for Phase 1:**
- Go deep, not wide — thoroughly understand 10 files rather than skim 50.
- Follow the threads — trace suspicious code to its root before deciding if it's a real issue.
- Fix real problems only — don't nitpick style.

### Phase 2: Peer Review of Agent-Written Code

Review code written by other agents or contributors. Find bugs, errors, inefficiencies, security issues, and reliability problems. Diagnose root causes using first-principle analysis and fix them. Use ultrathink. Cast a wide net.

1. **Survey changes** — Look at git history beyond just the latest commits. Identify code that may not have been thoroughly reviewed.

2. **Read with skepticism** — AI-generated code has characteristic failure modes:
   - Plausible-looking but subtly wrong logic
   - Correct happy path but broken edge cases
   - Copy-paste patterns where names or values weren't fully updated
   - Over-engineered abstractions that obscure simple bugs
   - Missing integration between components
   - Hallucinated APIs or method signatures that don't exist

3. **First-principle analysis** — For each suspicious area:
   - What is this code supposed to accomplish?
   - Does the implementation actually achieve that goal?
   - What invariants should hold? Do they?
   - What happens at the boundaries?

4. **Check for systemic issues:**
   - Inconsistent error handling across modules
   - Data validation in some paths but not others
   - Security checks that can be bypassed through alternative code paths
   - Performance traps (N+1 queries, unbounded growth, missing indexes)
   - Resource leaks (unclosed connections, uncleared timers)

5. **Diagnose root causes** — Understand WHY each bug exists, then fix the cause, not the symptom.

**Rules for Phase 2:**
- Go super deep — surface-level review catches nothing useful.
- No sacred cows — review all code equally regardless of who wrote it.
- Fix root causes, not symptoms.

### Phase 3: UI/UX Polish Pass

Scrutinize every aspect of the application's UI/UX. Find things that are sub-optimal or wrong. Polish the interface to be slicker, more intuitive, and premium-feeling. Use extended thinking.

> **Note:** Skip this phase if the project has no user-facing interface.

1. **Walk the full user flow** — Go through every screen, interaction, and workflow. Read the component code, styles, and state management.

2. **Identify friction:**
   - Unclear labels, confusing terminology, ambiguous actions
   - Missing feedback (no loading states, no success confirmation, no error messages)
   - Jarring transitions or layout shifts
   - Inconsistent patterns across the app
   - Too many clicks for common tasks

3. **Evaluate visual quality** — Compare against premium standards (Stripe, Linear, Vercel):
   - Typography — hierarchy, readability, consistent sizing
   - Spacing — consistent padding/margins, alignment
   - Color — intentional palette, proper contrast
   - Micro-interactions — hover states, transitions, focus indicators
   - Empty and error states — designed or afterthoughts?

4. **Implement the polish** — Make the changes:
   - Tighten spacing and alignment
   - Add missing micro-interactions
   - Improve copy and labels for clarity
   - Add loading, empty, and error states where missing
   - Smooth transitions
   - Ensure visual consistency

**Rules for Phase 3:**
- Be opinionated — don't ask permission for obvious improvements.
- Sweat the details — premium feel comes from hundreds of tiny things done right.
- Don't redesign — polish what's there, don't change the design direction.

## Completion

After all phases, provide a summary:
- **Phase 1** — How many areas inspected, what was found and fixed
- **Phase 2** — What agent-written code issues were found, root causes identified
- **Phase 3** — What UI/UX improvements were made (or "skipped — no UI")
