#!/usr/bin/env bash
# bootstrap.sh — apply project-state setup for claude-code-utils plugins.
#
# Idempotent: every action checks current state before mutating, so running
# this twice on a configured project is a no-op. Each action prints one of:
#   created: <path>
#   already-exists: <path>
#   added: <file> <- <line>
#   already-present: <file> <- <line>
#   skipped: <reason>
#
# Usage:
#   bootstrap.sh [--ccu] [--gitignore] [--beads] [--all]
#
# Flags pick which actions to run. With no flags, prints help and exits.
#   --ccu        create .ccu/ and .ccu/CAPTURES.md
#   --gitignore  ensure .gitignore has the .ccu/* exclusion lines
#   --beads      run `br init` to create .beads/ (no-op if already initialized)
#   --all        equivalent to --ccu --gitignore --beads

set -u

DO_CCU=0
DO_GITIGNORE=0
DO_BEADS=0

if [ $# -eq 0 ]; then
  sed -n '2,19p' "$0"
  exit 0
fi

while [ $# -gt 0 ]; do
  case "$1" in
    --ccu)       DO_CCU=1 ;;
    --gitignore) DO_GITIGNORE=1 ;;
    --beads)     DO_BEADS=1 ;;
    --all)       DO_CCU=1; DO_GITIGNORE=1; DO_BEADS=1 ;;
    -h|--help)   sed -n '2,19p' "$0"; exit 0 ;;
    *)           echo "Unknown flag: $1" >&2; exit 2 ;;
  esac
  shift
done

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

# --- .ccu/ + CAPTURES.md ---
if [ "$DO_CCU" = "1" ]; then
  if [ -d .ccu ]; then
    echo "already-exists: .ccu/"
  else
    mkdir -p .ccu
    echo "created: .ccu/"
  fi
  if [ -f .ccu/CAPTURES.md ]; then
    echo "already-exists: .ccu/CAPTURES.md"
  else
    : > .ccu/CAPTURES.md
    echo "created: .ccu/CAPTURES.md"
  fi
fi

# --- .gitignore entries ---
if [ "$DO_GITIGNORE" = "1" ]; then
  [ -f .gitignore ] || { : > .gitignore; echo "created: .gitignore"; }
  for line in ".ccu/CAPTURES.md" ".ccu/artifacts/" ".ccu/brainstorm/"; do
    if grep -Fxq "$line" .gitignore; then
      echo "already-present: .gitignore <- $line"
    else
      printf '%s\n' "$line" >> .gitignore
      echo "added: .gitignore <- $line"
    fi
  done
fi

# --- beads init ---
if [ "$DO_BEADS" = "1" ]; then
  if [ -d .beads ]; then
    echo "already-exists: .beads/"
  elif ! command -v br >/dev/null 2>&1; then
    echo "skipped: br not installed (see /br skill)"
  else
    if br init >/dev/null 2>&1; then
      echo "created: .beads/ (via br init)"
    else
      echo "skipped: br init failed (run manually to see error)" >&2
    fi
  fi
fi

exit 0
