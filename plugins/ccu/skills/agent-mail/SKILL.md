---
name: agent-mail
description: MCP Agent Mail coordination contract — registration, file reservations, message semantics, and stale-lock handling for agents sharing one working tree. Use when running /auto as a swarm peer, dispatching orchestrator workers, or resolving a reservation conflict.
---

# Agent Mail

Agent Mail carries live coordination between agents that share one working tree: identity, file reservations, progress mail, rejections. It does not replace bead state or git — those arbitrate.

Two workflows depend on this contract, and they can run at the same time in the same tree:

| Workflow | Shape | Peers are |
| --- | --- | --- |
| [[auto]] | N identical peers, each self-scheduling from the bead graph, no dispatcher | other `/auto` sessions and any orchestrator worker |
| [[orchestrator]] | One coordinator spawning role-scoped subagents per bead | its own workers and any `/auto` session |

Neither uses worktree isolation, so **a reservation is the only mechanical lock between two agents editing the same file**. An agent that skips registration holds no locks and sees none — it overwrites a peer's work with no error and no warning.

When the `mcp-agent-mail` server is not available, every workflow here degrades to a single agent working alone. Say so once, then proceed; do not fail.

## Registration

Agent Mail calls are MCP calls, not shell. A `$VAR` argument does not expand; it becomes a garbage key and a private mailbox where no other agent's reservations are visible, with no error. Echo the value first and paste the literal string:

```bash
git rev-parse --show-toplevel   # e.g. /Users/you/code/myrepo
```

```
macro_start_session(
  human_key="/Users/you/code/myrepo",   # the literal repo root you just echoed
  program="claude-code",
  task_description="<what this session is doing>"
)
```

- Names are auto-generated adjective+noun pairs (`TopazRiver`). Do not pass a custom name; capture `agent.name` from the response and keep it for the session.
- Open the contact policy so peer contact requests auto-accept without a handshake round-trip: `set_contact_policy(agent_name=<your name>, policy="open")`.
- `list_contacts()` shows peers already active on this repo, including sessions you did not start. Their reservations are live; you must respect them.

Every agent registers under the same literal repo root. The key is what makes reservations mutually visible. Use the API to discover peers — never hand-derive the server's on-disk directory name, because a slug mismatch reports "no peers" and leaves you blind.

## File reservations

Reserve every path before editing it, including paths discovered mid-task, and release them when the work lands:

```
file_reservation_paths(paths=["src/foo.ts", "src/bar.ts"], reason="<bead-id>")
release_file_reservations()
```

A failed reservation names the holder. Do not proceed on that path. Resolve by cause:

| Cause | Resolution |
| --- | --- |
| Both beads need the path | The graph is missing an edge. `br dep add <blocked> <blocker>`, run them sequentially |
| You are a swarm peer with other work available | Release what you hold for this bead, leave it unclaimed, pick a different ready bead |
| You are an orchestrator worker | Report the conflict to the orchestrator and stop |
| The requesting change is unnecessary | Reject it |
| The holder is a dead agent | `force_release_file_reservation`, only after its session ended and its mail is silent |

Shared mutable state outside the file tree — a database, a port, a lockfile — is not covered by path reservations. Declare it on the bead's `## Coordination Resources` block so scheduling can serialize it.

## Message semantics

| Need | Call |
| --- | --- |
| Durable record that survives the agent's exit | `send_message` / `reply_message` on a shared thread |
| Resume a live agent | `SendMessage(to=<harness agent id>)` |
| Resume an exited agent | Respawn with the mail thread referenced in the prompt |
| Keep the inbox actionable | `mark_message_read` / `acknowledge_message` after handling |

Mail addressing and `SendMessage` addressing differ; when you need both, record both.

**Never send a message and wait for the reply.** A subagent's run ends when it returns, and a peer may be mid-bead for an hour. Post what peers need to know, then keep working — this is the rule that keeps coordination from becoming the work. Deliver a rejection or decision on both channels: mail for the durable record, then `SendMessage` or a respawn to make work actually resume.

## Stale locks

A reservation nobody releases blocks the next session. Before ending a session, release everything you hold. When you find a lock whose owner looks gone, confirm the owner's session ended and its mail is silent before calling `force_release_file_reservation` — force-releasing a live agent's lock is how two agents end up in the same file.

## Orchestrator specifics

The orchestrator registers with `task_description="Orchestrator for <epic-id>"`, records the returned name as `ORCH_NAME`, and threads all epic mail on `<epic-id>`. After the final phase it broadcasts the epic summary (bead summaries, deliverables) to every participating agent on that thread, then verifies no reservations remain held for the project. Worker reservation flow and rejection routing are in [verification.md](../orchestrator/references/verification.md).
