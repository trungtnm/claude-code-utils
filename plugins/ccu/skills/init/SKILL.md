---
name: init
description: Check and set up prerequisite tools and project state for claude-code-utils plugins
---

Check and set up the prerequisite tools and project state required by claude-code-utils plugins, plus optional Telegram notifications when Claude needs you. Detection is handled by deterministic shell scripts; this workflow runs them, presents results, and handles the interactive parts (asking the user, applying installs, summarizing).

## Steps

1. **Parse arguments** — Inspect `$ARGUMENTS` for these flags:
   - `--check` → read-only diagnostic; never mutate the filesystem and never install anything
   - `--all` → after a single up-front confirmation, run every safe install/bootstrap action
   - `--no-bootstrap` → skip `.ccu/` and beads init; only check binaries

   With no flags, run interactively: detect, report, ask before each mutation.

2. **Resolve script paths** — Detection logic lives in shell scripts shipped with this plugin. Set:

   ```bash
   SCRIPT_DIR="${PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-}}/skills/init/scripts"
   if [ ! -d "$SCRIPT_DIR" ]; then
     # Marketplace install fallback: search the host plugin caches.
     SCRIPT_DIR="$(find "$HOME/.claude/plugins" "$HOME/.agents" -type d -path '*/skills/init/scripts' 2>/dev/null | head -1)"
   fi
   if [ ! -d "$SCRIPT_DIR" ]; then
     echo "Error: init scripts not found. Reinstall the ccu plugin." >&2
     exit 1
   fi
   ```

   Use `$SCRIPT_DIR/check-tools.sh`, `$SCRIPT_DIR/check-state.sh`, `$SCRIPT_DIR/bootstrap.sh`, and `$SCRIPT_DIR/setup-telegram.sh` from here on. Do not re-implement detection in your own bash blocks — the scripts are the source of truth.

3. **Run detection** — In a single Bash call, run both checkers in human format and capture the output:

   ```bash
   echo "=== TOOLS ==="
   "$SCRIPT_DIR/check-tools.sh"
   echo
   echo "=== PROJECT STATE ==="
   "$SCRIPT_DIR/check-state.sh"
   ```

   Display this output to the user verbatim — it's already formatted as a scannable table with ✓/✗ markers and platform info.

4. **Capture structured missing list** — Run the same checkers in `--missing` mode to get a machine-parseable list of what's not installed or not present. Use this to drive the remediation step, not your own visual inspection of the human table:

   ```bash
   "$SCRIPT_DIR/check-tools.sh" --missing  # tab-separated: name<TAB>category<TAB>install_hint
   "$SCRIPT_DIR/check-state.sh" --missing  # tab-separated: key<TAB>label
   ```

   If both produce empty output, the project is fully set up — skip to Step 9 (final summary) and report "all set".

5. **Check MCP server** — Only one MCP server is checked: `mcp-agent-mail`. It powers multi-agent coordination (used by `/auto` and `/orchestrator`); without it those commands fall back to solo mode. Look in the active session's MCP server reminders for `mcp-agent-mail` and record ✓ connected or ✗ not connected. Do not check, list, or report on any other MCP servers — they are out of scope for `/init`. MCP servers are configured per-user in Claude Code settings and cannot be installed from a slash command; if `mcp-agent-mail` is missing, the install hint is "configure in Claude Code settings (or accept solo mode)".

6. **Build remediation plan** — Group missing items into three buckets:

   - **Missing REQUIRED tools** (`git`, `jq`) — blocking. The remediation is to install them. On darwin, the install hint will be `brew install <tool>`. Print the install hints and stop after this step if any REQUIRED is missing — the user must install before bootstrap can proceed. Re-running `/init` will pick up where they left off.
   - **Missing RECOMMENDED/OPTIONAL tools** — non-blocking. Print install hints. For tools whose hints reference a skill (e.g., "see /br skill for install"), do not auto-install — those have project-specific install procedures. For `gh`/`curl`, offer `brew install`.
   - **Missing project state** (`.ccu/`, `.gitignore` lines, `.beads/`) — handled by `bootstrap.sh`. Print the bootstrap command that will be run.

7. **Confirm with user** — If `--check` was passed, stop here. If `--all` was passed, ask once: "Apply all listed changes? [y/N]". Otherwise, ask per-action:
   - "Install missing brew packages? (jq/gh/curl as applicable) [Y/n]"
   - "Initialize project state (.ccu/, .gitignore, beads)? [Y/n]"

   On any "n" or empty input where the default is N, skip that action.

8. **Apply** — Skip this step entirely under `--check`.

   a. **brew installs** — For each confirmed darwin install, run `brew install <tool>` directly. On linux, do NOT run package-manager commands (sudo isn't guaranteed); print the suggested `apt-get install <tool>` command and ask the user to run it themselves. Never auto-install Rust tools (`br`, `bv`, `cm`, `cass`, `ubs`, `dcg`, `gkg`) — defer to each tool's own skill.

   b. **Project-state bootstrap** — Run the script with the confirmed flags. Pick the flag set based on what was missing in Step 4 plus what the user confirmed in Step 7:

   ```bash
   # Examples — use only the flags that match what's needed and confirmed
   "$SCRIPT_DIR/bootstrap.sh" --all                         # .ccu/ + .gitignore + beads
   "$SCRIPT_DIR/bootstrap.sh" --ccu --gitignore             # if br missing
   ```

   Skip this whole sub-step if `--no-bootstrap` was passed.

   The script is idempotent — passing `--ccu` when `.ccu/` already exists prints `already-exists: .ccu/` and moves on. Display the script's output to the user.

9. **Offer Telegram notifications** — Skip this step entirely if `--check` or `--no-telegram` is in `$ARGUMENTS`. This is optional and never blocking. It sets up a single hook that messages you on Telegram **the moment Claude asks you something via `AskUserQuestion`**, tagged with the working directory (`.cwd`):
   - **`PreToolUse` matcher `AskUserQuestion`** — sends the **exact question and every option** (label — description), pulled from `tool_input.questions[]`, at ask-time (before you answer), so you can read what's being asked remotely. (`Elicitation` is not used — it does not fire for `AskUserQuestion`; `PostToolUse` would arrive only after you already answered; the `Notification` event — permission prompts / idle waiting — is intentionally **not** wired up.)

   a. **Detect existing config** — Run the checker for both scopes and read the first tab-separated field:

      ```bash
      "$SCRIPT_DIR/setup-telegram.sh" --check --scope global
      "$SCRIPT_DIR/setup-telegram.sh" --check --scope project
      ```

      If either prints `configured`, tell the user Telegram notifications are already set for that scope and do not re-prompt unless they explicitly ask to reconfigure.

   b. **Ask whether to enable** — If neither scope is configured, ask: `Bật thông báo Telegram mỗi khi Claude cần bạn? [y/N]`. On `n` or empty, skip the rest of this step.

   c. **Choose scope** — Ask: `Global (mọi project) hay chỉ project này? [global/project]`. `global` writes `~/.claude/settings.json`; `project` writes `.claude/settings.local.json` (which the script also adds to `.gitignore` so the bot token is never committed).

   d. **Check for existing credentials first, offer reuse** — Before showing any create-a-bot guide, detect whether a token + chat id already exist (in the session env `$TELEGRAM_BOT_TOKEN`/`$TELEGRAM_CHAT_ID` or a settings `.env` block):

      ```bash
      "$SCRIPT_DIR/setup-telegram.sh" --detect-creds --scope <scope>
      ```

      - If it prints `found\t<chat_id>\t…<last4>`, **do not walk the user through creating a bot**. Ask them to confirm reuse: `Đã có token (…<last4>) + chat_id <chat_id> trong env/settings. Dùng lại? [Y/n]`. On yes/empty, skip straight to step e and reuse them (no re-paste).
      - Only if it prints `none`, or the user declines reuse, show the create-a-bot guide and wait for the user to paste both values — never invent or guess them:
        - **`TELEGRAM_BOT_TOKEN`** — In Telegram, chat with **@BotFather** → send `/newbot` → pick a name and username → copy the token it returns (form `123456789:AAH...`).
        - **`TELEGRAM_CHAT_ID`** — Send your new bot any message, then run `curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates" | jq '.result[].message.chat.id'` and copy the numeric id it prints.

   e. **Apply and test** — Run apply then test. When **reusing** existing creds, omit `--token/--chat-id` — the script resolves them from env/settings. When the user **pasted new** ones, pass them explicitly:

      ```bash
      # reusing existing env/settings creds:
      "$SCRIPT_DIR/setup-telegram.sh" --apply --scope <scope>
      "$SCRIPT_DIR/setup-telegram.sh" --test

      # or with freshly pasted creds:
      "$SCRIPT_DIR/setup-telegram.sh" --apply --scope <scope> --token "<TOKEN>" --chat-id "<CHAT_ID>"
      "$SCRIPT_DIR/setup-telegram.sh" --test  --token "<TOKEN>" --chat-id "<CHAT_ID>"
      ```

      Display both outputs. If `--test` prints `test: ok`, the credentials work. Tell the user the hook is live, and that Claude Code may need `/hooks` opened once (or a restart) for the new settings file to be picked up this session. If `--test` fails, show the error (usually a wrong token or chat id) and let them re-enter.

10. **Final summary** — Re-run Step 3 and **display the full tables** so the user can see the per-item state of every tool and every project-state key. After both tables, print the MCP block from Step 5 — exactly one line: `mcp-agent-mail   ✓ connected` or `mcp-agent-mail   ✗ not connected`. Then print one line for Telegram notifications using `setup-telegram.sh --check` for whichever scope is active: `telegram-notify   ✓ configured (global)`, `✓ configured (project)`, or `✗ not configured`. Then print a single-line status and stop:

   - All REQUIRED present, no project-state misses → `Status: ✓ ready`
   - REQUIRED missing → `Status: ✗ blocked — install <tools> and re-run /init`
   - REQUIRED present but RECOMMENDED/OPTIONAL still missing → `Status: ✓ ready (N optional items skipped)` with a one-line list

   Never collapse the result into a single sentence like "all tools and state present" — the user wants to see each item's status explicitly. Show the tables every time, even on a fully-set-up project.

## Rules

- **Detection lives in the scripts, not in this workflow** — Never implement tool-presence checks or version parsing in inline bash here. If the scripts are wrong, fix the scripts. The whole point of this design is to keep detection deterministic.
- **Read-only under `--check`** — Steps 7, 8, and 9 must never run when `--check` is in `$ARGUMENTS`. Print the report (including the `setup-telegram.sh --check` status line) and stop; never prompt for a token or mutate any settings file.
- **Telegram is opt-in; check env before asking for a token** — Step 9 must run `setup-telegram.sh --detect-creds` first. If a token + chat id already exist in env or settings, offer to reuse them (confirm, then apply/test without re-pasting) — never make the user create a new bot when creds already exist. Only prompt for a fresh token when none are found or the user declines reuse. `--all` does not silently enable Telegram; still ask in Step 9. `--no-telegram` skips the offer entirely. Never write a placeholder or guessed token.
- **Always confirm before mutation** — Every install or filesystem mutation requires explicit confirmation. `--all` collapses the per-action prompts into one up-front confirmation; otherwise prompt per action.
- **Never auto-install Rust tools** — `br`, `bv`, `cm`, `cass`, `ubs`, `dcg`, `gkg` have install hints that reference each tool's skill. Always defer; never run `cargo install` or similar from here.
- **Idempotent** — On a fully-set-up project, `/init` should produce a clean status report and zero prompts. The scripts already enforce idempotency in their bootstrap operations.
- **Don't probe MCP servers via tool calls** — Detection is from the session's MCP server reminders only. Never invoke MCP tools just to test connectivity; that has side effects.
- **Trust the scripts' exit codes** — `check-tools.sh` exits 1 if any REQUIRED tool is missing. Use that for the blocked/ready determination in Step 9.

## Arguments

- (no args): full check + interactive install/bootstrap + Telegram offer, prompts per action
- `--check`: read-only diagnostic, no mutations, no installs, no Telegram prompt
- `--all`: detect, then ask once and apply every safe install/bootstrap action (Telegram still asked interactively — it needs a token)
- `--no-bootstrap`: skip `.ccu/` and beads init; only check binaries and MCP servers
- `--no-telegram`: skip the Telegram notification offer in Step 9

$ARGUMENTS
