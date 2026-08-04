# Verify-Then-Report Checklist

Run this when a delegation signals completion (idle + `RESULT.md` present). **Verify from evidence — never from the pane's screen, never from the peer's self-report alone.** Every check is mechanical; judgment calls escalate to the user.

Inputs you need: the delegation id, its bead id, the bead's `## Files` scope (`br show <bead>`), the work type from `BRIEF.md`, and the dispatch timestamp from the ledger.

## 1. RESULT.md complete per template

`.ccu/delegations/<id>/RESULT.md` exists and fills every section of [../templates/result.md](../templates/result.md): status, commit SHAs, gates run with outcomes, deviations, out-of-scope failures observed, follow-ups. A missing section = incomplete report = reject.

## 2. Commits exist, with provenance trailers

```bash
git log --format="%H %s" --grep="Delegation: <id>" --all-match
git show -s --format="%(trailers)" <sha>       # for each claimed SHA
```

Every commit SHA claimed in `RESULT.md` must exist in `git log` and carry **both** trailers:

```
Delegation: <id>
Bead: <bead-id>
```

A claimed SHA that doesn't exist, or a commit missing a trailer, fails. Record verified SHAs in the ledger.

## 3. Scope check

```bash
git show <sha> --stat --format=""               # file list per commit
```

Every touched file must be inside the bead's `## Files` block (Create/Modify/Test paths). Files outside it mean the peer drifted or swept up someone else's staged work — reject either way. (Worktree-exception delegations: run this on the merge's combined diff.)

## 4. Smell grep — work-type aware

The brief's work type decides what counts:

| Work type | Rule |
|---|---|
| `production` | `mock`/`stub`/`TODO`/`FIXME`/`not implemented`/`placeholder` in **non-test** changed files = fail |
| `demo`, `mockup` | **Exempt** — mocks and stubs are the point; skip this check entirely |
| any | Mocks in **test files** (`*.test.*`, `*.spec.*`, `__tests__/`, `tests/`) never count, anywhere |

```bash
git show <sha> -p -- . ':(exclude)*test*' ':(exclude)*spec*' \
  | grep -inE '(mock|stub|placeholder|not.implemented|TODO|FIXME|test\.skip|it\.skip)' | head -20
```

Treat hits as candidates, not verdicts — read the surrounding diff line before failing (a variable named `stubbornRetries` is not a stub). Real hits in production code = reject with the exact lines as evidence.

## 5. Foreign-edit check

The lock-free model cannot *prevent* an outside actor (human editor, stray session) touching a peer's scope — this check *detects* it:

```bash
git log --since="<dispatch timestamp>" --format="%H %s" -- <scope paths>
git status --porcelain -- <scope paths>
```

- Every commit in the window must be this peer's (trailer-checked in step 2).
- `git status` on the scope must be clean (no uncommitted leftovers).

A foreign commit or dirty file = **hold the delegation and report to the user** with the offending commits/paths. Never auto-overwrite; never silently accept.

## 6. Full-suite gate (coordinator-owned)

Peers run scoped gates only; **you** run the repo's full test/lint/build, serially, at verification:

- Run the project's standard full gates (whatever CLAUDE.md/package scripts define).
- **Skip suites flagged `expected-red` in the ledger** by an in-flight tiered delegation (an Architect's contract tests are red by design until the Coder lands) — and say so in the report.
- A full-suite failure **inside** the peer's scope = reject. A failure **outside** every active scope = pre-existing or foreign; investigate before blaming the peer (check `RESULT.md`'s "out-of-scope failures observed" — a good peer already recorded it).

## 7. Bead closed

```bash
br show <bead-id>    # status must be closed/done, with a close reason pointing at RESULT.md
```

Peer forgot to close but everything else passes → that alone is a trivial rejection ("close your bead") — do not close it on the peer's behalf; the close is part of the peer's completion contract.

## Outcomes

**All pass** → ledger `verified`; report to the user with per-item ✓/✗ (never collapse to a one-liner); dispatch anything `queued` on this scope.

**Any fail** → durable rejection:

1. Write `.ccu/delegations/<id>/REJECTION-<n>.md` per [../templates/rejection.md](../templates/rejection.md) — what failed, the evidence (exact SHAs, paths, grep lines), what to redo.
2. Then inject: `herdr agent send <label> "Read .ccu/delegations/<id>/REJECTION-<n>.md and address it"` + `herdr pane send-keys <pane_id> Enter`.
3. Ledger: status `rejected`, rejection count +1. If the pane is gone, start a
   fresh same-host peer at the repo root, pointing it to the brief and latest
   rejection file; see [host-adapters.md](host-adapters.md).

Three rejections on one delegation = stop and escalate to the user with the full history; don't loop forever.

## Tiered-run extras

Tiered delegations (Architect → Coder → Reviewer) add two checks at the Coder's verification — see [tiered-execution.md](tiered-execution.md):

- **Assertion-line rejection rule:** any Coder diff to an Architect-owned test file that changes a line containing `expect(`, `assert`, or `toBe` = reject. Mechanical breakage fixes (imports, fixtures) on non-assertion lines are allowed.
- **Reviewer verdict:** the host-native Reviewer subagent's findings feed this
  same reject path.
