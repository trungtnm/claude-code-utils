# Claude Code Utils

A plugin marketplace for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — custom skills, agents, and commands organized as installable plugins.

## Install

In Claude Code session:

```bash
/plugin marketplace add trungtnm/claude-code-utils
/plugin install claude-code-utils
```

For local development, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Skills

| Skill | Description |
|-------|-------------|
| `/planning` | Feature planning and execution plan generation |
| `/brainstorming` | Idea-to-design process, hard-gates implementation |
| `/test-driven-development` | Write-tests-first methodology |
| `/ubs` | Ultimate Bug Scanner: 18 detection categories, 8 languages |
| `/dcg` | Destructive Command Guard: blocks dangerous commands |
| `/security-review` | Security checklist for auth, input, secrets, APIs |
| `/qa-sweep` | Three-phase quality sweep (inspect, review, polish) |
| `/coding-standards` | TypeScript/JavaScript/React/Node.js standards |
| `/orchestrator` | Spawn and monitor parallel workers (haiku coordinator) |
| `/file-beads` | File detailed Beads epics and issues from a plan |
| `/review-beads` | Review and refine filed Beads issues |
| `/docs-seeker` | Discover docs via llms.txt, Repomix, parallel exploration |
| `/context-engineering` | AI agent architecture and memory system patterns |
| `/frontend-patterns` | React, Next.js, state management patterns |
| `/backend-patterns` | Node.js, Express, Next.js API route patterns |
| `/vercel-react-best-practices` | Vercel Engineering optimization guidelines |
| `/web-design-guidelines` | Web Interface Guidelines compliance review |
| `/design-md` | Semantic design system synthesis |
| `/reactcomponents` | Vite/React component generation from designs |
| `/stitch-loop` | Iterative website building with Stitch |
| `/writing-skills` | Create, edit, and verify skills |
| `/using-skills` | Skill discovery and usage conventions |
| `/cass` | Coding Agent Session Search across multiple agents |
| `/cm` | CASS Memory: procedural memory with confidence decay |
| `/br` | Beads Rust issue tracker: create, triage, dependencies, sync |
| `/bv` | Beads Viewer: graph-aware triage engine with PageRank and critical path |
| `/bd-to-br-migration` | Beads migration utilities |

## Agents

| Agent | Description |
|-------|-------------|
| **TDD Guide** | Test-driven development enforcement |
| **Code Reviewer** | Quality, security, maintainability review |
| **Security Reviewer** | OWASP Top 10, secrets, injection detection |
| **Worker** | Bead implementation agent (opus, TDD-first) |
| **Oracle** | Advisory consultant for complex reasoning (read-only) |
| **Architect** | System design and scalability decisions |
| **Database Reviewer** | PostgreSQL optimization, Supabase practices |
| **Build Error Resolver** | TypeScript/build error fixes (minimal diffs) |

## Commands

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
│   ├── skills/                 # All skills (SKILL.md + references)
│   ├── agents/                 # All agent definitions
│   └── commands/               # All t: session commands
└── README.md
```
