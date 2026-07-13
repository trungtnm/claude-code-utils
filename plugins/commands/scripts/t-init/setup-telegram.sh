#!/usr/bin/env bash
# setup-telegram.sh — configure Telegram notifications for Claude Code.
#
# Sends you a Telegram message whenever Claude Code needs you, tagged with the
# working directory:
#   • Notification event                      → permission prompt / idle waiting
#   • PreToolUse matcher AskUserQuestion       → the exact question + its options,
#                                                sent the moment Claude asks
#
# The AskUserQuestion payload carries `tool_input.questions[]`, so the message
# includes the real question text and every option label/description.
#
# The formatting + send logic lives in the sibling script `telegram-notify.sh`,
# which --apply installs to ~/.claude/ccu-telegram-notify.sh; the settings hooks
# just call that path (no inline one-liner in settings.json).
#
# Requires: jq, curl
#
# Scopes:
#   global   → ~/.claude/settings.json                 (every project)
#   project  → <git-root>/.claude/settings.local.json  (this project only,
#              gitignored so the bot token never gets committed)
#
# Credential resolution: --token / --chat-id are OPTIONAL for --apply and --test.
# When omitted, they are resolved in order: flags → environment
# ($TELEGRAM_BOT_TOKEN / $TELEGRAM_CHAT_ID) → the scope's settings.json .env block.
# So if the token/chat id already live in your env or settings, you never re-paste.
#
# Usage:
#   setup-telegram.sh --check [--scope global|project]
#       Print "configured" or "not-configured" for the given scope (default global).
#   setup-telegram.sh --detect-creds [--scope global|project]
#       Print "found\t<chat_id>\t…<last4>" if a token+chat id already exist in env
#       or the scope's settings, else "none". Use this to offer reuse before
#       walking the user through creating a new bot.
#   setup-telegram.sh --apply [--scope global|project] [--token <TOKEN>] [--chat-id <ID>]
#       Merge env vars + hooks into the scope's settings file (idempotent).
#   setup-telegram.sh --test [--token <TOKEN>] [--chat-id <ID>]
#       Send a one-off test message right now, print the Telegram API result.
#
# Every hook this script writes is tagged with the marker `ccu-telegram-notify`
# so re-applying replaces rather than duplicates it.

set -u

MODE=""
SCOPE="global"
TOKEN=""
CHATID=""

while [ $# -gt 0 ]; do
  case "$1" in
    --check)        MODE="check" ;;
    --detect-creds) MODE="detect-creds" ;;
    --apply)        MODE="apply" ;;
    --test)         MODE="test" ;;
    --scope)   SCOPE="${2:-}"; shift ;;
    --token)   TOKEN="${2:-}"; shift ;;
    --chat-id) CHATID="${2:-}"; shift ;;
    -h|--help) sed -n '2,42p' "$0"; exit 0 ;;
    *)         echo "Unknown flag: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ -z "$MODE" ]; then
  sed -n '2,42p' "$0"
  exit 0
fi

command -v jq   >/dev/null 2>&1 || { echo "error: jq not installed"   >&2; exit 3; }
command -v curl >/dev/null 2>&1 || { echo "error: curl not installed" >&2; exit 3; }

case "$SCOPE" in
  global|project) ;;
  *) echo "error: --scope must be 'global' or 'project'" >&2; exit 2 ;;
esac

# Resolve the settings file for the requested scope.
settings_file() {
  if [ "$SCOPE" = "global" ]; then
    echo "$HOME/.claude/settings.json"
  else
    local root
    root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
    echo "$root/.claude/settings.local.json"
  fi
}

# Fill TOKEN / CHATID from, in order: explicit flags → environment →
# the scope's settings.json .env → the global settings.json .env. Never
# overwrites a value already supplied by a flag.
resolve_creds() {
  [ -n "$TOKEN" ]  || TOKEN="${TELEGRAM_BOT_TOKEN:-}"
  [ -n "$CHATID" ] || CHATID="${TELEGRAM_CHAT_ID:-}"
  local f
  for f in "$(settings_file)" "$HOME/.claude/settings.json"; do
    [ -n "$TOKEN" ] && [ -n "$CHATID" ] && break
    [ -f "$f" ] || continue
    [ -n "$TOKEN" ]  || TOKEN="$(jq -r '.env.TELEGRAM_BOT_TOKEN // empty' "$f" 2>/dev/null)"
    [ -n "$CHATID" ] || CHATID="$(jq -r '.env.TELEGRAM_CHAT_ID // empty' "$f" 2>/dev/null)"
  done
}

MARKER="ccu-telegram-notify"

# The notifier that actually formats + sends the Telegram message lives in a
# separate script beside this one. On --apply it is copied to a stable path so
# the hook keeps working even if the plugin cache moves or is cleaned.
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
NOTIFIER_SRC="$SELF_DIR/telegram-notify.sh"
NOTIFIER_DEST="$HOME/.claude/ccu-telegram-notify.sh"
# The hook command is just the notifier path — its filename contains MARKER,
# which doubles as the idempotency tag. Same script serves both hooks; it
# auto-detects the payload (AskUserQuestion vs Notification).
HOOK_CMD="$NOTIFIER_DEST"

# --- detect-creds: report whether a token+chat id already exist ---
if [ "$MODE" = "detect-creds" ]; then
  resolve_creds
  if [ -n "$TOKEN" ] && [ -n "$CHATID" ]; then
    printf 'found\t%s\t…%s\n' "$CHATID" "${TOKEN: -4}"
  else
    echo "none"
  fi
  exit 0
fi

# --- test: fire a message immediately ---
if [ "$MODE" = "test" ]; then
  resolve_creds
  [ -n "$TOKEN" ] && [ -n "$CHATID" ] || { echo "error: no token/chat-id (pass --token/--chat-id or set them in env/settings)" >&2; exit 2; }
  resp="$(curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${CHATID}" \
    --data-urlencode "text=✅ Claude Code Telegram hook đã sẵn sàng! (📂 $(pwd))")"
  if echo "$resp" | jq -e '.ok == true' >/dev/null 2>&1; then
    echo "test: ok — message delivered"
    exit 0
  else
    echo "test: failed — $(echo "$resp" | jq -r '.description // .' 2>/dev/null)" >&2
    exit 1
  fi
fi

FILE="$(settings_file)"

# --- check: is the hook already present in this scope's settings? ---
if [ "$MODE" = "check" ]; then
  if [ -f "$FILE" ] && jq -e --arg m "$MARKER" '
      [.hooks // {} | to_entries[] | .value[]?.hooks[]?.command // ""]
      | any(index($m))
    ' "$FILE" >/dev/null 2>&1; then
    echo "configured	$FILE"
  else
    echo "not-configured	$FILE"
  fi
  exit 0
fi

# --- apply: merge env + hooks into the settings file ---
if [ "$MODE" = "apply" ]; then
  resolve_creds
  [ -n "$TOKEN" ] && [ -n "$CHATID" ] || { echo "error: no token/chat-id (pass --token/--chat-id or set them in env/settings)" >&2; exit 2; }

  # Install the notifier to a stable path the hook can always reach.
  [ -f "$NOTIFIER_SRC" ] || { echo "error: notifier not found at $NOTIFIER_SRC" >&2; exit 1; }
  mkdir -p "$(dirname "$NOTIFIER_DEST")"
  cp "$NOTIFIER_SRC" "$NOTIFIER_DEST" && chmod +x "$NOTIFIER_DEST"
  echo "installed: $NOTIFIER_DEST"

  mkdir -p "$(dirname "$FILE")"
  [ -f "$FILE" ] || echo '{}' > "$FILE"

  tmp="$(mktemp)"
  if jq \
      --arg token  "$TOKEN" \
      --arg chatid "$CHATID" \
      --arg cmd    "$HOOK_CMD" \
      --arg marker "$MARKER" '
    { hooks: [ { type: "command", command: $cmd, async: true } ] } as $ng
    | { matcher: "AskUserQuestion",
        hooks: [ { type: "command", command: $cmd, async: true } ] } as $ag
    | .env = ((.env // {}) + { TELEGRAM_BOT_TOKEN: $token, TELEGRAM_CHAT_ID: $chatid })
    | .hooks = (.hooks // {})
    # Remove OUR marked groups from EVERY event (also migrates away any old
    # PostToolUse hook), keeping all other hooks intact.
    | .hooks = (.hooks | with_entries(.value |= map(select(
        [(.hooks // [])[].command // ""] | any(index($marker)) | not
      ))))
    # Drop events left with no hooks.
    | .hooks = (.hooks | with_entries(select(.value | length > 0)))
    # Add fresh hooks: Notification (permission/idle) + PreToolUse:AskUserQuestion.
    | .hooks.Notification = ((.hooks.Notification // []) + [$ng])
    | .hooks.PreToolUse   = ((.hooks.PreToolUse   // []) + [$ag])
  ' "$FILE" > "$tmp"; then
    mv "$tmp" "$FILE"
    echo "configured: $FILE (Notification + PreToolUse:AskUserQuestion)"
  else
    rm -f "$tmp"
    echo "error: failed to update $FILE" >&2
    exit 1
  fi

  # For project scope, keep the secret out of git.
  if [ "$SCOPE" = "project" ]; then
    root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
    gi="$root/.gitignore"
    line=".claude/settings.local.json"
    if [ -f "$gi" ] && grep -Fxq "$line" "$gi"; then
      echo "already-present: .gitignore <- $line"
    else
      printf '%s\n' "$line" >> "$gi"
      echo "added: .gitignore <- $line"
    fi
  fi
  exit 0
fi
