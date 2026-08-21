---
name: dc-deploy-cloudflare
description: >
  Deploy a Claude Code Design canvas directory (.dc.html artboards with support.js and a
  _ds/ design system) to Cloudflare Workers, with clean URLs and an optional GitHub Actions
  pipeline. Covers auditing orphaned and hotlinked assets, renaming artboards to URL-safe
  names without breaking dc-import resolution, the Worker route table, the allow-list build,
  and render-level verification. Use when asked to deploy, publish, ship, or host a design
  canvas, a .dc.html site, or a Claude Design export.
---

# DC deploy to Cloudflare Workers

Takes a Claude Code Design canvas directory and produces a deployable repo: a route Worker,
an allow-list build, cache headers, and a CI workflow. The design and the page content are
not touched.

| Stage | Output |
|---|---|
| Audit | Orphaned assets, broken references, external hotlinks, junk files |
| Rename | Kebab-case English artboard names with every reference intact |
| Scaffold | `worker/`, `scripts/build.mjs`, `wrangler.jsonc`, `_headers`, `package.json` |
| CI | `.github/workflows/deploy.yml` |
| Verify | Real headless render, not an HTTP status sweep |

Templates for every generated file are in `templates/`. They carry placeholder values; the
[Scaffold](#3-scaffold) section states which values are derived from the repo and which are
asked for.

## Preconditions

Run only when the working directory has all three:

```bash
ls *.dc.html >/dev/null 2>&1        # artboards
test -f support.js                   # canvas runtime
ls -d _ds/*/ >/dev/null 2>&1         # design system tokens
```

Any one missing: stop and report that this is not a DC canvas directory. Do not fall back to
a generic static-site deploy.

## Inputs

Ask for these before scaffolding. Do not guess any of them.

| Input | Default when the user declines |
|---|---|
| Worker name | Kebab-cased directory name, confirmed with the user before use |
| Custom domain | None — the site is served at `https://<worker-name>.<subdomain>.workers.dev` |
| GitHub remote | Skip [CI and secrets](#5-ci-and-secrets); the user deploys with `npx wrangler deploy` |

**Custom domain.** Ask whether the site gets one. When the user supplies a hostname, first
confirm both conditions in [Custom domain rejects an existing CNAME](#custom-domain-rejects-an-existing-cname),
then add this key to `wrangler.jsonc`:

```jsonc
"routes": [{ "pattern": "<domain>", "custom_domain": true }]
```

When the user declines, has no domain ready, or does not answer, leave `templates/wrangler.jsonc`
as written. `workers_dev: true` already serves the site. The zone row of the
[API token permissions](#api-token-permissions-a-missing-zone-scope-still-deploys-green) table
and the CNAME precondition do not apply in that case.

**Cloudflare account.** Never write an account ID into `wrangler.jsonc` or any committed file.
CI reads it from the `CLOUDFLARE_ACCOUNT_ID` secret. Local `wrangler` calls read it from
`wrangler login` or from a `CLOUDFLARE_ACCOUNT_ID` environment variable the user sets.

## 1. Audit

Run before changing anything. Print the report and wait for the user to approve deletions.

**Orphaned and missing assets.** Match the raw string `uploads/...` across all HTML, CSS, and
JS. Do not parse `<img src>` tags — background images live inside `background: url(...)` in
`style` attributes, and a tag parser misses them and deletes files that are in use.

```bash
grep -oh "uploads/[^\"')[:space:]]*" *.html *.css *.js \
  | sed 's|uploads/||' | sort -u > /tmp/ref.txt
ls uploads | sort > /tmp/have.txt
comm -13 /tmp/ref.txt /tmp/have.txt   # orphaned: on disk, never referenced
comm -23 /tmp/ref.txt /tmp/have.txt   # missing: referenced, not on disk
```

**External hotlinks.** Images and fonts pointing at a host outside the deployment:

```bash
grep -roh "url('https\?://[^']*')" *.dc.html *.css
```

Download each into `uploads/`, rewrite the reference, and add a matching declaration inside
the artboard's `<helmet>` so it is declared the same way as every other asset:

```html
<meta name="ext-resource-dependency" content="uploads/x.jpg">
```

**Secrets and junk.** `.DS_Store`, key and token strings, absolute paths from the author's
machine.

> [!WARNING]
> An external process — the canvas app or the file manager — can delete files from `uploads/`
> between the audit and the deletion step. When deleting, copy to a backup location first,
> verify the count matches, and only then delete. A `mv` loop is not a backup when the source
> list was computed in an earlier step.

## 2. Name normalization

Rename artboards to kebab-case English. **Take the names from data already in the repo**
rather than inventing them: the `active="..."` attribute on nav elements is usually already
the canonical English name.

Use `git mv` so the rename stays staged. Then update three groups of references:

1. `href="<old-name>.dc.html"` in every artboard
2. Path arrays inside `<script data-dc-script>` blocks
3. `<dc-import name="X">` — see [dc-import resolves filenames at runtime](#dc-import-resolves-filenames-at-runtime)

Re-grep the old names across `*.dc.html *.md *.css` until nothing matches.

## 3. Scaffold

Copy the files from `templates/` and fill in the values below.

**Route table** (`worker/index.js`). A page is any artboard that is not pulled in as a
component:

```bash
grep -roh 'dc-import name="[^"]*"' *.dc.html | sed 's/.*name="\(.*\)"/\1/' | sort -u > /tmp/components.txt
ls *.dc.html | sed 's/\.dc\.html$//' | sort > /tmp/all.txt
comm -23 /tmp/all.txt /tmp/components.txt   # → one ROUTES entry each
```

`/` maps to the artboard named `home` or `index`. When neither exists, ask which artboard is
the landing page. Components stay out of `ROUTES`; the asset layer serves them by filename.

**Build lists** (`scripts/build.mjs`). Derive `FILES` and `DIRS` from the repo — every
top-level `.css` and `.js` file, and every asset directory. Exclude `node_modules`, `dist`,
`worker`, `scripts`, `.github`, and `.git`.

**`wrangler.jsonc`.** Set `name` to the worker name and `compatibility_date` to today. Add
the `routes` key only when the user supplied a custom domain. `html_handling: "none"` is
required — see [html_handling does not cover .dc.html](#html_handling-does-not-cover-dchtml).

Validate the config shape against `node_modules/wrangler/config-schema.json` at
`definitions.CustomDomainRoute` rather than from memory. Config fields change between
wrangler versions.

**`package.json`.**

```json
{
  "private": true,
  "type": "module",
  "scripts": {
    "build": "node scripts/build.mjs",
    "dev": "wrangler dev --port 8788 --local",
    "deploy": "wrangler deploy"
  }
}
```

Install wrangler with `npm i -D wrangler@latest` and let npm write the version range.

## 4. Local verification

```bash
npm install && npm run build
npx wrangler dev --port 8788 --local
```

Check three layers, in order.

**Status codes** for every clean route, its trailing-slash form, one asset, and one unknown
path.

**Inline script syntax:**

```bash
for f in *.dc.html; do
  perl -0777 -ne 'while (/<script(?![^>]*\bsrc=)[^>]*>(.*?)<\/script>/gs){print "$1\n;\n"}' "$f" > /tmp/c.js
  [ -s /tmp/c.js ] && node --check /tmp/c.js
done
```

**Real render** — see [Verification requires a real render](#verification-requires-a-real-render).

## 5. CI and secrets

Generate `.github/workflows/deploy.yml` from `templates/deploy.yml`, resolving each
`<LATEST>` action version at run time instead of pinning a remembered one:

```bash
curl -s https://api.github.com/repos/cloudflare/wrangler-action/releases/latest \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])"
```

Never accept a token value in conversation. Tell the user to set both secrets themselves:

```
! gh secret set CLOUDFLARE_API_TOKEN
! gh secret set CLOUDFLARE_ACCOUNT_ID
```

## 6. Production verification

Repeat [Local verification](#4-local-verification) against the deployed hostname — the custom
domain when one is configured, otherwise the `workers.dev` URL — plus cache headers and TLS.

## Pitfalls

### dc-import resolves filenames at runtime

`support.js` builds each component URL as `COMPONENT_DIR + "/" + name + ".dc.html"`. So
`<dc-import name="site-nav">` fetches `./site-nav.dc.html`, and **the filename never appears
in the markup**.

Renaming a file without updating `name=` blanks that component with no build error, and a
grep for the old filename finds nothing. Components embedded into a page as a section are the
easiest to miss, because nothing links to them.

```bash
grep -roh 'dc-import name="[^"]*"' *.dc.html | sed 's/.*name="\(.*\)"/\1.dc.html/' \
  | sort -u | while read f; do [ -f "$f" ] || echo "MISS $f"; done
```

### html_handling does not cover .dc.html

Cloudflare Static Assets maps `/about` to `/about.html`. The extension here is `.dc.html`, so
that convention does not match. `"html_handling": "none"` plus an explicit Worker route table
is the only combination that serves clean URLs.

### Assets are served before the Worker

A request matching a real file in `dist/` never reaches Worker code. That keeps the Worker to
a route table, but it also means `/about.dc.html` cannot be redirected to `/about` without
`run_worker_first`. Serving both URL forms is the simpler choice.

### Trailing slash breaks relative paths silently

The most dangerous failure, because **the status code stays 200**.

Artboards reference assets relatively (`support.js`, `uploads/x.jpg`, `./site-nav.dc.html`).
At `/about` those resolve against the root and work. At `/about/` they become
`/about/support.js` and 404 — the page renders bare, with no CSS and no nav, while HTTP
reports success. Any sweep that only counts status codes passes.

Detect it by requesting a **subresource** of the slashed form, not the page:

```bash
curl -o /dev/null -w "%{http_code}\n" http://localhost:8788/about/support.js   # must be 404
```

The Worker template already answers with a 301 to the slashless form.

### Custom domain rejects an existing CNAME

A Custom Domain differs from a Route: Cloudflare creates the DNS record and issues the
certificate, and in exchange it refuses a hostname that already has a CNAME record. The
symptom is a green deploy with a live Worker and a domain that silently never attaches.

Confirm both before the first deploy:

- The zone is active in the target Cloudflare account
- The hostname has no existing CNAME record

Neither applies when no custom domain is configured.

### API token permissions: a missing zone scope still deploys green

| Scope | Permission |
|---|---|
| Account | Workers Scripts → Edit |
| Account | Account Settings → Read |
| Zone (the domain's zone) | Workers Routes → Edit |

Without the zone permission the Worker still deploys successfully and only the custom domain
fails to attach. The zone row is unnecessary when the site stays on `workers.dev`.

### Force-remove in a heredoc trips destructive-command guards

A shell build script that force-removes the output directory is blocked by the guard hook
even while the command is only being **written into a file**, never executed. Write the build
in Node and use `fs.rmSync(dist, { recursive: true, force: true })`.

### GitHub Actions hides empty inputs from logs

An unset secret resolves to an empty string, and GitHub omits that input from the logged
`with:` block entirely:

```
with:
  command: deploy
  quiet: false
```

`apiToken` vanishing looks like a YAML syntax error and is not. Confirm with `gh secret list`.

### Verification requires a real render

A 200 does not prove the page works: unrendered `{{ }}` placeholders and unresolved
`<dc-import>` elements both return 200. Use a headless shell:

```bash
CHS=~/.cache/puppeteer/chrome-headless-shell/*/chrome-headless-shell-*/chrome-headless-shell
"$CHS" --dump-dom --virtual-time-budget=8000 --no-sandbox --disable-gpu "$URL" > dom.html

grep -c '{{'          dom.html   # 0
grep -c '<dc-import'  dom.html   # 0
grep -c 'id="dc-root"' dom.html  # 1
```

A rendered DOM is substantially larger than its source. A dump whose size approximates the
source file means the runtime never ran.

### UI strings built from filenames break on rename

A caption built as `page.replace('.dc.html','')` displays the new filename after a rename,
discarding whatever label it used to show. Grep for expressions that operate on filenames:

```bash
grep -rn "replace('.dc.html'\|\.dc\.html'," *.dc.html
```

### _headers counts as config, not an asset

Cloudflare reads `_headers` as configuration, so the uploaded asset count is one lower than
the file count in `dist/`. The number wrangler prints under `--dry-run` uses a third counting
method and matches neither.

### Absolute links break local viewing

Clean URLs exist only through the Worker route table. An internal link written as `/about`
breaks when an artboard is opened over `file://` or through a plain static server. Keep
internal links relative (`<name>.dc.html`) so they work everywhere; clean URLs still work when
shared directly.

## Verification checklist

Run every item and report each result. None is optional.

- [ ] Every `dc-import name=` resolves to a file that exists
- [ ] Every `href`, `src`, and `url()` resolves to a file that exists, ignoring `{{ }}` and http
- [ ] Every inline script passes `node --check`
- [ ] Every clean route returns 200
- [ ] Trailing slash returns 301, **and** a subresource of the slashed form returns 404
- [ ] An unknown path returns 404
- [ ] Render: zero `{{`, zero `<dc-import>`, one `#dc-root`
- [ ] `dist/` contains no `CLAUDE.md`, `README.md`, `.git`, or config files
- [ ] Cache headers apply to `uploads/` and to HTML
- [ ] No internal absolute links remain

## Out of scope

Request these from the user instead of attempting them:

- Creating a Cloudflare API token and setting GitHub secrets
- Confirming the zone is active and removing a conflicting CNAME
- Deciding whether to delete orphaned assets — propose, then wait for approval
- Editing page content or design
