# Claude Code Utils

A plugin marketplace for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — custom skills, agents, and commands organized as installable plugins.

## Install

```bash
/install trungtnm/claude-code-utils
```

Then enable the plugins you want from the list. Each plugin can be toggled independently.

## Plugins

### workflow

Disciplined development workflows: planning, brainstorming, and TDD enforcement.

| Skills | Agents |
|--------|--------|
| `/planning` — Feature planning and execution plan generation | **TDD Guide** — Test-driven development enforcement |
| `/brainstorming` — Idea-to-design process, hard-gates implementation | |
| `/test-driven-development` — Write-tests-first methodology | |

### quality-safety

Quality gates and safety tools for AI-generated code.

| Skills | Agents |
|--------|--------|
| `/ubs` — Ultimate Bug Scanner: 18 detection categories, 8 languages | **Code Reviewer** — Quality, security, maintainability review |
| `/dcg` — Destructive Command Guard: blocks dangerous commands | **Security Reviewer** — OWASP Top 10, secrets, injection detection |
| `/security-review` — Security checklist for auth, input, secrets, APIs | |
| `/qa-sweep` — Three-phase quality sweep (inspect, review, polish) | |
| `/coding-standards` — TypeScript/JavaScript/React/Node.js standards | |

### multi-agent

Orchestrator/worker architecture for parallelizing complex epics.

| Skills | Agents |
|--------|--------|
| `/orchestrator` — Spawn and monitor parallel workers (haiku coordinator) | **Worker** — Bead implementation agent (opus, TDD-first) |
| `/file-beads` — File detailed Beads epics and issues from a plan | |
| `/review-beads` — Review and refine filed Beads issues | |

```
/planning → execution-plan.md
    ↓
/orchestrator (haiku) → spawns workers → monitors progress
    ↓           ↓           ↓
Worker A    Worker B    Worker C   (opus)
Track 1     Track 2     Track 3
    ↓           ↓           ↓
TDD cycle → commit → report back
```

### knowledge

Documentation discovery, architecture patterns, and expert advisory agents.

| Skills | Agents |
|--------|--------|
| `/docs-seeker` — Discover docs via llms.txt, Repomix, parallel exploration | **Oracle** — Advisory consultant for complex reasoning (read-only) |
| `/context-engineering` — AI agent architecture and memory system patterns | **Architect** — System design and scalability decisions |
| `/frontend-patterns` — React, Next.js, state management patterns | **Database Reviewer** — PostgreSQL optimization, Supabase practices |
| `/backend-patterns` — Node.js, Express, Next.js API route patterns | |
| `/vercel-react-best-practices` — Vercel Engineering optimization guidelines | |
| `/web-design-guidelines` — Web Interface Guidelines compliance review | |
| `/design-md` — Semantic design system synthesis | |
| `/reactcomponents` — Vite/React component generation from designs | |
| `/stitch-loop` — Iterative website building with Stitch | |

### dev-tools

Developer utilities for skill authoring, session history, and build fixes.

| Skills | Agents |
|--------|--------|
| `/writing-skills` — Create, edit, and verify skills | **Build Error Resolver** — TypeScript/build error fixes (minimal diffs) |
| `/using-skills` — Skill discovery and usage conventions | |
| `/cass` — Coding Agent Session Search across multiple agents | |
| `/cm` — CASS Memory: procedural memory with confidence decay | |
| `/bd-to-br-migration` — Beads migration utilities | |

### session-commands

Quick-action `t:` commands for common session tasks. Run immediately without configuration.

| Command | Purpose |
|---------|---------|
| `t:rootfix` | Diagnose and fix root causes — no bandaid fixes |
| `t:fresh-eyes` | Re-read session code and catch bugs with fresh perspective |
| `t:peer-review` | Review code written by other agents or contributors |
| `t:random-inspect` | Randomly explore code files, trace flows, fix issues |
| `t:polish` | Scrutinize UI/UX and implementation for quality |
| `t:enrich-readme` | Add new substantive content to the project README |
| `t:enrich-docs` | Find undocumented functionality and create documentation |
| `t:top-ideas` | Generate the 10 most impactful feature ideas |
| `t:opinion` | Get an honest assessment of the project |
| `t:prime` | Deep-read AGENTS.md and README.md for full context |
| `t:remove-stub` | Find and replace all stubs, placeholders, and TODOs |
| `t:reorganize` | Reorganize a target directory |
| `t:done` | Session completion — close beads, sync state, wrap up |

## Structure

```
claude-code-utils/
├── .claude-plugin/
│   └── marketplace.json        # Marketplace manifest
├── plugins/
│   ├── workflow/               # Planning, brainstorming, TDD
│   ├── quality-safety/         # UBS, DCG, security, QA
│   ├── multi-agent/            # Orchestrator + workers
│   ├── knowledge/              # Docs, patterns, references
│   ├── dev-tools/              # Skill authoring, CASS, CM
│   └── session-commands/       # t: quick-action commands
└── README.md
```
