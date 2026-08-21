---
name: onboard
description: Guide the user through setting up, running, and testing the app after auto dev mode completes
---

Guide the user to set up, run, and test the application after auto dev mode has completed. Walk through environment setup, seed data, and key workflows so the user can start using the app in real life immediately.

## Steps

1. **Assess what was built** — Gather the full picture of what agents produced:
   - Read `README.md` for project overview and stated setup instructions (may be outdated)
   - Read `CLAUDE.md` or `AGENTS.md` for architecture, tech stack, conventions
   - `br list --status closed --json` — what beads were completed, what was actually built
   - `.ccu/DECISIONS.md` — architectural decisions that affect setup (DB choice, auth strategy, etc.)
   - `git log --oneline -30` — recent commits to understand the full scope of work
   - `br list --json 2>/dev/null` — check if any beads are still open (incomplete features the user should know about)

2. **Map the runtime dependencies** — Investigate what the app needs to run:
   - Read `package.json` / `requirements.txt` / `Cargo.toml` — dependency list
   - Read `docker-compose.yml` / `Dockerfile` if they exist — containerized services
   - Search for `.env.example`, `.env.template`, `.env.local.example` — required environment variables
   - Check for database migrations: `prisma/`, `drizzle/`, `migrations/`, `alembic/` directories
   - Check for seed files: `seed.ts`, `seed.sql`, `fixtures/`, `seeds/`
   - Identify external services: Redis, MinIO/S3, email providers, OAuth providers, payment gateways

3. **Generate the setup guide** — Walk the user through each step in order:

   ```
   ## Environment Setup

   ### Prerequisites
   - [ ] Node.js {version} / Python {version} / etc.
   - [ ] Docker + Docker Compose (if used)
   - [ ] {Database} running on {port}

   ### 1. Install dependencies
   {exact commands}

   ### 2. Environment variables
   Copy `.env.example` to `.env` and fill in:
   | Variable | Purpose | How to get it |
   |----------|---------|---------------|
   | DATABASE_URL | ... | ... |
   | ... | ... | ... |

   ### 3. Database setup
   {migration commands}

   ### 4. Seed data
   {seed commands, or explain what data needs to be created manually}

   ### 5. Start the app
   {exact commands to start all services}

   ### 6. Verify it works
   - Open {URL} in browser
   - You should see: {description of what the landing page looks like}
   - Try: {first action the user should take}
   ```

4. **Identify seed data needs** — Determine what data the user needs to actually USE the app:
   - If seed scripts exist, explain what they create and how to run them
   - If no seed scripts exist, **create one** or provide step-by-step instructions:
     - What's the first account to create? (admin user, test company, etc.)
     - What reference data is needed? (categories, roles, statuses, etc.)
     - What sample data makes the app feel real? (example records, test content)
   - For multi-tenant apps: explain how to create the first tenant/organization

5. **Document key workflows** — Walk through the 3-5 most important user flows:
   ```
   ## Key Workflows

   ### Flow 1: {Primary use case}
   1. Go to {page}
   2. Click {button}
   3. Fill in {fields}
   4. Expected result: {what should happen}

   ### Flow 2: {Secondary use case}
   ...
   ```
   Focus on the happy path. Note any known limitations or unfinished features (from open beads).

6. **Flag known gaps** — Be honest about what's NOT ready:
   - Open beads (`br list --status open --json 2>/dev/null`) — features not yet implemented
   - Missing tests, missing auth, missing error handling
   - Hardcoded values that need to be configured
   - Demo/mock data that needs to be replaced with real integrations
   - Any `TODO`, `FIXME`, `HACK` markers in the code: `grep -r "TODO\|FIXME\|HACK" src/ --include="*.ts" --include="*.tsx" -l 2>/dev/null`

7. **Write the onboarding doc** — Save the complete guide to `docs/ONBOARDING.md` (or `GETTING_STARTED.md`). This becomes a permanent artifact that future developers can use too.

   Write it under the [`tech-doc`](../tech-doc/SKILL.md) skill with `doc-type: runbook` — when to run this → prerequisites → numbered steps with expected output → verification → rollback. The reader is a developer who was not in this session, so nothing about auto dev mode, what the agents built, or what you just fixed belongs in the file. Every command in it is copy-pasteable and was actually run. The same applies to any README setup instructions you correct under "Create missing pieces".

8. **Offer to help** — Ask the user:
   - "Want me to run the setup commands now?"
   - "Want me to create a seed script for test data?"
   - "Any specific workflow you want to test first?"

## Arguments

- No args: full onboarding guide for the entire app
- `--setup-only`: just environment setup, skip workflows
- `--seed`: focus on creating/running seed data
- `--workflows`: just document the key user flows

$ARGUMENTS

## Rules

- **Verify, don't assume** — Don't say "run `npm install`" without checking that `package.json` exists. Don't say "run migrations" without checking which migration tool is used.
- **Test the commands** — If possible, run the setup commands yourself and report the results. Don't give the user untested instructions.
- **Be specific about versions** — "Node.js 20+" not "Node.js". "PostgreSQL 15" not "a database".
- **Create missing pieces** — If there's no `.env.example`, create one. If there's no seed script, write one. If README setup instructions are wrong, fix them.
- **Real data, not lorem ipsum** — Seed data should feel real. Use realistic names, amounts, dates. For Vietnamese apps, use Vietnamese names and content with proper diacritics.
- **Flag what's demo vs production** — Clearly distinguish between "this works" and "this is a placeholder/mock."
- **One command to rule them all** — If possible, create a `scripts/setup.sh` or similar that automates the entire setup sequence.
