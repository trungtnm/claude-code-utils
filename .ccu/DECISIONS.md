# Architectural Decisions

---
## D001 — Keep `t:` command prefix, don't migrate to skills
- **date:** 2026-03-19
- **context:** Anthropic docs say custom commands are "merged into skills" (legacy). Investigated whether to migrate all `t:*.md` commands to `skills/*/SKILL.md` format.
- **decision:** Keep the `t:` command format. Do not migrate.
- **rationale:** Three practical benefits outweigh the "legacy" label: (1) `disable-model-invocation` by default — commands never auto-trigger, ensuring explicit user control over actions like commit, handoff, done; (2) `t:` prefix is a namespace that prevents collisions with other plugins' skills; (3) fast to type and visually groups all action commands in autocomplete. Skills with `disable-model-invocation: true` would be functionally identical but add migration cost with zero workflow improvement.
- **alternatives:** (A) Migrate all to skills with `disable-model-invocation: true` — same behavior, cosmetic change only. (B) Migrate only daily workflow commands — partial inconsistency. Both rejected because the current setup works and the `t:` convention is a feature, not a bug.
