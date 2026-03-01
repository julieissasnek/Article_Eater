"""Theory Link Extraction Prompts for CMR-SPEC Section 3.5.

This module provides structured prompts for LLM-based theory link extraction.
When given a paper's text and extracted findings, identifies which T1.5 and T2 theories
the findings relate to, returning structured theory link objects suitable for
ae.rule.v2.theory_links array.

Usage:
    from prompts.theory_link_extraction import (
        generate_theory_link_prompt,
        parse_theory_link_response,
        THEORY_ROSTER_SUMMARY
    )

    prompt = generate_theory_link_prompt(paper_text, findings_list)
    response_text = llm.generate(prompt)
    theory_links = parse_theory_link_response(response_text)
"""

import json
from pathlib import Path
from typing import Any, Optional


# ============================================================================
# THEORY ROSTER LOADING
# ============================================================================

def _load_theories() -> dict[str, dict[str, Any]]:
    """Load all T1.5 and T2 theories from data/theories/*.json.

    Returns:
        Dictionary mapping theory_id -> theory object
    """
    theories_dir = Path(__file__).parent.parent / "data" / "theories"
    theories = {}

    if not theories_dir.exists():
        raise FileNotFoundError(f"Theories directory not found: {theories_dir}")

    for theory_file in sorted(theories_dir.glob("*.json")):
        try:
            with open(theory_file, "r") as f:
                theory = json.load(f)
                theory_id = theory.get("theory_id")
                if theory_id:
                    theories[theory_id] = theory
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load {theory_file}: {e}")

    return theories


# Load theories once at module init
_THEORIES_CACHE = _load_theories()


def get_theory_roster() -> dict[str, dict[str, Any]]:
    """Get the loaded theory roster.

    Returns:
        Dictionary mapping theory_id -> theory object
    """
    return _THEORIES_CACHE


# ============================================================================
# THEORY ROSTER SUMMARY
# ============================================================================

def _build_theory_roster_summary() -> str:
    """Build a formatted summary of all T1.5 and T2 theories for prompts.

    Returns:
        Formatted string listing theories with IDs and brief descriptions
    """
    theories = get_theory_roster()

    if not theories:
        return "(No theories loaded)"

    lines = ["CANONICAL THEORY ROSTER (T1.5 and T2 Theories):", "=" * 60]

    # Sort theories alphabetically by theory_id
    for theory_id in sorted(theories.keys()):
        theory = theories[theory_id]
        name = theory.get("name", "Unknown")
        originator = theory.get("originator", "Unknown")
        lines.append(f"  {theory_id}: {name}")
        if originator:
            lines.append(f"      (Originator: {originator})")

    return "\n".join(lines)


# Build roster summary once at module init
THEORY_ROSTER_SUMMARY = _build_theory_roster_summary()


# ============================================================================
# SYSTEM AND EXTRACTION PROMPTS
# ============================================================================

THEORY_LINK_SYSTEM_PROMPT = """You are an expert epistemologist specializing in theory alignment.

Your task: Given a research finding, identify which theoretical frameworks (T1.5 and T2 theories)
from a canonical roster best explain or predict that finding.

Theory Levels:
- T1: Neural-Architecture Mapping (10 Tier-1 frameworks grounded in neuroscience)
- T1.5: Mid-Level Theories (~24 formal reductions bridging T1 and empirical phenomena)
- T2: Architectural Theories (domain-specific, less mechanistically explicit)

Your job is to identify T1.5 and T2 theories ONLY (not T1 frameworks directly).

For each finding-theory pair you identify:
1. Verify the theory actually applies (not speculative)
2. Map variables from the finding to the theory's terminology
3. Assess maturity: how-actually (empirically established), how-plausibly (theoretically coherent), or how-possibly (speculative)
4. Classify the relationship: supports, contradicts, extends, or qualifies the theory

Return valid JSON only. No markdown, no explanations, no code blocks."""


THEORY_LINK_EXTRACTION_PROMPT = """Extract theory links from the following finding(s) in the context of this paper.

{theory_roster}

PAPER TEXT:
{paper_text}

FINDINGS (in canonical form):
{findings_json}

For each finding, identify which theories predict or explain it. Return a JSON object:

{{
  "theory_links": [
    {{
      "finding_id": "f1",
      "theory_id": "PROCESSING_FLUENCY",
      "from_variable": "visual_complexity",
      "to_variable": "aesthetic_preference",
      "from_level": "T1.5",
      "to_level": "T1.5",
      "activity": "supports",
      "maturity": "how-actually",
      "rationale": "Brief explanation of why this theory applies to this finding"
    }}
  ]
}}

SCHEMA REQUIREMENTS:

1. finding_id: Exactly matches a finding_id from FINDINGS above
2. theory_id: MUST be from the CANONICAL THEORY ROSTER above (case-sensitive)
3. from_variable: Independent variable in theory's canonical form
4. to_variable: Dependent variable in theory's canonical form
5. from_level: T1, T1.5, or T2 (be accurate to the theory's hierarchy)
6. to_level: T1, T1.5, or T2 (be accurate to the theory's hierarchy)
7. activity: One of: supports, contradicts, extends, qualifies
   - supports: finding aligns with theory's predictions
   - contradicts: finding conflicts with theory's predictions
   - extends: finding expands theory's scope beyond original claims
   - qualifies: finding adds boundary conditions or moderators
8. maturity: One of: how-actually, how-plausibly, how-possibly
   - how-actually: empirically established in the literature
   - how-plausibly: theoretically coherent but not yet empirically validated
   - how-possibly: speculative connection

CRITICAL RULES:

1. Only include theory_ids that appear in the CANONICAL THEORY ROSTER
2. Each finding may have 0, 1, or multiple theory links
3. Do not invent theories or theory_ids
4. If a finding has no clear theoretical connection, omit it from theory_links
5. Be conservative: prefer how-actually and how-plausibly over how-possibly
6. Map variables to the theory's own terminology (not the paper's)
7. Return valid JSON only; no explanations outside the JSON object

FEW-SHOT EXAMPLES:

Example 1 (Processing Fluency):
  Finding: "Visual complexity increases aesthetic preference (r=.45, p<.001)"
  Theory Link:
    {{
      "finding_id": "f1",
      "theory_id": "PROCESSING_FLUENCY",
      "from_variable": "visual_complexity",
      "to_variable": "aesthetic_preference",
      "from_level": "T1.5",
      "to_level": "T1.5",
      "activity": "supports",
      "maturity": "how-actually",
      "rationale": "Processing Fluency theory predicts that moderate complexity enhances aesthetic judgment via fluency signals. This empirical finding aligns with core theory predictions."
    }}

Example 2 (Biophilia):
  Finding: "Exposure to plant images reduces cortisol levels (Cohen's d=0.62, p<.01)"
  Theory Link:
    {{
      "finding_id": "f2",
      "theory_id": "BIOPHILIA",
      "from_variable": "biotic_presence_score",
      "to_variable": "stress_reduction",
      "from_level": "T2",
      "to_level": "T2",
      "activity": "supports",
      "maturity": "how-actually",
      "rationale": "Biophilia theory (Wilson, Kellert) predicts innate stress reduction from nature exposure. This cortisol reduction directly supports the theory's core mechanism."
    }}

Example 3 (Prospect-Refuge with Qualifier):
  Finding: "Spatial openness increases preference for young adults (β=.38) but decreases preference for older adults (β=-.21)"
  Theory Links:
    [
      {{
        "finding_id": "f3",
        "theory_id": "PROSPECT_REFUGE",
        "from_variable": "spatial_openness",
        "to_variable": "spatial_preference",
        "from_level": "T1.5",
        "to_level": "T1.5",
        "activity": "qualifies",
        "maturity": "how-actually",
        "rationale": "Prospect-Refuge theory predicts preference for moderate openness (balance of prospect and refuge). This finding qualifies the theory: the optimal openness level depends on age."
      }}
    ]

Example 4 (No Clear Theory Connection):
  Finding: "Font size affects reading speed (r=.72, p<.001)"
  Theory Links: [] (no theory applies; font size is ergonomic, not architectural or psychological)"""


# ============================================================================
# FUNCTIONS
# ============================================================================

def generate_theory_link_prompt(
    paper_text: str,
    findings: list[dict[str, Any]],
) -> str:
    """Generate a complete theory link extraction prompt.

    Args:
        paper_text: Full text of the paper to analyze
        findings: List of finding dicts with keys: finding_id, content, ...
                 (from prior extraction step)

    Returns:
        Complete prompt ready for LLM
    """
    # Convert findings to JSON for the prompt
    findings_json = json.dumps(findings, indent=2)

    prompt = THEORY_LINK_EXTRACTION_PROMPT.format(
        theory_roster=THEORY_ROSTER_SUMMARY,
        paper_text=paper_text[:5000],  # Truncate to keep prompt reasonable
        findings_json=findings_json,
    )

    return prompt


def parse_theory_link_response(response_text: str) -> list[dict[str, Any]]:
    """Parse LLM response JSON, validate against canonical theory roster.

    Args:
        response_text: Raw LLM response text

    Returns:
        List of validated theory link dicts, or empty list on parse error

    Raises:
        ValueError: If response contains invalid theory_ids or malformed JSON
    """
    # Try to extract JSON from response
    # (handles cases where LLM wraps response in markdown code blocks)
    response_text = response_text.strip()

    # Remove markdown code block markers if present
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response_text[:200]}")

    # Extract theory_links array
    if not isinstance(data, dict):
        raise ValueError(f"Response root must be an object, got {type(data)}")

    theory_links = data.get("theory_links", [])
    if not isinstance(theory_links, list):
        raise ValueError(f"theory_links must be an array, got {type(theory_links)}")

    # Validate each theory link
    theories = get_theory_roster()
    valid_links = []

    for i, link in enumerate(theory_links):
        if not isinstance(link, dict):
            raise ValueError(f"theory_links[{i}] must be an object, got {type(link)}")

        # Validate required fields
        required_fields = ["finding_id", "theory_id", "activity", "maturity"]
        for field in required_fields:
            if field not in link:
                raise ValueError(f"theory_links[{i}] missing required field: {field}")

        # Validate theory_id exists in canonical roster
        theory_id = link["theory_id"]
        if theory_id not in theories:
            raise ValueError(
                f"theory_links[{i}] invalid theory_id '{theory_id}' "
                f"(not in canonical roster of {len(theories)} theories)"
            )

        # Validate enum fields
        valid_activities = {"supports", "contradicts", "extends", "qualifies"}
        if link["activity"] not in valid_activities:
            raise ValueError(
                f"theory_links[{i}] invalid activity '{link['activity']}' "
                f"(must be one of {valid_activities})"
            )

        valid_maturities = {"how-actually", "how-plausibly", "how-possibly"}
        if link["maturity"] not in valid_maturities:
            raise ValueError(
                f"theory_links[{i}] invalid maturity '{link['maturity']}' "
                f"(must be one of {valid_maturities})"
            )

        valid_levels = {"T1", "T1.5", "T2"}
        if "from_level" in link and link["from_level"] not in valid_levels:
            raise ValueError(
                f"theory_links[{i}] invalid from_level '{link['from_level']}' "
                f"(must be one of {valid_levels})"
            )
        if "to_level" in link and link["to_level"] not in valid_levels:
            raise ValueError(
                f"theory_links[{i}] invalid to_level '{link['to_level']}' "
                f"(must be one of {valid_levels})"
            )

        valid_links.append(link)

    return valid_links


def validate_theory_roster() -> dict[str, int]:
    """Validate that theory roster loaded successfully.

    Returns:
        Dict with validation results: {
            "total_theories": int,
            "theory_ids": list of theory_ids,
        }
    """
    theories = get_theory_roster()
    return {
        "total_theories": len(theories),
        "theory_ids": sorted(theories.keys()),
    }
