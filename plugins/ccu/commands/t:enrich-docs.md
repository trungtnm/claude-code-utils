---
description: Find undocumented functionality and add comprehensive narrative documentation for it
argument-hint: "[area or path to focus on]"
---

Find undocumented or under-documented functionality in the project and create comprehensive, narrative documentation for it. This is incremental — add NEW documentation, don't replace existing docs.

**Scope: `$ARGUMENTS`** — if an area, path, or subsystem is named above, restrict the gap analysis to it. Otherwise sweep the whole project.

**Prose style is owned by the `tech-doc` skill.** Read [`plugins/ccu/skills/tech-doc/SKILL.md`](../skills/tech-doc/SKILL.md) before writing a single sentence and follow it for every sentence you write here. It defines the banned patterns (history, process narration, AI voice), the sentence-level rules, and the per-doc-type structure. This command owns *what* to document; that skill owns *how it reads*. Delegate to it with `doc-type: module` (or `api`/`design`, whichever fits the gap) and `constraints: add only, never delete existing docs`.

## Steps

1. **Locate the docs** — Find where documentation lives in the project: a `docs/` folder, markdown files, a documentation site, or inline docs. Understand the current structure and organization.

2. **Inventory existing documentation** — Scan all documentation files (`.md`, `.mdx`, `.rst`, etc.). Build a mental map of what topics, features, APIs, and concepts are already covered and how thoroughly.

3. **Inventory the actual codebase** — Explore the source code: public APIs, exported functions, CLI commands, configuration options, hooks, plugins, components, utilities, data models, workflows, and architectural patterns. Understand what the project actually does.

4. **Gap analysis** — Compare the two inventories. Identify:
   - Features/modules with **zero documentation**
   - Features with **stub or shallow docs** (just a name or one-liner, no real explanation)
   - **Architectural concepts** that exist in code but aren't explained anywhere
   - **Workflows and patterns** a contributor would need to understand but can't learn from current docs
   - **Configuration and extension points** that are undocumented

5. **Prioritize** — Rank gaps by importance: core functionality and common workflows first, edge cases and internals later.

6. **Write the documentation** — For each gap, create or expand doc pages with:
   - **Narrative explanation** — What it does, why it exists, how it fits into the bigger picture. Write for a developer who is new to the project.
   - **How it's organized** — Where the relevant code lives, how modules relate to each other.
   - **Practical examples** — Real usage scenarios, code snippets, common patterns.
   - **Gotchas and tips** — Non-obvious behavior, common mistakes, best practices.
   - Use headings, code blocks, tables, and diagrams (mermaid) where they aid understanding.

7. **Wire into navigation** — If the project has a sidebar, nav config, or table of contents, add new pages so they're discoverable. Place them in logical categories.

## Rules

- **Incremental only** — Never delete, rewrite, or restructure existing documentation. Only add.
- **Follow `tech-doc` for all prose** — it is authoritative for voice, banned phrasing, and structure. In particular its "No history" rule replaces any changelog-style framing here: no "we added X", "now supports Y", "new in this version". Run its checklist before you finish.
- **Explain, don't only enumerate** — a dump of method signatures is not documentation. Write the reference tables first, then prose for the behaviour the tables don't reveal (`tech-doc` Procedure, steps 3–4).
- **Cover new commands, options, and features exhaustively** — During the codebase inventory, explicitly hunt for commands, flags, CLI subcommands, configuration keys, environment variables, hooks, skills, plugins, extension points, and public APIs that do not appear in existing docs. Missing surface area is the primary reason docs drift — document every one you find.
- **Match existing style** — Follow the tone, formatting, and conventions already used in the existing docs.
- **Be exhaustive but organized** — Cover everything you find, but group related topics into coherent pages rather than one giant page.
- **Keep it pragmatic** — Focus on what a developer actually needs to know to use and contribute to the project. Skip trivial internals that don't affect usage.
