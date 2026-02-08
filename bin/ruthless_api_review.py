#!/usr/bin/env python3
"""
ruthless_api_review.py - Call ChatGPT and Gemini APIs for Ruthless System Review
=================================================================================

Sends the Article Eater source code + ruthless review prompt to external LLMs
and saves their critiques.

Usage:
    ./bin/ruthless_api_review.py                    # Both ChatGPT and Gemini
    ./bin/ruthless_api_review.py --chatgpt          # ChatGPT only
    ./bin/ruthless_api_review.py --gemini           # Gemini only
    ./bin/ruthless_api_review.py --quick            # Core files only (smaller context)

Environment Variables Required:
    OPENAI_API_KEY      - For ChatGPT/GPT-4
    GOOGLE_API_KEY      - For Gemini (or GEMINI_API_KEY)

Output:
    docs/RUTHLESS_CHATGPT_RESPONSE_YYYY-MM-DD.md
    docs/RUTHLESS_GEMINI_RESPONSE_YYYY-MM-DD.md
"""

from __future__ import annotations
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add repo root to path for imports
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app.services.llm import LLMClient


# Files to include in review (priority order)
CORE_FILES = [
    "src/services/web_of_belief.py",
    "src/services/extraction_to_web.py",
    "src/services/web_persistence.py",
]

EXTENDED_FILES = [
    "src/services/epistemic_causal_bridge.py",
    "src/services/social_epistemology.py",
    "src/services/scalable_coherence.py",
    "src/services/theory_matcher.py",
    "src/services/scope_extractor.py",
    "src/services/incremental_bn.py",
    "src/services/credibility_testing.py",
    "src/services/voi_search.py",
]

# Models to use
CHATGPT_MODEL = os.environ.get("RUTHLESS_CHATGPT_MODEL", "gpt-4-turbo-preview")
GEMINI_MODEL = os.environ.get("RUTHLESS_GEMINI_MODEL", "gemini-1.5-pro")


def load_file_contents(file_path: Path) -> str | None:
    """Load file contents, return None if file doesn't exist."""
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    return None


def build_review_payload(quick_mode: bool = False) -> str:
    """Build the combined source code payload for review."""
    files_to_include = CORE_FILES if quick_mode else CORE_FILES + EXTENDED_FILES

    sections = []
    total_lines = 0

    for rel_path in files_to_include:
        file_path = REPO_ROOT / rel_path
        content = load_file_contents(file_path)
        if content:
            line_count = len(content.splitlines())
            total_lines += line_count
            sections.append(f"# FILE: {rel_path} ({line_count} lines)\n```python\n{content}\n```\n")
            print(f"  Loaded: {rel_path} ({line_count} lines)")
        else:
            print(f"  Skipped (not found): {rel_path}")

    print(f"  Total: {total_lines} lines of code")

    return "\n".join(sections)


def load_ruthless_prompt() -> str:
    """Load the ruthless review prompt."""
    today = datetime.now().strftime("%Y-%m-%d")

    # Try today's prompt first
    prompt_paths = [
        REPO_ROOT / f"docs/RUTHLESS_REVIEW_PROMPT_V5_{today}.md",
        REPO_ROOT / "docs/RUTHLESS_REVIEW_PROMPT_V5_2026-02-08.md",
        REPO_ROOT / "Post_Quinean Setup/ruthless_prompts/RUTHLESS_SYSTEM_REVIEW_PROMPT_v3_2026_01_22.md",
    ]

    for path in prompt_paths:
        if path.exists():
            print(f"  Using prompt: {path.name}")
            return path.read_text(encoding="utf-8")

    raise FileNotFoundError("No ruthless review prompt found!")


def call_chatgpt(client: LLMClient, system_prompt: str, code_payload: str) -> str:
    """Call ChatGPT API with ruthless review."""
    print(f"\nCalling ChatGPT ({CHATGPT_MODEL})...")
    print("  (This may take 1-3 minutes for a thorough review)")

    response = client.complete_openai(
        model=CHATGPT_MODEL,
        system=system_prompt,
        user=f"Here is the Article Eater source code to review:\n\n{code_payload}\n\nProvide your ruthless critique following the prompt instructions.",
        temperature=0.3,  # Slightly higher for creative critique
        max_tokens=8192,
    )

    return response


def call_gemini(client: LLMClient, system_prompt: str, code_payload: str) -> str:
    """Call Gemini API with ruthless review."""
    print(f"\nCalling Gemini ({GEMINI_MODEL})...")
    print("  (This may take 1-3 minutes for a thorough review)")

    response = client.complete_gemini(
        model=GEMINI_MODEL,
        system=system_prompt,
        user=f"Here is the Article Eater source code to review:\n\n{code_payload}\n\nProvide your ruthless critique following the prompt instructions.",
        temperature=0.3,
        max_tokens=8192,
    )

    return response


def save_response(name: str, response: str) -> Path:
    """Save API response to docs/ directory."""
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = REPO_ROOT / f"docs/RUTHLESS_{name.upper()}_RESPONSE_{today}.md"

    # Add header
    full_content = f"""# Ruthless Review Response: {name}

**Date**: {today}
**Model**: {CHATGPT_MODEL if name.lower() == 'chatgpt' else GEMINI_MODEL}
**Generated by**: ruthless_api_review.py

---

{response}
"""

    output_path.write_text(full_content, encoding="utf-8")
    print(f"  Saved: {output_path.name}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Run ruthless review via ChatGPT/Gemini APIs")
    parser.add_argument("--chatgpt", action="store_true", help="Call ChatGPT only")
    parser.add_argument("--gemini", action="store_true", help="Call Gemini only")
    parser.add_argument("--quick", action="store_true", help="Use core files only (smaller context)")
    args = parser.parse_args()

    # If neither specified, do both
    do_chatgpt = args.chatgpt or (not args.chatgpt and not args.gemini)
    do_gemini = args.gemini or (not args.chatgpt and not args.gemini)

    print("=" * 60)
    print("Article Eater Ruthless API Review")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Check API keys
    client = LLMClient()

    if do_chatgpt and not client.openai_key:
        print("\nERROR: OPENAI_API_KEY not set. Skipping ChatGPT.")
        do_chatgpt = False

    if do_gemini and not client.google_key:
        print("\nERROR: GOOGLE_API_KEY/GEMINI_API_KEY not set. Skipping Gemini.")
        do_gemini = False

    if not do_chatgpt and not do_gemini:
        print("\nNo API keys available. Set OPENAI_API_KEY and/or GOOGLE_API_KEY.")
        sys.exit(1)

    # Load prompt and code
    print("\nLoading ruthless review prompt...")
    system_prompt = load_ruthless_prompt()

    print("\nLoading source files...")
    code_payload = build_review_payload(quick_mode=args.quick)

    results = []

    # Call APIs
    if do_chatgpt:
        try:
            response = call_chatgpt(client, system_prompt, code_payload)
            output_path = save_response("ChatGPT", response)
            results.append(("ChatGPT", output_path, True))
        except Exception as e:
            print(f"  ERROR: ChatGPT failed - {e}")
            results.append(("ChatGPT", None, False))

    if do_gemini:
        try:
            response = call_gemini(client, system_prompt, code_payload)
            output_path = save_response("Gemini", response)
            results.append(("Gemini", output_path, True))
        except Exception as e:
            print(f"  ERROR: Gemini failed - {e}")
            results.append(("Gemini", None, False))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, path, success in results:
        if success:
            print(f"  {name}: SUCCESS -> {path.name}")
        else:
            print(f"  {name}: FAILED")

    print("\nReview the responses in docs/ directory.")
    print("Compare ChatGPT vs Gemini findings for alignment.")


if __name__ == "__main__":
    main()
