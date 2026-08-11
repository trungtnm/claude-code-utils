---
name: random-inspect
description: Randomly explore code files, trace execution flows, and fix any bugs found
---

Randomly explore code files in this project, deeply investigate their functionality, trace execution flows, and fix any bugs or issues you find. Use extended thinking.

## Steps

1. **Sample broadly** — Pick code files semi-randomly across different parts of the project. Don't just look at the most obvious entry points — dig into utilities, helpers, middleware, workers, and less-visited corners of the codebase.

2. **Deep-read each file** — For each file you pick, read it completely. Understand what it does, why it exists, and how it fits into the larger system.

3. **Trace connections** — Follow the imports and exports. Read the files that this file imports from, and find the files that import from it. Understand the full execution flow — where data comes from, how it's transformed, where it goes.

4. **Inspect with fresh eyes** — Once you understand the purpose and context, do a super careful, methodical, critical review looking for:
   - Obvious bugs, logic errors, off-by-one mistakes
   - Silly mistakes like typos, copy-paste errors, wrong variable names
   - Missing error handling at system boundaries
   - Race conditions or state management issues
   - Dead code, unreachable branches, impossible conditions
   - Inconsistencies with how similar patterns are handled elsewhere in the codebase
   - Security issues (injection, unsanitized input, exposed secrets)

5. **Check against project standards** — Read AGENTS.md, CLAUDE.md and any referenced best-practice guides. Verify the code conforms to them.

6. **Fix what you find** — For each issue, fix it directly. Keep fixes minimal and targeted — don't refactor working code just because you'd write it differently.

7. **Move on and repeat** — After finishing one cluster of files, pick another area and repeat. Cover at least 3-4 different areas of the codebase.

## Rules

- **Go deep, not wide** — It's better to thoroughly understand 10 files than to skim 50.
- **Follow the threads** — When you find something suspicious, trace it to its root before deciding if it's a real issue.
- **Fix real problems only** — Don't nitpick style or add unnecessary improvements. Focus on correctness, reliability, and security.
- **Respect existing patterns** — If the codebase has a convention, follow it even if you'd personally prefer something different.
