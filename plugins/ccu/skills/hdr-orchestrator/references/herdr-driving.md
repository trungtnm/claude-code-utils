# Herdr Driving Manual (pinned to the verified 0.7.4 CLI surface)

Herdr (herdr.dev) is a terminal workspace manager with native agent awareness: it detects the coding agent running in each pane, tracks its state, and exposes a CLI over a local socket API. This manual covers **only** the commands this skill uses, verified against `herdr 0.7.4` via `--help`. Herdr is pre-1.0: **never invent flags**. If a documented command errors on a newer herdr, that is version drift — surface it to the user; do not guess replacements.

**Principle: Herdr is signal; files + git are truth.** Every wait carries `--timeout`; every conclusion is confirmed against `RESULT.md`, `git log`, and bead status.

## Liveness and targets

```bash
herdr agent list          # all detected agents; "Connection refused" = no Herdr server running
herdr agent get <target>  # one agent's detail (pane id, state)
```

- `Error: ... Connection refused` means the Herdr server is not running — the prerequisite gate refuses on this; tell the user to launch `herdr` first.
- **Targets** accept terminal ids, unique agent names, detected/reported agent labels, and legacy pane ids. This skill addresses peers by their **pane label** (the bead id; delegation slug in non-bead repos); use `herdr agent get <label>` when a `pane` subcommand needs the numeric pane id.

## Spawning a peer

```bash
herdr agent start <name> --cwd <repo-root> -- <claude|codex> "<bootstrap prompt>"
```

- Atomic spawn + name + cwd — no detection race, no separate rename step needed.
- `<name>` is the **bead id** (e.g. `a04-3f2c`); it becomes the sidebar label, keying the pane to `br`, commits, and the ledger. Non-bead repos: use the delegation slug instead. Bead ids are unique — no collisions.
- Everything after `--` is the argv. The bootstrap prompt is one sentence pointing at `BRIEF.md`; the brief and bead carry everything else.
- `<claude|codex>` is the peer CLI selected for this run. Default to the
  coordinator's host and do not mix hosts; see
  [host-adapters.md](host-adapters.md).
- Other verified flags, use only when needed: `--workspace ID`, `--tab ID`, `--split right|down`, `--env KEY=VALUE`, `--focus|--no-focus`.

## Waiting on state

```bash
herdr agent wait <target> --status <idle|working|blocked|unknown> --timeout <MS>
```

- **There is no `done` state on `agent wait`.** `idle` is the completion signal — and it can misfire (a peer pausing mid-task also reads idle). Completion is confirmed only by `RESULT.md` existing and verification passing.
- **Always pass `--timeout`** (milliseconds). On expiry with no transition: `test -f .ccu/delegations/<id>/RESULT.md`, check `git log`, and `herdr agent read` to peek. A wait without a timeout can hang forever on a dead pane.
- `--status blocked` waits catch stuck peers (agent detected as waiting on input).

## Reading a pane

```bash
herdr agent read <target> [--source visible|recent|recent-unwrapped] [--lines N]
```

- `--source recent` is the default choice for "what is this peer actually asking?" on a blocked signal.
- Screen text is for **diagnosis only** — never verify completion from it.

## Sending input

```bash
herdr agent send <target> "<text>"       # writes LITERAL text — does NOT press Enter
herdr pane send-keys <pane_id> Enter     # the Enter goes separately (pane id from `herdr agent get`)
```

- `agent send` writes literal text; a message that should be submitted needs the follow-up `send-keys Enter`.
- `herdr pane run <pane_id> <command>` exists for command-plus-Enter in one call — meant for shell panes; for messaging an interactive coding-agent peer, prefer `agent send` + `send-keys Enter` so the text lands in the agent's input box exactly as written.
- **Never depend on injected keystrokes having landed.** Durable instructions (rejections, change requests) are written to files first; the keystroke only points at the file.

## Housekeeping

```bash
herdr agent rename <target> <name>   # relabel (only needed to fix a label; start names atomically)
herdr agent focus <target>           # bring a pane into view for the user
herdr agent attach <target>          # attach the current terminal to a peer's pane (user-driven)
herdr pane close <pane_id>           # close a finished pane — only after its delegation is verified
herdr pane current                   # your OWN pane id — for the coordinator's self-rename
herdr pane rename <pane_id> <label>  # coordinator labels itself hdr-<epic-or-bead-id> at init
herdr --version                      # log this in the ledger header at session start
```

## Error modes

| Symptom | Meaning | Response |
|---|---|---|
| `Connection refused` on any command | Herdr server down | Prerequisite gate refuses; user launches `herdr` |
| `agent wait` timeout, no transition | Dead/hung pane, or slow work | Poll files (`RESULT.md`, `git log`), `agent read` to peek |
| Label missing from `agent list` | Pane died | Reconcile by evidence precedence; if work is unfinished, start a fresh same-host peer pointing at the brief + latest rejection |
| Unknown flag / usage error | Version drift (pre-1.0 CLI) | Escalate to the user; do not guess a replacement flag |
