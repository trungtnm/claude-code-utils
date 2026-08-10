# Agent Mail Protocol

Agent Mail carries live coordination: identity, file reservations, progress mail, rejections. It does not replace Task results or bead state.

## Registration

Agent Mail calls are MCP calls, not shell. A `$VAR` argument does not expand; it becomes a garbage key and a private mailbox where no other agent's reservations are visible, with no error. Echo the value first and paste the literal string:

```bash
git rev-parse --show-toplevel   # e.g. /Users/you/code/myrepo
```

```
macro_start_session(
  human_key="/Users/you/code/myrepo",   # the literal repo root you just echoed
  program="claude-code",
  task_description="Orchestrator for <epic-id>"
)
```

- Names are auto-generated adjective+noun pairs (`TopazRiver`). Do not pass a custom name; capture `agent.name` from the response as `ORCH_NAME`.
- Open the contact policy so worker contact requests auto-accept: `set_contact_policy(agent_name=ORCH_NAME, policy="open")`.
- `list_contacts()` shows peers already active on this repo, including sessions you did not start. Their reservations are live; your workers must respect them.

Every worker registers under the same literal repo root. The key is what makes reservations mutually visible.

## File reservations

A worker reserves the paths it will touch before editing (`file_reservation_paths`) and releases them when the bead lands (`release_file_reservations`). The reservation is the only mechanical lock in the shared tree. A failed reservation names the holder; the worker stops and reports the conflict.

On a conflict, resolve the cause:

| Cause | Resolution |
| --- | --- |
| Both beads need the path | The graph is missing an edge. `br dep add <blocked> <blocker>`, run them sequentially |
| The requesting worker's change is unnecessary | Reject per [verification.md](verification.md) |
| The holder is a dead agent | `force_release_file_reservation`, only after its Task returned and its mail is silent |

## Message semantics

| Need | Call |
| --- | --- |
| Durable record that survives the agent's exit | `send_message` / `reply_message` on thread `<epic-id>` |
| Resume a live agent | `SendMessage(to=<harness agent id>)` |
| Resume an exited agent | Respawn with the mail thread referenced in the prompt |
| Keep the inbox actionable | `mark_message_read` / `acknowledge_message` after handling |

A subagent's run ends when it returns. Never instruct an agent to send a message and wait for the reply. Deliver a rejection or decision on both channels: mail for the durable record, then `SendMessage` or a respawn to make work actually resume. The mailed record is what makes a respawn cheap — the new agent reads the thread and has the full history.

## Completion broadcast

After the final phase, `send_message` the epic summary (bead summaries, deliverables) to every participating agent on thread `<epic-id>`. Then verify `file_reservation_paths()` returns nothing held for this project; a stale lock blocks the next session. Force-release only reservations whose owners are confirmed gone.
