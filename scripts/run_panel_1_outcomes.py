"""
PANEL-1: Outcome Vocabulary Resolution
========================================

Classifies unresolved outcome terms through panel resolution.

Primary source: data/unresolved_outcomes.jsonl (4,080 terms)
Fallback: Regex scan of extraction files

Steps:
1. Load unresolved terms from queue (or scan extractions)
2. Filter against existing vocab (112 terms)
3. Cluster similar terms
4. Feed batches through PanelResolver with outcome_vocab config
5. Output: proposed vocab additions as JSON

Usage:
    python scripts/run_panel_1_outcomes.py --dry-run     # Heuristic only
    python scripts/run_panel_1_outcomes.py --apply        # Full panel (LLM)
"""

import json
import logging
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
VOCAB_PATH = PROJECT_ROOT / "contracts" / "outcome_vocab" / "outcome_vocab.json"
UNRESOLVED_QUEUE = PROJECT_ROOT / "data" / "unresolved_outcomes.jsonl"
OUTPUT_DIR = PROJECT_ROOT / "data" / "panel_results"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# Step 1A: Harvest from Unresolved Queue (Primary)
# =============================================================================

def harvest_from_queue() -> Tuple[Counter, Dict[str, List[str]]]:
    """Load unresolved terms directly from the queue file.
    
    Returns same format as harvest_outcome_terms for compatibility.
    """
    existing_names: Set[str] = set()
    if VOCAB_PATH.exists():
        with open(VOCAB_PATH) as f:
            vocab = json.load(f)
        for t in vocab.get("terms", []):
            existing_names.add(t["name"].lower().strip())
            existing_names.add(t["term_id"].lower().strip())
            for c in t.get("cognates", []):
                existing_names.add(c.lower().strip())
    
    term_counts = Counter()
    term_sources = defaultdict(list)
    
    with open(UNRESOLVED_QUEUE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception as e:
                logger.debug(f"Skipped: {e}")
                continue
            
            raw = entry.get("raw_term", "").strip().lower()
            if not raw or raw in existing_names or not _is_valid_term(raw):
                continue
            
            term_counts[raw] += 1
            paper = entry.get("paper_id", "unknown")
            if paper not in term_sources[raw]:
                term_sources[raw].append(paper)
    
    logger.info(f"Loaded {len(term_counts)} unique terms from queue ({sum(term_counts.values())} total)")
    return term_counts, dict(term_sources)


# =============================================================================
# Step 1B: Harvest from Extraction Files (Fallback)
# =============================================================================

# Structured field names that contain outcomes
OUTCOME_FIELDS = [
    "outcomes", "measures", "dependent_variables", "dvs",
    "outcome_measures", "outcome_variables", "measurement_instruments",
    "dependent_measures", "measured_outcomes",
]

# Patterns for outcome-like text in findings
OUTCOME_TEXT_PATTERNS = [
    # "measured X using Y"
    re.compile(r'(?:measured|assessed|evaluated|recorded)\s+(.{5,40}?)\s+(?:using|with|via|by)', re.I),
    # "X was the outcome/DV"
    re.compile(r'(.{5,40}?)\s+(?:was|were|as)\s+(?:the\s+)?(?:primary\s+)?(?:outcome|dependent\s+variable|DV|endpoint)', re.I),
    # "outcome: X"
    re.compile(r'(?:outcome|DV|endpoint|measure)[\s:]+([A-Za-z][\w\s\-]{3,35}?)(?:[,;.\"\'\]])', re.I),
]

# Known noise terms to filter out
NOISE_TERMS = {
    "results", "data", "measures", "values", "scores", "levels",
    "ratings", "responses", "variables", "parameters", "conditions",
    "participants", "subjects", "samples", "groups", "trials",
    "the", "a", "an", "of", "in", "for", "to", "and", "or",
    "after", "before", "during", "between", "among", "from",
    "this", "that", "these", "those", "their", "its",
}


def harvest_outcome_terms(max_files: int = 0) -> Tuple[Counter, Dict[str, List[str]]]:
    """Scan extraction files for outcome terms.
    
    Returns:
        (term_counts, term_sources) where:
        - term_counts: Counter of term → frequency
        - term_sources: Dict of term → [source file list]
    """
    # Load existing vocab for filtering
    existing_names: Set[str] = set()
    if VOCAB_PATH.exists():
        with open(VOCAB_PATH) as f:
            vocab = json.load(f)
        for t in vocab.get("terms", []):
            existing_names.add(t["name"].lower().strip())
            existing_names.add(t["term_id"].lower().strip())
            for c in t.get("cognates", []):
                existing_names.add(c.lower().strip())
    
    term_counts = Counter()
    term_sources = defaultdict(list)
    files_scanned = 0
    
    extraction_files = sorted(EXTRACTIONS_DIR.glob("*.json"))
    if max_files:
        extraction_files = extraction_files[:max_files]
    
    for ef in extraction_files:
        try:
            with open(ef) as f:
                data = json.load(f)
        except Exception as e:
            logger.debug(f"Skipped: {e}")
            continue
        files_scanned += 1
        source = ef.stem
        
        # Method 1: Extract from structured fields
        if isinstance(data, dict):
            for field_name in OUTCOME_FIELDS:
                items = data.get(field_name, [])
                if isinstance(items, list):
                    for item in items:
                        term = _extract_term(item)
                        if term and term not in existing_names and _is_valid_term(term):
                            term_counts[term] += 1
                            if source not in term_sources[term]:
                                term_sources[term].append(source)
        
        # Method 2: Extract from findings text
        findings = []
        if isinstance(data, dict):
            findings = data.get("findings", [])
        elif isinstance(data, list):
            findings = data
        
        for finding in findings:
            text = finding if isinstance(finding, str) else json.dumps(finding)
            for pattern in OUTCOME_TEXT_PATTERNS:
                for m in pattern.finditer(text):
                    term = m.group(1).strip().lower()
                    term = re.sub(r'\s+', ' ', term).strip('., ')
                    if term and term not in existing_names and _is_valid_term(term):
                        term_counts[term] += 1
                        if source not in term_sources[term]:
                            term_sources[term].append(source)
    
    logger.info(f"Scanned {files_scanned} files, found {len(term_counts)} unique candidates")
    return term_counts, dict(term_sources)


def _extract_term(item) -> str:
    """Extract a term string from various item formats."""
    if isinstance(item, str):
        return item.strip().lower()
    elif isinstance(item, dict):
        for key in ["name", "measure", "term", "variable", "outcome", "label"]:
            if key in item and isinstance(item[key], str):
                return item[key].strip().lower()
    return ""


def _is_valid_term(term: str) -> bool:
    """Filter out noise terms."""
    if len(term) < 4 or len(term) > 50:
        return False
    if term in NOISE_TERMS:
        return False
    if all(w in NOISE_TERMS for w in term.split()):
        return False
    # Must contain at least one alpha character
    if not re.search(r'[a-z]', term):
        return False
    # Filter out terms that are just articles/prepositions
    if re.match(r'^(?:the|a|an|in|on|at|to|of|for|by|with)\s', term):
        term_rest = re.sub(r'^(?:the|a|an|in|on|at|to|of|for|by|with)\s+', '', term)
        if len(term_rest) < 3:
            return False
    return True


# =============================================================================
# Step 2: Cluster Similar Terms
# =============================================================================

def cluster_terms(term_counts: Counter) -> Dict[str, List[str]]:
    """Group similar terms into clusters.
    
    Returns: Dict of canonical_term → [variant1, variant2, ...]
    """
    terms = sorted(term_counts.keys())
    clusters = {}
    assigned = set()
    
    for term in terms:
        if term in assigned:
            continue
        
        # Find similar terms
        cluster = [term]
        for other in terms:
            if other == term or other in assigned:
                continue
            if _terms_similar(term, other):
                cluster.append(other)
        
        # Pick canonical form (most frequent)
        canonical = max(cluster, key=lambda t: term_counts[t])
        clusters[canonical] = cluster
        assigned.update(cluster)
    
    return clusters


def _terms_similar(a: str, b: str) -> bool:
    """Check if two terms are similar enough to cluster."""
    # Exact substring
    if a in b or b in a:
        return True
    
    # Shared stem (first 5 chars)
    if len(a) >= 5 and len(b) >= 5 and a[:5] == b[:5]:
        return True
    
    # Singular/plural
    if a + 's' == b or b + 's' == a:
        return True
    if a + 'es' == b or b + 'es' == a:
        return True
    
    return False


# =============================================================================
# Step 3: Build Panel Items
# =============================================================================

# Domain hints for routing
DOMAIN_HINTS = {
    # Affect/emotion
    "stress": "affect", "anxiety": "affect", "mood": "affect",
    "wellbeing": "affect", "well-being": "affect", "happiness": "affect",
    "satisfaction": "affect", "pleasure": "affect", "comfort": "affect",
    "emotion": "affect", "affect": "affect", "arousal": "affect",
    "valence": "affect", "annoyance": "affect", "irritation": "affect",
    "calm": "affect", "relax": "affect", "restorat": "affect",
    "discomfort": "affect", "fatigue": "affect", "boredom": "affect",
    # Cognitive
    "attention": "cog", "memory": "cog", "cognitive": "cog",
    "focus": "cog", "concentration": "cog", "performance": "cog",
    "creativity": "cog", "problem solving": "cog", "thinking": "cog",
    "mental": "cog", "learning": "cog", "executive": "cog",
    "reaction time": "cog", "working memory": "cog", "vigilance": "cog",
    # Behavioral
    "productivity": "behav", "engagement": "behav", "behavior": "behav",
    "wayfinding": "behav", "navigation": "behav", "movement": "behav",
    "absenteeism": "behav", "sick leave": "behav", "turnover": "behav",
    "time spent": "behav", "dwell time": "behav", "eye movement": "behav",
    # Preference/perception
    "preference": "pref", "choice": "pref", "rating": "pref",
    "beauty": "pref", "aesthetic": "pref", "attractive": "pref",
    "pleasantness": "pref", "liking": "pref", "appraisal": "pref",
    "perceived": "pref", "visual quality": "pref", "evaluation": "pref",
    # Physiological
    "heart rate": "physio", "cortisol": "physio", "eeg": "physio",
    "skin conductance": "physio", "blood pressure": "physio", "hrv": "physio",
    "alpha": "physio", "galvanic": "physio", "salivary": "physio",
    "pupil": "physio", "respiration": "physio", "emg": "physio",
    # Health
    "sleep": "health", "recovery": "health", "healing": "health",
    "pain": "health", "symptom": "health", "health": "health",
    "hospital": "health", "patient": "health", "clinical": "health",
    "illness": "health", "morbidity": "health",
    # Social
    "social": "social", "interaction": "social", "collaboration": "social",
    "privacy": "social", "crowding": "social", "communication": "social",
    "territory": "social", "personal space": "social",
    # Environmental/physical
    "temperature": "env", "thermal": "env", "noise": "env",
    "sound": "env", "acoustic": "env", "illuminan": "env",
    "daylight": "env", "air quality": "env", "ventilation": "env",
    "humidity": "env", "co2": "env", "glare": "env",
    "color temperature": "env", "cct": "env", "lux": "env",
}


def build_panel_items(clusters: Dict[str, List[str]], 
                      term_counts: Counter,
                      term_sources: Dict[str, List[str]]) -> List[Dict]:
    """Build items for PanelResolver from clustered terms."""
    # Load existing outcome vocab for options
    vocab_path = Path(__file__).resolve().parent.parent / "data" / "outcome_vocab.json"
    existing_vocab = []
    if vocab_path.exists():
        try:
            vocab_data = json.loads(vocab_path.read_text(encoding="utf-8"))
            if isinstance(vocab_data, list):
                existing_vocab = [v.get("id", v) if isinstance(v, dict) else str(v) for v in vocab_data]
            elif isinstance(vocab_data, dict):
                existing_vocab = list(vocab_data.keys())
        except Exception as e:
            logger.debug(f"Non-critical: {e}")
    
    # Build options list with explicit decision instructions
    decision_options = [
        {"id": "MAP_TO_EXISTING", "label": "Map to an existing canonical outcome term (specify which one in reasoning)"},
        {"id": "CREATE_NEW", "label": "Create a new canonical outcome term (the raw term is distinct and useful)"},
        {"id": "REJECT", "label": "Reject: too vague, noisy, or not a real outcome measure"},
    ]
    
    items = []
    
    for canonical, variants in sorted(clusters.items(), 
                                       key=lambda x: term_counts[x[0]], 
                                       reverse=True):
        total_freq = sum(term_counts[v] for v in variants)
        sources = []
        for v in variants:
            sources.extend(term_sources.get(v, []))
        sources = list(set(sources))[:5]  # Cap at 5
        
        # Guess domain
        domain_guess = "unknown"
        for keyword, domain in DOMAIN_HINTS.items():
            if keyword in canonical:
                domain_guess = domain
                break
        
        # Find most similar existing vocab terms for context
        similar_vocab = []
        canon_lower = canonical.lower()
        for v in existing_vocab:
            v_lower = v.lower() if isinstance(v, str) else str(v).lower()
            # Quick similarity: shared words
            canon_words = set(canon_lower.split())
            vocab_words = set(v_lower.replace("_", " ").replace(".", " ").split())
            if canon_words & vocab_words:
                similar_vocab.append(v)
        similar_vocab = similar_vocab[:10]  # Cap at 10 most similar
        
        vocab_context = ""
        if similar_vocab:
            vocab_context = f" Potentially similar existing terms: {', '.join(similar_vocab)}."
        elif existing_vocab:
            vocab_context = f" Existing vocab has {len(existing_vocab)} terms (none obviously similar)."
        
        items.append({
            "id": f"ov_{canonical.replace(' ', '_')[:30]}",
            "term": canonical,
            "variants": variants,
            "frequency": total_freq,
            "sources": sources,
            "domain_hint": domain_guess,
            "options": decision_options,
            "context": f"Found {total_freq} times across {len(sources)} papers. "
                       f"Variants: {', '.join(variants[:3])}.{vocab_context}",
        })
    
    return items


# =============================================================================
# Step 4: Run Panel (or Simulate)
# =============================================================================

def run_panel_dry(items: List[Dict]) -> Dict:
    """Dry run: classify without LLM using domain hints + heuristics."""
    results = {
        "map_to_existing": [],
        "create_new": [],
        "split": [],
        "reject_as_noise": [],
    }
    
    # Load existing vocab for matching
    existing_terms = {}
    if VOCAB_PATH.exists():
        with open(VOCAB_PATH) as f:
            vocab = json.load(f)
        for t in vocab.get("terms", []):
            existing_terms[t["term_id"]] = t
    
    for item in items:
        term = item["term"]
        freq = item["frequency"]
        domain = item["domain_hint"]
        
        # Heuristics
        if freq < 2 and domain == "unknown":
            results["reject_as_noise"].append({
                "term": term, "reason": "Low frequency + unknown domain",
                "frequency": freq,
            })
        elif domain != "unknown":
            # Check if similar to existing term in same domain
            mapped = False
            for tid, t in existing_terms.items():
                if t.get("domain") == domain:
                    tname = t["name"].lower()
                    if _terms_similar(term, tname):
                        results["map_to_existing"].append({
                            "term": term, "maps_to": tid,
                            "confidence": 0.7, "frequency": freq,
                        })
                        mapped = True
                        break
            
            if not mapped:
                results["create_new"].append({
                    "term": term,
                    "proposed_id": f"{domain}.{term.replace(' ', '_')[:20]}",
                    "proposed_domain": domain,
                    "frequency": freq,
                    "variants": item["variants"],
                    "confidence": 0.6,
                })
        else:
            results["reject_as_noise"].append({
                "term": term, "reason": "Cannot classify domain",
                "frequency": freq,
            })
    
    return results


def run_panel_live(items: List[Dict], batch_size: int = 50) -> Dict:
    """Live panel: use PanelResolver with LLM calls."""
    from src.services.ai_panel_resolver import PanelResolver, PanelConfig
    
    config = PanelConfig(
        panel_type="outcome_vocab",
        n_panelists=5,
        consensus_threshold=0.6,
        bulk_model="gemini-2.5-flash",
        dispute_model="claude-sonnet-4-20250514",
    )
    
    resolver = PanelResolver(config)
    all_decisions = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(items) + batch_size - 1) // batch_size
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)")
        result = resolver.resolve_batch(batch)
        for d in result.get("decisions", []):
            # Convert ResolutionResult to dict if needed
            if hasattr(d, "to_dict"):
                all_decisions.append(d.to_dict())
            elif isinstance(d, dict):
                all_decisions.append(d)
            else:
                all_decisions.append({"item_id": str(d), "decision": "unknown"})
        logger.info(f"  → Batch {batch_num} done, {len(all_decisions)} total decisions")
    
    # Sort decisions into categories
    results = {
        "map_to_existing": [],
        "create_new": [],
        "split": [],
        "reject_as_noise": [],
    }
    
    # Load existing vocab for matching
    vocab_path = Path(__file__).resolve().parent.parent / "data" / "outcome_vocab.json"
    existing_vocab_ids = set()
    if vocab_path.exists():
        try:
            vocab_data = json.loads(vocab_path.read_text(encoding="utf-8"))
            if isinstance(vocab_data, list):
                existing_vocab_ids = {(v.get("id", v) if isinstance(v, dict) else str(v)).lower() for v in vocab_data}
            elif isinstance(vocab_data, dict):
                existing_vocab_ids = {k.lower() for k in vocab_data.keys()}
        except Exception as e:
            logger.debug(f"Non-critical: {e}")
    
    for d in all_decisions:
        decision_raw = d.get("decision", "").strip()
        decision = decision_raw.lower()
        item_id = d.get("item_id", "")
        metadata = d.get("metadata", {})
        reasoning = metadata.get("reasoning", d.get("reasoning", ""))
        confidence = d.get("confidence", 0.5)
        
        # Find matching original item
        orig = None
        for it in items:
            if it["id"] == item_id:
                orig = it
                break
        
        term = orig["term"] if orig else item_id
        freq = orig.get("frequency", 1) if orig else 1
        
        # Classification logic — check explicit decision keywords first,
        # then check if the decision matches an existing vocab term
        if any(kw in decision for kw in ("map", "existing", "map_to_existing")):
            maps_to = metadata.get("maps_to", reasoning[:50] if reasoning else decision_raw)
            results["map_to_existing"].append({
                "term": term,
                "maps_to": maps_to,
                "confidence": confidence,
                "frequency": freq,
                "reasoning": reasoning,
            })
        elif any(kw in decision for kw in ("create", "new", "create_new")):
            domain = orig.get("domain_hint", "unknown") if orig else "unknown"
            results["create_new"].append({
                "term": term,
                "proposed_id": f"{domain}.{term.replace(' ', '_')[:20]}",
                "proposed_domain": domain,
                "frequency": freq,
                "variants": orig.get("variants", []) if orig else [],
                "confidence": confidence,
                "reasoning": reasoning,
            })
        elif "split" in decision:
            results["split"].append({
                "term": term,
                "confidence": confidence,
            })
        elif any(kw in decision for kw in ("reject", "noise", "vague", "discard")):
            results["reject_as_noise"].append({
                "term": term,
                "reason": reasoning or decision_raw,
                "frequency": freq,
                "decision_raw": decision_raw,
            })
        elif decision_raw in existing_vocab_ids or decision in existing_vocab_ids:
            # The LLM returned an existing vocab term directly as the decision
            results["map_to_existing"].append({
                "term": term,
                "maps_to": decision_raw,
                "confidence": confidence,
                "frequency": freq,
                "reasoning": reasoning,
            })
        elif decision not in ("", "unknown", "unparseable", "unresolved"):
            # Non-empty decision that doesn't match keywords — likely a new term suggestion
            domain = orig.get("domain_hint", "unknown") if orig else "unknown"
            results["create_new"].append({
                "term": term,
                "proposed_id": f"{domain}.{decision_raw.replace(' ', '_')[:20]}",
                "proposed_domain": domain,
                "frequency": freq,
                "variants": orig.get("variants", []) if orig else [],
                "confidence": confidence,
                "reasoning": reasoning,
                "decision_raw": decision_raw,
            })
        else:
            # Truly unresolved
            results["reject_as_noise"].append({
                "term": term,
                "reason": reasoning or decision_raw or "unresolved",
                "frequency": freq,
                "decision_raw": decision_raw,
            })
    
    return results


# =============================================================================
# Step 5: Generate Vocab Additions
# =============================================================================

def generate_vocab_additions(panel_results: Dict) -> List[Dict]:
    """Convert panel results to outcome_vocab.json format."""
    additions = []
    
    for item in panel_results.get("create_new", []):
        addition = {
            "term_id": item["proposed_id"],
            "name": item["term"].title(),
            "domain": item["proposed_domain"],
            "cognates": item.get("variants", []),
            "access_level": "reported",
            "operationalization_hint": "",
            "panel_confidence": item.get("confidence", 0.5),
            "source": "panel_1_auto",
            "frequency": item.get("frequency", 1),
        }
        additions.append(addition)
    
    return additions


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PANEL-1: Outcome Vocabulary Resolution")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true", help="Run with LLM calls")
    parser.add_argument("--max-files", type=int, default=0, help="Max extraction files to scan (0=all)")
    args = parser.parse_args()
    
    live = args.apply
    
    # Step 1: Harvest
    print("Step 1: Harvesting outcome terms...")
    if UNRESOLVED_QUEUE.exists():
        print(f"  Using queue: {UNRESOLVED_QUEUE}")
        term_counts, term_sources = harvest_from_queue()
    else:
        print(f"  Queue not found, scanning extraction files...")
        term_counts, term_sources = harvest_outcome_terms(max_files=args.max_files)
    print(f"  Found {len(term_counts)} unique candidates ({sum(term_counts.values())} total)")
    
    # Step 2: Cluster
    print("Step 2: Clustering similar terms...")
    clusters = cluster_terms(term_counts)
    print(f"  Clustered into {len(clusters)} groups")
    
    # Step 3: Build panel items
    print("Step 3: Building panel items...")
    items = build_panel_items(clusters, term_counts, term_sources)
    print(f"  {len(items)} items ready for panel")
    
    # Step 4: Run panel
    if live:
        print("Step 4: Running LIVE panel (LLM calls)...")
        results = run_panel_live(items)
    else:
        print("Step 4: Running DRY panel (heuristic classification)...")
        results = run_panel_dry(items)
    
    # Stats
    print(f"\nResults:")
    for action, items_list in results.items():
        if isinstance(items_list, list):
            print(f"  {action}: {len(items_list)}")
    
    # Step 5: Generate additions
    additions = generate_vocab_additions(results)
    print(f"\nProposed vocab additions: {len(additions)}")
    
    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    mode = "live" if live else "dry"
    
    output_path = OUTPUT_DIR / f"panel_1_results_{mode}.json"
    with open(output_path, "w") as f:
        json.dump({
            "panel": "PANEL-1",
            "mode": mode,
            "stats": {
                "terms_harvested": len(term_counts),
                "clusters": len(clusters),
                **{k: len(v) for k, v in results.items() if isinstance(v, list)},
            },
            "results": results,
            "proposed_additions": additions,
        }, f, indent=2, default=str)
    print(f"\nSaved to: {output_path}")
    
    # Show top additions
    if additions:
        print(f"\nTop 10 proposed additions:")
        for a in additions[:10]:
            print(f"  {a['term_id']:30s} [{a['domain']:8s}] freq={a['frequency']} — {a['name']}")
    else:
        # Show mapped terms instead
        mapped = results.get("map_to_existing", [])
        if mapped:
            print(f"\nTop mapped terms:")
            for m in mapped[:10]:
                print(f"  {m['term']:40s} → {m.get('maps_to', '?')}")

