# Admission Control

Run admission before every spawn. Treat the dependency graph and the active resource set as live state.

## Resource declaration

Require this block on every bead:

```markdown
## Coordination Resources
- Database: `app_test` (`read-write`)
- Ports: `none`
- Lockfiles: `pnpm-lock.yaml`
- Other: `none`
- Expected red: `@app/api typecheck`, `tests/session.integration.test.ts`
```

Use `none` for an empty axis. List every database by stable local identifier and mark it `read-write` or `schema-mutating`. List exact ports, lockfile paths, and named exclusive resources. Record expected red as an exact package, suite, or test set; use `none` when the bead expects no red gates.

Backfill a missing or ambiguous block before claiming the bead. Do not infer a declaration silently.

## Conflict matrix

| Axis | Conflict |
| --- | --- |
| Planned files | Paths overlap, or one path contains the other |
| Database | The same database appears on both beads and either access mode is `schema-mutating` |
| Ports | The same port appears on both beads |
| Lockfiles | The same lockfile path appears on both beads |
| Other | The same named exclusive resource appears on both beads |

Ordinary `read-write` access to the same database may coexist. Project rules may impose stricter isolation. Conflicting beads run sequentially; when they also lack a dependency edge, add one with `br dep add`.

A worker that discovers an undeclared exclusive resource mid-bead pauses before using it and reports; update the bead's declaration and the active resource picture before rescheduling.
