---
description: Review, proofread, and refine filed Beads epics and issues
argument-hint: [optional: specific epic or issue IDs to focus on]
---

# Review and Refine Beads Issues

You are tasked with thoroughly reviewing, proofreading, and polishing the filed Beads epics and issues to ensure workers have a smooth implementation experience.

## Plan Space Philosophy

> **Changing a bead takes seconds. Changing implemented code takes hours.**

Review time is the highest-leverage investment in the entire pipeline. Every minute spent improving a bead description saves 10-60 minutes of worker confusion, false starts, and rework. Approach this review as the last checkpoint before expensive implementation begins.

## Step 1: Load Current Issues

First, get the current state:

```bash
br list --json
br ready --json
```

If specific IDs were provided (`$ARGUMENTS`), focus on those. Otherwise, review all issues.

## Step 2: Systematic Review Checklist

For EACH issue, verify:

### Clarity

- [ ] Written in English — title and description (quoted user-facing product copy is the only exception; rewrite any bead filed in another language)
- [ ] Title is action-oriented and specific
- [ ] Description is clear and unambiguous
- [ ] A developer unfamiliar with the codebase could understand the task
- [ ] No jargon without explanation

### Completeness

- [ ] Acceptance criteria are defined and testable
- [ ] Technical implementation hints are provided where helpful
- [ ] Relevant file paths or modules are mentioned
- [ ] Edge cases and error handling are considered

### Contracts (see [[file-beads]] Structured Blocks)

- [ ] `## Files` block exists with exact Create/Modify/Test paths — no prose hints
- [ ] `## Interfaces` block exists on every bead that has dependents or cross-bead consumers
- [ ] **Interface consistency:** every `Consumes` matches — verbatim, names and types — a `Produces` on an upstream bead or an existing symbol named in Technical notes (`rateLimit()` in one bead but `rateLimiter()` in its consumer is a plan bug; fix it now, not at integration)
- [ ] Every acceptance criterion names its verify command/test and expected result
- [ ] No "No Placeholders" failure phrases: "handle edge cases", "add appropriate error handling", "TBD", "similar to bead X"
- [ ] Files scopes across beads that can run in parallel are disjoint — overlapping Files sets mean the beads must be sequenced (add a dependency) or merged

### Dependencies

- [ ] All blocking dependencies are linked
- [ ] No circular dependencies exist
- [ ] Dependencies are minimal (not over-constrained)
- [ ] Ready issues exist for parallel work

### Scope

- [ ] Issue is appropriately sized (not too large)
- [ ] Large issues are broken into subtasks
- [ ] No duplicate or overlapping issues

### Priority

- [ ] Priority reflects actual importance
- [ ] Critical path items are prioritized correctly
- [ ] Dependencies and priorities align

### Self-Documentation

- [ ] Project context explains how this task serves overarching goals
- [ ] Reasoning/justification captures why this approach was chosen
- [ ] Considerations document constraints, edge cases, and related decisions
- [ ] A worker with zero prior context could implement this bead standalone

### Optimality & User Value

- [ ] This is the right decomposition (not too granular, not too coarse)
- [ ] The scope delivers meaningful user value (not just "technical cleanup")
- [ ] No better decomposition exists that would serve users more directly
- [ ] Every bead earns its place — no "nice to have" filler

## Step 3: Common Issues to Fix

Watch for and correct:

1. **Vague titles**: "Fix bug" → "Fix null pointer in UserService.getProfile when user not found"
2. **Missing context**: Add relevant file paths, function names, or module references
3. **Implicit knowledge**: Make assumptions explicit
4. **Missing or vague acceptance criteria**: Each criterion must name its verify command/test and expected result — "verify: `npm test x -- -t \"...\"` → PASS"
5. **Over-coupling**: Break dependencies that aren't strictly necessary
6. **Under-specified**: Add technical notes for complex tasks
7. **Duplicate work**: Merge or link related issues
8. **Missing dependencies**: Link issues that should be sequenced
9. **Wrong priorities**: Adjust based on critical path analysis
10. **Typos and grammar**: Fix for professionalism
11. **Missing "why"**: Add project context explaining how this serves overarching goals, and reasoning explaining why this approach was chosen over alternatives
12. **Locally optimal, globally suboptimal**: Individual beads may look fine in isolation but the overall decomposition doesn't serve users well — restructure from the user's perspective, not the developer's
13. **Interface drift**: A bead references a function/type/endpoint under a different name than the bead that produces it — align both to the producer's `Produces` signature

## Step 4: Update Issues

Use br update to fix issues:

```bash
br update <id> --title "Improved title" --json
br update <id> --priority <new-priority> --json
br update <id> --description "New description" --json
br update <id> --acceptance "Acceptance criteria" --json
```

For adding reasoning, context, or review notes that don't fit in the main description:

```bash
br comments add <id> "Project context: This enables the Developer Platform epic by..." --json
br comments add <id> "Reasoning: Chose token-bucket over sliding window because..." --json
br comments add <id> "Review note: Consider merging with bd-15 if scope overlaps" --json
```

Manage dependencies separately with `br dep`:

```bash
br dep add <issue-id> <dependency-id> --json   # Add dependency
br dep remove <issue-id> <dependency-id> --json # Remove dependency
br dep tree <issue-id> --json                   # View dependency tree
br dep cycles --json                            # Check for circular deps
```

For major rewrites, close and recreate:

```bash
br close <id> --reason "Replaced by <new-id>" --json
br create "Better title" -t <type> -p <priority> --deps <dep-id> --json
```

## Step 5: Dependency Graph Validation

After refinements, validate:

```bash
br list --json                    # View all issues
br list --status open --json      # View only open issues
br ready --json                   # View unblocked issues ready for work
br dep cycles --json              # Check for circular dependencies
br dep tree <epic-id> --json      # View dependency tree for an epic
```

Check:

- No orphaned issues (except entry points)
- No circular dependencies
- Critical path is clear
- Parallelization opportunities are preserved

## Step 6: Spec Coverage Check

Verify the beads cover the plan, not just that each bead is individually good. Open the source design/plan doc (check `.ccu/artifacts/<dir>/` — design.md, approach.md, or the doc named in the epic) and walk it requirement by requirement:

- For **each requirement**, point to the bead that implements it. A requirement with no bead is a plan gap — file the missing bead now (delegate to [[file-beads]]).
- For **each bead**, point to the requirement it serves. A bead serving no requirement is scope creep — challenge it.
- Confirm the **epic's `## Global Constraints`** section matches the design doc verbatim (version floors, naming/copy rules, platform requirements). Child beads inherit these; if the epic is missing them, add them.

## Step 7: Final Quality Gate

Before completing, ensure:

1. **Readability**: Any developer can pick up any ready issue
2. **Traceability**: Issues link to epics, epics link to the plan
3. **Testability**: Each issue has clear "done" criteria
4. **Parallelism**: Multiple issues can be worked simultaneously
5. **Completeness**: Spec coverage check (Step 6) passed — every requirement has a bead

## Output Format

Provide a review report:

### Summary

- Total issues reviewed: X
- Issues updated: Y
- Issues created: Z
- Issues closed/merged: W

### Changes Made

- List significant updates with rationale

### Remaining Concerns

- Any issues that need user input
- Ambiguities that couldn't be resolved

### Ready for Implementation

- List of ready issues workers can start with
- Suggested execution order for optimal flow

## Iteration Tracking

You may iterate on refinements up to 5 times if asked. Track iterations:

- Iteration 1: Initial review pass
- Iteration 2-5: Deeper refinements based on feedback

After 5 iterations, respond: "I don't think we can do much better than this. The issues are thoroughly reviewed, well-documented, and ready for workers to implement."