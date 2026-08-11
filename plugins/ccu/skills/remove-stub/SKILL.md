---
name: remove-stub
description: Replace all stubs, placeholders, mocks, and TODO markers with complete working code
---

Find and replace ALL stubs, placeholders, mocks, TODO markers, and incomplete implementations in the codebase with fully fleshed out, working, correct, performant, idiomatic code. Use extended thinking to reason through each replacement carefully.

## What counts as a stub

- `// TODO`, `// FIXME`, `// HACK`, `// PLACEHOLDER`, `// STUB` comments
- Functions that return hardcoded/dummy values instead of real logic
- `throw new Error("Not implemented")` or `pass` placeholders
- Mock data used where real data fetching/processing should be
- Empty or skeleton function/method bodies
- `console.log("TODO")` or equivalent placeholder logging
- Commented-out code blocks with "replace this" notes
- Hardcoded values that should be computed or configured
- Fake/sample data standing in for real implementations
- Any pattern that says "fill this in later" in any form

## Steps

1. **Scan the codebase** -- Search exhaustively for stubs across all source files. Use grep for TODO, FIXME, HACK, STUB, PLACEHOLDER, "not implemented", mock, dummy, fake, hardcoded, sample, and similar markers. Also read recently changed files for incomplete implementations that lack marker comments.

2. **Inventory every stub** -- List every stub found with its file, line number, and what it's supposed to do. Group related stubs together. Present this inventory to the user before proceeding.

3. **Understand the intended behavior** -- For each stub, read surrounding code, tests, types, interfaces, and any referenced beads/issues to understand what the real implementation should do. If a bead exists for the work, follow its specification exactly.

4. **Implement each replacement** -- Replace every stub with complete, production-quality code that:
   - Fully implements the intended behavior
   - Follows the patterns and conventions of the surrounding codebase
   - Is performant and avoids unnecessary allocations or computations
   - Handles edge cases and errors properly
   - Is idiomatic for the language and framework in use
   - Passes any existing tests and type checks

5. **Verify replacements** -- Run tests, type checks, and linting after replacements. Confirm no stub markers remain. Ensure no regressions were introduced.

## Rules

- **No stub left behind** -- Every single stub, placeholder, and mock must be addressed. If a stub cannot be replaced because requirements are unclear, flag it explicitly to the user rather than silently skipping it.
- **No new stubs** -- Do not introduce new TODOs, placeholders, or incomplete code while replacing existing ones.
- **Real implementations only** -- Every replacement must be working, tested code. Do not replace one stub with another stub.
- **Minimal blast radius** -- Replace stubs in place. Do not refactor surrounding code unless necessary for the replacement to work.
- **Follow the beads** -- If beads/issues exist that describe the intended behavior, implement exactly what they specify.
