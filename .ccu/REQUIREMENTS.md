# Requirements

---

## R001 — Migrate planning + brainstorming artifacts to `.ccu/artifacts/`

- **date:** 2026-05-05
- **status:** active
- **scope:** plugins/skills/{planning, brainstorming, file-beads, recipe, orchestrator}/SKILL.md, plugins/skills/planning/templates/{approach,execution-plan,spike}.md, plugins/agents/worker.md
- **excluded:** plugins/skills/daily-learnings/SKILL.md (the skill itself is being removed in separate work; do not migrate its `history/` references)

### Requirements

- **REQ-1.1** Replace `history/<date>-<epic-id>-<slug>/` with `.ccu/artifacts/<date>-<epic-id>-<slug>/` everywhere in planning skill and templates.
- **REQ-1.2** Replace `docs/plans/YYYY-MM-DD-<topic>-design.md` with `.ccu/artifacts/<date>-draft-<slug>/design.md` in brainstorming skill.
- **REQ-1.3** Per-feature subdirectory layout — each feature owns one directory containing `design.md`, `discovery.md`, `approach.md`, `execution-plan.md`.
- **REQ-1.4** Brainstorming creates the directory with `<date>-draft-<slug>/` placeholder. Planning Phase 4 renames it to `<date>-<epic-id>-<slug>/` once the epic ID is assigned by `br create`.
- **REQ-1.5** Brainstorming MUST NOT run `git commit` on the design doc (current behavior). Removing this step also removes "Commit the design document to git" from brainstorming's checklist and process flow.
- **REQ-1.6** `.ccu/artifacts/` is gitignored — feature plans are local working artifacts, not committed history. Add to `.gitignore`.

### Spike removal

- **REQ-2.1** Delete `plugins/skills/planning/templates/spike.md` entirely.
- **REQ-2.2** Remove Phase 3 (Verification) from `plugins/skills/planning/SKILL.md`. Renumber phases: Discovery (1), Synthesis (2), Decomposition (3), Bead Review (4), Validation (5), Track Planning (6), Artifact Check (7).
- **REQ-2.3** Update Pipeline Overview ASCII diagram and phase table — drop the Verification row.
- **REQ-2.4** Remove `.spikes/<dir>/` from the Completion Gate checklist.
- **REQ-2.5** Remove spike-related red flags from "Red Flags - You Are About to Skip Steps" section.
- **REQ-2.6** Remove "Key Learnings (from Spikes)" section from `plugins/skills/planning/templates/execution-plan.md`.
- **REQ-2.7** Remove "Spike learnings embedded in description" and "Reference to .spikes/ code" requirements from Phase 4 (Decomposition). Replace the Stripe spike example with a non-spike example bead.
- **REQ-2.8** Keep risk classification (LOW/MED/HIGH) in Phase 2 (Synthesis) and `approach.md` template, but reframe HIGH-risk handling: instead of triggering spike beads, HIGH-risk items get a `⚠ HIGH RISK: <reason>` annotation in their bead description telling the worker to investigate before coding.

### Cross-skill consistency

- **REQ-3.1** Update `plugins/agents/worker.md` to read execution plans from `.ccu/artifacts/<dir>/execution-plan.md`.
- **REQ-3.2** Update `plugins/skills/orchestrator/SKILL.md` to read tracks from `.ccu/artifacts/<dir>/execution-plan.md`.
- **REQ-3.3** Update `plugins/skills/file-beads/SKILL.md` — remove any spike-bead references, keep only standard epic/issue/task creation.
- **REQ-3.4** Update `plugins/skills/recipe/SKILL.md` — adjust the brainstorming → planning chain to reflect that brainstorming no longer commits and the directory rename happens in planning.

### Out of scope

- **OUT-1** `~/.claude/skills/` mirror copies — not edited (they're plugin-install artifacts, regenerated on `claude plugin install`).
- **OUT-2** Migration of any pre-existing `history/` or `docs/plans/` content — none exists in this repo, so the migration is forward-only.
- **OUT-3** Removal of `daily-learnings` skill — separate work, tracked separately.
- **OUT-4** Updating the `session-state` skill schema docs to mention `artifacts/` — optional follow-up if the skill should advertise the new subdir.
