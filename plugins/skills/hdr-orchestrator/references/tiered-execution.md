# Tiered Execution: Architect → Coder → Reviewer

For beads too complex for a single peer. **Trigger — any one of:**

- the bead is file-beads **Tier 3** (high-risk template), or
- it has a **populated `## Interfaces` block with downstream consumers**, or
- it touches **≥ 5 files**.

Everything else runs the single-peer flow in SKILL.md. Tiered execution is a **temporal handoff, not a concurrency problem**: at most two panes per delegation (`<slug>-arch`, then `<slug>`), strictly sequential. The delegation dir gains `DESIGN.md` and `TESTPLAN.md`.

```
Architect (pane <slug>-arch)          Coder (pane <slug>)              Reviewer (Task() subagent)
DESIGN.md + TESTPLAN.md         →     implementation +            →    judges conformance AND
+ contract tests (land RED)           own unit tests,                  test adequacy; findings
                                      contract tests GREEN             feed normal verify/reject
        ↑  change requests: Coder → Architect pane directly (while it lives);
           else Coder reports blocked → coordinator forwards VERBATIM to a respawned Architect
```

## Stage 1: Architect

Spawn pane `<slug>-arch` with a brief scoped to design-only output:

- Designs the abstractions and interfaces; writes `DESIGN.md` + `TESTPLAN.md` into `.ccu/delegations/<id>/`.
- Writes the **behavioral/contract tests** against the bead's `## Interfaces` surface (e.g. `*.spec.ts` on the bead's `Test:` paths). **These land red — that is correct.** TDD evidence is preserved: the tests demonstrably exist before any implementation.
- Commits with the same `Delegation:`/`Bead:` trailers and pathspec discipline as any peer.

**Coordinator, on Architect completion:** verify its outputs (files exist, tests exist and are red for the right reason — missing implementation, not syntax errors), then mark the delegation **`expected-red` in the ledger**, listing the red suites — so the full-suite gate on *other* delegations doesn't misattribute these failures. Only then spawn the Coder.

## Stage 2: Coder

Spawn pane `<slug>` (the Architect pane may stay alive for change requests). The Coder implements until the contract tests pass.

**Split test ownership — this is how TDD survives delegation:**

| Tests | Owner | Coder may… |
|---|---|---|
| Contract tests (Architect's, on the `## Interfaces` surface) | Architect — **immutable to the Coder** | fix *non-assertion* mechanical breakage only: import paths, fixtures, setup. **Never a line containing `expect(` / `assert` / `toBe`** |
| Unit tests for internals | Coder | write and edit freely |

**Enforcement is a real mechanism, not just a prompt rule.** Spawn the Coder with a settings file denying edits to the Architect's test paths (verified available on the installed Claude Code — `claude --settings <file-or-json>`):

```bash
cat > .ccu/delegations/<id>/coder-settings.json <<'EOF'
{ "permissions": { "deny": [ "Edit(<architect test path glob>)", "Write(<architect test path glob>)" ] } }
EOF
herdr agent start <slug> --cwd <repo-root> -- \
  claude --settings .ccu/delegations/<id>/coder-settings.json "<bootstrap>"
```

The coordinator's **diff check is the backstop** (and the only line of defense if the flag is unavailable on some install): at verification, reject any Coder diff to an Architect test file that changes an assertion line — the **assertion-line rejection rule** in [verification.md](verification.md).

**Change requests.** If the Coder needs the abstractions, interfaces, use cases, or contract tests changed:

- **Architect pane alive** → the Coder asks it **directly**: `herdr agent send <slug>-arch "<request>"` + Enter. Peer-to-peer; the coordinator stays out of it.
- **Architect pane gone** → the Coder reports blocked; the coordinator **forwards the request verbatim to a (re)spawned Architect — without exploring the details itself**. The coordinator is a router here, not a reviewer of the request.
- Either way: the Architect's revised `DESIGN.md`/`TESTPLAN.md`/contract tests **re-verify** (Stage 1 checks, ledger `expected-red` updated) before the Coder resumes.

## Stage 3: Reviewer

Not a pane — a read-only, short-lived subagent inside the coordinator's session:

```
Task(subagent_type="reviewer", prompt="Review delegation <id>: read
.ccu/delegations/<id>/DESIGN.md and TESTPLAN.md, then the implementation commits
(git log --grep='Delegation: <id>'). Verify the implementation against the design
and test plan — and judge TEST ADEQUACY: what behavior does this suite NOT verify?
Report findings; do not edit anything.")
```

The Reviewer judges two things: **conformance** (does the implementation match `DESIGN.md`/`TESTPLAN.md`?) and **test adequacy** ("what behavior does this suite not verify?") — not just that existing tests pass. Its findings feed the normal verify/reject path in [verification.md](verification.md): significant gaps become a `REJECTION-<n>.md` for the Coder (or a forwarded change request to the Architect if the gap is in the contract surface).

## Completion

The tiered delegation reaches `verified` only when: contract tests green, Coder's unit tests green, assertion-line rule clean, Reviewer findings resolved, and the standard checklist ([verification.md](verification.md)) passes — at which point clear the ledger's `expected-red` flag and run the full-suite gate without the exemption.
