# Codex compatibility

The `skills/` and default `hooks/hooks.json` components are shared directly by
Claude Code and Codex. Every workflow lives in `skills/<name>/SKILL.md` and both
hosts run the same file. The `agents/` directory is a native Claude Code
component, so Codex loads that Markdown as subagent personas when needed.

## Running a shared workflow

When a skill under `skills/` describes a multi-step workflow:

1. Read the whole `SKILL.md` before acting.
2. Treat the scope or details supplied with the user's invocation as
   `$ARGUMENTS` or `${ARGUMENTS}`. Never pass those placeholders literally.
3. Translate product-specific tool names by intent:
   - `AskUserQuestion` means the current Codex user-input mechanism when one is
     available, or a concise question to the user when input is required.
   - `Task(...)`, `TaskList`, `TaskOutput`, and `SendMessage` mean Codex's
     current collaboration/subagent tools when the workflow is explicitly
     authorized to use subagents.
   - `Skill(...)` means invoke or read the named installed skill.
   - Claude planning or effort commands mean use the closest current Codex
     planning or reasoning capability.
4. Read both `AGENTS.md` and `CLAUDE.md` when either is requested and present.
   `AGENTS.md` is Codex's native durable-instructions file.
5. Keep Claude-specific setup isolated. Do not write `~/.claude/` or assume
   Claude's clipboard cache while running in Codex unless the user explicitly
   asks to configure Claude Code too.
6. If a workflow has no safe Codex equivalent, explain the narrow limitation
   and continue with the closest supported behavior.

## Agent personas

Codex does not install the Markdown files under `agents/` as native subagent
types. When a shared workflow needs one of those roles, read the matching file
under `agents/` and include its role, constraints, and verification contract in
the task sent to a Codex subagent. Do this only when subagent work is explicitly
allowed by the user's request or the active skill instructions.

## Hooks and host-specific components

- Both hosts discover `hooks/hooks.json` at the plugin root. The beads guard
  uses `PLUGIN_ROOT` with `CLAUDE_PLUGIN_ROOT` as a compatibility fallback.
- Codex requires the user to inspect and trust plugin hooks (for example via
  `/hooks`) before they run. Never bypass that trust review.
- Claude invokes a skill as `/name` (or `/ccu:name` when disambiguating).
- Codex invokes the same skill as `$name` or by asking for the workflow in
  natural language.
- Workflow scripts ship beside their `SKILL.md` (for example
  `skills/init/scripts/`). Resolve them from `PLUGIN_ROOT`, falling back to
  `CLAUDE_PLUGIN_ROOT`, rather than hardcoding a host cache path.
