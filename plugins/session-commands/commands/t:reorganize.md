**Target directory: `$ARGUMENTS`**

We really have WAY too many code files scattered inside `$ARGUMENTS` with no rhyme or reason to the structure and location of code files; I feel like we could make things a lot more organized, logical, intuitive, etc. by reorganizing these into a nice, sensible folder structure, although I don't want something that has too many levels of nesting; basically, we should at least start out with making "no brainer" type changes to the folder structure, like putting all the "x" functionality-related code files into an "x" folder (and perhaps that inside of a data_sources folder which might also contain a "y" folder, etc.).

Before making any of these changes, I really need you to take the time to explore and read ALL of the many, many files in that folder and understand what they do, how they fit together, which code files import which others, how they interact in functional ways, etc., and then propose a reorganization plan in a new document called PROPOSED_CODE_FILE_REORGANIZATION_PLAN.md so I can review it before doing anything; this plan should include not just your detailed reorganization plan but the super-detailed rationale and justification for your proposed file/folder structure and why you think it's optimal for aiding any developer or coding agent working on this project to immediately and intuitively understand the project structure and where to look for things, etc.

I'm also open to merging/consolidating/splitting individual code files; if we have multiple small related code files that you think should be combined into a single code file, explain why. If you think any particular code files are WAY too big and really should be refactored into several smaller code files, then explain that too and your proposed strategy for how to restructure them.

Always keep in mind, and track in this plan document, changes you will need to make to any calling code to properly reflect the new folder structure and file structure so that we don't break anything. I don't want to discover after you do all this that nothing works anymore and we have to do a massive slog to get anything running again properly.

## Constraints

- **No excessive nesting** — Aim for flat-ish structure. 2-3 levels max under the target directory.
- **Start with no-brainers** — Group obviously related files first (e.g., all "X" functionality into an "x/" folder, perhaps inside a "data_sources/" parent alongside "y/").
- **Don't break anything** — Track every import path change needed so the codebase keeps working after reorganization.

## Steps

1. **Deep exploration first** — Read ALL files in `$ARGUMENTS` (and any other relevant directories). Understand:
   - What each file does and its responsibility
   - Which files import which others (build a dependency map)
   - How files interact functionally (shared types, data flow, event handling)
   - Which files are tightly coupled vs. loosely related
   - File sizes — identify candidates for splitting or merging

2. **Identify natural groupings** — Based on your exploration, find clusters:
   - Files that serve the same feature or domain
   - Files that share a common abstraction layer (e.g., all API clients, all data models, all utilities)
   - Files that are always changed together (high co-change frequency)
   - Tiny related files that should be consolidated into one
   - Oversized files that should be split

3. **Draft a reorganization plan** — Create `PROPOSED_CODE_FILE_REORGANIZATION_PLAN.md` at the project root containing:

   ### a. Current State Analysis
   - Complete inventory of all files with brief descriptions
   - Dependency graph (which files import which)
   - Pain points in current structure

   ### b. Proposed New Structure
   - Full directory tree showing where every file moves
   - For each folder: its purpose and what belongs there
   - Any files being merged (with rationale)
   - Any files being split (with rationale and proposed split strategy)

   ### c. Rationale & Justification
   - Why this structure is optimal for developer/agent intuition
   - Design principles applied (colocation, separation of concerns, discoverability)
   - Trade-offs considered and why you chose this approach

   ### d. Import Path Migration Checklist
   - Every file that imports a moved file, with old and new import paths
   - Config files that reference paths (tsconfig, package.json, etc.)
   - Test files that need path updates
   - Any dynamic imports or path-based references

   ### e. Execution Order
   - Recommended sequence of moves to minimize breakage during migration
   - Which moves are independent (can be done in parallel) vs. sequential

4. **Stop and wait for review** — Do NOT execute any file moves. Present the plan and wait for user approval.

## Rules

- **Read everything before proposing anything** — No skimming. You need full understanding of the codebase to propose good structure.
- **Preserve working state** — The plan must account for every import, every reference, every config path. Nothing should break.
- **Justify every move** — If you can't articulate why a file belongs in a specific folder, don't move it.
- **Consolidation candidates** — If multiple small files (<50 lines each) serve closely related purposes, propose merging them. Explain the combined file's responsibility.
- **Splitting candidates** — If any file exceeds ~400 lines and has clearly separable concerns, propose splitting it. Define the responsibility boundary.
- **Think about discoverability** — A new developer or coding agent should be able to look at the folder structure and immediately understand where to find things and where to put new code.
