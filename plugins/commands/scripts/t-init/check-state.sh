#!/usr/bin/env bash
# check-state.sh — detect project state for claude-code-utils plugins.
#
# Checks .ccu/, .gitignore entries, and .beads/.
# Resolves the project root via `git rev-parse --show-toplevel`, falling
# back to the current directory if the cwd is not a git repository.
#
# Usage:
#   check-state.sh             # human-readable table (default)
#   check-state.sh --tsv       # tab-separated KEY<TAB>VALUE pairs
#   check-state.sh --missing   # list missing keys only

set -u

FORMAT="human"
case "${1:-}" in
  --tsv) FORMAT="tsv" ;;
  --missing) FORMAT="missing" ;;
  --human|"") FORMAT="human" ;;
  -h|--help)
    sed -n '2,12p' "$0"
    exit 0
    ;;
  *)
    echo "Unknown flag: $1" >&2
    exit 2
    ;;
esac

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

bool() { [ "$1" = "1" ] && echo "true" || echo "false"; }

ccu_dir=0;       [ -d .ccu ]               && ccu_dir=1
captures_md=0;   [ -f .ccu/CAPTURES.md ]   && captures_md=1
beads_dir=0;     [ -d .beads ]             && beads_dir=1

gi_captures=0
if [ -f .gitignore ]; then
  grep -Fxq ".ccu/CAPTURES.md"     .gitignore && gi_captures=1
fi

emit() {
  local key="$1" value="$2" label="$3"
  case "$FORMAT" in
    tsv)
      printf "%s\t%s\n" "$key" "$value"
      ;;
    missing)
      [ "$value" = "false" ] && printf "%s\t%s\n" "$key" "$label"
      ;;
    human)
      if [ "$value" = "true" ]; then
        printf "%-32s %s\n" "$label" "✓ present"
      elif [ "$value" = "false" ]; then
        printf "%-32s %s\n" "$label" "✗ missing"
      else
        printf "%-32s %s\n" "$label" "$value"
      fi
      ;;
  esac
}

if [ "$FORMAT" = "human" ]; then
  echo "Project root: $ROOT"
  echo
fi

emit "ccu_dir"               "$(bool "$ccu_dir")"            ".ccu/"
emit "captures_md"           "$(bool "$captures_md")"        ".ccu/CAPTURES.md"
emit "gitignore_captures"    "$(bool "$gi_captures")"        ".gitignore: CAPTURES.md"
emit "beads_dir"             "$(bool "$beads_dir")"          ".beads/"

exit 0
