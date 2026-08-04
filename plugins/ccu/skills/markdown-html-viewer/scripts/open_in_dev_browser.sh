#!/usr/bin/env bash
# Open an HTML file in a "dev browser" that can fetch sibling files over file:// — NO server.
#
# Why: a fetch-mode page (md2html.py default) loads its .md with fetch(), which a normal
# browser blocks over file://. Chrome started with --allow-file-access-from-files lifts that
# restriction. A dedicated --user-data-dir is REQUIRED: Chrome ignores the flag if it just
# attaches to your already-running default profile.
#
# Usage: open_in_dev_browser.sh <file.html>
set -euo pipefail

FILE="${1:?usage: open_in_dev_browser.sh <file.html>}"
[ -f "$FILE" ] || { echo "no such file: $FILE" >&2; exit 1; }
ABS="$(cd "$(dirname "$FILE")" && pwd)/$(basename "$FILE")"
PROFILE="${TMPDIR:-/tmp}/md-html-dev-browser"

# Find a Chromium-family browser (macOS paths first, then PATH).
CANDIDATES=(
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  "/Applications/Chromium.app/Contents/MacOS/Chromium"
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
  "google-chrome" "chromium" "chromium-browser" "microsoft-edge"
)
BROWSER=""
for c in "${CANDIDATES[@]}"; do
  if [ -x "$c" ] || command -v "$c" >/dev/null 2>&1; then BROWSER="$c"; break; fi
done
[ -n "$BROWSER" ] || { echo "No Chrome/Chromium/Edge found. Install one, or serve over HTTP instead." >&2; exit 1; }

echo "Opening $ABS"
echo "  browser: $BROWSER"
echo "  profile: $PROFILE  (separate dev profile; --allow-file-access-from-files)"
"$BROWSER" --allow-file-access-from-files --user-data-dir="$PROFILE" "file://$ABS" >/dev/null 2>&1 &
