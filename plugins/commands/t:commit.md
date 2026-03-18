Commit all changed files now in a series of logically connected groupings with detailed commit messages, then push. Do NOT edit any code — this is a commit-only operation. Use extended thinking.

## Rules

- **Read-only first** — Examine all changes (staged, unstaged, untracked) before making any commits. Understand the full picture.
- **No code edits** — Do not modify, fix, or refactor any source files. If you spot a bug, note it but do not fix it.
- **Skip ephemeral files** — Do not commit obviously ephemeral files (`.DS_Store`, `*.log`, `node_modules/`, `__pycache__/`, `.env`, editor swap files, etc.). If unsure whether a file is ephemeral, err on the side of skipping it.
- **Logical groupings** — Group related changes into separate commits. One commit per logical unit of work (e.g., a new feature, a refactor, a docs update). Do not lump unrelated changes into a single commit.
- **Detailed messages** — Each commit message should explain *what* changed and *why*. Use a short summary line (≤72 chars), then a blank line, then a detailed body. Use conventional commit prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`, `style:`).
- **Correct ordering** — Commit foundational changes before dependent ones (e.g., a new utility before the feature that uses it).
- **Push at the end** — After all commits are made, push to the remote.

## Steps

1. **Survey changes** — Run `git status` and `git diff` to understand all staged, unstaged, and untracked changes. Read changed files if needed to understand context.

2. **Plan commit groups** — Organize changes into logical groups. List them in commit order with a draft message for each. Consider:
   - Are there independent docs changes that should be separate from code changes?
   - Are there new files that form a cohesive unit?
   - Are there refactors mixed in with feature work that should be split?

3. **Execute commits** — For each group, stage only the relevant files and commit with a detailed message. Never use `git add -A` or `git add .` — always add specific files by name.

4. **Push** — Push all commits to the remote.

5. **Verify** — Run `git status` and `git log --oneline -10` to confirm everything is clean and pushed.
