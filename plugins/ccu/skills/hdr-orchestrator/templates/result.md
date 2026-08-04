# RESULT.md Template

The peer's completion authority. The coordinator copies this file into `.ccu/delegations/<id>/RESULT-TEMPLATE.md` at dispatch; the peer fills it as `RESULT.md` — its **final act** (bead repos: followed only by `br close`). Every section is required; an empty section says "none" explicitly. Verification rejects a `RESULT.md` with missing sections.

```markdown
# Result: <YYYYMMDD>-<kebab-slug>

Status: <done | blocked>
Bead: <bead-id, or "none (non-bead repo)">

## Commits
<!-- Every commit you made, full SHA + subject. All carry the Delegation:/Bead: trailers. -->
- <sha> <subject>

## Gates run
<!-- Scoped gates only — exact command → outcome. The coordinator runs the full suite. -->
- `<command>` → <PASS | FAIL (why)>

## Deviations
<!-- Anything done differently than the bead/brief specified, and why. "None" if none. -->

## Out-of-scope failures observed
<!-- Failing tests/builds OUTSIDE your ## Files scope that you saw and did NOT touch
     (the not-yours rule). Name the test/file. "None" if none. -->

## Follow-ups
<!-- Work you noticed but correctly left alone: candidate beads, risks, TODOs for the
     coordinator to triage. "None" if none. -->
```

**If Status is `blocked`:** say what you are blocked on in Deviations, leave the bead open, and stop — the coordinator reads the pane and either answers or escalates. Do not guess your way past a blocker.
