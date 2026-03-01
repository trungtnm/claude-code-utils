The user has confirmed that the current work is complete. Follow the **Session Work Tracking** steps:

1. **Check if Beads is available** — Look for a `.beads/` directory at the repo root. If it does not exist, inform the user that Beads is not set up in this workspace and skip the remaining steps.

2. **Ensure a bead exists** — If a bead was created earlier in this session, use it. If not, create one now with a title and details describing the work that was done:
   ```bash
   br create --title "<short description of work>" --labels <relevant-label> --priority <p0|p1|p2|p3>
   ```

3. **Add a summary comment** — Add a comment summarizing the work (files changed, key decisions, anything the next session should know):
   ```bash
   br comments add <bead-id> "<what was done, files changed, key decisions>"
   ```

4. **Close the bead** — Close it with a short completion reason:
   ```bash
   br close <bead-id> --reason "Completed: <brief summary>"
   ```

5. **Sync beads** — Export the updated state so other sessions and agents can see it:
   ```bash
   br sync --flush-only
   ```

6. **Confirm** — Let the user know the session tracking is complete.
