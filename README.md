# Acorn prototype

Open **http://127.0.0.1:8765** while the local server is running.

## Try it

1. Add your first medicine → Scan a prescription label → Try the sample label.
2. The sample passes through real Apple Vision OCR. Review and confirm the draft, then confirm the schedule.
3. Return to Forest and record taken or missed. Try the clearing and the structured JSON export.
4. Use the scenario controls for ambiguous PRN directions and missing clock time.
5. Import an image or PDF to explore the limited parser. Use synthetic data for demonstrations.

The seeded Forest and all built-in medication examples are fictional. The parser supports English oral tablet/capsule directions taken once to four times daily, with optional clock times and course length. Unsupported directions are held, not scheduled. This is not a clinical product.

## Run again

From this folder, on macOS with Swift Command Line Tools and Python 3:

```sh
swiftc -module-cache-path /tmp/acorn-swift-cache ocr.swift -o ocr
./ocr --sample sample-label.png
python3 server.py
```

The server binds only to 127.0.0.1:8765. No Python packages or cloud credentials are required. Fonts load from Google Fonts; medication files are sent only to the local server. Uploaded files are temporarily held on disk for reading and deleted afterward. Schedule data stays in browser memory until the user explicitly downloads JSON. Reloading clears it.

## Files

- `ANALYSIS.md`: comprehensive product critique, structural rationale, research, architecture and next steps.
- `index.html`, `styles.css`, `app.js`: interactive prototype.
- `server.py`, `ocr.swift`: local extraction pipeline.
- `sample-label.png`: fictional pharmacy label.
- `storyboard.svg`, `figma-screens/`: editable vector screen handoff.
- `FIGMA-HANDOFF.md`: tokens, screen connections and implementation notes.

Claude is completing the native Figma file at https://www.figma.com/design/hJ1fXuN9vmmoMX3mk1v6Wa while Codex owns this implementation. The local SVGs are importable design artifacts, not a claim that Figma interactions are already wired. The browser prototype is the working interactive deliverable.
