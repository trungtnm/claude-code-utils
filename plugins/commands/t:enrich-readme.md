Enrich the project's README. Add missing sections, and update only those sections that are factually outdated versus the current code. Leave accurate content alone.

## Steps

1. **Read the current README** — Read the existing README.md (or README) in the repo root. Map what's already covered so you don't duplicate.

2. **Explore the codebase** — Scan the project structure, key source files, configs, and tests. Identify what deserves to be in the README: features, setup steps, architecture, usage, contribution flow.

3. **Gap analysis against the canonical structure below** — Classify each canonical section:
   - **Missing** → add a new section using the template.
   - **Outdated / incorrect** (contradicts current code, references removed features, wrong commands) → update in place with correct info; preserve the section's existing tone and heading level.
   - **Present and accurate** → leave untouched, even if it could be written better.

4. **Draft new sections** — For each gap, write substantive content (no fluff). Use tables, code blocks, or mermaid, excalidraw diagrams where they help.

5. **Insert at the right location** — Place each new section where it logically belongs in the existing flow, roughly following the canonical order below. Don't dump everything at the bottom.

## Canonical README structure

```
# [Project Name] — [tagline]

[badges: build, version, license, downloads — only if meaningful]

[Hero: screenshot, asciicast, or short "what it looks like" snippet]

## What is it?
[2-3 sentence pitch. Problem it solves + who it's for.]

## Requirements
[Runtime versions, OS, external deps, API keys. Omit only if truly none.]

## Quick Start
[Shortest path to a working example. Copy-pasteable commands. Under 2 minutes to first success.]

## Why [Project]?
[3-5 outcome-framed bullets — what the user accomplishes, not feature names.
Include a "Why not X?" bullet comparing to the obvious alternative.]

## Usage
[One canonical runnable example, then progressively complex variants as needed.
Link out to /examples or docs for more.]

## Configuration
[Table: option | type | default | description — only if >3 options. Inline prose otherwise.]

## Troubleshooting
[Top 3 failure modes and fixes. Optional — include once the project has known common issues.]

## Contributing
[How to contribute, code style, PR process. Link to CONTRIBUTING.md if one exists.]

## License
[License type + link.]
```

## Rules

- **Add or correct, never restyle** — Add missing sections. Fix sections that are factually wrong or outdated relative to the current code. Do NOT rewrite accurate content just because you'd phrase it differently.
- **Update means minimal diff** — When correcting an outdated section, change only the stale facts (commands, file paths, feature claims). Keep the rest of the section as-is.
- **Frame all updates as if they were always present** — Describe the current state of the project. Do NOT write "we added X", "X is now Y", "recently introduced", "new in this version", or any other changelog-style phrasing. The README documents what the project *is*, not what just changed.
- **Cover new commands, options, and features exhaustively** — When scanning the codebase, identify every command, flag, configuration option, environment variable, skill, hook, or feature the README does not yet document, and add it. Missing surface area is the most common reason READMEs go stale.
- **Match the existing tone** — headings, voice, and code-block style from the current README.
- **Be substantive** — each new section teaches something specific about this project, not generic filler like "this project is great".
- **Quick Start must be embarrassingly easy** — if a reader can't get a working example in under 2 minutes, the section isn't done.
