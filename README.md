# Claude Code Utils

Custom skills, agents, and commands for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Why

AI coding agents are powerful but need guardrails, workflows, and domain knowledge to be consistently effective. This repo provides a curated toolkit that addresses common gaps:

- **Quality gates** — Static analysis and security scanning tuned for AI-generated code patterns (null safety, async/await, XSS)
- **Workflow structure** — Planning, brainstorming, and TDD skills that enforce disciplined processes before code gets written
- **Multi-agent coordination** — An orchestrator/worker architecture for parallelizing complex epics across multiple agents
- **Safety** — A destructive command guard that intercepts dangerous shell commands before execution
- **Knowledge access** — Documentation discovery, coding standards, and architecture pattern references available in-context

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

The `t:` prefixed commands are quick-action prompts designed for common session tasks. They run immediately without configuration.

| Command | Purpose |
|---------|---------|
| `t:rootfix` | Diagnose and fix root causes — no bandaid fixes. Uses extended thinking. |
| `t:fresh-eyes` | Re-read all code from the current session and catch bugs with a fresh perspective. |
| `t:peer-review` | Review code written by other agents or contributors across the project. |
| `t:random-inspect` | Randomly explore code files, trace execution flows, and fix issues found. |
| `t:polish` | Scrutinize UI/UX and implementation for Stripe-level quality. |
| `t:enrich-readme` | Add new substantive content to the project README. |
| `t:enrich-docs` | Find undocumented functionality and create narrative documentation. |
| `t:top-ideas` | Generate the 10 most impactful feature ideas for the project. |
| `t:done` | Session completion — closes beads, syncs state, and wraps up cleanly. |

## Skill Catalog

### Workflow & Process

| Skill | Description |
|-------|-------------|
| `/planning` | Feature planning, roadmaps, and implementation approach design. Generates execution plans. |
| `/brainstorming` | Collaborative idea-to-design process. Hard-gates implementation until a design is approved. |
| `/test-driven-development` | Enforces write-tests-first methodology before any implementation code. |
| `/finishing-a-development-branch` | Guides branch completion — merge, PR, or cleanup options. |
| `/using-git-worktrees` | Creates isolated git worktrees for feature work with safety verification. |

### Quality & Safety

| Skill | Description |
|-------|-------------|
| `/ubs` | Ultimate Bug Scanner — 18 detection categories, 8 languages, 4-layer static analysis. The pre-commit quality gate. |
| `/dcg` | Destructive Command Guard — Rust hook that blocks dangerous commands (rm -rf, git reset --hard) with SIMD-accelerated filtering. |
| `/security-review` | Comprehensive security checklist for auth, user input, secrets, and API endpoints. |
| `/qa-sweep` | Three-phase quality sweep: random inspection, peer review, and UI/UX polish. Runs autonomously. |
| `/coding-standards` | TypeScript/JavaScript/React/Node.js coding standards and best practices reference. |

### Multi-Agent Coordination

| Skill | Description |
|-------|-------------|
| `/orchestrator` | Spawns and monitors parallel worker agents for epic execution. Uses haiku for coordination, opus for workers. |
| `/file-beads` | Files detailed Beads epics and issues from an execution plan. |
| `/review-beads` | Reviews, proofreads, and refines filed Beads issues before work begins. |

### Knowledge & Reference

| Skill | Description |
|-------|-------------|
| `/docs-seeker` | Discovers documentation via llms.txt, Repomix GitHub analysis, and parallel exploration agents. |
| `/context-engineering` | Patterns for designing AI agent architectures, memory systems, and token optimization. |
| `/frontend-patterns` | React, Next.js, state management, and performance optimization patterns. |
| `/backend-patterns` | Node.js, Express, and Next.js API route architecture patterns. |
| `/vercel-react-best-practices` | Vercel Engineering's React/Next.js performance optimization guidelines. |
| `/web-design-guidelines` | Web Interface Guidelines compliance review for UI code. |

### Meta & Tooling

| Skill | Description |
|-------|-------------|
| `/writing-skills` | Create, edit, and verify skills before deployment. |
| `/using-skills` | Establishes skill discovery and usage conventions at session start. |
| `/cass` | Coding Agent Session Search — index and search local agent history across Claude Code, Codex, Gemini, Cursor, and more. |
| `/cm` | CASS Memory — three-layer procedural memory with confidence decay and cross-agent knowledge transfer. |

## Agent Catalog

Agents are specialized sub-agents spawned via the Task tool. Each is a focused expert with constrained tool access.

| Agent | Role | Key Trait |
|-------|------|-----------|
| **Oracle** | Advisory consultant for complex reasoning | Read-only — opinions, not directives |
| **Architect** | System design and scalability decisions | Proactive on new features and refactors |
| **Code Reviewer** | Quality, security, and maintainability review | Expected after every code change |
| **Security Reviewer** | OWASP Top 10, secrets, injection, SSRF detection | Proactive on auth and user input code |
| **TDD Guide** | Test-driven development enforcement | Targets 80%+ coverage |
| **Build Error Resolver** | TypeScript and build error fixes | Minimal diffs only — no architectural edits |
| **Database Reviewer** | PostgreSQL query optimization and schema design | Incorporates Supabase best practices |
| **Worker** | Bead implementation agent for orchestrated epics | TDD-first, uses Agent Mail for coordination |

## Architecture: Orchestrator + Worker

For large features, the repo supports a multi-agent execution model:

```
┌──────────────────────────────────────────────────┐
│              /planning                           │
│  Generates execution-plan.md with tracks & beads │
└──────────────┬───────────────────────────────────┘
               ▼
┌──────────────────────────────────────────────────┐
│            /orchestrator (haiku)                  │
│  Reads plan → spawns workers → monitors progress │
│  Handles cross-track blockers via Agent Mail     │
└──────┬───────────┬───────────┬───────────────────┘
       ▼           ▼           ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │Worker A│ │Worker B│ │Worker C│  (opus)
   │Track 1 │ │Track 2 │ │Track 3 │
   └────────┘ └────────┘ └────────┘
       │           │           │
       ▼           ▼           ▼
   TDD cycle → commit → report back
```

**Key design decisions:**
- **Model split** — Haiku handles orchestration (lightweight coordination), Opus handles workers (code reasoning). This optimizes cost without sacrificing code quality.
- **Agent Mail** — Workers communicate through a message bus rather than shared state, preventing file conflicts in parallel execution.
- **File reservations** — Workers reserve file paths before editing, avoiding merge conflicts when multiple agents modify the codebase simultaneously.
- **Beads tracking** — Each unit of work is a "bead" with dependencies, status, and history. Beads persist across sessions via git-backed storage.

## Creating New Skills

1. Create a directory in `skills/` with your skill name
2. Add a `SKILL.md` file with the skill definition
3. The skill is immediately available in Claude Code

See [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code) for skill format details.
