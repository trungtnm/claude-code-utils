---
name: gates
description: The check ladder for a code change — what an agent runs locally before committing a bead, at what scope and in what order, and how to handle a red result. The whole-repo suite belongs to CI, not to the agent. Use when an /auto session or a worker agent is about to verify a bead, or when deciding whether a failed check is yours to fix.
---

# Gates

This skill is the single authority for **which checks an agent runs, at what scope, in what order,
and what to do when one comes back red**. Other skills and agents cite it; they do not restate the
commands. ("Gate" here means a check on a code change. The ADR gate in [[tech-doc]] and
admission in [[orchestrator]] are unrelated uses of the word.)

Each stage of the ladder runs longer than the stage before it, and agent quota is finite. Stage 1
rejects the largest share of errors for the least time spent, which is why it runs first and why
stage 4 runs once.

| Consumer | Reaches this file by |
|---|---|
| [[auto]] | `[[gates]]` from its Verify step |
| `worker` agent | `Skill(skill: "ccu:gates")` — agents cite by invocation, not wikilink |
| `tester` agent | `Skill(skill: "ccu:gates")`, for the functional suite it owns |

## Verification scope

Behavior this repository owns. Not the framework's, not a dependency's, not the language's. A test
that only proves a library still works belongs to that library.

The narrowest correct scope is already written down: [[file-beads]] compiles a
`— verify: <command> → PASS` line into every acceptance criterion. Run what the bead names before
inventing a command.

## Command discovery

```bash
cat package.json 2>/dev/null | jq '.scripts | keys[]' 2>/dev/null
```

Map discovered scripts: `lint*` → Lint, `typecheck`/`tsc` → Types, `test*` → Tests, `build` →
Build. With no `package.json` or no matching script, use the project-specific commands in
`CLAUDE.md`. Skip any stage that has no corresponding command — do not invent one.

## The ladder

Cheapest first. Stop at the first red and deal with it; do not run the remaining stages to collect
a fuller list of failures.

| Stage | What | Scope | When |
|---|---|---|---|
| 1 | Lint, typecheck | Repo-wide | Every cycle |
| 2 | The bead's `— verify:` commands | The change | Every cycle |
| 3 | Related integration | The modules the change touches | Only when the change crosses a module boundary |
| 4 | `build`, then the full suite | Repo-wide | Once, at the last responsible moment |

Stage 2 with no `— verify:` command: select tests by diff rather than running the suite —
`jest --findRelatedTests <files>`, `vitest related <files>`, `pytest --lf`, or the project's
equivalent. A bead that named no verify command was filed incomplete; note it in a comment so the
gap is visible.

Stage 4 holds the two checks that run once, and "once" means a different moment for each:

- **`build` — once, before you complete the bead.** It is the only local check that catches a
  broken import across bead boundaries, which no diff-scoped test reaches. It runs at the end of
  the bead rather than inside the edit loop.
- **The full suite — once, before merge.** See [The CI boundary](#the-ci-boundary).

## Escalation

Stage 3 fires when the change crosses a boundary — a schema, a shared interface, an environment or
dependency change. It does not fire because a change felt significant.

E2E, race, load, and stress runs are deliberate. Reach for one when you have a specific question it
answers, and name that question. Authorship of functional, integration, and e2e tests belongs to
the `tester` agent; a coder writing them is doing another role's work.

## Concurrency

**Sequential means one test process at a time, not one agent at a time.**

Use the project's default runner invocation. Do not add `-j`, `--parallel`, or `--workers=N` to
finish sooner: parallel workers share ports, temp directories, and the test database, and the
failures they produce do not reproduce on re-run.

Agent-level concurrency is a different axis and this rule does not touch it. [[orchestrator]] caps
workers deliberately and serializes beads that conflict; [[auto]] peers self-schedule. When two
agents' runs collide on a port or a database, the bead is missing a `## Coordination Resources`
declaration — fix the bead rather than stop running agents in parallel.

## A red result

**Decide causality before you touch it.** In a shared tree, peers commit while you work, so a check
can fail on code you never edited. A failure your change caused is yours, even when the failing
file sits outside the bead's `## Files`. An independent failure is reported, not fixed, and never
charged to your bead. This is the runner's side of causality; the orchestrator applies the same
test as an auditor of a finished report, in
[verification.md](../orchestrator/references/verification.md).

Then:

1. **Read the output.** Re-running a check without reading why it failed adds no information.
2. **Fix the cause, once.** Type errors: fix the type. Lint: `--fix` where it applies, otherwise by
   hand. Test failures: fix the implementation, never the test.
3. **Re-run only the stage that failed.**
4. **Cap it.** After two targeted attempts, stop and report with the evidence. A third attempt
   without a new hypothesis is guessing.

Never weaken, skip, delete, or narrow a test to reach green. A test edited to accommodate broken
code removes the signal that the code is broken. A test that is itself wrong is a finding to
report, not a line to edit on the way past.

## The CI boundary

The full suite runs **once, before merge**, and CI owns that run. It is never a per-bead local run:
in a shared tree it fails on other agents' in-flight work, and it consumes the quota stages 1-3
exist to conserve.

Where a project has no CI, the full suite runs once at the end of the epic or session, and its
result is reported.

Never shape a local run to make CI green. Skipping a suite, narrowing a matrix, or pinning a flaky
test locally converts a failure now into a failure later, further from its cause.
