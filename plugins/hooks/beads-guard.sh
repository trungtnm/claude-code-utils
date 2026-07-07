#!/usr/bin/env bash
# beads-guard.sh — SessionStart drift warner for git-tracked beads.
#
# Why this exists:
#   beads keeps a SQLite DB (.beads/beads.db, local-only) and a JSONL file
#   (.beads/issues.jsonl, the git-tracked source of truth). `br` decides which
#   is fresher by FILE MTIME. A `git checkout` / `git pull` / branch-switch
#   rewrites issues.jsonl and stamps its mtime to "now" — even when the content
#   git restored is logically OLDER. On the next `br` command, br's auto-import
#   sees "JSONL newer" and imports that stale file, silently reverting the DB.
#
#   This hook runs at SessionStart, BEFORE any beads command, and warns when
#   the on-disk JSONL is ahead of the local DB so the agent/user can reconcile
#   deliberately instead of letting auto-import clobber local state.
#
# Design constraints:
#   - Read-only: passes --no-auto-import --no-auto-flush so the *check itself*
#     never triggers the very import it's warning about.
#   - Silent on the happy path: SessionStart stdout is injected into context, so
#     it emits NOTHING unless real drift is detected.
#   - Never blocks: always exits 0, even on error or missing tools.
#   - Zero hard deps beyond `br` + POSIX tools (no jq required).

set -u

# Resolve the repo root (SessionStart CWD is the project dir; fall back to it).
repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || repo_root="$PWD"

# Nothing to guard if beads isn't present or installed.
[ -d "$repo_root/.beads" ] || exit 0
command -v br >/dev/null 2>&1 || exit 0

# Observational status only — suppress auto-import/auto-flush side effects.
status_json="$(
  cd "$repo_root" 2>/dev/null \
    && br --no-auto-import --no-auto-flush sync --status --json 2>/dev/null
)" || exit 0

# Drift fingerprint: the on-disk JSONL is mtime-ahead of the local DB.
printf '%s' "$status_json" \
  | grep -Eq '"jsonl_newer"[[:space:]]*:[[:space:]]*true' || exit 0

# Extract dirty_count (unflushed local DB changes) for a sharper message.
dirty="$(printf '%s' "$status_json" \
  | sed -n 's/.*"dirty_count"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p')"
dirty="${dirty:-0}"

echo "⚠️  beads drift: .beads/issues.jsonl on disk is AHEAD of your local DB."
echo "   A git checkout/pull/branch-switch or another session changed the JSONL."
echo "   Note: 'newer' is by file mtime — a checkout that restored OLDER content"
echo "   still trips this. Running a beads command now may auto-import it and"
echo "   overwrite local issues."
if [ "$dirty" -gt 0 ] 2>/dev/null; then
  echo "   You ALSO have $dirty unflushed local change(s) — both sides diverged."
  echo "   Reconcile (do NOT blind-import):"
  echo "     br sync --status -v     # inspect what differs"
  echo "     br sync --merge         # 3-way merge DB + JSONL (safest)"
else
  echo "   Reconcile before working:"
  echo "     br sync --status -v     # inspect what differs"
  echo "     br sync --import-only   # accept the JSONL as authoritative, OR"
  echo "     br sync --merge         # 3-way merge if unsure"
fi
echo "   Local DB backups: .beads/.br_history/"

exit 0
