Review code written by other agents (or other contributors) across the project. Find bugs, errors, inefficiencies, security issues, and reliability problems. Diagnose root causes using first-principle analysis and fix them. Use ultrathink. Cast a wide net — don't restrict yourself to recent commits.

## Steps

1. **Survey recent and not-so-recent changes** — Look at git history beyond just the latest commits. Check multiple branches if relevant. Identify code written by other agents or contributors that may not have been thoroughly reviewed.

2. **Read with skepticism** — Approach each piece of code assuming it might contain errors. AI-generated code has characteristic failure modes:
   - Plausible-looking but subtly wrong logic
   - Correct happy path but broken edge cases
   - Copy-paste patterns where names or values weren't fully updated
   - Over-engineered abstractions that obscure simple bugs
   - Missing integration between components (each piece works alone but not together)
   - Hallucinated APIs or method signatures that don't exist

3. **First-principle analysis** — For each suspicious area, reason from first principles:
   - What is this code supposed to accomplish?
   - Does the implementation actually achieve that goal?
   - What invariants should hold? Do they?
   - What happens at the boundaries — empty inputs, max values, concurrent access, network failures?

4. **Check for systemic issues** — Look beyond individual bugs for patterns:
   - Inconsistent error handling strategies across modules
   - Data validation in some paths but not others
   - Security checks that can be bypassed through alternative code paths
   - Performance traps (N+1 queries, unbounded growth, missing indexes)
   - Resource leaks (unclosed connections, uncleared timers, unremoved listeners)

5. **Diagnose root causes** — Don't just find symptoms. Understand WHY the bug exists. Is it a misunderstanding of the API? A wrong assumption about data shape? A missing requirement?

6. **Fix with precision** — Apply minimal, targeted fixes. Explain what was wrong and why your fix is correct.

## Rules

- **Go super deep** — Surface-level review catches nothing useful. Trace execution paths, check data flow, verify assumptions.
- **No sacred cows** — Review all code equally regardless of who wrote it or when.
- **Fix root causes** — Don't add bandaids. If a pattern is broken, fix the pattern.
- **Verify fixes** — Run tests after making changes. Don't introduce new bugs while fixing old ones.
