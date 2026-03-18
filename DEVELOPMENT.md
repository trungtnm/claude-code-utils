# Development

## Quick Start

```bash
# Clone and link into Claude Code
git clone https://github.com/trungtnm/claude-code-utils.git
cd claude-code-utils

# Link all plugin content (skills, agents, commands)
for type in skills agents commands; do
  dest="$HOME/.claude/$type"; mkdir -p "$dest"
  for item in "$(pwd)/plugins/$type"/*; do
    [ -e "$item" ] || continue
    name=$(basename "$item")
    [ -e "$dest/$name" ] && [ ! -L "$dest/$name" ] && continue
    ln -sfn "$item" "$dest/$name"
  done
done

# Restart Claude Code to load the new content
```

## How It Works

Claude Code discovers content from `~/.claude/skills/`, `~/.claude/agents/`, and `~/.claude/commands/`. The setup creates per-item symlinks (e.g., `~/.claude/skills/ubs → plugins/skills/ubs`) so plugin content coexists with your personal skills without conflicts.

**No build step.** Edits to files in `plugins/` take effect on the next Claude Code session start — just restart to pick up changes.

## Adding Content

### Skills

Create a new directory under `plugins/skills/<name>/` with a `SKILL.md` file. The file must begin with YAML frontmatter:

```yaml
---
name: my-skill                    # Required. Kebab-case, matches directory name.
description: "One-liner summary"  # Required. Include trigger keywords for discovery.
model: sonnet                     # Optional. Force a specific model (haiku, sonnet, opus).
domain: testing                   # Optional. Category (security, project-management, testing, etc.)
role: specialist                  # Optional. (specialist, guide, reviewer)
triggers:                         # Optional. Keywords that help Claude match this skill.
  - keyword1
  - keyword2
---

# Skill Title

Body content: rules, workflows, command reference, integration points, anti-patterns.
```

Skills can include supporting resource directories alongside `SKILL.md`:

| Directory | Purpose | Example |
|-----------|---------|---------|
| `resources/` | Templates, checklists, reference data | `architecture-checklist.md` |
| `references/` | Deep-dive topic files loaded on demand | `context-fundamentals.md` |
| `examples/` | Gold-standard output samples | `gold-standard-card.tsx` |
| `templates/` | Structured output formats | `execution-plan.md` |

### Agents

Create `plugins/agents/<name>.md` with YAML frontmatter and a persona definition:

```yaml
---
name: my-agent
description: When to spawn this agent (used by the orchestrator and agent picker)
---

You are a <role>. Your goal is <purpose>.

# Agent Workflow
## 1. Step one
...
```

Agent design principles:
- **Scope tools deliberately** — each agent type has restricted tool access to enforce separation of concerns (e.g., Oracle is read-only, Code Reviewer can read but not edit)
- **Specify model when it matters** — use `model: haiku` for lightweight coordination, `model: opus` for heavy implementation work

### Commands

Create `plugins/commands/<name>.md`. Commands are raw Markdown instruction scripts — no YAML frontmatter. They use the `t:` prefix naming convention (e.g., `t:fresh-eyes.md`).

```markdown
Describe the task in imperative voice. This is the instruction Claude will follow.

## Steps

1. **First step** — What to do and how.
2. **Second step** — Next action.

## Rules

- Constraint or guardrail.
```

**Accepting arguments:** Use `$ARGUMENTS` as a placeholder anywhere in the command body. It gets replaced with whatever the user types after the command name:

```markdown
**Scope: `$ARGUMENTS`**

If a target is provided above, focus on that scope. Otherwise, sweep everything.
```

Example invocations: `/t:prime /t:auto`, `/t:polish sidebar`, `/t:peer-review a02-1a2b`.

## Verification

After adding or modifying content:

1. **Restart Claude Code** — content is loaded at session start, not hot-reloaded mid-session
2. **Test skill invocation** — type `/skill-name` and verify it triggers correctly
3. **Test command invocation** — type `/t:command-name` and verify the instruction runs
4. **Check trigger matching** — ensure your `description` and `triggers` contain the keywords users would naturally type
5. **Test with arguments** (if applicable) — verify `$ARGUMENTS` substitution works for scoped commands

## Contributing

### Commit conventions

- Use conventional commit prefixes: `feat:`, `fix:`, `docs:`, `refactor:`
- If the workspace has Beads initialized (`.beads/` directory exists), include bead IDs in commit messages: `feat: add capture screen [a02-1a2b]`

### Marketplace verification

To verify your changes work through the plugin marketplace (not just symlinks):

```bash
# In a separate Claude Code session:
/plugin marketplace add trungtnm/claude-code-utils
/plugin install ccu
```

This tests that `marketplace.json` and `plugin.json` are correctly configured.

## Teardown

Remove only the plugin symlinks, leaving your personal content intact:

```bash
for type in skills agents commands; do
  src="$(pwd)/plugins/$type"; dest="$HOME/.claude/$type"
  for item in "$src"/*; do
    [ -e "$item" ] || continue
    name=$(basename "$item"); link="$dest/$name"
    [ -L "$link" ] && rm "$link" && echo "Unlinked $type/$name"
  done
done
```
