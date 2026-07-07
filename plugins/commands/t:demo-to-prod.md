Convert a working demo/prototype UI into a production application. Copies demo markup exactly into the production stack, stubs the backend, and files beads for implementation agents to wire up real business logic.

The demo is sacred — the production UI must look identical to what was designed.

## Steps

1. **Discover the demo** — Find the demo directory:
   - Search for: `ui/`, `demo/`, `prototype/`, `packages/demo/`, `apps/demo/`, `playgrounds/`
   - If `$ARGUMENTS` provides a path, use that
   - Detect the demo format:
     - **React app** (most common): `.tsx`/`.jsx` files with components, Tailwind classes, shadcn/ui imports → this is the primary path
     - **Static HTML**: `.html` files with inline CSS or linked stylesheets → fallback path
     - **Other framework**: Vue SFC, Svelte, etc. → adapt accordingly
   - Read ALL demo source files. Catalog every page and component:
     ```
     | Demo File | Page Name | Key Components | Mock Data Used |
     |-----------|-----------|----------------|----------------|
     | board-page.tsx | Board | KanbanColumn, BeadCard, CaptureInbox | 5 epics, 3 agents |
     | agents-page.tsx | Agents | AgentCard, StreamPreview, QueueList | 4 running agents |
     ```
   - Read shared files: `shared.css`, `globals.css`, layout components, design tokens
   - **Check for ui-spec-writer output**: Look for `docs/ui-specs/` or similar spec directory. If `/ui-spec-writer` was run on the demo, these specs contain per-page component inventories, mock→API data mappings, and `⚠️ UNMAPPED` flags — use them as the authoritative reference for steps 7-8 instead of re-discovering data shapes from scratch

2. **Discover the production stack** — Read the project's `package.json`, `tsconfig.json`, directory structure:
   - Framework: React / Vue / Svelte / Next.js / etc.
   - Styling: Tailwind / CSS Modules / styled-components
   - Component library: shadcn/ui / MUI / Radix / none
   - Router: TanStack Router / React Router / Next.js App Router
   - State: Zustand / Jotai / TanStack Query / Redux
   - If the production project doesn't exist yet, ask the user which stack to scaffold

3. **Map demo pages → production routes** — Create the mapping:
   ```
   | Demo Source | Production Route | Component Path | Status |
   |-------------|-----------------|----------------|--------|
   | board-page.tsx (or 01-board.html) | /board | src/pages/board-page.tsx | pending |
   | agents-page.tsx (or 02-agents.html) | /agents | src/pages/agents-page.tsx | pending |
   ```

4. **Copy + adapt each page** — For each demo page, one at a time:

   **If demo is React (primary path):**
   a. Read the demo component completely — JSX, props, state, Tailwind classes, shadcn imports
   b. Copy the component into the production directory structure
   c. Restructure to match production conventions (file naming, directory layout, export patterns)
   d. Replace hardcoded navigation with the production router (`<Link>`, route params)
   e. Replace inline mock data with typed state/props, keeping mock values as defaults:
      ```tsx
      // BEFORE (demo — hardcoded)
      <h3>Authentication Service</h3>
      <Badge variant="outline">Running</Badge>
      <span>2h 15m</span>

      // AFTER (production — typed, data-driven)
      <h3>{agent.name}</h3>
      <Badge variant="outline">{agent.status}</Badge>
      <span>{formatDuration(agent.startedAt)}</span>
      ```
   f. Preserve ALL Tailwind classes, shadcn component usage, and layout structure exactly
   g. If the demo uses CDN shadcn or inline component definitions, migrate to proper `npx shadcn@latest add <component>` imports

   **If demo is static HTML (fallback path):**
   a. Read the HTML completely — every element, every class, every inline style
   b. Convert HTML → JSX, CSS → Tailwind classes, `<a>` → `<Link>`
   c. Replace raw HTML elements with shadcn equivalents where applicable:
      `<button class="...">` → `<Button>`, `<div class="card...">` → `<Card>`

   **For both paths:**
   h. Keep mock data as default/fallback so the page renders without a backend
   i. Place in the correct production directory
   j. **Verify**: the page should render identically to the demo

5. **Extract shared components** — After converting all pages, identify repeated patterns:
   - Navigation (sidebar, header) → `src/components/layout/`
   - Cards, badges, status indicators → `src/components/ui/`
   - Page shells, grids → `src/components/layout/`
   - Use the project's component library conventions (shadcn patterns if available)
   - Each extracted component retains the demo's exact visual appearance

6. **Extract design tokens** — Pull the demo's design language into the project's theme:
   - Colors → `tailwind.config.ts` extend section or CSS variables
   - Fonts → font imports + Tailwind font family config
   - Spacing scale → verify it matches Tailwind defaults, note deviations
   - Border radii, shadows, transitions → document in a design system file if not standard
   - Animations (pulse-dot, glow-ring, etc.) → `@keyframes` in global CSS

7. **Stub the backend contracts** — If ui-spec-writer output exists (`docs/ui-specs/`), use its per-page data mapping tables and `⚠️ UNMAPPED` flags as the source of truth for what needs backend stubs. Otherwise, discover from the demo source directly. For each piece of data shown in the demo:
   a. Create TypeScript interfaces for all data shapes:
      ```typescript
      // src/types/agent.ts
      interface Agent {
        id: string;
        name: string;
        status: 'running' | 'idle' | 'error';
        startedAt: Date;
        // ...
      }
      ```
   b. Create API route stubs that return the demo's mock data:
      ```typescript
      // src/api/agents.ts (or server route)
      export async function getAgents(): Promise<Agent[]> {
        // TODO: implement real data source
        return MOCK_AGENTS;
      }
      ```
   c. Create query hooks (TanStack Query / SWR / framework equivalent) that call the stubs
   d. Wire the converted pages to use the query hooks instead of inline mock data
   e. Mark every stub with `// TODO: implement real data source`

8. **File beads for backend work** — Create beads for each backend domain:
   ```bash
   ACTOR="${BR_ACTOR:-assistant}"

   # Schema bead
   br create --actor "$ACTOR" "Database schema + migrations" \
     --priority p0 --type task --labels backend,schema \
     --description "Create tables for: [list all data types from step 7]. See types in src/types/. Demo pages that consume this data: [list pages]."

   # API beads (one per domain)
   br create --actor "$ACTOR" "API: [domain] endpoints" \
     --priority p1 --type task --labels backend,api \
     --description "Implement real endpoints for [domain]. Stubs exist at [paths]. Pages consuming: [list]. Replace TODO stubs with actual DB queries."

   # Auth bead (if demo shows auth UI)
   br create --actor "$ACTOR" "Authentication + authorization" \
     --priority p0 --type task --labels backend,auth \
     --description "Implement auth flow shown in demo. Login page at [path]. Protected routes: [list]."

   # Real-time bead (if demo shows live updates)
   br create --actor "$ACTOR" "Real-time: WebSocket/SSE for [feature]" \
     --priority p2 --type task --labels backend,realtime \
     --description "Demo shows live updates on [pages]. Implement WebSocket/SSE for [data types]."
   ```
   Set dependencies: schema bead blocks all API beads. Auth blocks protected routes.

9. **Verify the copy** — Start the dev server and check each page:
   ```bash
   npm run dev  # or project's start command
   ```
   - Open each page in the browser
   - Compare against the demo (run demo alongside if it has its own dev server, or open demo source as reference)
   - Check: layout, colors, spacing, typography, responsive behavior, component appearance
   - Report any visual drift with specific details
   - Fix any drift before proceeding

10. **Next steps** — Report to the user:
    ```
    ## Demo-to-Prod Complete

    ### Converted
    - N pages converted from demo to production components
    - N shared components extracted
    - N TypeScript interfaces created
    - N API stubs with TODO markers

    ### Backend Beads Filed
    - {bead-id}: Schema + migrations (p0)
    - {bead-id}: API: [domain] (p1)
    - ...

    ### To start backend implementation:
    Run `/t:auto` to let agents work through the backend beads.
    Or run `/t:onboard` first to set up the development environment.
    ```

## Arguments

- No args: auto-detect demo dir, convert all pages
- `<demo-dir>`: explicit path to demo directory
- `--auto`: after conversion, immediately start `/t:auto` for backend beads
- `--page <name>`: convert only a specific page (useful for incremental conversion)

$ARGUMENTS

## Rules

- **Demo is sacred** — The production UI must look identical to the demo. When in doubt, match the demo pixel-for-pixel.
- **Copy first, refactor later** — Get it working with copied markup before abstracting into components. Don't over-engineer the first pass.
- **Types over mocks** — Replace demo's hardcoded data with TypeScript interfaces immediately. Mock data stays but is properly typed.
- **One page at a time** — Convert each page fully (step 4a-h) before moving to the next. Don't batch partial conversions across pages.
- **Preserve Vietnamese diacritics** — All Vietnamese text in the demo must be copied with full diacritics. `Đang thực hiện`, not `Dang thuc hien`.
- **Stubs return demo data** — API stubs must return the exact data shown in the demo so the converted pages render correctly with zero backend work.
- **Backend beads reference frontend** — Every backend bead must say which pages/components consume its data, so implementation agents understand the impact of their work.
- **Don't touch the demo** — The demo files are read-only reference. Never modify them. They're the source of truth for visual fidelity.
