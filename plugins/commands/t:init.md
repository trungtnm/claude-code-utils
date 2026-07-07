Check and set up the prerequisite tools and project state required by claude-code-utils plugins. Detection is handled by deterministic shell scripts; this command runs them, presents results, and handles the interactive parts (asking the user, applying installs, summarizing).

## Steps

1. **Parse arguments** — Inspect `$ARGUMENTS` for these flags:
   - `--check` → read-only diagnostic; never mutate the filesystem and never install anything
   - `--all` → after a single up-front confirmation, run every safe install/bootstrap action
   - `--no-bootstrap` → skip `.ccu/` and beads init; only check binaries

   With no flags, run interactively: detect, report, ask before each mutation.

2. **Resolve script paths** — Detection logic lives in shell scripts shipped with this plugin. Set:

   ```bash
   SCRIPT_DIR="$HOME/.claude/commands/scripts/t-init"
   if [ ! -d "$SCRIPT_DIR" ]; then
     # Marketplace install fallback: search plugin caches.
     SCRIPT_DIR="$(find "$HOME/.claude/plugins" -type d -path '*/scripts/t-init' 2>/dev/null | head -1)"
   fi
   if [ ! -d "$SCRIPT_DIR" ]; then
     echo "Error: t-init scripts not found. Reinstall the ccu plugin." >&2
     exit 1
   fi
   ```

   Use `$SCRIPT_DIR/check-tools.sh`, `$SCRIPT_DIR/check-state.sh`, and `$SCRIPT_DIR/bootstrap.sh` from here on. Do not re-implement detection in your own bash blocks — the scripts are the source of truth.

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

5. **Check MCP server** — Only one MCP server is checked: `mcp-agent-mail`. It powers multi-agent coordination (used by `/t:auto` and `/orchestrator`); without it those commands fall back to solo mode. Look in the active session's MCP server reminders for `mcp-agent-mail` and record ✓ connected or ✗ not connected. Do not check, list, or report on any other MCP servers — they are out of scope for `/t:init`. MCP servers are configured per-user in Claude Code settings and cannot be installed from a slash command; if `mcp-agent-mail` is missing, the install hint is "configure in Claude Code settings (or accept solo mode)".

6. **Build remediation plan** — Group missing items into three buckets:

   - **Missing REQUIRED tools** (`git`, `jq`) — blocking. The remediation is to install them. On darwin, the install hint will be `brew install <tool>`. Print the install hints and stop after this step if any REQUIRED is missing — the user must install before bootstrap can proceed. Re-running `/t:init` will pick up where they left off.
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

9. **Final summary** — Re-run Step 3 and **display the full tables** so the user can see the per-item state of every tool and every project-state key. After both tables, print the MCP block from Step 5 — exactly one line: `mcp-agent-mail   ✓ connected` or `mcp-agent-mail   ✗ not connected`. Then print a single-line status and stop:

   - All REQUIRED present, no project-state misses → `Status: ✓ ready`
   - REQUIRED missing → `Status: ✗ blocked — install <tools> and re-run /t:init`
   - REQUIRED present but RECOMMENDED/OPTIONAL still missing → `Status: ✓ ready (N optional items skipped)` with a one-line list

   Never collapse the result into a single sentence like "all tools and state present" — the user wants to see each item's status explicitly. Show the tables every time, even on a fully-set-up project.

## Rules

- **Detection lives in the scripts, not in this command** — Never implement tool-presence checks or version parsing in inline bash here. If the scripts are wrong, fix the scripts. The whole point of this design is to keep detection deterministic.
- **Read-only under `--check`** — Steps 7 and 8 must never run when `--check` is in `$ARGUMENTS`. Print the report and stop.
- **Always confirm before mutation** — Every install or filesystem mutation requires explicit confirmation. `--all` collapses the per-action prompts into one up-front confirmation; otherwise prompt per action.
- **Never auto-install Rust tools** — `br`, `bv`, `cm`, `cass`, `ubs`, `dcg`, `gkg` have install hints that reference each tool's skill. Always defer; never run `cargo install` or similar from here.
- **Idempotent** — On a fully-set-up project, `/t:init` should produce a clean status report and zero prompts. The scripts already enforce idempotency in their bootstrap operations.
- **Don't probe MCP servers via tool calls** — Detection is from the session's MCP server reminders only. Never invoke MCP tools just to test connectivity; that has side effects.
- **Trust the scripts' exit codes** — `check-tools.sh` exits 1 if any REQUIRED tool is missing. Use that for the blocked/ready determination in Step 9.

## Arguments

- (no args): full check + interactive install/bootstrap, prompts per action
- `--check`: read-only diagnostic, no mutations, no installs
- `--all`: detect, then ask once and apply every safe install/bootstrap action
- `--no-bootstrap`: skip `.ccu/` and beads init; only check binaries and MCP servers

$ARGUMENTS
