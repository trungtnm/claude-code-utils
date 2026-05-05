# Architectural Decisions

---
## D001 — Keep `t:` command prefix, don't migrate to skills
- **date:** 2026-03-19
- **context:** Anthropic docs say custom commands are "merged into skills" (legacy). Investigated whether to migrate all `t:*.md` commands to `skills/*/SKILL.md` format.
- **decision:** Keep the `t:` command format. Do not migrate.
- **rationale:** Three practical benefits outweigh the "legacy" label: (1) `disable-model-invocation` by default — commands never auto-trigger, ensuring explicit user control over actions like commit, handoff, done; (2) `t:` prefix is a namespace that prevents collisions with other plugins' skills; (3) fast to type and visually groups all action commands in autocomplete. Skills with `disable-model-invocation: true` would be functionally identical but add migration cost with zero workflow improvement.
- **alternatives:** (A) Migrate all to skills with `disable-model-invocation: true` — same behavior, cosmetic change only. (B) Migrate only daily workflow commands — partial inconsistency. Both rejected because the current setup works and the `t:` convention is a feature, not a bug.
---
## D002 — Unify planning + brainstorming artifacts under `.ccu/artifacts/<date>-<epic>-<slug>/`
- **date:** 2026-05-05
- **context:** Planning skill writes to `history/<date>-<epic>-<slug>/` (discovery.md, approach.md, execution-plan.md). Brainstorming writes to `docs/plans/YYYY-MM-DD-<topic>-design.md`. Two separate paths, two separate conventions, no shared lifecycle view per feature.
- **decision:** All feature-lifecycle artifacts live under `.ccu/artifacts/<date>-<epic-id>-<slug>/` with four standard files: `design.md` (brainstorming), `discovery.md` + `approach.md` + `execution-plan.md` (planning). Brainstorming uses `<date>-draft-<slug>/` placeholder; planning Phase 4 renames the directory to use the real epic ID.
- **rationale:** Per-feature subdirs give a one-row-per-feature view in `ls .ccu/artifacts/` and co-locate the full lifecycle (design → discovery → approach → execution plan). `.ccu/` is already the established staging surface (managed by `session-state` skill alongside `DECISIONS.md`, `EVIDENCE.md`, `HANDOFF.md`), so adding `artifacts/` here keeps all session continuity in one place.
- **alternatives:** (A) Flat files prefixed by date+slug — easier to `ls` but loses per-feature grouping and clutters as features × phases grow. (B) Split: `.ccu/artifacts/designs/` for brainstorming, `.ccu/artifacts/<dir>/` for planning — avoids the rename dance but separates design.md from its planning siblings. Rejected in favor of co-location, accepting the one-time `mv` at Phase 4.
---
## D003 — `.ccu/artifacts/` is gitignored
- **date:** 2026-05-05
- **context:** Most `.ccu/` files are committed (DECISIONS.md, EVIDENCE.md, HANDOFF.md, SESSION.md, CHECKPOINT.md). CAPTURES.md and PRIME-CACHE.md are gitignored as ephemeral working notes.
- **decision:** Add `.ccu/artifacts/` to `.gitignore`. Feature plans are local working artifacts, not part of the project's permanent record.
- **rationale:** Plans are per-developer scratchpads — the durable record of *why* a feature exists belongs in commit messages, DECISIONS.md, and beads (which sync via JSONL). Committing every discovery.md and execution-plan.md would clutter history without adding signal that isn't already captured elsewhere. Also avoids merge conflicts when two developers plan in parallel.
- **alternatives:** (A) Commit artifacts alongside DECISIONS.md — symmetric with other `.ccu/` files but conflates ephemeral planning state with permanent decisions. (B) Commit only execution-plan.md (the orchestrator input) — partial commit creates confusion about which files are tracked. Rejected; full gitignore is cleaner.
---
## D004 — Remove SPIKE phase from planning skill, keep risk classification as annotation
- **date:** 2026-05-05
- **context:** Planning skill's Phase 3 (Verification) creates spike beads for HIGH-risk items, runs them via parallel `Task()` calls, writes results to `.spikes/<dir>/`, then aggregates learnings back into `approach.md`. Phase 2 produces LOW/MED/HIGH risk ratings that *trigger* Phase 3.
- **decision:** Delete Phase 3 entirely — no more spike beads, no `.spikes/` directory, no spike template. Keep Phase 2's risk classification (LOW/MED/HIGH) as an annotation in `approach.md` and bead descriptions. HIGH-risk beads get a `⚠ HIGH RISK: <reason>` note telling the worker to investigate before coding, but no separate verification phase.
- **rationale:** Spike beads add a phase before any productive work begins, and in practice the user has not been running them. Removing Phase 3 simplifies the pipeline (8 phases → 7) and matches actual usage. Risk ratings remain useful as a "this is unfamiliar territory" signal for workers, even without a dedicated verification phase. Workers can investigate inline rather than via a separate bead.
- **alternatives:** (A) Remove risk classification entirely — cleaner but loses the novelty signal. (B) Repurpose risk as "complexity" (effort estimation) — useful for prioritization but loses what risk was capturing. Rejected; risk-as-annotation preserves the signal at zero process cost.
---
## D005 — Brainstorming does not git-commit; planning artifacts not committed at all
- **date:** 2026-05-05
- **context:** Brainstorming skill currently runs `git commit` on the design doc as its terminal step. With artifacts moving to `.ccu/artifacts/<date>-draft-<slug>/` and the directory renamed later by planning, auto-committing creates `git mv` churn.
- **decision:** Remove all `git commit` instructions from brainstorming. Since `.ccu/artifacts/` is gitignored (D003), no commits happen anywhere — artifacts are pure local working files.
- **rationale:** Consistent with D003 (gitignored). Brainstorming's terminal deliverable is the design doc on disk, not in git history. Planning's terminal deliverable is the execution-plan.md on disk, consumed by the orchestrator. Neither needs to be in git for the workflow to function.
- **alternatives:** (A) Brainstorming commits draft dir, planning commits the rename — two commits per feature start, history pollution. (B) Use a non-`draft-` placeholder so the dir name doesn't change — loses the at-a-glance epic-ID-in-`ls` benefit. Rejected; gitignored + no commits is simplest.
---
## D006 — Full sweep migration; daily-learnings excluded
- **date:** 2026-05-05
- **context:** 10 files reference the old `history/`, `docs/plans/`, or `.spikes/` paths. `daily-learnings/SKILL.md` writes daily digests to `history/learnings-YYYY-MM-DD.md`, but the skill itself is being removed in separate work.
- **decision:** Update all 9 files in scope (planning, brainstorming, file-beads, recipe, orchestrator, worker.md, plus templates). Skip `daily-learnings/SKILL.md` entirely — its `history/` references will be removed when the skill is deleted.
- **rationale:** Half-migrations leave the orchestrator and workers reading from old paths, breaking the brainstorming → planning → orchestration → worker chain. Touching only SKILL.md files would be smaller but would create silent breakage. Daily-learnings is excluded because path migration on a soon-to-be-deleted skill is wasted work.
- **alternatives:** (A) Just SKILL.md files — leaves dangling references in templates and downstream skills. (B) Include daily-learnings — adds churn to a file slated for deletion. Rejected; full sweep minus daily-learnings is the right scope.
