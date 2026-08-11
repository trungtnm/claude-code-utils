---
name: capture
description: Append an idea or observation to .ccu/CAPTURES.md for later triage
argument-hint: [idea text, image, or file path]
---

Append an idea or observation to `.ccu/CAPTURES.md` for later triage. Supports text, images, and document files. This should take less than 10 seconds.

**Capture: `$ARGUMENTS`**

## Steps

1. **Ensure .ccu/ exists** — If `.ccu/` doesn't exist, create it and initialize `CAPTURES.md`. Ensure gitignore rules are in place for ephemeral files.

2. **Handle input type:**

   **Text only** — Append directly to `.ccu/CAPTURES.md`:
   ```
   - [ ] C{NN} | {YYYY-MM-DD HH:MM} — {$ARGUMENTS}
   ```
   Where `{NN}` is the next sequential number (count existing `C{NN}` entries + 1, starting from `C01`). If no IDs exist yet in the file, start at `C01`.

   **Image or document file** (screenshot, photo, diagram, PDF, markdown) — If the user pastes an image or provides a file:

   First, determine the source type by checking the file path:
   - **Claude Code clipboard image** — path is under `~/.claude/image-cache/` (e.g., `~/.claude/image-cache/{uuid}/{N}.png`). These are stable files — `cp` works reliably.
   - **Pasted screenshot** — path contains `NSIRD_screencaptureui` or is under `/private/var/folders/.../T/TemporaryItems/`. These are ephemeral — macOS deletes them before Bash can access them.
   - **Dragged/referenced file** — any other path (e.g., `~/Screenshots/...`, `~/Desktop/...`, project-relative paths). Stable — `cp` works reliably.

   **For clipboard images and dragged/referenced files** (stable paths — copy works reliably):
   ```bash
   mkdir -p .ccu/captures && cp "{source_path}" ".ccu/captures/{YYYY-MM-DD-HH-MM}-{descriptive-name}.{ext}"
   ```
   Then read the saved copy with the **Read tool** and write a brief text summary.

   **For pasted screenshots** (macOS temp paths — file is deleted before Bash can access it):
   1. Use the **Read tool** on the temp path immediately — this is the ONLY way to see pasted screenshots, as the Read tool processes the image synchronously before macOS deletes the temp file.
   2. Write a **detailed text summary** of what the image shows. Be specific: UI elements, text content, layout, error messages, data values — enough to understand the image without seeing it.
   3. Do NOT attempt `cp` — it will always fail with `FileNotFoundError` for pasted screenshots. The text summary is the capture.
   4. Tell the user: "Image captured as text summary. To also save the file, drag the image from Finder instead of pasting."

   Append to CAPTURES.md (with the next sequential `C{NN}` ID):
   - With saved file: `- [ ] C{NN} | {YYYY-MM-DD HH:MM} — {summary} [attachment: .ccu/captures/{filename}]`
   - Text-only (pasted screenshot): `- [ ] C{NN} | {YYYY-MM-DD HH:MM} — [screenshot] {detailed summary}`

   If no argument or file was provided, ask the user what they want to capture.

3. **Confirm** — Report: "Captured. {N} total untriaged items in queue."

## Rules

- **Fast and non-disruptive** — do not investigate, analyze, or act on the capture. Just record it.
- **No duplicate checking** — just append. Deduplication happens during triage.
- **No formatting** — write the capture text exactly as the user said it. Don't rewrite or improve it.
- **Summarize attachments** — images and documents get a brief text summary so CAPTURES.md is scannable without opening files.
- **Preserve originals** — for dragged/referenced files, always copy (not move) to `.ccu/captures/`.
- **Clipboard images from `~/.claude/image-cache/` CAN be saved** — these are stable files that persist. Always `cp` them to `.ccu/captures/`. They are NOT ephemeral like pasted screenshots.
- **Pasted screenshots (macOS temp paths) cannot be saved as files** — macOS deletes temp files before Bash runs. Use the Read tool for visual analysis, then capture as a detailed text summary. Never retry `cp` on pasted screenshot paths — it will always fail.
