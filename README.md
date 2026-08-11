# Claude Code & Codex Utils

A shared plugin marketplace for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [Codex](https://developers.openai.com/codex/) — reusable engineering skills and workflows organized as one installable plugin (`ccu`).

## Install

### Claude Code

In a Claude Code session:

```bash
/plugin marketplace add trungtnm/claude-code-utils
/plugin install ccu
```

### Codex

From a terminal:

```bash
codex plugin marketplace add trungtnm/claude-code-utils
codex plugin add ccu@ccu
```

Restart Codex and open a new conversation after installation. Every skill is
available by name — the same workflows Claude invokes as `/name`, Codex invokes
as `$name` (`/capture` ↔ `$capture`, `/commit` ↔ `$commit`). Open `/hooks` once
to inspect and trust the bundled read-only beads drift guard.

For local development, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Compatibility

The same `SKILL.md` files and `SessionStart` hook power both products — every
workflow has exactly one definition under `skills/`, with no per-host copy to
keep in sync. Claude Code additionally loads native `agents/`; Codex maps those
personas onto its own subagents. Workflows translate product-specific tool names
to the current host's user-input, planning, and collaboration tools.

See [the compatibility contract](plugins/ccu/CODEX.md) for the full mapping.

## The Core Workflow

Everything in this plugin serves one loop: **capture ideas without losing flow, triage them into beads, and let agents execute the beads autonomously.**

```mermaid
graph LR
    A["/capture<br/>idea → .ccu/CAPTURES.md"] --> B["/triage<br/>quick-fix / bead / defer"]
    B --> C["Beads backlog<br/>br + bv"]
    C --> D["/auto<br/>single agent"]
    C --> E["/orchestrator<br/>worker per bead"]
```

### 1. Capture — `/capture`

The most valuable habit: record every idea, bug, or observation the moment it occurs. Takes under 5 seconds, never breaks focus:

```bash
/capture this API should have rate limiting
/capture flaky test in checkout.test.ts — race condition?
/capture [paste image]      # saved to .ccu/captures/, summarized in text
```

Everything lands in `.ccu/CAPTURES.md` as a timestamped checklist — no analysis, no formatting, no interruption.

### 2. Triage — `/triage`

At natural breaks (between beads, end of day), classify every unchecked capture:

```bash
/triage    # each capture → quick-fix (done now) / new bead / defer / discard
```

Small fixes get done immediately; substantial ideas become beads (via [[file-beads]] templates); noise gets consciously discarded. Capture fast, triage deliberately — good ideas never slip through and you never lose flow chasing them.

### 3. Execute — `/auto` or `/orchestrator`

**`/auto`** — a single autonomous agent works through the beads backlog:

- Picks the highest-value ready bead (`br ready` + `bv`), claims it, implements with TDD, verifies (tests/lint/typecheck/build), commits per bead, closes it, and loops until nothing actionable remains.
- Detects other active agents via Agent Mail; when peers are present it runs in multi-agent mode with file reservations, otherwise solo.
- Commits land directly on your current branch; pushing is always your call.

**`/orchestrator`** — coordinated multi-agent execution for a planned epic:

- The orchestrator only coordinates, never writes code. It spawns **one worker per ready bead** (capped at 3 concurrent), driven by the `bv`/`br ready` dependency graph — closing a bead unblocks and dispatches the next wave.
- After all beads are verified, one independent **tester** agent writes functional/e2e tests against the epic's public surface, bugs bounce back to fix-scoped coders, and a **reviewer** agent does an integrated sweep + writes docs.
- Verification is objective: the orchestrator checks that a commit exists per bead, greps diffs for `mock`/`stub`/`TODO`, and confirms every commit stays inside the bead's `## Files` scope.

### Coordination: Agent Mail + Beads

All agents work in the same tree, on the current branch. Two mechanisms keep them from colliding:

- **Agent Mail file reservations** — every worker reserves its bead's `## Files` before editing and releases on completion. A failed reservation means stop and report, never proceed. Agent Mail is keyed to the repo root, so reservations from every session and epic collide correctly.
- **Beads dependencies (`br dep`, scheduled by `bv`)** — only beads whose dependencies are closed get dispatched. Beads that can run in parallel must have disjoint `## Files` sets; beads that share files are sequenced with an explicit dependency.

Commit discipline follows: agents stage named files only and commit with a pathspec (`git commit -m "..." -- <paths>`), so concurrent work in the shared index never leaks between commits.

## Planning a Feature

For anything bigger than a quick fix, plan before executing:

```mermaid
graph LR
    A["/brainstorming<br/>intent → design.md"] --> B["/plan-beads<br/>7-phase pipeline"]
    B --> C["/file-beads<br/>epic + issues"]
    C --> D["/review-beads<br/>optimize before work"]
    D --> E["/orchestrator or /auto"]
```

**`/brainstorming`** is the required front door for creative work — it explores user intent, requirements, and design *before* any implementation, and writes the agreed design to `.ccu/artifacts/<dir>/design.md`. Alternatively `/discuss` runs guided requirements gathering for a concrete feature.

**`/plan-beads`** runs the full planning pipeline: parallel codebase discovery → Oracle synthesis (approach + risk map) → decomposition into beads → bead review → `bv` graph validation → a bead-level execution plan (`.ccu/artifacts/<dir>/execution-plan.md` with planned files, coordination resources, integration checkpoints, entry points, and waves).

### The Beads Ecosystem

Beads are the source of truth for all work — bead IDs link to Agent Mail threads, git commits (`Bead: <id>` footer), and the dependency graph.

**`br`** (Beads Rust) is the issue tracker: types (task/bug/feature/epic), priorities (p0–p4), dependency links, JSONL sync via git. It never runs git itself — committing bead state is always explicit. Agents resolve identity via `ACTOR="${BR_ACTOR:-assistant}"`.

**`bv`** (Beads Viewer) computes graph metrics over the backlog: degree and topological sort instantly, then PageRank, betweenness, cycles, and critical path. Agents use `--robot-*` flags (`--robot-triage`, `--robot-priority`, `--robot-plan`) — bare `bv` opens a TUI that blocks automation.

**`/file-beads`** is the single source of truth for bead structure. Every bead is self-contained for a worker with zero context: project context, reasoning, executable acceptance criteria, a **`## Files`** block with the best-known production and test footprint, a **`## Coordination Resources`** block for admission, and an **`## Interfaces`** block for known cross-bead seams. Epics carry inherited `## Global Constraints` and project-specific `## Orchestration Environment` commands.

**`/review-beads`** applies the plan-space philosophy — *"changing a bead takes seconds, changing implemented code takes hours"* — checking self-documentation, interface consistency, test ownership, and file/resource conflicts between parallel-ready beads.

## Skills

Beads & workflow:

| Skill | Description |
|-------|-------------|
| `/brainstorming` | Explore intent, requirements, and design before any implementation |
| `/plan-beads` | Feature planning pipeline: discovery → approach → beads → execution plan |
| `/file-beads` | File epics and self-documented issues; owns the bead templates |
| `/review-beads` | Review, proofread, and refine filed beads |
| `/br` | Beads Rust issue tracker: create, triage, dependencies, sync |
| `/bv` | Beads Viewer: graph-aware triage (PageRank, critical path, cycles) |
| `/triage` | Classify captures into quick-fixes, beads, or deferrals |
| `/orchestrator` | Multi-agent bead execution: dispatch, monitor, verify |
| `/recipe` | Pre-built workflow chains (new-feature, bug-fix, quality-review) |
| `/grill-with-docs` | Stress-test a plan against the domain model; update CONTEXT.md and ADRs inline |
| `/session-state` | `.ccu/` directory: captures, decisions journal, recipe checkpoint, artifacts |

Quality & safety:

| Skill | Description |
|-------|-------------|
| `/test-driven-development` | Write-tests-first methodology |
| `/ubs` | Ultimate Bug Scanner: static analysis quality gate |
| `/dcg` | Destructive Command Guard: blocks dangerous commands pre-execution |
| `/security-review` | Security checklist for auth, input, secrets, APIs |
| `/qa-sweep` | Three-phase quality sweep (inspect, peer-review, polish) |

Frontend & design:

| Skill | Description |
|-------|-------------|
| `/ui-spec-writer` | Implementation specs from a working demo, for handoff to agents |
| `/excalidraw-diagram` | Excalidraw diagrams that make visual arguments |
| `/markdown-html-viewer` | Render Markdown docs as a polished HTML viewer with Mermaid |

Knowledge & memory:

| Skill | Description |
|-------|-------------|
| `/cass` | Search session history across coding agents |
| `/cm` | Procedural memory with confidence decay and anti-pattern learning |
| `/docs-seeker` | Discover docs via llms.txt, Repomix, parallel exploration |
| `/tech-doc` | Owns documentation prose style: READMEs, ADRs, API refs, runbooks |
| `/deslopify` | Remove AI tropes and clichés from text |
| `/mcp-builder` | Build MCP servers in Python (FastMCP) or TypeScript |

## Agents

| Agent | Model | Role |
|-------|-------|------|
| **worker** | opus | Implements one assigned bead with TDD; the only role that edits production logic |
| **tester** | opus | Independent functional/integration/e2e tests against the epic, black-box |
| **reviewer** | opus | Final integrated review + documentation for what was built |
| **oracle** | — | Read-only advisory consultant for complex reasoning |
| **architect** | — | System design and scalability analysis (read-only) |
| **code-reviewer** | — | Quality, security, maintainability review |
| **security-reviewer** | — | OWASP Top 10, secrets, injection detection |
| **database-reviewer** | — | PostgreSQL/Supabase schema and query review |
| **build-error-resolver** | — | Build/type errors only, minimal diffs |
| **tdd-guide** | — | Enforces write-tests-first methodology |

Tool access is deliberately scoped per agent: reviewers and consultants read but don't edit; the worker has full access because it owns implementation.

## Workflow skills

Session workflows are single-purpose instruction scripts. Most accept optional `$ARGUMENTS` to scope their work. Invoke them as `/name` in Claude Code and `$name` in Codex.

### Core loop

| Workflow | Purpose |
|----------|---------|
| `capture` | Record an idea, observation, or bug in <5 seconds |
| `auto` | Autonomous agent: register with Agent Mail, work through ready beads |
| `next` | Analyze all state, recommend the single best next action |
| `commit` | Commit all changes in logical groups with detailed messages |
| `done` | Session completion: close beads, sync state, wrap up |
| `init` | Check and set up prerequisite tools and project state |

### Implementation & review

| Workflow | Purpose |
|----------|---------|
| `blindspot` | Surface your unknown unknowns about a domain or module before starting work |
| `discuss` | Guided requirements gathering for a new feature |
| `peer-review` | Review code for bugs, security issues, reliability problems |
| `fresh-eyes` | Re-read all session code and catch bugs with fresh perspective |
| `random-inspect` | Randomly explore code files, trace flows, fix issues |
| `rootfix` | Diagnose and fix root causes — no bandaid fixes |
| `remove-stub` | Replace all stubs, placeholders, mocks, and TODOs with real code |
| `demo-to-prod` | Convert a working demo/prototype UI into a production app |
| `onboard` | Guide setup, running, and testing after auto dev mode completes |
| `quiz` | Explain a change set and quiz the user on it before merging unread code |

### Polish, docs & analysis

| Workflow | Purpose |
|----------|---------|
| `polish` | Scrutinize UI/UX and implementation quality |
| `performance-audit` | Find and fix performance problems |
| `enrich-readme` | Enrich the README with real content from the codebase |
| `enrich-docs` | Find undocumented functionality and document it |
| `reorganize` | Reorganize a target directory |

### Ideation

| Workflow | Purpose |
|----------|---------|
| `top-ideas` | Top 10 most impactful feature ideas |
| `idea-wizard` | Best ideas for improving the project |
| `opinion` | Honest, critical assessment of the project (or a target) |

## A Typical Day

```
Morning:
  /next                               ← "In-progress bead a02-1a2b — resume it"
  /auto                               ← Resumes from beads + git, completes remaining beads
  /capture fix the flaky test in auth.test.ts
  /capture [pasted image] -> check and improve the styling of CTA button
  /capture we need to support ZNS for messages sending
  /capture #more captures...

Midday:
  /triage                               ← "flaky test → quick-fix (doing now), other beads..."
  /next                               ← "3 ready beads. Start a02-4e5f"
  /auto                               ← Works through ready beads

Afternoon:
  /brainstorming add SSO support        ← Design exploration for the next feature
  /plan-beads                           ← Decompose into beads + execution plan
  /orchestrator                         ← Parallel workers, one per ready bead
  /commit                             ← Commit in logical groups
```

Both execution paths record verification in bead close reasons and commits, and route decisions per the session-state promote rule: ADR-worthy ones to `docs/adr/`, the rest to the `.ccu/DECISIONS.md` journal. Resume state lives in beads and git.

## How It Works

### Plugin system

| Type | Shared source | Claude Code | Codex |
|------|---------------|-------------|-------|
| **Skill / workflow** | `plugins/ccu/skills/<name>/SKILL.md` | `/name` or auto-trigger | `$name` or auto-trigger |
| **Agent persona** | `plugins/ccu/agents/<name>.md` | Native `Task(subagent_type=...)` | Loaded into a generic Codex subagent task when allowed |
| **Hook** | `plugins/ccu/hooks/hooks.json` | Native plugin hook | Native plugin hook; review/trust with `/hooks` |

Skill frontmatter is minimal — `name`, `description` (with trigger phrases), and optionally `argument-hint` or `model`. The body is the workflow itself: comprehensive enough to reference mid-work, not a thin wrapper.

There is no separate command layer and no code generation step: knowledge skills
and session workflows are the same component type, so each one has a single
definition that both hosts run.

### Repository layout

```
claude-code-utils/
├── .claude-plugin/
│   └── marketplace.json        # Claude Code marketplace
├── .agents/plugins/
│   └── marketplace.json        # Codex repo marketplace
├── plugins/
│   └── ccu/                    # Shared plugin root
│       ├── .claude-plugin/     # Claude Code plugin manifest
│       ├── .codex-plugin/      # Codex plugin manifest
│       ├── skills/             # Shared knowledge skills + session workflows
│       ├── agents/             # Claude roles; Codex persona resources
│       ├── CODEX.md            # Cross-host compatibility contract
│       └── hooks/              # Shared Claude Code/Codex SessionStart hook
├── scripts/
│   └── ccu-refresh.sh          # Reinstall the plugin from this checkout
├── DEVELOPMENT.md
└── README.md
```

### Session state (`.ccu/`)

Project-local, plain-Markdown session state: `CAPTURES.md` (ideas), `DECISIONS.md` (append-only journal of decision claims, grep-on-demand), `CHECKPOINT.md` (recipe progress, deleted on completion), and `artifacts/<dir>/` (planning docs: discovery, approach, execution plan, summary — browsable via a generated HTML index). Durable knowledge lives outside `.ccu/`: ADRs in `docs/adr/`, requirements as beads, verification in bead close reasons and commits.

## Contributing

See [DEVELOPMENT.md](DEVELOPMENT.md) for local setup and the skill authoring workflow. When adding skills, follow the existing `SKILL.md` frontmatter convention: `name`, a `description` rich in trigger phrases, and a workflow body with concrete commands.
