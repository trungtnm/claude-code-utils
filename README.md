# Claude Code Utils

Custom skills, agents, and commands for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Structure

```
├── skills/      # Custom slash commands (e.g., /commit, /review-pr)
├── agents/      # Custom agent definitions for Task tool
└── commands/    # Custom CLI commands
```

## Setup

This repo is symlinked to `~/.claude/` so changes here automatically reflect in Claude Code:

```bash
~/.claude/skills   → /path/to/this/repo/skills
~/.claude/agents   → /path/to/this/repo/agents
~/.claude/commands → /path/to/this/repo/commands
```

## Usage

### Skills

Skills are invoked with `/skill-name` in Claude Code. Each skill is a directory containing a `SKILL.md` file.

Example: `/planning` invokes `skills/planning/SKILL.md`

### Agents

Agents are markdown files that define specialized sub-agents for the Task tool. They're automatically available as `subagent_type` options.

Example: `agents/oracle.md` defines the "Oracle" agent

### Commands

Custom CLI commands that extend Claude Code functionality.

## Creating New Skills

1. Create a directory in `skills/` with your skill name
2. Add a `SKILL.md` file with the skill definition
3. The skill is immediately available in Claude Code

See [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code) for skill format details.
