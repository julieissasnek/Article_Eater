#!/usr/bin/env python3
"""
Extract text from a PDF file. Used by AG (Claude Code terminal) which
cannot read PDFs natively.

Usage:
    python3 scripts/pdf_to_text.py <pdf_path> [--output <txt_path>]

If --output is not specified, prints to stdout.
Requires: pip3 install pdfplumber --break-system-packages
"""
import sys
import argparse

def extract_text(pdf_path: str) -> str:
    try:
        import pdfplumber
    except ImportError:
        print("Installing pdfplumber...", file=sys.stderr)
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber", "--break-system-packages", "-q"])
        import pdfplumber

    parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            txt = page.extract_text()
            if txt:
                parts.append(f"--- PAGE {i+1} ---\n{txt}")
    return "\n\n".join(parts)

def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output", "-o", help="Output text file (default: stdout)")
    args = parser.parse_args()

    text = extract_text(args.pdf_path)

    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
        print(f"Extracted {len(text)} chars to {args.output}", file=sys.stderr)
    else:
        print(text)

if __name__ == "__main__":
    main()
