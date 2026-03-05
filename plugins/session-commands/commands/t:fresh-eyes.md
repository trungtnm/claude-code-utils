Re-read all code you wrote or modified in this session with fresh eyes. Look for bugs, errors, and problems. Fix anything you find.

## Steps

1. **Identify what changed** — Review the conversation history to find every file you created or modified in this session. List them all.

2. **Re-read each file completely** — Read every changed file from top to bottom. Do NOT skim or rely on your memory of what you wrote. Actually re-read the code as if seeing it for the first time.

3. **Inspect for problems** — At each file, look specifically for:
   - **Logic bugs** — off-by-one errors, wrong operator, inverted condition, missing edge case
   - **Typos and naming errors** — misspelled variable/function names, wrong import paths, copy-paste errors where a name wasn't updated
   - **Missing code** — forgotten return statements, unhandled branches, incomplete implementations, TODO placeholders left in
   - **Wrong assumptions** — code that assumes a value exists, assumes an array has elements, assumes a specific type without checking
   - **Integration errors** — function signatures that don't match their call sites, wrong argument order, mismatched types between modules
   - **State bugs** — mutations that shouldn't happen, stale closures, race conditions, missing cleanup
   - **Regressions** — existing functionality broken by the new changes

4. **Cross-check connections** — For every function you wrote that is called elsewhere (or calls something else), verify the interface matches on both sides. Check imports, exports, and type signatures.

5. **Fix what you find** — For each issue, fix it immediately. Keep fixes minimal and targeted.

6. **Report** — Summarize what you found and fixed. If everything was clean, say so.

## Rules

- **Actually re-read the code** — Do not skip this step. Use the Read tool on every changed file.
- **Fresh perspective** — Pretend you didn't write this code. Look at it as a reviewer would.
- **Fix immediately** — Don't just report issues. Fix them.
- **No scope creep** — Only fix actual bugs and errors. Don't refactor, improve style, or add features.
