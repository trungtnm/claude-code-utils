---
description: Wrap up a completed session — audit decisions, close beads, sync state, and commit
---

The user has confirmed that the current work is complete. Follow these steps:

0.5. **Audit decisions** — If significant work was done this session (beads completed, features implemented), run `/t:audit-decisions today` to capture undocumented decisions. Append each new decision as a `##` section to `.ccu/DECISIONS.md`.

0.8. **Check for untriaged captures** — If `.ccu/CAPTURES.md` has unchecked items, warn: "There are N untriaged captures in .ccu/CAPTURES.md. Consider running /triage before ending the session."

1. **Commit changes** — Check `git status` and `git diff` for any uncommitted work. If there are staged or unstaged changes, commit them using the standard commit workflow (review changes, draft a descriptive message, commit). Do NOT add any `Co-Authored-By` trailer to commit messages. If there are no changes to commit, skip this step. Include the bead ID in the commit message if one exists from this session.

2. **Check if Beads is available** — Look for a `.beads/` directory at the repo root. If it does not exist, inform the user that the commit is done and Beads is not set up in this workspace, then skip the remaining steps.

3. **Ensure a bead exists** — If a bead was created earlier in this session, use it. If not, create one now with a title and details describing the work that was done:
   ```bash
   br create --title "<short description of work>" --labels <relevant-label> --priority <p0|p1|p2|p3>
   ```

4. **Add a summary comment** — Add a comment summarizing the work (files changed, key decisions, anything the next session should know):
   ```bash
   br comments add <bead-id> "<what was done, files changed, key decisions>"
   ```

5. **Close the bead** — Close it with a short completion reason:
   ```bash
   br close <bead-id> --reason "Completed: <brief summary>"
   ```

6. **Sync beads** — Export the updated state so other sessions and agents can see it:
   ```bash
   br sync --flush-only
   ```

7. **Record session outcome in CM** — If `cm` is installed, record the session outcome so CM can learn from this work (skip silently if `cm` is not available):
   ```bash
   cm outcome success <rule-ids-used-this-session> 2>/dev/null
   ```
   If any CM rules were particularly helpful or harmful during this session, record feedback:
   ```bash
   cm mark <bullet-id> --helpful 2>/dev/null
   cm mark <bullet-id> --harmful --reason "<why>" 2>/dev/null
   ```

8. **Confirm** — Let the user know the session tracking is complete.
