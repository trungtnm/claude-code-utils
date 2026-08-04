# Delegation Brief Template

Two shapes. **Bead repo (`.beads/` exists): use Shape A — always.** The bead owns the work definition; a Shape-A brief containing a `## Files` block, acceptance criteria, or context narrative is a bug (delete it and fix the bead). **Non-bead repo: use Shape B** — the brief absorbs the work definition using the file-beads Tier-1 section shapes verbatim, so peers develop one reading habit.

Both shapes end with the same Git rules and Completion sections. Fill every `<placeholder>`; delete nothing else.

---

## Shape A — bead repo (thin pointer, ~15 lines)

```markdown
# Delegation <YYYYMMDD>-<kebab-slug>

Bead: <bead-id>   ← AUTHORITATIVE. Run `br show <bead-id>` and read it in full.
                    Its ## Files block is your hard edit boundary. Its acceptance
                    criteria are your gates. Nothing here overrides it.
Work type: <production | demo | mockup>
Authority: you may choose naming and internal structure. Escalate anything that
           changes ## Interfaces, adds a dependency, or needs files outside
           ## Files — do not decide it yourself; ask and wait.
Gates: the bead's acceptance criteria + scoped tests/lint on your paths only
       (the coordinator runs the full suite at verification — not you).

## Git rules
- Work in this tree, on the current branch. Stage named files only; commit with a
  pathspec: `git add <files> && git commit -m "..." -- <files>`. `git add -A` is
  FORBIDDEN. If the commit hits a ref lock, retry up to 3 times with 200/400/800ms
  backoff.
- Every commit message ends with two trailers:
  `Delegation: <YYYYMMDD>-<kebab-slug>` and `Bead: <bead-id>`.
- A failing test OUTSIDE your ## Files scope is not yours — record it in RESULT.md
  and continue; do NOT fix it.

## Completion
Your FINAL act, in order:
1. Write .ccu/delegations/<YYYYMMDD>-<kebab-slug>/RESULT.md per the template at
   .ccu/delegations/<YYYYMMDD>-<kebab-slug>/RESULT-TEMPLATE.md (the coordinator
   copies it there), filling every section.
2. `br close <bead-id> --reason "<one line> — see RESULT.md"`
```

---

## Shape B — non-bead repo (brief carries the full Tier-1 definition)

```markdown
# Delegation <YYYYMMDD>-<kebab-slug>

Work type: <production | demo | mockup>
Authority: you may choose naming and internal structure. Escalate anything that
           changes ## Interfaces, adds a dependency, or needs files outside
           ## Files — do not decide it yourself; ask and wait.

## Project Context
<1 sentence — why this task exists>

## Files
- Create: `<exact path>`
- Modify: `<exact path>` (<what changes>)
- Test:   `<exact path>`

## Interfaces
<!-- Include only when the task has consumers; exact signatures, per file-beads -->
- Consumes: `<exact signature>` — <where it comes from>
- Produces: `<exact signature>` — <who consumes it>

## Acceptance Criteria
- [ ] <criterion> — verify: `<exact command>` → <expected result>
- [ ] <criterion> — verify: `<exact command>` → <expected result>

Gates: the acceptance criteria above + scoped tests/lint on your paths only
       (the coordinator runs the full suite at verification — not you).

## Git rules
- Work in this tree, on the current branch. Stage named files only; commit with a
  pathspec: `git add <files> && git commit -m "..." -- <files>`. `git add -A` is
  FORBIDDEN. If the commit hits a ref lock, retry up to 3 times with 200/400/800ms
  backoff.
- Every commit message ends with the trailer:
  `Delegation: <YYYYMMDD>-<kebab-slug>`.
- A failing test OUTSIDE your ## Files scope is not yours — record it in RESULT.md
  and continue; do NOT fix it.

## Completion
Your FINAL act: write .ccu/delegations/<YYYYMMDD>-<kebab-slug>/RESULT.md per the
template the coordinator placed beside this brief, filling every section.
```
