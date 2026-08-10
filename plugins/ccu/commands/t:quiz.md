---
description: Explain a change set and quiz the user on it before they merge code they didn't watch being written
argument-hint: [commit range, branch, or blank for the current session branch]
---

Comprehension gate for code produced without the user watching — an autonomous `/t:auto` or `/orchestrator` run, a long agent session, or any branch the user is about to merge unread. Produce an HTML explainer of the change set with a quiz at the bottom, then grade the user's answers in conversation. The user merges only what they can pass a quiz on.

**Range: `$ARGUMENTS`**

## Steps

1. **Resolve the change set** — In priority order:
   - `$ARGUMENTS` names a commit range (`a1b2c3..HEAD`) or a branch → use it (for a branch: `$(git merge-base <default-branch> <branch>)..<branch>`).
   - Otherwise → current branch vs the default branch: `$(git merge-base main HEAD)..HEAD` (substitute `master` when that is the default).

   Empty range → report "nothing to quiz on" and stop.

2. **Read every change** — `git log --oneline <range>`, then `git show <hash>` for each commit. Group commits by bead or feature (bead ids like `[xxx-1a2b]` in commit messages; otherwise by touched area). For each group, identify:
   - what changed and why it is shaped that way (data model, interfaces, control flow)
   - the riskiest or least obvious decisions — the places a reviewer would misjudge without context
   - anything that deviated from the plan (bead comments with `Deviation:`)

3. **Write the explainer** — `.ccu/artifacts/<yyyy-mm-dd>-quiz-<slug>/quiz.md`, one `##` section per group:
   - context: what problem this group solves in the project
   - intuition: how the solution works, in prose a stranger to the diff can follow
   - key decisions with exact `file:line` pointers
   - deviations and their reasons, if any

   End the file with a `## Quiz` section: 5–10 questions targeting exactly the risky and non-obvious parts identified in step 2. Number the questions; do not include answers in the file.

4. **Render and open**:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/markdown-html-viewer/scripts/md2html.py" .ccu/artifacts/<dir>/
   "${CLAUDE_PLUGIN_ROOT}/skills/markdown-html-viewer/scripts/open_in_dev_browser.sh" .ccu/artifacts/<dir>/index.html
   ```

5. **Grade in conversation** — Ask the user to answer in chat (all at once or question by question, their choice). For each answer report ✓/✗/partial with the correct answer explained against the exact code (`file:line`). Wrong or partial answers get a short follow-up explanation, not just the verdict. Finish with a per-question ✓/✗ list and the score.

6. **Verdict** — All correct: say the change set is understood and ready for the user's merge decision. Misses remaining: name the specific commits/files the user should re-read, and offer to re-quiz just those areas.

## Rules

- **Questions test understanding, not recall** — every question must be answerable only by someone who understood the change: "why does X hold the lock before Y", "what breaks if Z is reordered", "which caller depends on this new field". Never trivia ("what is the function called", "how many files changed").
- **Target the risk** — questions come from the riskiest and least obvious decisions found in step 2, not evenly from every commit. A mechanical rename earns no question.
- **Grade honestly** — a partial answer is partial, not correct. The gate only works if the score is real.
- **Never merge or push** — the verdict informs the user's merge decision; the merge itself is theirs.
- **Read the code, not the reports** — build questions from the actual diffs, not from bead comments or commit messages alone; those are point-in-time claims, not ground truth.
