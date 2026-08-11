# Development

## Quick start

```bash
git clone https://github.com/trungtnm/claude-code-utils.git
cd claude-code-utils
```

The shared package lives at `plugins/ccu`. There is no application build step
and no generated content — every file in the repo is edited directly.

## Claude Code development

Register this checkout as a local marketplace and install the plugin (once):

```bash
claude plugin marketplace add .
claude plugin install ccu@ccu
```

Installation copies the plugin into Claude Code's cache, and `claude plugin
update` skips re-copying while the version is unchanged. After editing plugin
content, refresh the cache and start a new session:

```bash
scripts/ccu-refresh.sh
```

For a one-off test without touching the installed copy, load the directory
directly — but note this loads alongside the installed `ccu@ccu`, so skills
appear twice; prefer the refresh flow when the plugin is installed:

```bash
claude --plugin-dir "$(pwd)/plugins/ccu"
```

Do not symlink individual skills/agents/commands into `~/.claude/` — links
break when files move, and they duplicate the installed plugin's content.

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

### Cross-host session workflows

Session workflows (`auto`, `capture`, `commit`, …) are ordinary skills. Create
`plugins/ccu/skills/<name>/SKILL.md` and add an `argument-hint` when the
workflow takes a scope:

```yaml
---
name: my-workflow
description: What this workflow does, with useful trigger phrases.
argument-hint: [optional scope]
---
```

Use `$ARGUMENTS` for the caller's scope. Claude invokes it as `/name`; Codex
invokes the same file as `$name`. There is no separate command file and nothing
to regenerate.

Helper scripts belong in `plugins/ccu/skills/<name>/scripts/`, resolved at run
time from `PLUGIN_ROOT` with `CLAUDE_PLUGIN_ROOT` as the fallback — see
`skills/init/SKILL.md` for the pattern.

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
python3 scripts/check-skills.py
python3 /path/to/plugin-creator/scripts/validate_plugin.py plugins/ccu
bash plugins/ccu/hooks/test-beads-guard.sh
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
```

`check-skills.py` asserts that every `skills/*/SKILL.md` has frontmatter whose
`name` matches its directory and a non-empty `description` — the invariant both
hosts rely on to resolve `/name` and `$name`.

Then test a representative knowledge skill and session workflow in a new session
of each host:

- Claude Code: `/brainstorming`, `/next`
- Codex: `$brainstorming`, `$next`
- Both hosts: inspect/trust the hook, start a session in a repo with `.beads/`,
  and confirm the guard is silent when `jsonl_newer` is false

## Commit conventions

Use conventional prefixes such as `feat:`, `fix:`, `docs:`, and `refactor:`.
When Beads is initialized, include the bead ID in the subject, for example
`feat: add capture screen [a02-1a2b]`.

## Claude Code teardown

```bash
claude plugin uninstall ccu@ccu
claude plugin marketplace remove ccu
```

If a legacy setup symlinked `~/.claude/skills`, `~/.claude/agents`, or
`~/.claude/commands` into this checkout, remove those links and recreate the
directories for personal content:

```bash
for d in skills agents commands; do
  [ -L "$HOME/.claude/$d" ] && rm "$HOME/.claude/$d" && mkdir "$HOME/.claude/$d"
done
```
