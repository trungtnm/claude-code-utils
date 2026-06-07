---
name: markdown-html-viewer
description: >
  Turn a Markdown document into a polished, self-contained HTML reading page — branded header,
  sticky table-of-contents sidebar, GFM tables, live Mermaid diagrams, light/dark theme toggle,
  GFM-alert callouts, copy buttons, and a print-to-PDF stylesheet — or point it at several .md
  files / a folder to get one index with a document switcher. CRUCIALLY, also covers how to
  make a document readable in the first place: convert
  flows/state/relationships/architecture into Mermaid diagrams, dense field/parameter/data-model
  prose into clean tables, and leave literal artifacts (signatures, JSON, formulas, code) as code.
  Use this whenever the user wants to view, share, present, or "make readable/beautiful" a Markdown
  spec, design doc, README, report, or any .md; render Markdown as HTML; build a doc viewer; add a
  table of contents; or when a doc has dense data, wide code blocks, or describes a flow/architecture
  that a diagram or table would clarify — even if they don't say "HTML" or "Mermaid" explicitly.
---

# Markdown → HTML document viewer

Three core jobs, in order (then view + verify). The readability work is where the value is; the rendering is mechanical — but **Step 2 (asking the user how to build it) is required on every single run** and must never be skipped, even when the choice seems obvious.

1. **Make the Markdown render well** — convert flows, relationships, and dense data into diagrams and tables. See `references/readability.md` — read it before restructuring any substantial doc. This is the part users actually feel.
2. **Ask how to build it (REQUIRED every run)** — confirm the output mode and, when there are multiple files, the layout, before generating anything. See Step 2.
3. **Generate the viewer** — wrap the `.md`(s) in a styled HTML shell with `scripts/md2html.py`.

A document that is just walls of prose and runny inline-code chips is hard to scan no matter how nicely it's styled. The win comes from picking the right *representation* for each piece of content, then letting the viewer present it cleanly.

## Step 1 — Improve readability (the important part)

Skim the document and reshape content by what it *is*. The quick rule:

| Content shape | Best representation | Why |
|---|---|---|
| A process, handshake, request/response sequence | **Mermaid** `sequenceDiagram` / `flowchart` | shows order & actors at a glance |
| A lifecycle / status machine (states + transitions) | **Mermaid** `stateDiagram-v2` | transitions are invisible in prose |
| Entities & how they relate (data model, schema) | **Mermaid** `erDiagram` + per-entity tables | the join structure is the point |
| A system's parts and how data flows | **Mermaid** `flowchart` (subgraphs + `classDef`) | replaces ASCII art that overflows |
| Field/parameter lists, config options, comparisons | **Markdown table** | runny prose with inline-code chips is unscannable |
| A wide SQL `CREATE TABLE` / column dump | **Markdown table(s)** (+ an `erDiagram` for relations) | wide code blocks scroll horizontally and get cut off |
| A warning, gotcha, key decision, or recommendation | **GFM alert** (`> [!WARNING]`, `[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!CAUTION]`) | the viewer renders these as colored, icon-titled callout boxes — pulls the critical line out of the prose |
| Literal artifacts: signatures, IDs, JSON/YAML, formulas, real code/pseudocode | **Leave as a code block** | a diagram or table of a literal string *loses fidelity* — this is the one thing not to "improve" |

Full recipes, copy-paste diagram skeletons, before/after examples, and the Mermaid parser-safety rules (which characters break `sequenceDiagram`/`stateDiagram` labels) live in **`references/readability.md`**. Read it whenever you're restructuring a doc.

The guiding idea: pick the representation that makes the *structure* visible. Don't force it — if something is genuinely just a paragraph, leave it a paragraph; and never turn a literal artifact into a picture.

## Step 2 — Ask how to build it (REQUIRED — do this every run, before calling the script)

**This step is mandatory on every invocation.** Before generating anything, confirm the build choices with the user using the question tool (`AskUserQuestion`). Do not assume defaults and skip the ask — even when the request looks obvious, ask. Put the recommended option first.

First determine how many `.md` files are in scope (the file(s) the user named, or the `.md` files in the target directory). Then:

1. **Output mode — ALWAYS ask.** "Embed the content, or load the `.md` live?"
   - **Fetch — live `.md` loader (recommended):** the HTML `fetch()`es the `.md` at runtime, so the `.md` stays the single live source (edit, refresh). Needs a dev browser or HTTP to view (file:// CORS). → no `--inline` flag. This is the skill's whole point, so recommend it for anything still being edited.
   - **Inline — embed content:** the Markdown is baked into the HTML → one portable file that double-clicks open in any browser. It's a snapshot, so it must be regenerated after edits. → `--inline`. Recommend when the user wants to send/share one file.

2. **Layout — ask ONLY when there is more than one `.md` in scope.** "One index with a document switcher, or a separate HTML per file?"
   - **One index with switcher (recommended):** a single HTML whose header dropdown swaps between docs. → one `md2html.py` call with all the files (or the directory).
   - **Separate HTML per file:** one standalone page beside each `.md`. → call `md2html.py` once per file.
   - If there is only **one** `.md`, skip this question entirely (it doesn't apply).

Map the answers to commands:

| Files in scope | Layout | Mode | Command(s) |
|---|---|---|---|
| one | — (n/a) | Fetch | `md2html.py doc.md` |
| one | — (n/a) | Inline | `md2html.py doc.md --inline` |
| many | One index | Fetch | `md2html.py a.md b.md …` (or a directory) |
| many | One index | Inline | `md2html.py a.md b.md … --inline` |
| many | Separate | Fetch | run `md2html.py X.md` once **per file** |
| many | Separate | Inline | run `md2html.py X.md --inline` once **per file** |

Only after both answers are in (or the layout question was correctly skipped for a single file) do you move on to generate.

## Step 3 — Generate the HTML viewer

`scripts/md2html.py` (standard library only) wraps a `.md` in a styled shell that renders client-side: marked.js for GFM (tables included), mermaid.js for ` ```mermaid ` fences, a sticky TOC sidebar with scroll-spy, and a print stylesheet so **Print → Save as PDF** exports cleanly.

```bash
python3 scripts/md2html.py spec.md                    # one .md → spec.html
python3 scripts/md2html.py *.md                        # many .md → one index.html with a switcher
python3 scripts/md2html.py docs/                       # a directory → one index.html (all docs/*.md)
python3 scripts/md2html.py spec.md --brand "ACME" --badge "DRAFT v0.1" --mark "AC" \
  --link "design.html|Design →" --link "api.html|API ↗"
python3 scripts/md2html.py spec.md --lang vi          # Vietnamese chrome labels
```

Useful flags: `--title`, `--subtitle`, `--brand`, `--badge` (doc-type/status chip), `--mark` (1–3 char logo glyph), `--lang` (chrome language), `--link "href|label"` (repeatable header nav), `-o OUT.html`. Title defaults to the first `# H1`.

**Multiple docs → one index (this is the multi-doc fork):** pass several `.md` paths or a directory and you get a **single** HTML with a **document-switcher dropdown** in the header. The content area swaps between docs — each gets its own TOC, reading time, Mermaid render, and callouts. `README.md` sorts first; the rest alphabetically. The output defaults to `index.html` in the first doc's folder. Both modes apply: `--fetch` keeps every `.md` a live source (the index fetches whichever is selected); `--inline` embeds all of them into one portable file. Deep links are routable: `index.html#doc=api.md` opens a specific doc, and `#doc=api.md&s=sec-3` jumps to a section within it — the in-page TOC and heading anchors generate these automatically, so switching docs never clobbers the selected one.

**What the reader gets, automatically** (all client-side — the `.md` stays the source, nothing is baked into HTML):

- **Light / dark theme toggle** — header button, persisted in `localStorage`, defaults to the OS `prefers-color-scheme`. Mermaid diagrams re-render to match the theme.
- **Callouts from GFM alerts** — a blockquote starting `> [!NOTE]` / `[!TIP]` / `[!IMPORTANT]` / `[!WARNING]` / `[!CAUTION]` becomes a colored, icon-titled callout. Marker text is stripped; a plain `>` blockquote stays a plain blockquote. (This is the markdown-native way to get the reference repo's "callout" component without putting raw HTML in the source.)
- **Copy buttons** on code blocks (hover-reveal), **hover-reveal heading anchor links**, a **scroll progress bar**, a **skip-to-content** link, and **reduced-motion** support.
- **Auto reading-time** estimate in the header, and a **mobile TOC drawer** (hamburger + backdrop) below 1000px.
- **Localized chrome** — `--lang` (en, vi, zh, ja, ko, es, fr, de) translates the TOC label, copy button, callout titles, and reading-time string, and sets `<html lang>`. Body content always renders in the source language; only the UI chrome is translated. Vietnamese labels carry full diacritics.

### Two output modes (this is a real fork — get it right)

- **`--fetch` (default):** the HTML loads the `.md` with `fetch()` at runtime, so the `.md` stays the **single live source** — edit it, refresh, done. No copy of the content lives in the HTML. This is the default because keeping one source of truth is almost always what you want for a doc you're still editing.
- **`--inline`:** embeds the Markdown inside the HTML → a portable single file anyone can double-click. Use this only for **sharing/emailing one file**; it's a snapshot, so regenerate after editing the `.md`.

You still ask in Step 2 every time — but use any signal the user already gave to pick which option you mark "(Recommended)": "keep the .md as the source" / "no inline content" → lead with **Fetch**; "I want to send this to someone" / "just double-click it" → lead with **Inline**.

## Step 4 — View it with no server

A `--fetch` page can't be loaded by a plain double-click: normal browsers block `file://` from fetching a sibling file (CORS). Two no-server options:

- **Dev browser (recommended for live editing):** open the file in Chrome started with `--allow-file-access-from-files` and its own profile dir — the flag lifts the restriction. Use the helper:
  ```bash
  scripts/open_in_dev_browser.sh spec.html
  ```
  (The dedicated `--user-data-dir` matters — Chrome ignores the flag if it attaches to an already-running default profile.)
- **Portable copy:** regenerate with `--inline`, then double-click in any browser.

A `--fetch` page opened in a normal browser doesn't fail silently — it shows a banner explaining both options. Serving over HTTP (`python3 -m http.server`) also works but is usually unnecessary.

## Step 5 — Verify it actually renders

Don't assume — confirm, especially that Mermaid diagrams parsed (a single bad label silently drops a diagram). Two cheap checks:

- **Validate Mermaid syntax** with the CLI (catches parse errors per diagram):
  ```bash
  npx -y @mermaid-js/mermaid-cli -i diagram.mmd -o /tmp/out.svg   # needs Chrome; pass -p puppeteer.json with executablePath if no bundled Chromium
  ```
- **Render check** (if a headless browser is available): load the page (for `--fetch`, with `--allow-file-access-from-files`), wait a few seconds, then assert in the DOM that `#toc a`, `.content table`, and `.content .mermaid svg` counts match expectations and there are no `pageerror`s. A quick screenshot is worth a thousand assumptions — confirm tables don't overflow and diagrams rendered as SVG (not raw code).

If diagrams are missing, the cause is almost always a Mermaid label syntax issue — see the parser-safety section in `references/readability.md`.

## Gotchas worth remembering

- **Mermaid label characters:** a literal `→` arrow and unescaped parentheses/commas inside `sequenceDiagram`/`stateDiagram` transition labels are common parse-breakers. Prefer plain words ("to" not "→") and `<br/>` for line breaks in `flowchart` node labels.
- **`</script>` in inline mode:** the generator escapes `</script` → `<\/script` so embedded Markdown can't prematurely close the tag. (Only relevant for `--inline`.)
- **Callout syntax is strict:** the alert marker must be the **first line** of the blockquote, on its own (`> [!WARNING]`), with the body on the following `>` lines. `> [!warning] text on the same line` still works (case-insensitive), but an unknown tag (e.g. `[!FYI]`) silently falls back to a plain blockquote — use only the five GitHub tags.
- **Theme-aware callout/TOC tints use `color-mix()`** (Chrome 111+, Safari 16.2+, Firefox 113+). Current viewers handle it fine; on an ancient browser the tint just falls back to no background — harmless.
- **Multi-doc `--fetch` needs every `.md` reachable from the index's folder.** Paths in the switcher are stored relative to the output HTML, so generating an index for files spread across distant directories still works, but moving the HTML away from the docs breaks the relative links. For a self-contained bundle to move/share, use `--inline`.
- **CDN dependency:** marked.js and mermaid.js load from a CDN (works even over `file://`). Fully offline use needs vendored copies — note that to the user if it comes up.
