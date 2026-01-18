#!/usr/bin/env python3
import sys, os, re, base64
from pathlib import Path

MARK = re.compile(r"^----- FILE PATH: (.+)$")
ENC_MARK = re.compile(r"^----- ENCODING: (.+)$")
START = "----- CONTENT START -----"
END = "----- CONTENT END -----"

def main(inp: str, outdir: str):
    root = Path(outdir)
    root.mkdir(parents=True, exist_ok=True)
    with open(inp, "r", encoding="utf-8", errors="ignore") as f:
        state = "seek"
        rel = None
        buf = []
        encoding = "plain"
        for line in f:
            line_nostrip = line  # keep original
            line = line.rstrip("\n")

            if state == "seek":
                m = MARK.match(line)
                if m:
                    rel = m.group(1)
                    buf = []
                    encoding = "plain"
                    state = "await_encoding_or_start"
                continue

            if state == "await_encoding_or_start":
                if line == START:
                    # legacy format: no explicit encoding => plain text
                    state = "collect"
                    continue
                m_enc = ENC_MARK.match(line)
                if m_enc:
                    encoding = m_enc.group(1).strip().lower()
                    state = "await_start"
                    continue
                # tolerate blank lines
                if not line.strip():
                    continue
                # Unexpected line; treat as plain and start collecting
                state = "collect"
                buf.append(line_nostrip)
                continue

            if state == "await_start":
                if line == START:
                    state = "collect"
                    continue
                # tolerate blank lines
                if not line.strip():
                    continue
                # Unexpected -> assume we've already started content
                state = "collect"
                buf.append(line_nostrip)
                continue

            if state == "collect":
                if line == END:
                    if rel is None:
                        continue
                    fp = root / rel
                    fp.parent.mkdir(parents=True, exist_ok=True)
                    if encoding == "base64":
                        data = base64.b64decode("".join(buf).encode("utf-8"))
                        with open(fp, "wb") as w:
                            w.write(data)
                        # fall through
                    else:
                        with open(fp, "w", encoding="utf-8") as w:
                            w.write("".join(buf))
                    # reset
                    state = "seek"
                    rel = None
                    buf = []
                    encoding = "plain"
                else:
                    buf.append(line_nostrip)

    print(f"Reconstructed files under {root}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: deconcat.py <concatenated.txt> <output_dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
