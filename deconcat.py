#!/usr/bin/env python3
"""
Robust deconcatenation tool for Article Eater overlay / full dumps.

Format per file:

----- FILE PATH: relative/path
----- ENCODING: plain|base64
----- CONTENT START -----
<file contents or base64 blob>
----- CONTENT END -----

- FILE PATH line must appear at the start of a line.
- ENCODING line is optional; defaults to "plain" if omitted.
- For ENCODING=plain, content is written as UTF-8 text.
- For ENCODING=base64, content is base64-decoded and written as binary.
"""

import sys
import base64
from pathlib import Path
from typing import List, Optional


MARK_PATH = "----- FILE PATH:"
MARK_ENCODING = "----- ENCODING:"
MARK_START = "----- CONTENT START -----"
MARK_END = "----- CONTENT END -----"


def _flush_file(rel_path: str, encoding: str, content_lines: List[str]) -> None:
    """Write one file to disk from buffered lines."""
    if not rel_path:
        return
    target = Path(rel_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    if encoding == "base64":
        # Join lines without newlines; base64 is whitespace-insensitive
        blob = "".join(content_lines).strip()
        data = base64.b64decode(blob.encode("ascii"))
        with open(target, "wb") as f:
            f.write(data)
    else:
        # Default: plain UTF-8 text, preserve original newlines
        text = "".join(content_lines)
        target.write_text(text, encoding="utf-8")


def deconcat(txt_path: str, out_dir: Optional[str] = None) -> None:
    """Reconstruct files from a concatenated dump."""
    src = Path(txt_path)
    if out_dir:
        # Change working directory for reconstruction
        out_root = Path(out_dir)
        out_root.mkdir(parents=True, exist_ok=True)
    else:
        out_root = Path(".")

    # Read as UTF-8. The concatenator is responsible for ensuring UTF-8
    # safety (e.g. by base64-encoding binary blobs).
    data = src.read_text(encoding="utf-8")

    current_path: Optional[str] = None
    current_encoding: str = "plain"
    current_content: List[str] = []
    in_content = False

    def flush():
        nonlocal current_path, current_encoding, current_content
        if current_path is not None:
            rel = current_path.strip()
            if rel:
                # Ensure we write under out_root
                rel_path = out_root / rel
                rel_path.parent.mkdir(parents=True, exist_ok=True)
                if current_encoding == "base64":
                    blob = "".join(current_content).strip()
                    data_bytes = base64.b64decode(blob.encode("ascii"))
                    with open(rel_path, "wb") as f:
                        f.write(data_bytes)
                else:
                    rel_path.write_text("".join(current_content), encoding="utf-8")
        current_path = None
        current_encoding = "plain"
        current_content = []

    for line in data.splitlines(keepends=True):
        # Start of a new file
        if line.startswith(MARK_PATH):
            # Flush previous file, if any
            if in_content:
                flush()
                in_content = False
            # Parse path after marker
            current_path = line[len(MARK_PATH):].strip()
            current_encoding = "plain"
            current_content = []
            continue

        # Optional encoding line (must immediately follow FILE PATH)
        if line.startswith(MARK_ENCODING):
            # Example: "----- ENCODING: base64"
            enc = line[len(MARK_ENCODING):].strip().lstrip(":").strip()
            current_encoding = enc or "plain"
            continue

        # Start of content block
        if line.strip() == MARK_START:
            in_content = True
            current_content = []
            continue

        # End of content block
        if line.strip() == MARK_END:
            flush()
            in_content = False
            continue

        # Regular line: if we are inside content, buffer it
        if in_content and current_path is not None:
            current_content.append(line)

    # Flush trailing file if stream didn't end with MARK_END
    if in_content and current_path is not None:
        flush()


def main(argv: list) -> None:
    if len(argv) < 2 or len(argv) > 3:
        print("Usage: python deconcat.py <dump.txt> [output_dir]")
        raise SystemExit(1)
    txt_path = argv[1]
    out_dir = argv[2] if len(argv) == 3 else None
    deconcat(txt_path, out_dir)
    print("Reconstruction complete.")


if __name__ == "__main__":
    main(sys.argv)
