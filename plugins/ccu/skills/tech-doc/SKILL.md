---
name: tech-doc
description: Write technical documentation that states facts about the system as it exists now. Use this skill whenever the task involves writing or editing a README, API reference, architecture or design doc, ADR, runbook, module doc, migration guide, or any explanatory markdown in a repository — including when the user just says "document this", "write docs for X", "update the README", or asks for a write-up after a code change. Also use it when reviewing existing docs for AI-sounding prose, process narration, or unverifiable claims. Authoritative source for documentation prose style — other skills delegate here instead of restating writing rules.
argument-hint: "[target] [doc-type] [--review] [--lang=en|vi] — e.g. src/auth/ module, docs/api.md --review"
---

# Technical Documentation

Documentation describes **the system as it is now**, for a reader who was not present when it was built.

The reader is a competent engineer who has never seen this code. They have a task. Every sentence either helps them do that task or gets deleted.

This skill is the **single source of truth for documentation prose** in this project. Other skills, commands, and agents that write or edit markdown (`/enrich-docs`, `/enrich-readme`, [[ui-spec-writer]], the `reviewer` agent, and any workflow producing a design doc, runbook, or ADR) MUST delegate the writing rules here rather than restating their own, so the voice stays consistent.

## Scope

Not every markdown file is documentation. Some artifacts are **records of a moment**, and "No history" would destroy the very thing they exist to hold.

**Out of scope — do not apply this skill:**

| Artifact | Why |
|---|---|
| `.ccu/CHECKPOINT.md` | Session state. Its content is where an interrupted recipe run stopped, not how the system works. |
| `.ccu/CAPTURES.md` | Captures hold the user's words verbatim. Rewriting them loses the signal. |
| `CHANGELOG.md` | Change history is its subject. |
| Commit messages, PR descriptions, bead descriptions | Not documentation. Beads follow [[file-beads]]. |

**In scope with "No history" lifted** — these record a choice or a delta, so the rejected option and the previous version are the content. Every other rule holds:

| Artifact | What stays banned |
|---|---|
| ADRs, `.ccu/DECISIONS.md` | "We chose X over Y because Z" is the point. AI voice, marketing adjectives, and unverifiable claims are still banned. |
| Migration guides | The difference between two versions is the subject. The guide carries an expiry note naming the version after which it is deleted. |

**Fully in scope:** README, API reference, design doc, runbook, module doc, and any explanatory markdown describing how the system works today.

## Non-negotiable rules

1. **Present tense, indicative mood.** The system does X. Not: the system will do X, would do X, has been changed to do X.
2. **Every claim is checkable against the code.** Exact file paths, exact function and env var names, exact commands, exact numbers. Never approximate a name you did not read.
3. **No history.** The doc is a snapshot, not a story. Version control holds the history.
4. **No process narration.** The reader does not care how the doc or the code came to exist.
5. **If a fact is unknown, write `TODO:` and say what is missing.** Never fill a gap with plausible-sounding prose.

## Banned: history and process

Do not write, in any form:

- What the code used to do, what was replaced, what was removed, what was refactored, what was "recently" or "now" added
- Comparisons to a previous implementation ("unlike the old handler", "this replaces the legacy sync path")
- Anything about the working session that produced the change: what was investigated, tried, discovered, fixed, verified, discussed, or decided during it
- References to PRs, tickets, branches, commits, or conversations, unless the doc's stated purpose is to link them
- Changelog entries inside reference or design docs (changelogs live in `CHANGELOG.md`)
- Migration instructions inside a reference doc (they live in a separate migration guide with an expiry)
- Status commentary: "currently", "for now", "at the time of writing", "still", "as of today"

Test for a sentence: **if it only makes sense to someone who knows the previous version, delete it.**

```
BAD   The auth middleware was refactored to use a single validation pass instead of
      the two-stage check we had before, which fixes the race condition.
GOOD  `authMiddleware` validates the token in one pass and attaches `req.user`.
      A request with an expired token returns 401 with code `TOKEN_EXPIRED`.

BAD   After investigating the timeout issues, we found that connection pooling was
      needed, so the pool is now configured with a max of 20.
GOOD  The pool holds at most 20 connections (`DB_POOL_MAX`, default 20).
      Requests beyond that queue for up to 5s, then fail with `PoolTimeoutError`.
```

## Banned: claims you cannot check

This one fails quietly. History reads wrong immediately; one confident invented sentence reads fine and sends the reader down a path that does not exist. Four kinds get written without a source:

| Kind | Example | What to write instead |
|---|---|---|
| Behaviour of a system you did not read | "The gateway collapses repeats of the same idempotency key." | Describe what *this* code sends. The gateway's side is `TODO:` or a link to its docs. |
| The author's motive | "Obsolete adapters are deliberately not deleted so that hand-written files survive." | "Obsolete adapters are reported, never deleted. Removal is manual." Behaviour is observable; intent is not. |
| Verification you did not perform | "Tested on Python 3.13." / "Works with Postgres 14+." | Run it and quote the output, or drop the claim. |
| Numbers you did not measure | "Handles ~10k requests/second." | The measured figure with its conditions, or nothing. |

If you cannot name the file that proves a sentence, it is a guess — mark it `TODO:` with what is missing, or delete it.

## Banned: AI voice

These patterns mark text as machine-written. Remove all of them.

**Openers and closers.** No "In this document, we'll explore…". No "Let's dive in". No "By following these steps, you'll be able to…". No closing paragraph that restates the document. A doc starts with its first fact and ends with its last one.

**Filler transitions.** "It's important to note that", "It's worth mentioning", "Keep in mind that", "That said", "Essentially", "Simply put", "At its core", "Under the hood". Delete the phrase; keep the fact.

**Marketing adjectives.** robust, seamless, powerful, comprehensive, elegant, flexible, cutting-edge, blazing-fast, best-in-class, effortless, intuitive. If a property matters, give the number instead: not "fast lookups" but "O(1) lookups, ~40µs at 1M keys".

**Hedging.** "may potentially", "can sometimes", "generally speaking", "in most cases" — unless the exact condition is then stated. Vague hedging means the fact was not checked.

**The negation-contrast tic.** "This isn't just a cache — it's a coordination layer." "Not only X, but also Y." Write the claim directly.

**Rule of three.** Three parallel adjectives or three parallel clauses in one sentence, repeatedly. Vary sentence shape.

**Enthusiasm.** Exclamation marks, "Great!", "Perfect!", emoji in headings, ✅/🚀 bullets, "Happy coding!".

**Bold sprinkled mid-sentence** for emphasis. Bold is for defined terms and table keys only.

**Rhetorical questions as headings.** "Why does this matter?" → state what it does.

**Anthropomorphizing.** The service does not "know", "want", "try", "decide to", or "be smart about". It reads, writes, retries, returns.

## Sentence-level style

- Subject of the sentence is the component, not "we" and not "you" — except in procedures, where "you" is correct and direct imperatives are better still.
- Active voice. "The scheduler drops the job" over "the job is dropped".
- One idea per sentence. Split anything over ~25 words.
- No parenthetical asides stacked inside a sentence. Make it a second sentence or a note line.
- Define an acronym once, at first use, then use it bare.
- Name things exactly as the code names them, in backticks. Do not paraphrase an identifier into prose.

## Structure

Lead with what the reader needs first, not with context.

| Doc type | Order |
|---|---|
| README | one-line purpose → install/run → minimal working example → configuration → common tasks |
| API reference | endpoint/signature → params with types and defaults → return shape → errors → example |
| Design doc | problem and constraints → chosen design → interfaces and data flow → trade-offs and rejected options → open questions |
| ADR | context → decision → consequences (one page, no more) |
| Runbook | when to run this → prerequisites → numbered steps with expected output → verification → rollback → escalation |
| Module doc | responsibility (one sentence) → public surface → invariants → failure modes |
| Migration guide | who must migrate → what breaks → step-by-step change with before/after → verification → expiry note naming the version after which this file is deleted |

Rules that apply to all of them:

- Headings are noun phrases: "Configuration", "Error codes", "Rate limits". Not "Configuring the app" and not "Let's configure".
- Two heading levels. A third means the doc should be split.
- Tables for anything enumerable: config keys, error codes, params, env vars. Columns: name, type, default, meaning.
- Bullets only for genuinely unordered sets. Reasoning and trade-offs go in prose paragraphs — a bulleted argument is a hollow argument.
- Nesting: two levels maximum.
- Every code block is copy-pasteable and runs as written. Real values, not `<your-value-here>` where a real default exists. Include expected output when the reader needs to compare.
- Diagrams: Mermaid, only when the relationship is not linear. A three-step flow is a sentence, not a diagram.

## ADR gate

A decision earns an ADR only when all three of these hold:

1. **Hard to reverse** — the cost of changing your mind later is meaningful.
2. **Surprising without context** — a future reader looks at the code and asks why it was done this way.
3. **The result of a real trade-off** — there were genuine alternatives, and one was chosen for stated reasons.

A decision that fails any of the three belongs in the `.ccu/DECISIONS.md` journal instead. An easy-to-reverse decision gets reversed; an unsurprising one raises no question; one with no alternative records nothing beyond "we did the obvious thing".

What clears the gate:

- **Architectural shape.** "The write model is event-sourced, the read model is projected into Postgres."
- **Integration patterns between contexts.** "Ordering and Billing communicate via domain events, not synchronous HTTP."
- **Technology choices that carry lock-in.** Database, message bus, auth provider, deployment target — the ones that would take a quarter to swap out, not every library.
- **Boundary and scope decisions.** "Customer data is owned by the Customer context; other contexts reference it by ID only." The explicit no is worth as much as the yes.
- **Deliberate deviations from the obvious path.** "Hand-written SQL instead of an ORM, because X." These stop the next engineer from "fixing" something intentional.
- **Constraints not visible in the code.** A compliance rule that rules out a provider, a partner contract that caps response times.
- **Rejected alternatives whose rejection is non-obvious.** Otherwise the same alternative gets proposed again in six months.

ADRs live in `docs/adr/NNNN-slug.md`, numbered from the highest number already there. Create `docs/adr/` with the first ADR, not before. The body follows the ADR row in [Structure](#structure); a single paragraph naming the context, the decision, and the reason is a complete ADR. Add `Status` frontmatter (`proposed | accepted | deprecated | superseded by ADR-NNNN`) only where decisions get revisited.


## Procedure

1. **Read the code first.** Open the actual files, configs, and types. Do not document from what you remember writing earlier in the session — memory of the change is contaminated with process and with intent that never landed in the code.
2. **List the facts** the reader needs, before writing prose.
3. **Write the reference parts** (tables, signatures, error codes) before the explanatory parts. The tables usually reveal that half the intended prose is unnecessary.
4. **Write the explanation** only where behaviour is non-obvious from the reference.
5. **Cut.** Delete every sentence that adds no fact. Expect to remove 20–30% of the first draft.
6. **Run the checklist below.**

## Review mode

Enter review mode when `--review` is passed, **or** when the request is phrased as an assessment rather than a write: "check these docs", "is the README still accurate", "does this doc sound AI-written", "audit our docs". The distinction matters because rewriting a doc the user only wanted checked destroys their edit history and hides what was wrong. When the phrasing is genuinely ambiguous ("look at the README"), report first and offer to fix — reporting is the recoverable choice.

Read the doc and the code it describes. Report one line per violation, most severe first, and change nothing:

```
docs/api.md:31  unverifiable  Doc says default timeout 30s; `client.ts:88` sets 10s
docs/api.md:14  history       "This replaces the old sync endpoint" → delete
docs/api.md:52  ai-voice      "robust and flexible retry handling" → give the retry count and backoff
docs/api.md:60  structure     Error codes in prose → move to a name/meaning table
```

Severity order: unverifiable claim (a reader acts on it and is wrong) → history and process narration → AI voice → structure. End with the count per category and a one-line verdict: `PASS` or `NEEDS_REWRITE`.

A doc with zero violations gets `PASS` and nothing else. Do not invent findings to look thorough — a review that always finds something teaches the reader to ignore it.

## Checklist before returning the doc

- [ ] No sentence refers to a previous version, a change, or a work session
- [ ] No "currently", "now", "recently", "used to", "was updated", "we decided"
- [ ] No banned filler phrase or marketing adjective survives
- [ ] No opening preamble, no closing summary
- [ ] Every identifier, path, and command was read from the code, not recalled
- [ ] Every number has a unit and a source
- [ ] Every code block runs as written
- [ ] Failure modes and error cases are documented, not only the happy path
- [ ] Read the first three sentences: does a stranger get the point? If not, reorder

## Language

Write in the language of the surrounding repo and audience. When writing Vietnamese, the same rules apply, plus these tells to avoid:

- Openers: "Trong bài viết này, chúng ta sẽ…", "Đầu tiên, hãy cùng tìm hiểu…", "Như đã đề cập ở trên…"
- Closers: "Hy vọng bài viết này hữu ích", "Tóm lại, có thể thấy rằng…"
- Filler: "Điều quan trọng cần lưu ý là", "Nói một cách đơn giản", "Về cơ bản thì"
- Marketing: "mạnh mẽ", "linh hoạt", "tối ưu", "hiệu quả" without a number attached
- Over-polite framing: "chúng ta hãy", "bạn có thể dễ dàng…"

Keep technical terms in English (`middleware`, `retry`, `pool`, `schema`) rather than translating them. Keep sentences short; Vietnamese AI-generated prose drifts long and clause-heavy.

## Arguments

Most invocations carry none — the target comes from the conversation. Parse `$ARGUMENTS` when it is present; every token is optional.

| Token | Meaning |
|---|---|
| Path to code (file or directory) | The surface to document. Read it before writing — this is the source of every fact. |
| Path to a `.md` file | The doc to write into. It already exists → edit in place; it does not → create it. |
| `readme`, `api`, `design`, `adr`, `runbook`, `module`, `migration` | Doc type. Selects the row in [Structure](#structure). |
| `--review` | Audit only, as described in [Review mode](#review-mode). |
| `--lang=en` \| `--lang=vi` | Output language. Default: the language of the surrounding docs (see [Language](#language)). |
| Anything else | Free-text scope, e.g. "the retry behaviour and its env vars". |

Resolution rules:

- **No arguments** — the target is whatever the surrounding conversation asks to document. Do not ask which file to write unless two locations are equally plausible.
- **Code path, no doc path** — write to the project's existing docs home (`README.md`, `docs/`, or the sibling doc of the nearest module). Never create a new top-level docs tree without asking.
- **Doc path, no code path** — read the code the doc names, then verify every claim in it against that code.
- **No doc type** — infer it from the target: a repo root → README, an exported module → module doc, an HTTP handler → API reference, a `docs/adr/` path → ADR.
- **Ambiguous target** — ask one question naming the two candidates. Do not document both.

## Delegated invocation

When another skill or agent delegates here, it passes:

```
target:      <path(s) to the code being documented>
doc-path:    <file to write, or "caller-owned" if the caller writes the file>
doc-type:    readme | api | design | adr | runbook | module | migration
audience:    <who reads this and what task they have>
constraints: <caller rules that override defaults, e.g. "add only, never delete">
```

The caller owns *what* gets documented and *where* it lands. This skill owns *how the prose reads* — the rules above are not negotiable by a caller. A caller constraint that contradicts them (for example, asking for a changelog-style "what's new" section inside a reference doc) is refused, and the caller is told which rule it hit.
