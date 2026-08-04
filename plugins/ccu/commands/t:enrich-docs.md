---
description: Find undocumented functionality and add comprehensive narrative documentation for it
---

Find undocumented or under-documented functionality in the project and create comprehensive, narrative documentation for it. This is incremental — add NEW documentation, don't replace existing docs.

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
- **Narrative over reference** — Don't produce a dry dump of methods and parameters. Write prose that explains the "what", "why", and "how" so a new contributor can actually understand the system.
- **Frame everything as if it was always present** — Write documentation in the voice of timeless reference material. Do NOT write "we added X", "X is now Y", "recently introduced", "new in this version", "previously X did Y but now it does Z", or any other changelog-style phrasing. Describe the current state of the code as a standing fact.
- **Cover new commands, options, and features exhaustively** — During the codebase inventory, explicitly hunt for commands, flags, CLI subcommands, configuration keys, environment variables, hooks, skills, plugins, extension points, and public APIs that do not appear in existing docs. Missing surface area is the primary reason docs drift — document every one you find.
- **Match existing style** — Follow the tone, formatting, and conventions already used in the existing docs.
- **Be exhaustive but organized** — Cover everything you find, but group related topics into coherent pages rather than one giant page.
- **Keep it pragmatic** — Focus on what a developer actually needs to know to use and contribute to the project. Skip trivial internals that don't affect usage.
