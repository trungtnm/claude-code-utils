Append an idea or observation to `.ccu/CAPTURES.md` for later triage. This should take less than 5 seconds.

**Capture: `$ARGUMENTS`**

## Steps

1. **Ensure .ccu/ exists** — If `.ccu/` doesn't exist, create it and initialize `CAPTURES.md`. Ensure gitignore rules are in place for ephemeral files.

2. **Append the capture** — Add a new unchecked item to `.ccu/CAPTURES.md`:
   ```
   - [ ] {YYYY-MM-DD HH:MM} — {$ARGUMENTS}
   ```
   If no argument was provided, ask the user what they want to capture.

3. **Confirm** — Report: "Captured. {N} total untriaged items in queue."

## Rules

- **Fast and non-disruptive** — do not investigate, analyze, or act on the capture. Just record it.
- **No duplicate checking** — just append. Deduplication happens during triage.
- **No formatting** — write the capture exactly as the user said it. Don't rewrite or improve it.
