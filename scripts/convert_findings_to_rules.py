#!/usr/bin/env python3
"""
Convert extracted findings (JSONL) to rules (ae.rule.v2 schema).

This script reads all *_findings.jsonl files from data/extracted_findings/
and converts them to rules in ae.rule.v2 format, storing them in data/rules.jsonl.

Created: 2026-02-11
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Any

# Paths
FINDINGS_DIR = Path(__file__).parent.parent / "data" / "extracted_findings"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "rules.jsonl"


def normalize_var_name(text: str) -> str:
    """Convert text to a normalized variable name (e.g., 'env.lighting.daylight')."""
    # Simple normalization: lowercase, replace spaces with underscores
    clean = text.lower().strip()
    clean = clean.replace(" ", "_").replace("-", "_")
    # Remove special characters
    clean = "".join(c for c in clean if c.isalnum() or c == "_")
    return clean


def classify_var_domain(var_text: str) -> str:
    """Classify a variable into a domain prefix (env, cog, aff, phys, etc.)."""
    var_lower = var_text.lower()

    # Environment/stimulus variables
    env_keywords = [
        "light", "sound", "noise", "material", "texture", "color", "colour",
        "space", "room", "building", "architecture", "glass", "wood", "stone",
        "temperature", "humidity", "air", "ventilation", "view", "nature",
        "shadow", "illumination", "lux", "curtain", "wall", "office",
        "seasonal", "aged", "weathered", "VR", "virtual"
    ]

    # Cognitive/perceptual variables
    cog_keywords = [
        "perception", "attention", "memory", "cognition", "processing",
        "awareness", "recognition", "judgment", "decision", "pitch",
        "auditory", "visual", "spatial", "experience"
    ]

    # Affective/emotional variables
    aff_keywords = [
        "emotion", "mood", "affect", "feeling", "stress", "anxiety",
        "depression", "SAD", "well-being", "wellbeing", "comfort",
        "nostalgia", "safety", "satisfaction"
    ]

    # Physiological variables
    phys_keywords = [
        "heart", "cortisol", "blood", "sleep", "circadian", "physiological",
        "antidepressant", "therapy", "treatment"
    ]

    # Theoretical/framework variables
    theory_keywords = [
        "biophilia", "hypothesis", "theory", "framework", "sustainability",
        "biomimicry", "crossmodal", "synaesthetic", "multisensory"
    ]

    for kw in env_keywords:
        if kw in var_lower:
            return "env"
    for kw in cog_keywords:
        if kw in var_lower:
            return "cog"
    for kw in aff_keywords:
        if kw in var_lower:
            return "aff"
    for kw in phys_keywords:
        if kw in var_lower:
            return "phys"
    for kw in theory_keywords:
        if kw in var_lower:
            return "theory"

    return "misc"


def map_polarity(direction: str) -> str:
    """Map finding measure_direction to rule polarity."""
    mapping = {
        "positive": "positive",
        "negative": "negative",
        "unknown": "unknown",
        "null": "null",
        "u_shaped": "u_shaped"
    }
    return mapping.get(direction, "unknown")


def determine_rule_type(finding: dict) -> str:
    """Determine the rule type based on finding characteristics."""
    article_type = finding.get("article_type", "").lower()

    # Theoretical critiques become rebuttals
    if "critique" in article_type or "rebuttal" in article_type:
        return "rebuttal"

    # Theoretical frameworks become presumptions
    if "theoretical" in article_type or "framework" in article_type:
        return "presumption"

    # Case studies and design theses are associations (observational)
    if "case" in article_type or "design" in article_type:
        return "association"

    # Reviews are often about contrasts
    if "review" in article_type:
        return "edge"

    # Empirical validation studies show edges
    if "empirical" in article_type or "clinical" in article_type:
        return "edge"

    # Methodological papers
    if "method" in article_type:
        return "constraint"

    return "edge"  # Default


def determine_causal_level(finding: dict) -> str:
    """Determine Pearl's causal level based on finding characteristics."""
    article_type = finding.get("article_type", "").lower()
    finding_text = finding.get("finding_text", "").lower()

    # Experimental/intervention studies
    intervention_markers = ["treatment", "therapy", "intervention", "exposure", "manipulation"]
    for marker in intervention_markers:
        if marker in finding_text or marker in article_type:
            return "intervention"

    # Counterfactual reasoning
    counterfactual_markers = ["would", "if", "hypothetical", "could have"]
    for marker in counterfactual_markers:
        if marker in finding_text:
            return "counterfactual"

    # Default is associational (observational)
    return "association"


def extract_population_setting(finding: dict) -> tuple[list, list]:
    """Extract population and setting hints from finding text."""
    text = finding.get("finding_text", "").lower()
    quote = finding.get("quote", "").lower()
    combined = text + " " + quote

    populations = []
    settings = []

    # Population hints
    pop_hints = {
        "adult": "adults",
        "women": "women",
        "men": "men",
        "office_worker": "office_workers",
        "user": "building_users",
        "occupant": "building_occupants",
        "general": "general_population"
    }

    # Setting hints
    setting_hints = {
        "office": "office",
        "building": "building",
        "hospital": "healthcare",
        "residential": "residential",
        "urban": "urban",
        "indoor": "indoor",
        "outdoor": "outdoor",
        "europe": "central_europe"
    }

    for keyword, pop_id in pop_hints.items():
        if keyword in combined:
            populations.append({"id": pop_id})

    for keyword, setting_id in setting_hints.items():
        if keyword in combined:
            settings.append({"id": setting_id})

    # Default if none found
    if not populations:
        populations = [{"id": "general_population"}]
    if not settings:
        settings = [{"id": "general"}]

    return populations, settings


def finding_to_rule(finding: dict, rule_index: int) -> dict:
    """Convert a single finding to a rule in ae.rule.v2 format."""
    paper_id = finding.get("paper_id", "unknown")
    rule_id = f"{paper_id}#r{rule_index:02d}"

    # Build LHS from antecedents
    lhs = []
    for antecedent in finding.get("antecedents", []):
        domain = classify_var_domain(antecedent)
        var_name = f"{domain}.{normalize_var_name(antecedent)}"
        lhs.append({"var": var_name, "state": "present"})

    # Build RHS from consequent
    consequent = finding.get("consequent", "unknown_outcome")
    domain = classify_var_domain(consequent)
    var_name = f"{domain}.{normalize_var_name(consequent)}"
    rhs = [{"var": var_name, "state": "affected"}]

    # Get polarity
    polarity = map_polarity(finding.get("measure_direction", "unknown"))

    # Build strength from statistics
    stats = finding.get("statistics", {})
    strength = {"kind": "qualitative"}
    if stats.get("effect_size") is not None:
        strength = {
            "kind": "effect_size",
            "type": stats.get("effect_size_type"),
            "value": stats.get("effect_size")
        }
    elif stats.get("p_value") is not None:
        strength = {
            "kind": "significance",
            "type": "p_value",
            "value": stats.get("p_value")
        }

    # Get population and setting
    population, setting = extract_population_setting(finding)

    # Build applicability
    applicability = {
        "population": population,
        "setting": setting,
        "boundary_conditions": []
    }

    # BN mapping suggestions
    bn_nodes = []
    for item in lhs:
        bn_nodes.append(item["var"].split(".")[0] + "." + item["var"].split(".")[-1])
    for item in rhs:
        bn_nodes.append(item["var"].split(".")[0] + "." + item["var"].split(".")[-1])
    bn_nodes = list(set(bn_nodes))  # deduplicate

    bn_mapping = {
        "node_suggestions": bn_nodes[:4],  # limit to 4
        "discretization_hint": "low/med/high"
    }

    # Calculate AE confidence based on available evidence
    ae_confidence = 0.5  # base confidence
    if stats.get("p_value") is not None:
        ae_confidence += 0.15
    if stats.get("effect_size") is not None:
        ae_confidence += 0.15
    if stats.get("sample_size") is not None:
        ae_confidence += 0.1
    if finding.get("quote"):
        ae_confidence += 0.05
    ae_confidence = min(ae_confidence, 0.95)

    # Build the rule
    rule = {
        "schema": "ae.rule.v2",
        "rule_id": rule_id,
        "paper_id": paper_id,
        "rule_type": determine_rule_type(finding),
        "lhs": lhs,
        "rhs": rhs,
        "polarity": polarity,
        "strength": strength,
        "applicability": applicability,
        "evidence_links": [{"claim_id": f"{paper_id}#c{rule_index:02d}"}],
        "bn_mapping": bn_mapping,
        "ae_confidence": round(ae_confidence, 2),
        "causal_level": determine_causal_level(finding),
        "argument_scheme": None,
        "critical_questions": [],
        "contrast_class": None,
        "difference_maker": None,
        "enabling_conditions": [],
        "bridge_type": None,
        # Provenance markers: these rules are abstract-derived and provisional
        "evidence_level": "abstract_finding_rule",
        "provenance_tier": "abstract_provisional",
        "requires_pdf_confirmation": True,
    }

    return rule


def convert_all_findings():
    """Convert all findings files to rules."""
    all_rules = []
    rule_counter = {}

    print(f"Reading findings from: {FINDINGS_DIR}")

    for findings_file in sorted(FINDINGS_DIR.glob("*_findings.jsonl")):
        print(f"  Processing: {findings_file.name}")

        with open(findings_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    finding = json.loads(line)
                    paper_id = finding.get("paper_id", "unknown")

                    # Track rule index per paper
                    if paper_id not in rule_counter:
                        rule_counter[paper_id] = 0
                    rule_counter[paper_id] += 1

                    rule = finding_to_rule(finding, rule_counter[paper_id])
                    all_rules.append(rule)
                except json.JSONDecodeError as e:
                    print(f"    Warning: Could not parse line: {e}")

    # Write rules to output file
    print(f"\nWriting {len(all_rules)} rules to: {OUTPUT_FILE}")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w") as f:
        for rule in all_rules:
            f.write(json.dumps(rule) + "\n")

    print(f"Done! Converted {len(all_rules)} findings to rules.")
    return all_rules


if __name__ == "__main__":
    rules = convert_all_findings()

    # Print summary
    print("\n=== Rule Summary ===")
    rule_types = {}
    causal_levels = {}
    for rule in rules:
        rt = rule["rule_type"]
        cl = rule["causal_level"]
        rule_types[rt] = rule_types.get(rt, 0) + 1
        causal_levels[cl] = causal_levels.get(cl, 0) + 1

    print("\nBy rule type:")
    for rt, count in sorted(rule_types.items()):
        print(f"  {rt}: {count}")

    print("\nBy causal level:")
    for cl, count in sorted(causal_levels.items()):
        print(f"  {cl}: {count}")
