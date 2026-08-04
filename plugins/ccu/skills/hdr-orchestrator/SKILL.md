---
name: hdr-orchestrator
description: Turn this Claude Code or Codex session into the repo's delegation coordinator — spawn same-host peer sessions in visible Herdr terminal panes, one per task, with bead-authoritative briefs, lock-free admission control, and evidence-based verification. Use when delegating tasks to peer sessions, running ad-hoc parallel work in panes, coordinating main-agent-to-main-agent work via herdr, or when asked to "delegate this", "spawn a peer for X", or "run these in parallel panes".
---

# hdr-orchestrator: Main-Agent Delegation Through Herdr Panes

This skill turns the current Claude Code or Codex session into the **coordinator** for this repo. Peers are ordinary same-host main-agent sessions spawned in Herdr terminal panes — visible, attachable, persistent — working in the **same tree on the current branch**. Coordination signals (agent state, screen reads) are shell operations against the `herdr` CLI, free of model tokens.

**Hard rules (never weaken):**

- The coordinator **never edits code**. It writes briefs, spawns peers, monitors, verifies, reports. This skill owns the whole coordination loop — ad-hoc tasks, parallel batches, and full epics alike; it never hands coordination off to another skill.
- Peers get **zero coordination tooling** — no MCP handshake, no Agent Mail, no registration. A peer is a plain `claude` or `codex` session with a file to read.
- **No locks.** Exclusion = admission control before dispatch (disjoint `## Files` scopes) + post-hoc scope and foreign-edit checks at verification. **One coordinator per repo at a time**, and no other agent workflows run alongside it in this repo.
- The **bead is the task authority**. A brief that restates bead content is a bug.
- **Herdr is signal; files + git are truth.** Every `herdr agent wait` carries `--timeout`; on timeout, poll `RESULT.md` and `git log`.

## Prerequisite Gate

Run these checks before anything else. If any fails, **refuse with instructions — never half-run**:

```bash
[ "$(git rev-parse --show-toplevel)" = "$(pwd)" ]   # 1. cwd IS the repo root — else refuse:
                                                    #    "start /hdr-orchestrator from <root>"
command -v herdr                                    # 2. herdr installed — else refuse:
                                                    #    "install herdr (herdr.dev), v0.7.x"
herdr agent list                                    # 3. socket alive — "Connection refused"
                                                    #    means no Herdr server: refuse, tell the
                                                    #    user to launch `herdr` first
peer_cli=codex                                      # 4. use `claude` in Claude Code
command -v "$peer_cli"                              #    unless the user selects another host
```

This skill is pinned to the **verified herdr 0.7.4 CLI surface** — see [references/herdr-driving.md](references/herdr-driving.md). Never invent flags; version drift surfaces as CLI errors → escalate, don't guess.

## Host Selection

Default to a **same-host cohort**: a Claude Code coordinator spawns `claude`; a
Codex coordinator spawns `codex`. Honor an explicit user request to use the
other installed CLI, but record the choice in the ledger and do not mix hosts
inside one run. The durable protocol is identical; only spawn, reviewer, and
permission adapters differ. Read
[references/host-adapters.md](references/host-adapters.md) before the first
dispatch.

## Init: State Layout

Everything lives in this repo's `.ccu/` and is **gitignored**. First, append any missing entries to `.gitignore` (tracked ledger writes would trip the out-of-scope verification check):

```bash
for p in ".ccu/hdr/" ".ccu/delegations/" ".worktrees/"; do
  grep -qxF "$p" .gitignore || echo "$p" >> .gitignore
done
mkdir -p .ccu/hdr .ccu/delegations
```

- **Ledger:** `.ccu/hdr/LEDGER.md` — one row per delegation: id, pane label, bead id, work type, tier, status (`queued` → `running` → `done` → `verified` / `rejected` / `blocked`), rejection count, expected-red flag, commit SHAs. Header records peer host/CLI, `herdr --version`, and session start time.

**Name your own session when Herdr manages it.** The coordinator's pane is
labeled `hdr-<id>` — `hdr-<epic-id>` when driving an epic, `hdr-<bead-id>` for
a single delegation (re-rename when the target changes). This marks the
coordinator in the sidebar:

```bash
if own_pane_id="$(herdr pane current 2>/dev/null)"; then
  herdr pane rename "$own_pane_id" "hdr-<epic-or-bead-id>"
fi
```

Codex may run from an app or terminal outside Herdr. Failure to resolve the
coordinator pane is **not** a prerequisite failure: record `coordinator:
external` in the ledger and enforce the one-coordinator rule from the ledger
plus the existing Herdr agent list. Peer panes still run in Herdr.
- **Per-delegation dir:** `.ccu/delegations/<id>/` — `BRIEF.md`, `RESULT.md`, `REJECTION-<n>.md`, and for tiered runs `DESIGN.md` + `TESTPLAN.md`.

The ledger is a **cache**, not truth — see Evidence Precedence below.

## Task Definition: Bead Is the Authority, Brief Is a Pointer

One authority per fact — duplication drifts, and a peer working a stale spec is a silent failure:

| Fact | Owner |
|---|---|
| Objective, context, reasoning, acceptance criteria, `## Files` scope, `## Interfaces` | **Bead** ([[file-beads]] templates) |
| Delegation id, pane label, work type, granted authority, completion protocol, rejection history | **Brief** |

- **Bead repos (`.beads/` exists): every delegation gets a bead, even ad-hoc work.** `br create` is one command; it buys durability, status, comments, and recovery. The brief is then a ~15-line pointer — [templates/delegation-brief.md](templates/delegation-brief.md).
- **Non-bead repos:** `BRIEF.md` absorbs the work definition using the file-beads Tier-1/2 section shapes verbatim (`## Files`, executable acceptance criteria, `## Interfaces`) so peers develop one reading habit. The template carries this shape too.
- **Red-flag rule:** a `BRIEF.md` in a bead repo containing a `## Files` block, acceptance criteria, or context narrative is a **bug — delete it and fix the bead**.
- **`RESULT.md` is always a file, never bead comments.** It is the completion authority and the fallback poll target (`test -f` is cheap and unambiguous; `br close` and "report written" are different events). The bead gets a one-line close reason + pointer.

## Delegation Protocol

One delegation = **brief → spawn → result**.

**Ids and labels.** Delegation id: `<YYYYMMDD>-<kebab-slug>` (e.g. `20260729-fix-checkout-race`). The **pane label is the bead id** (e.g. `a04-3f2c`) — so the Herdr sidebar reads as a live task board keyed the same way as `br`, commits, and the ledger. Non-bead repos have no bead id: label the pane with the delegation slug instead. Bead ids are unique, so labels never collide. The ledger maps delegation id ↔ bead id (= pane label).

**1. Brief + bead.** Create/confirm the bead (`br create` for ad-hoc work), write the thin `BRIEF.md` from the template, and copy [templates/result.md](templates/result.md) into the delegation dir as `RESULT-TEMPLATE.md` (peers can't see the plugin dir; the brief points them at this copy). The brief carries the delegation's **work type** — `production` / `demo` / `mockup` — set by you from the task's nature; it decides which smell rules apply at verification.

**2. Admission check (the exclusion mechanism — before any tokens are spent):**

- Dispatch only if the bead's `## Files` scope is **disjoint from every running delegation's scope**. Overlap → ledger `queued`; dispatch when the blocker reaches `verified`.
- **Concurrency cap: 3 peers** — beyond that, the shared tree and build/test environment start thrashing.
- Peers treat their `## Files` block as a hard edit boundary (brief rule), verified post-hoc by the scope check.

**3. Spawn** — atomic spawn+name+cwd, no detection race. Use exactly one of
these same-host adapters:

```bash
# Claude Code coordinator
herdr agent start a04-3f2c --cwd "$(git rev-parse --show-toplevel)" -- \
  claude "Read .ccu/delegations/20260729-fix-checkout-race/BRIEF.md and execute it. Your final act is writing .ccu/delegations/20260729-fix-checkout-race/RESULT.md (and closing the bead it names)."

# Codex coordinator
herdr agent start a04-3f2c --cwd "$(git rev-parse --show-toplevel)" -- \
  codex "Read .ccu/delegations/20260729-fix-checkout-race/BRIEF.md and execute it. Your final act is writing .ccu/delegations/20260729-fix-checkout-race/RESULT.md (and closing the bead it names)."
```

The bootstrap prompt is that one sentence — everything else lives in the brief and the bead. Ledger row → `running`, record the dispatch timestamp (the foreign-edit check needs it).

**4. Result.** The peer's final act is writing `RESULT.md` per [templates/result.md](templates/result.md) — status, commit SHAs, gates run with outcomes, deviations, out-of-scope failures observed, follow-ups — then `br close <bead> --reason "<one line> — see RESULT.md"`.

**Epic-sized work (a bead graph, not one bead):** the coordinator runs the epic itself with the same loop — one delegation per bead, **dispatch driven by the dependency graph**. `br ready` (filtered to the epic) lists what can run now; `bv --robot-priority` ranks it. Each ready bead goes through the normal admission check and spawns as its own delegation; when one reaches `verified`, re-run `br ready` — closing a bead typically unblocks others — and dispatch the newly ready beads. The cap of 3 and disjoint-scope rule apply unchanged; two ready beads with overlapping `## Files` queue in graph order.

## Monitoring

Wait on state transitions, **always with `--timeout`** (v0.7.4 has no `done` state — idle is the completion signal, and it can misfire):

```bash
herdr agent wait a04-3f2c --status idle --timeout 600000     # completion signal
herdr agent wait a04-3f2c --status blocked --timeout 600000  # stuck-peer catch
```

- **On timeout with no transition:** poll the files — `test -f .ccu/delegations/<id>/RESULT.md`, `git log --oneline -5`, and `herdr agent read <label> --source recent` to peek at the screen. State is signal; files are truth.
- **On idle + `RESULT.md` present:** verify (next section).
- **On idle without `RESULT.md`:** the peer may have stopped mid-task — read the pane, and if it is genuinely stalled treat it as a rejection ("no RESULT.md was written").
- **On blocked:** `herdr agent read <label> --source recent` to see the actual question. If it falls **within the brief's granted authority**, answer straight into the pane (`herdr agent send` + Enter — see the driving manual). Anything touching plan, scope, or irreversible actions **escalates through the current host's user-input mechanism**. Ledger stays `blocked` — never silently dropped.

## Verification and Rejection

**Verify from evidence, never from the screen.** Run the full checklist in [references/verification.md](references/verification.md):

1. `RESULT.md` complete per template;
2. every claimed commit SHA exists in `git log`, carrying `Delegation:` + `Bead:` trailers;
3. commits stay inside the bead's `## Files` scope;
4. work-type-aware smell grep (production only; test files and demo/mockup exempt);
5. foreign-edit check over the scope since dispatch;
6. **coordinator-owned full-suite gate** — the repo's full test/lint/build, run serially here (peers never run it), skipping suites the ledger flags expected-red;
7. bead closed.

**Pass** → ledger `verified`, report to the user with per-item ✓/✗. **Fail** → durable rejection, in this order:

```bash
# 1. FIRST write the durable file — never depend on a keystroke having landed
Write .ccu/delegations/<id>/REJECTION-<n>.md          # per templates/rejection.md
# 2. THEN inject (agent send writes literal text — Enter goes separately)
herdr agent send <label> "Read .ccu/delegations/<id>/REJECTION-<n>.md and address it"
herdr pane send-keys <pane_id> Enter
```

The file makes rejection **idempotent**: if the pane died, spawn a fresh
same-host peer at the repo root with the original bootstrap plus “read the
latest `REJECTION-<n>.md` before continuing.” Ledger increments the rejection
count. Do not use an ambiguous global “resume last session” command.

## Git Workflow (Shared Tree, Hardened)

Peers work in one tree on the current branch. Pathspec commits don't touch each other's staged files; the real hazard is **test isolation** — one peer's half-written module turning another's suite red. Four rules (all carried by the brief template):

1. **Commit retry:** 3 attempts, 200/400/800ms backoff, on ref-lock contention. **`git add -A` is forbidden** — stage named files only, commit with a pathspec: `git commit -m "..." -- <paths>`.
2. **Gate split:** peers run **scoped gates only** — their own test paths (the bead's `## Files` `Test:` entries), lint on their own paths, the bead's acceptance commands. The **coordinator owns the full-suite gate**. Peers never block on global green.
3. **Not-yours rule:** *a failing test outside your file scope is not yours — record it in RESULT.md and continue; do NOT fix it.*
4. **Provenance trailers:** every commit carries `Delegation: <id>` and `Bead: <id>`; the coordinator records SHAs in the ledger.

**Single-worktree exception** (the standing no-worktrees default stands; this is its one documented exception): a delegation that is long-running *and* high-risk (major refactor, dependency upgrade, schema migration) or touches inherently repo-global files (lockfiles, `tsconfig.json`, CI config) may run as the **only** worktree peer: `git worktree add .worktrees/<id> -b hdr/<id>`, gates green in the worktree, coordinator merges `--no-ff` and **re-runs full gates in the main tree** before `verified`. Never multiple worktree peers at once — `.ccu/` and `.beads/` don't fork safely.

## Tiered Execution for Complex Beads

**Trigger:** the bead is file-beads Tier 3, **or** has a populated `## Interfaces` block with downstream consumers, **or** touches ≥ 5 files. Everything else runs the single-peer flow above.

Tiered runs go **Architect → Coder → Reviewer** — a temporal handoff, two panes per delegation maximum, sequential. Full protocol (split test ownership, host-specific permission enforcement, assertion-line rejection rule, change-request routing, host-native Reviewer subagent): [references/tiered-execution.md](references/tiered-execution.md).

## Error Handling and Recovery

**Evidence precedence, for all reconciliation:**

```
bead status  >  RESULT.md  >  git log  >  LEDGER.md  >  herdr agent list
└── evidence ──────────────────────┘    └── caches ──────────────────┘
```

| Failure | Detection | Response |
|---|---|---|
| Not at repo root / herdr missing / socket dead | Prerequisite gate | Refuse with instructions |
| Peer pane dies mid-task | `herdr agent list` lacks the label | Reconcile by evidence precedence: `RESULT.md` or closed bead → verify as done; else start a fresh same-host peer at the repo root, pointing it to the brief + latest rejection file |
| Herdr state misfire / wait timeout | `--timeout` expiry, no transition | Poll `RESULT.md` + `git log`; `herdr agent read` to peek |
| Coordinator session dies | — | Ledger + `.ccu/delegations/` + beads are the recovery state. On restart, `/hdr-orchestrator` re-reads the ledger and reconciles each in-flight row by evidence precedence (same philosophy as `/t:recover`). No locks to clean up |
| Peer blocked, question not answerable | `--status blocked` wait + agent read | Escalate to the user; ledger stays `blocked` |
| Injection lost (pane died right after send) | Next wait/reconcile pass | `REJECTION-<n>.md` is durable; respawn re-reads it |
| Foreign edits in a peer's scope | Foreign-edit check at verification | Report to the user with the offending commits/paths; delegation held, never auto-overwritten |
| Herdr version drift (pre-1.0) | `herdr --version` logged in ledger header | CLI errors → escalate, don't guess flags |

## Test Scenarios (dry-run checklist — no test scripts in v1)

1. **Happy path E2E:** delegate a trivial task → bead + thin brief, peer spawns via `agent start`, `RESULT.md` lands, verification (incl. full-suite gate + trailers) passes, ledger `verified`.
2. **Parallel pair:** two disjoint-scope delegations run in parallel; an overlapping pair correctly queues; readable labels appear in the Herdr sidebar.
3. **Rejection path:** a production-type task that leaves a `TODO` stub → smell detected, `REJECTION-1.md` written, injection lands, peer fixes, re-verifies. A demo-type task with mocks passes untouched.
4. **Tiered path:** a Tier-3 bead runs Architect → Coder → Reviewer; the Coder's attempt to edit a contract-test assertion is rejected; a change request round-trips through the Architect.
5. **Recovery:** kill the coordinator mid-flight → restart reconciles by evidence precedence.
6. **Degraded Herdr:** wait on a killed pane → timeout → file-polling fallback engages.

## Red Flags — STOP

- **The coordinator editing code** → never; write a brief and delegate, or tell the user it's out of role
- **Handing coordination off to another skill or agent workflow** → never; this skill owns dispatch, monitoring, and verification end to end — epics included (dispatch per ready bead, graph-driven)
- **A brief restating bead content** (`## Files`, acceptance criteria, narrative) in a bead repo → bug; delete and fix the bead
- **Dispatching overlapping `## Files` scopes concurrently** → queue the second; admission control IS the lock
- **More than 3 concurrent peers** → shared tree + build/test env starts thrashing
- **Mixing `claude` and `codex` peers in one run** → recovery and permission
  semantics become ambiguous; choose one host and record it in the ledger
- **A wait without `--timeout`** → can hang forever on a dead pane; files are the fallback, give them a chance to speak
- **Trusting `herdr agent list` or the ledger over `RESULT.md`/git/bead** → evidence precedence exists for exactly this
- **Rejecting via keystrokes before writing `REJECTION-<n>.md`** → a dead pane eats the rejection; the file makes it durable
- **Accepting a result whose commits lack `Delegation:`/`Bead:` trailers, drift out of scope, or smell (work-type aware)** → reject with evidence
- **Peers running the full suite, or `git add -A`** → gate split and pathspec discipline exist to keep parallel peers out of each other's way
- **Answering a blocked peer's plan/scope/irreversible question yourself** → escalate to the user
- **Two worktree peers at once** → `.ccu/` and `.beads/` don't fork safely; one, only per the documented exception

## Quick Reference

| Step | Action |
|---|---|
| Gate | repo root + `command -v herdr` + `herdr agent list` + selected peer CLI — else refuse |
| Init | gitignore entries, `.ccu/hdr/LEDGER.md` (peer host/CLI + herdr version + start), `.ccu/delegations/`; label the coordinator pane when Herdr-managed, otherwise record `external` |
| Define | bead (`br create` if ad-hoc) + thin `BRIEF.md` (work type, authority, completion) |
| Admit | `## Files` disjoint from running scopes, cap 3 — else `queued` |
| Spawn | `herdr agent start <bead-id> --cwd <root> -- <claude\|codex> "<bootstrap>"` → `running` |
| Monitor | `herdr agent wait <label> --status idle\|blocked --timeout <ms>`; timeout → poll `RESULT.md` + git |
| Verify | [references/verification.md](references/verification.md) — evidence only, full suite here |
| Reject | `REJECTION-<n>.md` first, then `agent send` + `pane send-keys Enter` |
| Tiered | Tier-3 / populated `## Interfaces` / ≥5 files → [references/tiered-execution.md](references/tiered-execution.md) |
| Recover | reconcile every in-flight ledger row by evidence precedence |
| Report | per-delegation ✓/✗ to the user; ledger `verified` |
