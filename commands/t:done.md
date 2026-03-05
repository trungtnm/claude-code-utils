The user has confirmed that the current work is complete. Follow these steps:

1. **Commit changes** — Check `git status` and `git diff` for any uncommitted work. If there are staged or unstaged changes, commit them using the standard commit workflow (review changes, draft a descriptive message, commit). If there are no changes to commit, skip this step. Include the bead ID in the commit message if one exists from this session.

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

7. **Confirm** — Let the user know the session tracking is complete.
