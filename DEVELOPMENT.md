# Development

## Quick start

```bash
git clone https://github.com/trungtnm/claude-code-utils.git
cd claude-code-utils
```

The shared package lives at `plugins/ccu`. There is no application build step;
the only generated files are the Codex adapters for Claude's `t:` commands.

## Claude Code development

Link each plugin component into Claude Code:

```bash
for type in skills agents commands; do
  dest="$HOME/.claude/$type"; mkdir -p "$dest"
  for item in "$(pwd)/plugins/ccu/$type"/*; do
    [ -e "$item" ] || continue
    name=$(basename "$item")
    [ -e "$dest/$name" ] && [ ! -L "$dest/$name" ] && continue
    ln -sfn "$item" "$dest/$name"
  done
done
```

Restart Claude Code after changing plugin content. To test the marketplace
package instead of symlinks, use a separate Claude Code session:

```bash
/plugin marketplace add trungtnm/claude-code-utils
/plugin install ccu
```

## Codex development

Install the repository as a local marketplace, then install `ccu`:

```bash
codex plugin marketplace add .
codex plugin add ccu@ccu
```

After changing the plugin, refresh the marketplace and reinstall it:

```bash
codex plugin marketplace upgrade ccu
codex plugin add ccu@ccu
```

Start a new Codex conversation to pick up changed skills. The repo marketplace
is defined in `.agents/plugins/marketplace.json`; its entry points at
`plugins/ccu`.

Codex discovers `plugins/ccu/hooks/hooks.json` with the plugin. Open `/hooks`
in a new conversation to review and trust the local hook after reinstalling.

## Adding content

### Shared skills

Create `plugins/ccu/skills/<name>/SKILL.md` with YAML frontmatter:

```yaml
---
name: my-skill
description: One-line summary with useful trigger phrases.
---

# Skill title

Workflow, rules, references, and examples.
```

Keep shared skills product-neutral where possible. When a workflow needs
host-specific tools, describe the intent and provide both mappings. Codex
compatibility rules live in `plugins/ccu/CODEX.md`.

Skills may include `references/`, `resources/`, `examples/`, `templates/`, and
`scripts/` directories beside `SKILL.md`.

### Claude Code agents

Create `plugins/ccu/agents/<name>.md` with YAML frontmatter and a complete role
definition. Claude Code installs these as native subagent types. Codex can use
the files as persona resources when a shared workflow delegates to a generic
subagent, but does not install them as named agent types.

### Cross-host command workflows

Create `plugins/ccu/commands/t:<name>.md` with at least a description:

```yaml
---
description: What this workflow does
argument-hint: [optional scope]
---
```

Use `$ARGUMENTS` for the caller's scope. Claude invokes the command as
`/t:name`; Codex invokes its generated adapter as `$t-name`.

After adding, renaming, or changing a command description, regenerate and check
the adapters:

```bash
python3 scripts/sync-command-skills.py
python3 scripts/sync-command-skills.py --check
```

Do not edit generated `plugins/ccu/skills/t-*/SKILL.md` files directly.

### Shared hooks

Codex and Claude Code both discover the default plugin hook at
`plugins/ccu/hooks/hooks.json`. Keep hook commands host-neutral: prefer
`PLUGIN_ROOT`, with `CLAUDE_PLUGIN_ROOT` only as the compatibility fallback.
Hooks must be safe to inspect before trust, read-only unless their contract says
otherwise, silent on the happy path, and non-blocking on missing tools.

Run the beads guard fixture test after changing either hook file:

```bash
bash plugins/ccu/hooks/test-beads-guard.sh
```

## Verification

Before committing plugin changes:

```bash
python3 scripts/sync-command-skills.py --check
python3 /path/to/plugin-creator/scripts/validate_plugin.py plugins/ccu
bash plugins/ccu/hooks/test-beads-guard.sh
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
```

Then test a representative shared skill and command workflow in a new session
of each host:

- Claude Code: `/brainstorming`, `/t:next`
- Codex: `$brainstorming`, `$t-next`
- Both hosts: inspect/trust the hook, start a session in a repo with `.beads/`,
  and confirm the guard is silent when `jsonl_newer` is false

## Commit conventions

Use conventional prefixes such as `feat:`, `fix:`, `docs:`, and `refactor:`.
When Beads is initialized, include the bead ID in the subject, for example
`feat: add capture screen [a02-1a2b]`.

## Claude Code symlink teardown

Remove only links that point into this checkout, leaving personal content
intact:

```bash
for type in skills agents commands; do
  src="$(pwd)/plugins/ccu/$type"; dest="$HOME/.claude/$type"
  for item in "$src"/*; do
    [ -e "$item" ] || continue
    name=$(basename "$item"); link="$dest/$name"
    [ -L "$link" ] && rm "$link" && echo "Unlinked $type/$name"
  done
done
```
