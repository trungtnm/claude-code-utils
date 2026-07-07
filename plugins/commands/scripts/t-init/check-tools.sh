#!/usr/bin/env bash
# check-tools.sh — detect prerequisite CLI tools for claude-code-utils plugins.
#
# Usage:
#   check-tools.sh             # human-readable table (default)
#   check-tools.sh --tsv       # tab-separated values for parsing
#   check-tools.sh --missing   # list missing tool names only, one per line
#
# Exit codes:
#   0  all REQUIRED tools present
#   1  one or more REQUIRED tools missing

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

PLATFORM="$(uname -s | tr '[:upper:]' '[:lower:]')"

# Tool registry: name|category|purpose|hint_darwin|hint_linux
TOOLS=(
  "git|REQUIRED|Version control|brew install git|apt-get install git"
  "jq|REQUIRED|JSON parsing|brew install jq|apt-get install jq"
  "br|RECOMMENDED|Beads issue tracker|see /br skill for install|see /br skill for install"
  "bv|RECOMMENDED|Beads graph triage|see /bv skill for install|see /bv skill for install"
  "gh|RECOMMENDED|GitHub CLI|brew install gh|see https://cli.github.com"
  "curl|RECOMMENDED|HTTP fetches|brew install curl|apt-get install curl"
  "cm|OPTIONAL|CASS Memory|see /cm skill for install|see /cm skill for install"
  "cass|OPTIONAL|CASS session search|see /cass skill for install|see /cass skill for install"
  "ubs|OPTIONAL|Ultimate Bug Scanner|see /ubs skill for install|see /ubs skill for install"
  "dcg|OPTIONAL|Destructive Command Guard|see /dcg skill for install|see /dcg skill for install"
  "gkg|OPTIONAL|GitLab Knowledge Graph|see /gkg skill for install|see /gkg skill for install"
)

detect_version() {
  # Try --version, then -V; combine stderr because some tools print to stderr.
  # Look for a version-like pattern (N.N) in the first 5 lines only — beyond
  # that we are reading help text, which often contains float ranges like
  # "(0.0-1.0)" that look like versions but aren't. If no match, fall back
  # to the first non-empty line of --version output.
  local name="$1" raw_v raw_v2 v
  raw_v="$("$name" --version 2>&1 </dev/null || true)"
  v="$(printf '%s\n' "$raw_v" | head -5 | grep -m1 -E '[0-9]+\.[0-9]+' 2>/dev/null \
       | sed 's/[[:cntrl:]]//g' | sed 's/[[:space:]]\+/ /g' \
       | sed 's/^ //; s/ $//')"
  if [ -z "$v" ]; then
    raw_v2="$("$name" -V 2>&1 </dev/null || true)"
    v="$(printf '%s\n' "$raw_v2" | head -5 | grep -m1 -E '[0-9]+\.[0-9]+' 2>/dev/null \
         | sed 's/[[:cntrl:]]//g' | sed 's/[[:space:]]\+/ /g' \
         | sed 's/^ //; s/ $//')"
  fi
  if [ -z "$v" ]; then
    v="$(printf '%s\n' "$raw_v" | sed '/^[[:space:]]*$/d' | head -1 \
         | sed 's/[[:cntrl:]]//g' | sed 's/[[:space:]]\+/ /g' \
         | sed 's/^ //; s/ $//')"
  fi
  [ -z "$v" ] && v="installed"
  printf '%s' "$v"
}

required_missing=0

if [ "$FORMAT" = "human" ]; then
  printf "%-7s %-13s %-12s %-32s %s\n" "TOOL" "CATEGORY" "STATUS" "VERSION" "PURPOSE"
  printf -- "─%.0s" {1..90}; echo
fi

for entry in "${TOOLS[@]}"; do
  IFS="|" read -r name category purpose hint_d hint_l <<< "$entry"
  case "$PLATFORM" in
    darwin) hint="$hint_d" ;;
    *)      hint="$hint_l" ;;
  esac

  if command -v "$name" >/dev/null 2>&1; then
    installed="true"
    version="$(detect_version "$name")"
  else
    installed="false"
    version=""
    [ "$category" = "REQUIRED" ] && required_missing=1
  fi

  case "$FORMAT" in
    tsv)
      printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$name" "$category" "$installed" "$version" "$purpose" "$hint"
      ;;
    missing)
      [ "$installed" = "false" ] && printf "%s\t%s\t%s\n" "$name" "$category" "$hint"
      ;;
    human)
      if [ "$installed" = "true" ]; then
        status="✓ installed"
        ver_disp="$version"
        # truncate long version strings
        [ ${#ver_disp} -gt 30 ] && ver_disp="${ver_disp:0:27}..."
      else
        status="✗ missing"
        ver_disp="—"
      fi
      printf "%-7s %-13s %-12s %-32s %s\n" "$name" "$category" "$status" "$ver_disp" "$purpose"
      ;;
  esac
done

if [ "$FORMAT" = "human" ]; then
  echo
  echo "Platform: $PLATFORM"
  if [ "$required_missing" = "1" ]; then
    echo "Status: ✗ blocked — one or more REQUIRED tools missing"
  else
    echo "Status: ✓ required tools present"
  fi
fi

exit "$required_missing"
