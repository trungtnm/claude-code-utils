#!/usr/bin/env bash

set -eu

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
guard="$script_dir/beads-guard.sh"
fixture_root="$(mktemp -d)"
trap 'rm -rf "$fixture_root"' EXIT

mkdir -p "$fixture_root/bin" "$fixture_root/repo/.beads"

cat > "$fixture_root/bin/git" <<'EOF'
#!/usr/bin/env bash
if [ "${1:-}" = "rev-parse" ] && [ "${2:-}" = "--show-toplevel" ]; then
  printf '%s\n' "$CCU_TEST_REPO"
  exit 0
fi
exit 1
EOF

cat > "$fixture_root/bin/br" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$CCU_TEST_STATUS"
EOF

chmod +x "$fixture_root/bin/git" "$fixture_root/bin/br"

run_guard() {
  PATH="$fixture_root/bin:/usr/bin:/bin" \
    CCU_TEST_REPO="$fixture_root/repo" \
    CCU_TEST_STATUS="$1" \
    bash "$guard"
}

quiet_output="$(run_guard '{"jsonl_newer":false,"dirty_count":0}')"
[ -z "$quiet_output" ] || {
  printf 'expected no output without drift, got:\n%s\n' "$quiet_output" >&2
  exit 1
}

clean_drift="$(run_guard '{"jsonl_newer":true,"dirty_count":0}')"
printf '%s' "$clean_drift" | grep -Fq 'beads drift'
printf '%s' "$clean_drift" | grep -Fq 'br sync --import-only'

dirty_drift="$(run_guard '{"jsonl_newer":true,"dirty_count":3}')"
printf '%s' "$dirty_drift" | grep -Fq '3 unflushed local change(s)'
printf '%s' "$dirty_drift" | grep -Fq 'br sync --merge'

printf 'beads-guard fixtures passed\n'
