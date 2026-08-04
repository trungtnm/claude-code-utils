# Claude Code and Codex Host Adapters

The delegation protocol is host-neutral. Beads, briefs, result files, rejection
files, git trailers, Herdr state, and verification are identical. Choose one
peer CLI for the run and vary only the adapters below.

## Peer process

Default to the coordinator's host unless the user explicitly selects another
installed CLI.

| Coordinator | Peer argv after Herdr's `--` |
|---|---|
| Claude Code | `claude "<bootstrap prompt>"` |
| Codex | `codex "<bootstrap prompt>"` |

Examples:

```bash
herdr agent start <label> --cwd <repo-root> -- claude "<bootstrap prompt>"
herdr agent start <label> --cwd <repo-root> -- codex "<bootstrap prompt>"
```

Run `command -v <peer-cli>` during the prerequisite gate. Record the selected
host and `<peer-cli> --version` in the ledger header. Do not mix peer hosts in a
single orchestration run; it makes recovery and permission behavior ambiguous.

## Recovery

Do not depend on “resume the last session.” Multiple peers share the same repo,
so a global last-session selector can attach to the wrong delegation. If a pane
dies and durable evidence does not show completion, start a fresh peer under
the original label with this bootstrap shape:

```text
Read <BRIEF.md> and continue the delegation. Before editing, read the latest
REJECTION-<n>.md if one exists. Inspect the existing working tree and git
history; do not redo completed work. Finish by writing RESULT.md.
```

The protocol survives a fresh process because all authority and state live in
the bead, delegation files, and git—not in chat history.

## Reviewer

The Reviewer is a short-lived, read-only subagent inside the coordinator:

- **Claude Code:** use the plugin's `reviewer` subagent type.
- **Codex:** use the current Codex collaboration tool (`spawn_agent` when that
  name is exposed), first loading `agents/reviewer.md` as its persona and
  constraints. Explicitly require a read-only review and no edits. Do not start
  another Herdr pane for this short-lived reviewer.

If a Codex surface exposes no collaboration/subagent facility, single-peer
delegations still work, but a tiered delegation must stop before dispatch and
ask the user to move it to a Codex surface with subagents. Never silently omit
the Reviewer stage.

Both adapters receive the same review prompt from
[tiered-execution.md](tiered-execution.md), and their findings enter the same
durable rejection path.

## Coder permissions

Claude Code can launch the Coder with a temporary `--settings` file that denies
edits to Architect-owned contract-test paths. Use that mechanism when the peer
CLI is `claude`.

Do not invent a Codex CLI flag for path-specific edit denial. For a `codex`
peer, put the immutable contract-test paths in the Coder brief, make the peer
acknowledge that boundary before implementation, and enforce it mechanically
with the assertion-line diff check during verification. Any assertion edit is
an automatic rejection. This is weaker prevention but the same acceptance
boundary.

## User escalation

Escalate plan, scope, and irreversible decisions with the coordinator host's
native user-input mechanism. In Codex, use its user-input tool when exposed;
otherwise ask the user a concise direct question and keep the ledger row
`blocked`. Never assume a Claude-only notification hook is available.
