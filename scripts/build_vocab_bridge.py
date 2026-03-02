#!/usr/bin/env python3
"""
Build vocabulary bridge between DB environment_ids/outcome_ids and template frameworks.

This script:
1. Extracts all unique environment_id and outcome_id values from findings
2. Extracts framework mappings from all 166 templates
3. Creates a mapping using token overlap, substring matching, and semantic similarity
4. Outputs data/vocab_bridge.json for use by enrichment script
"""

import json
import os
import re
from collections import defaultdict
from difflib import SequenceMatcher

def normalize_token(token):
    """Normalize a token for comparison."""
    # Remove common prefixes/suffixes
    token = re.sub(r'^(env_|out_|outcome_)', '', token)
    token = re.sub(r'^(unresolved_|generic_)', '', token)
    token = token.lower().strip()
    return token

def tokenize(s):
    """Split a string into normalized tokens."""
    # Split on underscores and camelCase
    s = re.sub(r'([a-z])([A-Z])', r'\1_\2', s)
    tokens = re.split(r'[_\-\s]+', s.lower().strip())
    return [t for t in tokens if t and len(t) > 1]

def token_overlap_score(db_id, template_frameworks):
    """Compute token overlap between db_id and framework names."""
    db_tokens = set(tokenize(db_id))

    if not db_tokens:
        return {}

    scores = {}
    for framework in template_frameworks:
        fw_tokens = set(tokenize(framework))

        if not fw_tokens:
            continue

        # Jaccard similarity
        overlap = len(db_tokens & fw_tokens)
        union = len(db_tokens | fw_tokens)

        if union > 0 and overlap > 0:
            score = overlap / union
            if score > 0.2:  # Lowered threshold
                scores[framework] = score

    return scores

def substring_match_score(db_id, template_frameworks):
    """Match using substring relationships."""
    scores = {}
    db_normalized = normalize_token(db_id).replace('_', '')

    for framework in template_frameworks:
        fw_normalized = normalize_token(framework).replace('_', '').replace('-', '')

        # Check if one is substring of other
        if db_normalized in fw_normalized or fw_normalized in db_normalized:
            scores[framework] = 0.85
        # Check if they share significant prefix
        elif db_normalized[:4] == fw_normalized[:4] and len(db_normalized) > 3:
            scores[framework] = 0.65

    return scores

def fuzzy_match_score(db_id, template_frameworks):
    """Use sequence matching for fuzzy matches."""
    scores = {}
    db_normalized = normalize_token(db_id)

    for framework in template_frameworks:
        fw_normalized = normalize_token(framework)

        # SequenceMatcher based similarity
        ratio = SequenceMatcher(None, db_normalized, fw_normalized).ratio()

        if ratio >= 0.6:
            scores[framework] = ratio * 0.8  # Scale down to avoid double-counting

    return scores

def merge_scores(score_dicts, weights):
    """Merge multiple score dictionaries with weights."""
    merged = defaultdict(float)

    for score_dict, weight in zip(score_dicts, weights):
        for framework, score in score_dict.items():
            merged[framework] = max(merged[framework], score * weight)

    return dict(merged)

def build_environment_mappings(env_ids, template_frameworks_by_id):
    """Build mapping from environment_ids to frameworks."""
    mappings = {}

    for env_id in env_ids:
        if not env_id or env_id == '':
            continue

        # Collect all frameworks from all templates
        all_frameworks = []
        for template_id, frameworks in template_frameworks_by_id.items():
            all_frameworks.extend(frameworks)

        all_frameworks = list(set(all_frameworks))  # deduplicate

        if not all_frameworks:
            continue

        # Compute scores using multiple strategies
        token_scores = token_overlap_score(env_id, all_frameworks)
        substring_scores = substring_match_score(env_id, all_frameworks)
        fuzzy_scores = fuzzy_match_score(env_id, all_frameworks)

        # Merge with weights: token overlap is most reliable
        merged = merge_scores(
            [token_scores, substring_scores, fuzzy_scores],
            [0.50, 0.35, 0.20]  # Prioritize token overlap
        )

        # Only keep matches above threshold (lowered)
        if merged:
            best_matches = sorted(
                merged.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]  # Top 5 matches

            mappings[env_id] = [
                {"framework": fw, "confidence": float(score)}
                for fw, score in best_matches
                if score >= 0.35  # Lowered threshold
            ]

    return mappings

def build_outcome_mappings(outcome_ids, template_frameworks_by_id):
    """Build mapping from outcome_ids to frameworks."""
    mappings = {}

    for outcome_id in outcome_ids:
        if not outcome_id or outcome_id == '':
            continue

        # Collect all frameworks
        all_frameworks = []
        for template_id, frameworks in template_frameworks_by_id.items():
            all_frameworks.extend(frameworks)

        all_frameworks = list(set(all_frameworks))

        if not all_frameworks:
            continue

        # Compute scores
        token_scores = token_overlap_score(outcome_id, all_frameworks)
        substring_scores = substring_match_score(outcome_id, all_frameworks)
        fuzzy_scores = fuzzy_match_score(outcome_id, all_frameworks)

        # Merge with weights
        merged = merge_scores(
            [token_scores, substring_scores, fuzzy_scores],
            [0.50, 0.35, 0.20]
        )

        if merged:
            best_matches = sorted(
                merged.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            mappings[outcome_id] = [
                {"framework": fw, "confidence": float(score)}
                for fw, score in best_matches
                if score >= 0.35  # Lowered threshold
            ]

    return mappings

def load_findings(fpath):
    """Load findings and extract unique env/outcome IDs."""
    with open(fpath) as f:
        data = json.load(f)

    env_ids = set()
    outcome_ids = set()

    for resolution in data.get('resolutions', []):
        env = resolution.get('environment_id', '')
        outcome = resolution.get('outcome_id', '')

        if env and env != '':
            env_ids.add(env)
        if outcome and outcome != '':
            outcome_ids.add(outcome)

    return env_ids, outcome_ids

def load_templates(templates_dir):
    """Load all templates and extract framework mappings."""
    template_frameworks_by_id = {}
    template_frameworks_by_display = {}

    for fname in os.listdir(templates_dir):
        if not fname.endswith('.json'):
            continue

        fpath = os.path.join(templates_dir, fname)
        try:
            with open(fpath) as f:
                template = json.load(f)
        except Exception:  
            continue

        # Find framework field
        frameworks = None
        for key in ['frameworks', 'framework_ids', 't1_frameworks', 't1_5_parent_theories']:
            if key in template:
                frameworks = template[key]
                break

        if not frameworks:
            continue

        # Normalize frameworks to list
        if isinstance(frameworks, dict):
            frameworks = list(frameworks.keys())
        elif not isinstance(frameworks, list):
            frameworks = [frameworks]

        template_id = template.get('template_id', '')
        display_id = template.get('display_id', '')

        if template_id:
            template_frameworks_by_id[template_id] = frameworks
        if display_id:
            template_frameworks_by_display[display_id] = frameworks

    return template_frameworks_by_id, template_frameworks_by_display

def main():
    """Main entry point."""
    repo_root = '/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1'

    # Load findings
    findings_path = os.path.join(repo_root, 'data/production/finding_template_theory_links.json')
    print(f"Loading findings from {findings_path}...")
    env_ids, outcome_ids = load_findings(findings_path)
    print(f"  Found {len(env_ids)} unique environment_ids")
    print(f"  Found {len(outcome_ids)} unique outcome_ids")

    # Load templates
    templates_dir = os.path.join(repo_root, 'data/templates')
    print(f"\nLoading templates from {templates_dir}...")
    template_frameworks_by_id, template_frameworks_by_display = load_templates(templates_dir)
    print(f"  Loaded {len(template_frameworks_by_id)} template mappings")

    # Sample frameworks
    sample_frameworks = list(template_frameworks_by_id.values())[:5]
    print(f"  Sample frameworks: {sample_frameworks}")

    # Build mappings
    print(f"\nBuilding environment_id mappings...")
    env_mappings = build_environment_mappings(env_ids, template_frameworks_by_id)
    env_with_mappings = sum(1 for m in env_mappings.values() if m)
    print(f"  {env_with_mappings} / {len(env_ids)} environment_ids mapped")

    print(f"\nBuilding outcome_id mappings...")
    outcome_mappings = build_outcome_mappings(outcome_ids, template_frameworks_by_id)
    outcome_with_mappings = sum(1 for m in outcome_mappings.values() if m)
    print(f"  {outcome_with_mappings} / {len(outcome_ids)} outcome_ids mapped")

    # Show some examples
    print("\nExample environment_id mappings:")
    for env_id in sorted(env_ids)[:5]:
        if env_mappings.get(env_id):
            print(f"  {env_id}: {env_mappings[env_id]}")

    print("\nExample outcome_id mappings:")
    for outcome_id in sorted(outcome_ids)[:5]:
        if outcome_mappings.get(outcome_id):
            print(f"  {outcome_id}: {outcome_mappings[outcome_id]}")

    # Create bridge output
    bridge = {
        "metadata": {
            "created_at": __import__('datetime').datetime.now().isoformat(),
            "environment_ids_total": len(env_ids),
            "environment_ids_mapped": env_with_mappings,
            "outcome_ids_total": len(outcome_ids),
            "outcome_ids_mapped": outcome_with_mappings,
            "templates_total": len(template_frameworks_by_id),
        },
        "environment_mappings": env_mappings,
        "outcome_mappings": outcome_mappings,
        "template_frameworks": template_frameworks_by_id,
    }

    # Write output
    output_path = os.path.join(repo_root, 'data/vocab_bridge.json')
    print(f"\nWriting vocab bridge to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(bridge, f, indent=2)

    print("Done!")

if __name__ == '__main__':
    main()
