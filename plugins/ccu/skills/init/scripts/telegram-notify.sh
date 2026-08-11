#!/usr/bin/env bash
# telegram-notify.sh — Claude Code hook notifier.
#
# Reads the AskUserQuestion hook payload on stdin and sends a Telegram message.
# Wired up by setup-telegram.sh, which installs a copy at
# ~/.claude/ccu-telegram-notify.sh and points the PreToolUse:AskUserQuestion
# hook at it. Keeping the logic in a real script (instead of an inline
# settings.json one-liner) makes it readable and testable.
#
# Formats `.tool_input.questions[]` → the question text + every option
# (label — description), tagged with the working directory.
#
# Credentials: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID from the environment (set in
# settings.json .env), falling back to ~/.claude/settings.json .env. Missing jq,
# curl, or creds → exit 0 silently (a hook must never break the session).

set -u

command -v jq   >/dev/null 2>&1 || exit 0
command -v curl >/dev/null 2>&1 || exit 0

IN="$(cat)"

TOKEN="${TELEGRAM_BOT_TOKEN:-}"
CHATID="${TELEGRAM_CHAT_ID:-}"
if [ -z "$TOKEN" ] || [ -z "$CHATID" ]; then
  gs="$HOME/.claude/settings.json"
  if [ -f "$gs" ]; then
    [ -n "$TOKEN" ]  || TOKEN="$(jq -r '.env.TELEGRAM_BOT_TOKEN // empty' "$gs" 2>/dev/null)"
    [ -n "$CHATID" ] || CHATID="$(jq -r '.env.TELEGRAM_CHAT_ID // empty' "$gs" 2>/dev/null)"
  fi
fi
[ -n "$TOKEN" ] && [ -n "$CHATID" ] || exit 0

TEXT="$(printf '%s' "$IN" | jq -r '
  "🔔 Claude Code hỏi bạn\n📂 \(.cwd // "?")\n\n"
  + ( (.tool_input.questions // [])
      | map("❓ " + (.question // .header // "?") + "\n"
            + ( (.options // [])
                | to_entries
                | map("  \(.key+1). \(.value.label // "")"
                      + (if (.value.description // "") != "" then " — \(.value.description)" else "" end))
                | join("\n") ) )
      | join("\n\n") )
' 2>/dev/null)"

[ -n "$TEXT" ] || exit 0

curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${CHATID}" \
  --data-urlencode "text=${TEXT}" >/dev/null 2>&1 || true

exit 0
