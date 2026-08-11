---
name: peer-review
description: Review code for bugs, security, and reliability issues; diagnose root causes and fix them
argument-hint: [scope]
---

Review code for bugs, errors, inefficiencies, security issues, and reliability problems. Diagnose root causes using first-principle analysis and fix them. Use ultrathink.

**Scope: `$ARGUMENTS`**

If a bead ID or epic ID is provided above, use `br show <id>` to understand the issue, find the relevant code changes (check git log for commits referencing that bead ID, and inspect the files touched), and focus your review on that scope. If no argument is provided, cast a wide net across the project — survey git history, check multiple branches, and don't restrict yourself to recent commits.

## Steps

1. **Determine review scope** — Check whether `$ARGUMENTS` contains a bead/epic ID or description:
   - **If a bead/epic ID is given**: Run `br show <id>` to understand the task. Find commits referencing that ID in git log. Identify all files touched by those commits. This is your review scope.
   - **If a description is given**: Use it to locate the relevant code area and focus your review there.
   - **If no argument is given**: Survey recent and not-so-recent git history broadly. Look at multiple branches if relevant. Identify code written by other agents or contributors that may not have been thoroughly reviewed.

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

7. **Report back** — If reviewing a specific bead, add a comment to the bead summarizing findings: `br comments add <id> "Peer review: <summary of findings and fixes>"`.

## Rules

- **Go super deep** — Surface-level review catches nothing useful. Trace execution paths, check data flow, verify assumptions.
- **No sacred cows** — Review all code equally regardless of who wrote it or when.
- **Fix root causes** — Don't add bandaids. If a pattern is broken, fix the pattern.
- **Verify fixes** — Run tests after making changes. Don't introduce new bugs while fixing old ones.
- **Stay in scope** — When a specific bead/epic is given, focus on that work. Don't wander into unrelated code unless you find a systemic issue connected to the scoped changes.
