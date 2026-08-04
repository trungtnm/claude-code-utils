---
description: Diagnose and fix the root cause of the described bugs — no bandaid fixes
argument-hint: [error details or context]
---

Diagnose and fix the ROOT CAUSE of the bugs or errors described below. No bandaid fixes. Use extended thinking to reason through causal chains before acting.

The user has provided the following error details / context as arguments:
${ARGUMENTS}

## Steps

1. **Understand the symptoms** — Read the error messages, stack traces, screenshots, or bug descriptions provided above. Identify every distinct symptom.

2. **Reproduce and trace** — Find the relevant code paths. Read the source files involved. Trace the execution flow from entry point through to where the error manifests. Read logs and inspect state to build a complete picture.

3. **Find the root cause** — Use ultrathink. Keep asking "why?" until you reach the actual underlying cause, not the surface symptom. Common traps to avoid:
   - Fixing where the error is *thrown* instead of where the bad state is *created*
   - Silencing an error instead of preventing the condition that triggers it
   - Adding a null check instead of understanding why the value is null
   - Catching an exception instead of preventing it
   - Adding a retry instead of fixing why it fails

4. **Verify your diagnosis** — Before writing any fix, explain to the user:
   - What is the root cause?
   - Why does this cause produce the observed symptoms?
   - Are there other symptoms this same root cause might produce?
   - Could there be a deeper cause beneath this one?

5. **Implement the real fix** — Fix the root cause directly. The fix should:
   - Eliminate the bad state or condition at its source
   - Not introduce defensive checks that merely hide the problem
   - Not add complexity that wouldn't be needed if the root cause were properly resolved
   - Handle any other symptoms produced by the same root cause

6. **Verify the fix** — Run tests, reproduce the original scenario, and confirm the symptoms are gone. Check that the fix doesn't introduce regressions.

## Rules

- **No bandaids** — If your fix involves `try/catch` that swallows errors, `|| fallbackValue`, `if (x != null)` guards around broken data, or `setTimeout` to "wait for it to be ready", stop and dig deeper.
- **Fix one root cause, not many symptoms** — If multiple symptoms share a root cause, one fix should resolve them all. Don't patch each symptom individually.
- **Explain the diagnosis** — Before writing any code, clearly explain what the root cause is and why your fix addresses it. The user should understand what went wrong.
- **Minimal diff** — Change only what's necessary to fix the root cause. Don't refactor surrounding code.
