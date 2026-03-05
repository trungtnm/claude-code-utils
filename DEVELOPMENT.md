# Development

## Local Setup

Symlink the plugin directories so Claude Code picks up changes immediately without reinstalling:

```bash
ln -sfn "$(pwd)/plugins/skills" ~/.claude/skills
ln -sfn "$(pwd)/plugins/agents" ~/.claude/agents
ln -sfn "$(pwd)/plugins/commands" ~/.claude/commands
```

Restart Claude Code (or start a new session) to load the symlinked content.

## How It Works

Claude Code discovers skills, agents, and commands from `~/.claude/skills/`, `~/.claude/agents/`, and `~/.claude/commands/`. Symlinks make these directories point to your local checkout, so any edits to files in `plugins/` are reflected immediately on next session start.

## Adding Content

**Skill** — create `plugins/skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`).

**Agent** — create `plugins/agents/<name>.md`.

**Command** — create `plugins/commands/<name>.md`.

## Teardown

Remove symlinks without affecting the repo:

```bash
rm ~/.claude/skills ~/.claude/agents ~/.claude/commands
```
