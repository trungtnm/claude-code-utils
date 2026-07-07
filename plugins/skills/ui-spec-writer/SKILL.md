---
name: ui-spec-writer
description: "Generate detailed UI/UX implementation specs from a demo or prototype, so other agents can implement production code. Use when you have a working demo/prototype and need to produce handoff documentation for implementation agents. Triggers on 'write UI specs', 'document the UI', 'spec the components', 'handoff docs', 'implementation specs from demo'."
argument-hint: "[demo-dir] [output-dir] — e.g. /ui /docs/ui-specs"
---

# UI Spec Writer — Demo-to-Implementation Handoff

Generate detailed, structured implementation specs from a demo/prototype UI so that implementation agents can build the production version without ambiguity.

<AUTONOMOUS>
Execute all phases without asking "should I continue?" between them. The user expects you to run the full pipeline. Only pause with AskUserQuestion when you encounter genuine ambiguity (e.g., a component with no clear data source and no API spec to reference).
</AUTONOMOUS>

## Arguments

Parse `$ARGUMENTS` for:
- **demo-dir**: Path to the demo/prototype source (e.g., `ui/`, `demo/`, `prototype/`)
- **output-dir**: Where to write spec files (default: `docs/ui-specs/`)

If `$ARGUMENTS` is empty, auto-detect by running Phase 0 discovery.

---

## Phase 0: Project Discovery

Before writing anything, build a mental model of the project. This phase adapts the skill to ANY frontend stack and directory structure.

### 0.1 — Detect Demo Location

Search for the demo/prototype directory:
```
Look for directories matching: ui/, demo/, prototype/, packages/demo/,
apps/demo/, sandbox/, storybook-static/, .storybook/
```
If multiple candidates exist or none found, ask the user.

### 0.2 — Detect Frontend Stack

Read `package.json` (or equivalent) in the demo directory. Identify:

| Signal | Stack Detection |
|--------|----------------|
| `react`, `react-dom` | React |
| `vue` | Vue |
| `svelte`, `@sveltejs/kit` | Svelte/SvelteKit |
| `@angular/core` | Angular |
| `next` | Next.js (React SSR) |
| `nuxt` | Nuxt (Vue SSR) |
| `solid-js` | SolidJS |
| `@tanstack/react-query`, `@tanstack/vue-query` | TanStack Query for server state |
| `zustand`, `pinia`, `vuex`, `@ngrx/store`, `redux`, `jotai`, `valtio` | State management library |
| `socket.io-client`, `@trpc/client`, `@connectrpc/connect` | Real-time / RPC layer |
| `tailwindcss`, `@mui/material`, `@chakra-ui/react`, `vuetify` | Styling system |
| `shadcn`, `radix-ui`, `headlessui`, `primevue` | Component library |
| `@dnd-kit/*`, `react-beautiful-dnd`, `vuedraggable` | Drag-and-drop |
| `@xyflow/react`, `vue-flow`, `d3`, `chart.js`, `recharts` | Visualization |

Record the detected stack as `STACK_PROFILE` — you will reference it in templates.

### 0.3 — Detect Project Documentation

Search for existing specs that components should reference:
```
Look for: docs/, spec/, specifications/, api-spec*, openapi*, swagger*,
schema*, database*, socket*, websocket*, events*, CLAUDE.md, README.md
```

Categorize what you find:
- **API spec**: REST/GraphQL/tRPC endpoint definitions
- **DB schema**: Database table/collection definitions
- **Event spec**: WebSocket/Socket.IO/SSE event definitions
- **Wireframes**: ASCII wireframes, Figma links, design docs
- **Project rules**: CLAUDE.md, coding conventions

### 0.4 — Detect Production Target

Search for the production app directory (where implementation agents will write code):
```
Look for: packages/client/, packages/web/, apps/web/, apps/frontend/,
src/ (if demo is separate), packages/app/
```

If demo and production live in the same directory, note this — specs will describe refactoring in-place rather than building fresh.

### 0.5 — Detect Mock Data

Search the demo for hardcoded/mock data:
```
Look for: data/, mocks/, fixtures/, __mocks__/, seed/, fake*, mock*,
sample*, placeholder*, dummy*, files with "mock" or "fake" in the name
```

Also scan for inline hardcoded arrays/objects in page/component files.

### 0.6 — Write Discovery Summary

Before proceeding, output a brief discovery summary to the user:

```
## Discovery Summary
- Demo: ui/ (Vite + React 19)
- Stack: React, TanStack Query, Zustand, Socket.IO, shadcn/ui, Tailwind
- Docs found: API spec (docs/02-api-spec.md), DB schema (docs/01-schema.md), Socket events (docs/04-events.md)
- Production target: packages/client/
- Mock data: ui/src/data/ (8 files)
- Pages found: 7
- Components found: 45
- Design system sources: tailwind.config.ts, globals.css (CSS vars), components.json (shadcn)
- Output: docs/ui-specs/ (includes 00-design-system.md + per-page specs)
```

---

## Phase 0.7: Design System Extraction

Extract the design-system foundations into **`{output-dir}/00-design-system.md`**. This is a **global** doc — one per project — that every per-page spec references. Do NOT redefine tokens inside per-page specs.

**Output shape**: follow the structure skeleton in §0.7.6 below. For tone, depth, and the level of detail expected in each section, study the worked example at `templates/design-system.example.md` (Apple's web design system) — match its rigor, but extract tokens from the actual demo, NEVER copy Apple's values.

### 0.7.1 — Parse token sources

Read stack-specific sources in this order:

**Tailwind** (if detected):
- `tailwind.config.{js,ts,cjs,mjs}` → `theme.{colors, fontFamily, fontSize, fontWeight, letterSpacing, lineHeight, spacing, borderRadius, boxShadow, screens, zIndex}`
- Merge `theme.extend.*` with defaults — only extended keys are "project decisions"

**CSS variables**:
- `globals.css`, `app.css`, `index.css`, `styles.css` — extract every `--*` custom property and its value
- Identify dark-mode overrides (`.dark { --* }`, `[data-theme="dark"]`, `@media (prefers-color-scheme: dark)`)

**shadcn/ui** (if `components.json` exists):
- `baseColor`, `cssVariables`, `tailwind.cssVariables`, component path aliases — these tell you which token system is authoritative (CSS vars vs Tailwind theme)

**Design token files** (if any):
- `tokens.json`, `design-tokens.*`, `theme.ts` — parse as W3C DTCG format if shape matches

**Font loading**:
- `next/font` imports, `@font-face` rules, linked Google Fonts, local font files — record the actual typefaces in use, not aspirational ones in config

### 0.7.2 — Usage scan

Grep the demo source for className strings to distinguish *defined* vs *actually used* tokens:

| Scan | Patterns | Purpose |
|------|---------|---------|
| Colors | `bg-`, `text-`, `border-`, `ring-`, `divide-`, `from-`, `to-`, `via-` | Build the color-role map (what colors appear where) |
| Typography | `text-{size}`, `font-{weight}`, `leading-*`, `tracking-*` | Build the used type scale |
| Spacing | `p[xytblr]?-`, `m[xytblr]?-`, `gap-`, `space-[xy]-` | Used spacing scale |
| Radius | `rounded(-(sm\|md\|lg\|xl\|2xl\|3xl\|full))?` | Used radius scale |
| Shadow | `shadow-`, `drop-shadow-`, `backdrop-` | Used elevation levels |
| Breakpoints | `sm:`, `md:`, `lg:`, `xl:`, `2xl:` prefixes | Responsive behavior |

For each category, record:
- **Defined in config**: full list from token source
- **Actually used**: subset found in className strings
- **Orphans**: defined but never used (candidates for pruning — note, do not delete)
- **Foreign values**: arbitrary values like `p-[13px]`, `text-[#abc123]` that break the scale — flag as `⚠️ off-scale`

### 0.7.3 — Component enumeration

For shadcn demos:
- List every import from `@/components/ui/*` — these are **primitives**
- List every custom component under `components/` or `src/components/` (non-page) — these are **domain components**
- For each primitive, detect variants via `cva()` calls, `class-variance-authority`, or conditional className patterns
- Record per component: name, variants, documented states, consumer count, file path

### 0.7.4 — Visual capture (recommended)

If the demo has a `dev` script in `package.json`:
- Start the dev server, wait until it serves a 200
- Screenshot each page at three breakpoints (360px mobile, 834px tablet, 1440px desktop) using Playwright or Puppeteer
- Save to `{output-dir}/screenshots/{page-slug}-{breakpoint}.png`
- Shut down the dev server

If no dev server is available, skip — flag in §1 as `⚠️ No visual capture — human-reviewed screenshots recommended`. Never block on this step.

### 0.7.5 — Consistency audit

Before rendering the doc, run these checks — findings seed §7 (Do's/Don'ts):

- **Button consistency**: all CTAs share radius? Same size scale? Same weight?
- **Accent-color count**: how many distinct accents appear? If >1, flag drift.
- **Shadow diversity**: how many distinct shadow values? If >3, flag inconsistency.
- **Radius scale coherence**: rational scale, or ad-hoc values?
- **Spacing scale coherence**: any `p-[Npx]` / `gap-[Npx]` arbitrary values?
- **Typography scale**: text sizes used only once? (consolidation candidates)

Record findings as `⚠️ AUTO — review before shipping` rules — agents draft, humans finalize.

### 0.7.6 — Write `00-design-system.md`

Render using this skeleton. Study `templates/design-system.example.md` to calibrate depth — aim for that level of specificity in your extracted doc.

```markdown
# {Project Name} — Design System

## 0. Metadata
- Source commit: `{git SHA}`
- Extraction date: `{ISO date}`
- Demo path: `{path}`
- Stack: `{STACK_PROFILE}`
- Coverage: {N pages screenshotted, M components audited}

## 1. Visual Theme & Atmosphere
`⚠️ AUTO-DRAFTED — human review recommended`
{2–4 paragraphs synthesizing visual character from screenshots + tokens: mood, typographic feel, color story, spatial philosophy. If no screenshots, mark more aggressively for review.}

## 2. Color Palette & Roles
### Primary / Background / Surface / Interactive / Text / State
{Group by *role*, not by hue. For each: token name, hex/rgba, CSS variable, where it's used.}

## 3. Typography Rules
### Font Family
### Hierarchy
{Table: Role | Font | Size | Weight | Line Height | Letter Spacing | Notes — one row per *actually used* style}
### Principles
{How type is used: tracking conventions, weight distribution, optical sizing}

## 4. Component Stylings
### Primitives (shadcn/ui)
{One subsection per primitive in use — variants, states, visual rules}
### Domain Components
{One subsection per custom component}
### Pages that use each component
{Cross-reference table — enables impact analysis}

## 5. Layout Principles
### Spacing Scale
### Grid & Container
### Whitespace Philosophy
### Border Radius Scale

## 6. Depth & Elevation
{Elevation levels table + shadow philosophy}

## 7. Do's and Don'ts
`⚠️ AUTO-SEEDED from §0.7.5 — finalize before shipping`
### Do
### Don't

## 8. Responsive Behavior
### Breakpoints
### Touch Targets
### Collapsing Strategy

## 9. Agent Prompt Guide
### Quick Token Reference
### Example Component Prompts
{5–8 prompts, each a complete instruction an implementation agent can execute end-to-end}
### Common Failure Modes
{What implementation agents typically get wrong about this system}

## 10. Changelog
- `v1` — {ISO date} — initial extraction from commit {SHA}
```

---

## Phase 1: Inventory

### 1.1 — Catalog Pages

Read every page/view file in the demo. For each page, record:
- File path
- Route (from router config or file-based routing)
- Title / purpose (inferred from content)
- Child components used

### 1.2 — Catalog Components

Read every component file. For each, record:
- File path
- Props (from TypeScript interface, PropTypes, or `defineProps`)
- Which pages use it
- Whether it's a **shared/ui primitive** vs **domain-specific** component
- Whether it consumes mock data (and which mock file)

### 1.3 — Catalog Stores / State

Read every state management file (stores, composables, hooks, contexts). Record:
- What state it holds
- Which components consume it
- Whether it holds server data (should migrate to query layer) or UI-only state

### 1.4 — Catalog Mock Data

Read every mock/data file. For each, record:
- Data shape (TypeScript type or inferred structure)
- Which components consume it
- Corresponding API endpoint from docs (if any)
- **⚠️ UNMAPPED** if no API endpoint exists for this data

### 1.5 — Write Inventory File

Write `{output-dir}/00-inventory.md` with the full catalog. This becomes the index for all other spec files.

---

## Phase 2: Per-Page Spec Generation

For each page discovered in Phase 1, write a spec file: `{output-dir}/{page-name}.md`

### Spec File Template

Adapt terminology based on `STACK_PROFILE` detected in Phase 0:

```markdown
# {Page Name} — Implementation Spec

## Overview

| Field | Value |
|-------|-------|
| Route | `{route path with params}` |
| URL params | `{list or "none"}` |
| Query params | `{list or "none"}` |
| Auth required | Yes/No |
| Role restrictions | `{roles that can access, or "all authenticated"}` |
| Demo file | `{path to demo page file}` |
| Production target | `{path where implementation agent writes}` |

### Visual Description
{Describe what the demo currently renders — layout, sections, key visual elements.
If wireframes exist in project docs, reference them.}

---

## Component Tree

{Show the full hierarchy. Use the component library name for primitives.}

---

## Components

### {ComponentName}

**File**: `{demo path}` → `{production path}`
**Type**: {shared primitive | domain component | layout component}
**Wrapper of**: {shadcn Card | MUI DataGrid | Headless UI Listbox | none}

#### Design System References

- **Tokens used**: {e.g. `color.surface.elevated`, `radius.md`, `shadow.card`, `text.cardTitle`}
- **Primitives used**: {e.g. `@/components/ui/card`, `@/components/ui/button`}
- **Variants × States**: see `00-design-system.md §4.{ComponentName}`
- Do **not** redefine tokens inline — reference by name. If a needed token does not yet exist in `00-design-system.md`, add it there first, then reference it here.

#### Props Interface

{TypeScript interface — or Vue defineProps, or Svelte export let, adapted to stack}

#### Data Requirements

##### Server Data ({TanStack Query | SWR | Apollo | Pinia + fetch | built-in loader})

| Field | Source | Mock file | API endpoint | Cache key |
|-------|--------|-----------|-------------|-----------|
| {field} | {API response path} | {mock file:line} | {endpoint} | {suggested key} |

{If the project uses tRPC, GraphQL, or server components instead of REST, adapt:
- tRPC: procedure path instead of endpoint
- GraphQL: query/mutation name + relevant fragment
- RSC/Server Components: server function or data loader
- SvelteKit: +page.server.ts load function
- Nuxt: useFetch/useAsyncData composable}

##### Real-Time Updates

| Event | Source | Action |
|-------|--------|--------|
| {event name} | {Socket.IO / WebSocket / SSE / Supabase realtime} | {invalidate query / update store / append to list} |

{If no real-time layer detected, write: "No real-time layer detected. If real-time updates are needed, flag as ⚠️ NEEDS DECISION."}

##### UI State ({Zustand | Pinia | Redux | Jotai | Svelte store | Angular service})

| Slice/Key | Store | Purpose |
|-----------|-------|---------|
| {key} | {store name or "local useState/ref"} | {what it controls} |

#### User Interactions

| # | Action | Element | Handler | API Call | Side Effects |
|---|--------|---------|---------|----------|-------------|
| 1 | {user action} | {button/input/drag} | {handler name} | {endpoint or "none"} | {socket emit, optimistic update, toast, navigation, store mutation} |

#### Conditional Rendering

| Condition | Shows | Hides |
|-----------|-------|-------|
| Loading | {skeleton/spinner} | {content} |
| Empty state | {empty message/CTA} | {list/grid} |
| Error | {error boundary/toast} | {content} |
| Role = {role} | {action buttons} | — |
| Entity state = {state} | {specific UI variant} | {other variants} |

#### Accessibility

- Keyboard: {tab order, keyboard shortcuts, arrow key navigation}
- ARIA: {labels, live regions, roles for custom widgets}
- Focus: {focus trap in modals, focus restoration, skip links}

---

{Repeat ### ComponentName for every component on this page}

---

## Shared Types

{TypeScript interfaces used by multiple components on this page.
Cross-reference with DB schema doc if available.}

---

## ⚠️ Gaps & Missing Dependencies

### Missing API Endpoints
{List data the demo shows that has no corresponding API endpoint in the spec.
Include: what data is needed, suggested endpoint, request/response shape.}

### Missing Events
{Real-time updates the UI needs but no event is defined in the spec.}

### Missing Types
{Types referenced but not defined in any shared location.}

### Ambiguities
{Design decisions that are unclear from the demo alone — need human input.}

---

## Integration Checklist

- [ ] {Each API endpoint connected via query layer}
- [ ] {Each real-time event wired to invalidation/update}
- [ ] {Each store slice drives the correct UI}
- [ ] {Role-based visibility enforced for each action}
- [ ] {Loading/error/empty states implemented for each data fetch}
- [ ] {Accessibility requirements met for each interactive component}
```

---

## Phase 3: Shared & Layout Spec

Write `{output-dir}/layout-and-shared.md` covering:
- App shell / layout wrapper
- Navigation (sidebar, navbar, breadcrumbs)
- Global components (toasts, modals, alert bars, notifications)
- Auth context / provider setup
- Theme / design tokens if relevant
- Router configuration (route definitions, guards, lazy loading)

---

## Phase 4: Gap Report & Summary

Write `{output-dir}/99-summary.md`:

```markdown
# UI Spec Summary

## Stats
- Pages documented: {n}
- Components documented: {n}
- Spec files written: {n}
- Design tokens extracted: {colors, type styles, spacing steps, radii, shadows} — see `00-design-system.md`
- Screenshots captured: {n pages × 3 breakpoints, or "skipped"}

## Stack Profile
{Detected stack and key libraries}

## Gaps Found
### Missing API Endpoints ({count})
{Consolidated list from all page specs}

### Missing Events ({count})
{Consolidated list}

### Ambiguities Requiring Human Decision ({count})
{Consolidated list with page references}

## Design System Consistency Findings
{Summary of `Phase 0.7.5` audit results. Surface the findings that seeded `00-design-system.md §7`:
- Accent color count (target: 1)
- Distinct shadow values (target: ≤3)
- Button radius / size drift
- Off-scale arbitrary values (`p-[13px]`, `text-[#abc123]`, etc.)
- Orphan tokens (defined, never used)
Each finding is actionable: either fix the demo, or codify the exception as an explicit rule.}

## Recommended Implementation Order
{Based on dependency analysis — which pages/components should be built first.
Consider: design system primitives FIRST (so every page has tokens to reference),
then shared components, then data layer, then pages.
Within pages: fewer gaps before more gaps.}

## File Index
| File | Page/Scope | Components |
|------|-----------|------------|
| `00-design-system.md` | global | {primitive count} |
| `00-inventory.md` | global | all |
| {filename} | {page name} | {count} |
```

---

## Critical Rules

1. **READ before you write** — open and read every demo file before documenting it. Never infer component behavior from filenames alone. If a component file exists, read it.

2. **Cross-reference obsessively** — every mock data field must map to a real API response field (or be flagged as ⚠️ UNMAPPED). Every user action must map to an API call (or be flagged as client-only).

3. **Stack-adaptive language** — use the terminology of the detected stack:
   - React: "props", "hooks", "context", "useEffect"
   - Vue: "props", "composables", "provide/inject", "onMounted"
   - Svelte: "props (export let)", "stores", "onMount", "$effect"
   - Angular: "inputs", "services", "observables", "ngOnInit"
   - Next.js: "server components", "server actions", "route handlers", "middleware"
   - SvelteKit: "load functions", "+page.server.ts", "form actions"

4. **No implementation code in page specs** — write specs, not components. In per-page specs, the only code blocks are TypeScript interfaces/types and pseudocode for complex interactions. **Exception**: `00-design-system.md` MAY contain CSS variable declarations, hex/rgba values, CSS property snippets, and Tailwind class references — these are design decisions, not implementation.

5. **Preserve design decisions** — document visual layout, spacing patterns, color usage, animations, transitions from the demo. Implementation agents must match the demo's visual output.

6. **One file per page** — enables parallel agent assignment. An implementation agent gets ONE spec file and builds ONE page.

7. **Flag, don't invent** — if the demo shows behavior that contradicts the API spec or schema, flag it as an ambiguity. Do not guess which is correct.

8. **Respect project conventions** — if CLAUDE.md or project docs define naming conventions, file organization, or coding patterns, reference them in specs so implementation agents follow them.

9. **Reference, don't duplicate** — `00-design-system.md` is the single source of truth for tokens, primitives, and style rules. Per-page specs MUST reference tokens by name (e.g. `color.surface.elevated`, `radius.md`, `shadow.card`) rather than repeating hex values or class strings. If a page needs a token that doesn't exist in `00-design-system.md`, add it there first — never inline a one-off value in a page spec.

10. **AUTO-drafted sections need review markers** — any section of `00-design-system.md` produced by LLM synthesis (§1 Visual Theme, §7 Do's/Don'ts seeded from consistency audit, §9 Common Failure Modes) MUST be labeled `⚠️ AUTO — review before shipping`. Humans finalize interpretation; agents propose.
