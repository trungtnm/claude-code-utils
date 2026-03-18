Append an idea or observation to `.ccu/CAPTURES.md` for later triage. Supports text, images, and document files. This should take less than 10 seconds.

**Capture: `$ARGUMENTS`**

## Steps

1. **Ensure .ccu/ exists** — If `.ccu/` doesn't exist, create it and initialize `CAPTURES.md`. Ensure gitignore rules are in place for ephemeral files.

2. **Handle input type:**

   **Text only** — Append directly to `.ccu/CAPTURES.md`:
   ```
   - [ ] {YYYY-MM-DD HH:MM} — {$ARGUMENTS}
   ```

   **Image or document file** (screenshot, photo, diagram, PDF, markdown) — If the user pastes an image or provides a file:
   - Read/view the file to understand its content
   - Write a brief text summary of what it shows
   - **MUST copy the file to `.ccu/captures/`** — pasted images live in temp paths that get deleted. Run:
     ```bash
     mkdir -p .ccu/captures
     cp "{source_path}" ".ccu/captures/{YYYY-MM-DD-HH-MM}-{descriptive-name}.{ext}"
     ```
     The source path is the temporary file path shown in the conversation (e.g., `/tmp/...` or `/var/folders/...`). If you can see the file but don't have a path, ask the user for it.
   - Append to CAPTURES.md:
     ```
     - [ ] {YYYY-MM-DD HH:MM} — {text summary} [attachment: .ccu/captures/{filename}]
     ```

   If no argument or file was provided, ask the user what they want to capture.

3. **Confirm** — Report: "Captured. {N} total untriaged items in queue."

## Rules

- **Fast and non-disruptive** — do not investigate, analyze, or act on the capture. Just record it.
- **No duplicate checking** — just append. Deduplication happens during triage.
- **No formatting** — write the capture text exactly as the user said it. Don't rewrite or improve it.
- **Summarize attachments** — images and documents get a brief text summary so CAPTURES.md is scannable without opening files.
- **Preserve originals** — always copy (not move) attached files to `.ccu/captures/`.
