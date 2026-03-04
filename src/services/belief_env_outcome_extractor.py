"""
Belief Env/Outcome Extractor with Confidence Grading
=====================================================
Extracts structured environment_id and outcome_id from raw belief content text
using the FTR bridge vocabularies as target dictionaries. Each extraction is
graded with a confidence score (0-1) to prevent inaccuracy from creeping in.

Design principles:
  - Uses the canonical ENV_BRIDGES and OUTCOME_BRIDGES from FTR as target vocabulary
  - Multi-signal grading: term frequency, position, context quality, specificity
  - Only HIGH and MEDIUM confidence matches are written; LOW are logged for review
  - Extends FTR capacity by populating the empty env_id/outcome_id fields
  - Includes success conditions for health monitoring

Usage:
    # As module
    from src.services.belief_env_outcome_extractor import extract_env_outcome, grade_match

    # As script (run by CC/user since AG is sandboxed)
    python3 -m src.services.belief_env_outcome_extractor --db data/web_persistence.db

Authors: AG (March 2026), building on FTR by AG (Feb 2026)
"""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Import bridge dictionaries from FTR (single source of truth)
try:
    from src.services.finding_template_relevance import (
        ENV_BRIDGES,
        OUTCOME_BRIDGES,
        DOMAIN_KEYWORDS,
        _normalize,
        _tokenize,
    )
except ImportError:
    # Fallback for standalone execution
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from src.services.finding_template_relevance import (
        ENV_BRIDGES,
        OUTCOME_BRIDGES,
        DOMAIN_KEYWORDS,
        _normalize,
        _tokenize,
    )


# ============================================================================
# Confidence levels
# ============================================================================

class Confidence:
    HIGH = "HIGH"        # >=0.70 — safe to write to DB automatically
    MEDIUM = "MEDIUM"    # 0.45-0.69 — write but flag for review
    LOW = "LOW"          # 0.25-0.44 — log only, do not write
    NONE = "NONE"        # <0.25 — no match


CONFIDENCE_THRESHOLDS = {
    Confidence.HIGH: 0.70,
    Confidence.MEDIUM: 0.45,
    Confidence.LOW: 0.25,
}

# Threshold for writing to DB — only HIGH and MEDIUM
WRITE_THRESHOLD = CONFIDENCE_THRESHOLDS[Confidence.MEDIUM]


# ============================================================================
# Extended vocabulary: content patterns → bridge terms
# ============================================================================

# Maps raw content phrases to canonical env bridge keys
# These are patterns commonly found in belief content text
ENV_CONTENT_PATTERNS: Dict[str, List[str]] = {
    "has_nature_view": [
        r"nature\s*(?:view|exposure|scene|contact|element)",
        r"(?:window|view)\s*(?:of|to|with)\s*(?:tree|green|nature|garden|plant|forest)",
        r"biophil(?:ic|ia)\b",
        r"(?:green|natural)\s*(?:space|area|environment|setting)",
        r"(?:vegetation|plant|tree|garden|park|forest)\b",
    ],
    "ambient_noise_dba": [
        r"noise\s*(?:level|exposure|reduction|control|impact)",
        r"(?:ambient|background)\s*(?:noise|sound|acoustic)",
        r"(?:acoustic|sound)\s*(?:environment|quality|comfort|insulation|treatment)",
        r"\b(?:decibel|dba?|db\b|spl)\b",
        r"(?:sound\s*masking|speech\s*privacy|open[\s-]*plan\s*(?:office|noise))",
        r"(?:reverberation|rt60|echo|absorption\s*coefficient)",
    ],
    "illuminance_lux": [
        r"(?:natural|day)\s*light(?:ing)?",
        r"illumin(?:ance|ation)\b",
        r"\b(?:lux|luminance|candela)\b",
        r"(?:light|lamp|led|fluorescent)\s*(?:exposure|intensity|level|condition)",
        r"melanopic\b",
        r"(?:color|colour)\s*temperature\b",
        r"\bcct\b",
    ],
    "window_area_ratio": [
        r"window\s*(?:size|area|ratio|access|presence)",
        r"\bwindow(?:s)?\b",
        r"(?:daylight|light)\s*access\b",
        r"(?:window|glazing)\s*(?:to[\s-]*wall|area)\s*ratio",
        r"fenestration\b",
        r"presence\s*of\s*window",
    ],
    "ceiling_height_m": [
        r"ceiling\s*height\b",
        r"(?:room|space)\s*(?:height|volume)\b",
        r"(?:spatial|vertical)\s*(?:volume|openness|confinement)",
        r"double[\s-]*height\b",
    ],
    "primary_material": [
        r"(?:primary|building|construction|interior)\s*material",
        r"\b(?:wood|timber|concrete|stone|brick|metal|glass|steel)\s*(?:surface|material|wall|floor|panel)?",
        r"(?:material|surface)\s*(?:perception|quality|identity|authentic)",
        r"(?:haptic|tactile|texture|thermal)\s*(?:quality|property|feel|signal)",
        r"(?:flow\s*resistivity|absorption\s*coefficient|porosity)\b",
    ],
    "floor_area_m2": [
        r"(?:room|floor|space)\s*(?:size|area|dimension)\b",
        r"(?:spatial|room)\s*(?:extent|layout|configuration)\b",
        r"(?:square\s*(?:meter|metre|foot|feet)|m[²2]|ft[²2])",
    ],
    "time_of_day": [
        r"(?:time|period)\s*of\s*day\b",
        r"(?:morning|afternoon|evening|night|dawn|dusk)\s*(?:light|exposure|condition)?",
        r"circadian\s*(?:phase|rhythm|timing|cycle|entrainment)\b",
        r"(?:diurnal|nocturnal)\b",
    ],
    "color": [
        r"\b(?:color|colour)\s*(?:of|scheme|palette|environment|effect|perception)",
        r"\b(?:hue|saturation|chrominance|chromatic)\b",
        r"\b(?:warm|cool)\s*(?:color|colour|tone)\b",
        r"\b(?:red|blue|green|yellow|orange|purple|pink)\s*(?:wall|room|light|color|colour)?",
    ],
}

# Maps raw content phrases to canonical outcome bridge keys
OUTCOME_CONTENT_PATTERNS: Dict[str, List[str]] = {
    "attention": [
        r"(?:directed|sustained|selective)\s*attention\b",
        r"attention(?:al)?\s*(?:restoration|fatigue|control|depletion|capacity|performance|task)",
        r"(?:impair|reduc|diminish|disrupt)(?:s|ed|ing)?\s*(?:\w+\s+)?attention\b",
        r"(?:cognitive|mental)\s*(?:fatigue|depletion|exhaustion|restoration)\b",
        r"\b(?:concentration|focus|distraction|vigilance)\b",
    ],
    "stress": [
        r"\bstress\s*(?:reduction|recovery|response|level|marker|regulation|hormone)",
        r"\bcortisol\b",
        r"(?:physiological|psychological)\s*stress\b",
        r"(?:anxiety|fear|threat|panic|alarm)\s*(?:response|level|reduction)?",
        r"(?:hpa|hypothalamic[\s-]*pituitary)\b",
        r"(?:allostatic|autonomic)\s*(?:load|arousal|response)\b",
    ],
    "mood": [
        r"\bmood\s*(?:improvement|change|regulation|effect|valence|shift)",
        r"(?:improv|enhanc|boost|elevat)(?:es?|ing)?\s*mood\b",
        r"(?:positive|negative)\s*(?:affect|mood|emotion)\b",
        r"\b(?:panas|affect\s*schedule)\b",
        r"(?:happiness|sadness|joy|pleasure|displeasure|anger)\b",
        r"(?:emotional|affective)\s*(?:response|state|experience|well[\s-]*being)\b",
    ],
    "well_being": [
        r"(?:well[\s-]*being|wellbeing|wellness)\b",
        r"(?:quality|satisfaction)\s*(?:of|with)\s*(?:life|living)\b",
        r"(?:subjective|psychological|hedonic|eudaimonic)\s*(?:well[\s-]*being|wellness)\b",
        r"(?:mental|physical)\s*(?:health|wellness)\b",
        r"(?:restoration|restorative)\s*(?:outcome|effect|experience|quality)\b",
    ],
    "productivity": [
        r"(?:cognitive|work|task)\s*performance\b",
        r"\bproductivity\b",
        r"(?:executive|cognitive)\s*function(?:ing)?\b",
        r"(?:working)\s*memory\s*(?:load|capacity|performance)\b",
        r"(?:error|mistake)\s*(?:rate|proneness|frequency)\b",
        r"(?:decision|judgment)\s*(?:quality|efficiency|speed|accuracy)\b",
    ],
    "recovery_time": [
        r"(?:stress|fatigue|surgery|patient|hospital)\s*recovery\b",
        r"recov(?:ery|ering)\s*(?:time|rate|speed|duration)\b",
        r"(?:healing|convalescence|recuperation|rehabilitation)\b",
    ],
    "sleep_quality": [
        r"sleep\s*(?:quality|duration|onset|efficiency|latency|pattern|disruption)\b",
        r"(?:insomnia|somnolence|sleepiness)\b",
        r"(?:melatonin|circadian)\s*(?:rhythm|phase|production|level)\b",
    ],
    "creativity": [
        r"(?:creative|creativity|divergent)\s*(?:thinking|output|performance|ideation)",
        r"(?:brainstorm|incubation|insight|aha\s*moment)\b",
        r"(?:exploration|exploitation)\s*(?:balance|trade[\s-]*off)\b",
    ],
    "memory": [
        r"\bmemory\s*(?:performance|retrieval|consolidation|formation|recall)",
        r"(?:episodic|spatial|working)\s*memory\b",
        r"(?:recall|recognition|retention|forgetting)\s*(?:rate|performance|accuracy)?\b",
    ],
    "cognitive_load": [
        r"cognitive\s*(?:load|overload|burden|demand)\b",
        r"(?:mental|information)\s*(?:overload|load|demand)\b",
        r"(?:processing|attentional)\s*(?:resource|capacity|demand|load)\b",
    ],
    "visual_comfort": [
        r"visual\s*(?:comfort|discomfort|strain|fatigue|quality)\b",
        r"(?:glare|flicker|brightness)\s*(?:discomfort|sensitivity|perception)?\b",
    ],
    "preference": [
        r"(?:aesthetic|environmental|design)\s*(?:preference|judgment|evaluation|rating)\b",
        r"(?:beauty|attractiveness|appeal)\s*(?:perception|judgment|rating)?\b",
        r"(?:approach|avoidance)\s*(?:behavior|tendency|response)\b",
    ],
    "social_interaction": [
        r"(?:social)\s*(?:interaction|behavior|engagement|connection|cohesion|belonging)\b",
        r"(?:interpersonal|prosocial)\s*(?:behavior|contact|relationship|interaction)\b",
        r"(?:privacy|proxemic|territorial)\s*(?:regulation|behavior|comfort)\b",
        r"(?:loneliness|isolation|belonging|community)\b",
        r"sense\s*of\s*belonging\b",
    ],
    "physiological_arousal": [
        r"(?:physiological|autonomic|sympathetic|parasympathetic)\s*(?:arousal|response|activation)",
        r"(?:heart|pulse)\s*rate\b",
        r"(?:galvanic|electrodermal)\s*(?:skin|response|activity)\b",
        r"\b(?:hrv|gsr|eda|scr|sbp|dbp)\b",
    ],
    "thermal_comfort": [
        r"thermal\s*(?:comfort|discomfort|perception|sensation|satisfaction)\b",
        r"(?:temperature|thermal)\s*(?:preference|acceptance|neutrality)\b",
    ],
    "wayfinding": [
        r"wayfinding\s*(?:efficiency|performance|ability|difficulty)\b",
        r"(?:navigation|spatial)\s*(?:performance|orientation|cognition|efficiency)\b",
        r"(?:getting|being)\s*(?:lost|disoriented|confused)\b",
        r"\bnavigat(?:ion|e|ing)\b.*\b(?:complex|hospital|building|layout)\b",
    ],
    "reward": [
        r"(?:reward|pleasure|hedonic)\s*(?:response|value|signal|processing)\b",
        r"(?:dopamine|endorphin|opioid)\b",
    ],
    "restorativeness": [
        r"(?:perceived|subjective)\s*(?:restorativeness|restoration)\b",
        r"(?:restorative)\s*(?:environment|quality|experience|potential|effect)\b",
    ],
}


# ============================================================================
# Dataclasses
# ============================================================================

@dataclass
class ExtractionResult:
    """A single env or outcome extraction from belief content."""
    term: str                    # The canonical bridge key (e.g., "has_nature_view")
    confidence: float            # 0.0-1.0
    confidence_level: str        # HIGH, MEDIUM, LOW, NONE
    matching_patterns: List[str] # Which regex patterns matched
    matched_text: str            # The actual text that matched
    signal_details: Dict[str, float]  # Breakdown of confidence signals


@dataclass
class BeliefExtraction:
    """Full extraction result for a single belief."""
    belief_id: str
    content: str
    env_extractions: List[ExtractionResult]
    outcome_extractions: List[ExtractionResult]
    best_env_id: Optional[str] = None
    best_env_confidence: float = 0.0
    best_outcome_id: Optional[str] = None
    best_outcome_confidence: float = 0.0

    @property
    def is_writable(self) -> bool:
        """Whether at least one extraction meets the WRITE_THRESHOLD."""
        return (
            self.best_env_confidence >= WRITE_THRESHOLD
            or self.best_outcome_confidence >= WRITE_THRESHOLD
        )


@dataclass
class ExtractionReport:
    """Summary report with success condition grading."""
    total_beliefs: int = 0
    beliefs_with_env: int = 0
    beliefs_with_outcome: int = 0
    beliefs_with_both: int = 0
    beliefs_writable: int = 0    # Meet threshold for DB write

    high_confidence_env: int = 0
    medium_confidence_env: int = 0
    low_confidence_env: int = 0
    high_confidence_outcome: int = 0
    medium_confidence_outcome: int = 0
    low_confidence_outcome: int = 0

    # Success condition scores
    sc_coverage: float = 0.0       # SC-FTR-1: % beliefs with env or outcome
    sc_precision: float = 0.0      # SC-FTR-2: % writable that are HIGH confidence
    sc_env_coverage: float = 0.0   # SC-FTR-3: % beliefs with env_id
    sc_out_coverage: float = 0.0   # SC-FTR-4: % beliefs with outcome_id
    sc_bridge_util: float = 0.0    # SC-FTR-5: % of bridge vocabs used at least once

    timestamp: str = ""
    env_terms_used: Set[str] = field(default_factory=set)
    outcome_terms_used: Set[str] = field(default_factory=set)


# ============================================================================
# Core extraction functions
# ============================================================================

def _grade_confidence(signals: Dict[str, float]) -> Tuple[float, str]:
    """
    Compute confidence score from multiple signals.

    Signals:
      - pattern_count: how many regex patterns matched (0-1, scaled)
      - match_position: where in the content the match appears (earlier = better)
      - specificity: how specific the matched term is (multi-word > single-word)
      - context_quality: whether surrounding words support the match
      - uniqueness: whether only one env/outcome matched (reduces ambiguity)
    """
    weights = {
        "pattern_count": 0.30,
        "match_position": 0.10,
        "specificity": 0.25,
        "context_quality": 0.20,
        "uniqueness": 0.15,
    }

    score = sum(
        weights.get(key, 0.0) * min(1.0, max(0.0, value))
        for key, value in signals.items()
    )
    score = min(1.0, max(0.0, score))

    if score >= CONFIDENCE_THRESHOLDS[Confidence.HIGH]:
        level = Confidence.HIGH
    elif score >= CONFIDENCE_THRESHOLDS[Confidence.MEDIUM]:
        level = Confidence.MEDIUM
    elif score >= CONFIDENCE_THRESHOLDS[Confidence.LOW]:
        level = Confidence.LOW
    else:
        level = Confidence.NONE

    return score, level


def extract_term(
    content: str,
    patterns: Dict[str, List[str]],
    all_matches_count: int = 0,
) -> List[ExtractionResult]:
    """Extract terms from content text using regex patterns."""
    content_lower = content.lower()
    content_len = max(len(content_lower), 1)
    results: List[ExtractionResult] = []

    for term, regexes in patterns.items():
        matched_patterns = []
        matched_texts = []
        earliest_pos = content_len  # Track earliest match position

        for regex in regexes:
            try:
                matches = list(re.finditer(regex, content_lower))
                if matches:
                    matched_patterns.append(regex)
                    for m in matches:
                        matched_texts.append(m.group(0))
                        earliest_pos = min(earliest_pos, m.start())
            except re.error:
                continue

        if not matched_patterns:
            continue

        # Signal: pattern_count — more patterns matching = higher confidence
        pattern_ratio = len(matched_patterns) / max(len(regexes), 1)
        pattern_count_signal = min(1.0, pattern_ratio * 2.0)  # 2+ patterns → 1.0

        # Signal: match_position — matches early in content are more likely correct
        position_signal = 1.0 - (earliest_pos / content_len) * 0.5

        # Signal: specificity — longer matched text = more specific
        longest_match = max(matched_texts, key=len) if matched_texts else ""
        word_count = len(longest_match.split())
        specificity_signal = min(1.0, word_count / 3.0)  # 3+ words → 1.0

        # Signal: context_quality — check if related domain keywords are nearby
        content_tokens = _tokenize(content)
        domain_matches = 0
        for domain, keywords in DOMAIN_KEYWORDS.items():
            if content_tokens & keywords:
                domain_matches += 1
        context_signal = min(1.0, domain_matches / 3.0)

        # Signal: uniqueness — fewer total matches across all terms = less ambiguous
        uniqueness_signal = 1.0 if all_matches_count <= 2 else max(0.3, 1.0 - all_matches_count * 0.15)

        signals = {
            "pattern_count": pattern_count_signal,
            "match_position": position_signal,
            "specificity": specificity_signal,
            "context_quality": context_signal,
            "uniqueness": uniqueness_signal,
        }

        confidence, level = _grade_confidence(signals)

        if level != Confidence.NONE:
            results.append(ExtractionResult(
                term=term,
                confidence=round(confidence, 4),
                confidence_level=level,
                matching_patterns=matched_patterns,
                matched_text=longest_match,
                signal_details={k: round(v, 4) for k, v in signals.items()},
            ))

    # Sort by confidence descending
    results.sort(key=lambda r: -r.confidence)
    return results


def extract_env_outcome(
    belief_id: str,
    content: str,
) -> BeliefExtraction:
    """
    Extract environment_id and outcome_id from belief content.

    Returns a BeliefExtraction with graded confidence scores.
    Only HIGH and MEDIUM confidence matches should be written to DB.
    """
    # First pass: count total matches to inform uniqueness signal
    env_preliminary = extract_term(content, ENV_CONTENT_PATTERNS, all_matches_count=0)
    out_preliminary = extract_term(content, OUTCOME_CONTENT_PATTERNS, all_matches_count=0)

    total_matches = len(env_preliminary) + len(out_preliminary)

    # Second pass with uniqueness signal
    env_results = extract_term(content, ENV_CONTENT_PATTERNS, all_matches_count=total_matches)
    out_results = extract_term(content, OUTCOME_CONTENT_PATTERNS, all_matches_count=total_matches)

    extraction = BeliefExtraction(
        belief_id=belief_id,
        content=content,
        env_extractions=env_results,
        outcome_extractions=out_results,
    )

    if env_results:
        extraction.best_env_id = env_results[0].term
        extraction.best_env_confidence = env_results[0].confidence

    if out_results:
        extraction.best_outcome_id = out_results[0].term
        extraction.best_outcome_confidence = out_results[0].confidence

    return extraction


# ============================================================================
# Batch processing and DB integration
# ============================================================================

def process_beliefs_from_db(
    db_path: Path,
    dry_run: bool = True,
    write_threshold: float = WRITE_THRESHOLD,
) -> ExtractionReport:
    """
    Process all beliefs in a DB, extract env/outcome, optionally write back.

    Args:
        db_path: Path to web persistence DB
        dry_run: If True, don't write to DB (just report)
        write_threshold: Minimum confidence to write (default 0.45 / MEDIUM)

    Returns:
        ExtractionReport with success condition scores
    """
    report = ExtractionReport(timestamp=datetime.now(timezone.utc).isoformat())

    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()

        # Check table structure
        tables = {row[0] for row in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}

        if 'beliefs' not in tables:
            print(f"  ❌ No 'beliefs' table in {db_path}")
            return report

        # Get columns
        cols = {row[1] for row in cur.execute("PRAGMA table_info(beliefs)").fetchall()}

        # Ensure env/outcome columns exist
        if 'environment_id' not in cols:
            if not dry_run:
                cur.execute("ALTER TABLE beliefs ADD COLUMN environment_id TEXT DEFAULT ''")
                conn.commit()
            print("  Added environment_id column")

        if 'outcome_id' not in cols:
            if not dry_run:
                cur.execute("ALTER TABLE beliefs ADD COLUMN outcome_id TEXT DEFAULT ''")
                conn.commit()
            print("  Added outcome_id column")

        # Read all beliefs
        cur.execute("SELECT belief_id, content FROM beliefs")
        rows = cur.fetchall()
        report.total_beliefs = len(rows)

        extractions: List[BeliefExtraction] = []
        for belief_id, content in rows:
            if not content:
                continue
            extraction = extract_env_outcome(str(belief_id), str(content))
            extractions.append(extraction)

            # Track stats
            if extraction.best_env_id and extraction.best_env_confidence >= write_threshold:
                report.beliefs_with_env += 1
                report.env_terms_used.add(extraction.best_env_id)
                if extraction.env_extractions[0].confidence_level == Confidence.HIGH:
                    report.high_confidence_env += 1
                elif extraction.env_extractions[0].confidence_level == Confidence.MEDIUM:
                    report.medium_confidence_env += 1

            if extraction.env_extractions:
                best_env = extraction.env_extractions[0]
                if best_env.confidence_level == Confidence.LOW:
                    report.low_confidence_env += 1

            if extraction.best_outcome_id and extraction.best_outcome_confidence >= write_threshold:
                report.beliefs_with_outcome += 1
                report.outcome_terms_used.add(extraction.best_outcome_id)
                if extraction.outcome_extractions[0].confidence_level == Confidence.HIGH:
                    report.high_confidence_outcome += 1
                elif extraction.outcome_extractions[0].confidence_level == Confidence.MEDIUM:
                    report.medium_confidence_outcome += 1

            if extraction.outcome_extractions:
                best_out = extraction.outcome_extractions[0]
                if best_out.confidence_level == Confidence.LOW:
                    report.low_confidence_outcome += 1

            if (extraction.best_env_confidence >= write_threshold
                    and extraction.best_outcome_confidence >= write_threshold):
                report.beliefs_with_both += 1

            if extraction.is_writable:
                report.beliefs_writable += 1

        # Write to DB if not dry_run
        if not dry_run:
            written = 0
            for ext in extractions:
                updates = {}
                if ext.best_env_id and ext.best_env_confidence >= write_threshold:
                    updates['environment_id'] = ext.best_env_id
                if ext.best_outcome_id and ext.best_outcome_confidence >= write_threshold:
                    updates['outcome_id'] = ext.best_outcome_id

                if updates:
                    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
                    cur.execute(
                        f"UPDATE beliefs SET {set_clause} WHERE belief_id = ?",
                        list(updates.values()) + [ext.belief_id],
                    )
                    written += 1

            conn.commit()
            print(f"  ✅ Wrote env/outcome to {written} beliefs")

        # Compute success condition scores
        if report.total_beliefs > 0:
            report.sc_coverage = (
                (report.beliefs_with_env + report.beliefs_with_outcome)
                / (report.total_beliefs * 2)  # Normalize: both env+outcome per belief
            )
            report.sc_env_coverage = report.beliefs_with_env / report.total_beliefs
            report.sc_out_coverage = report.beliefs_with_outcome / report.total_beliefs

        writable_total = report.high_confidence_env + report.medium_confidence_env + \
                         report.high_confidence_outcome + report.medium_confidence_outcome
        high_total = report.high_confidence_env + report.high_confidence_outcome
        if writable_total > 0:
            report.sc_precision = high_total / writable_total

        total_bridge_terms = len(ENV_BRIDGES) + len(OUTCOME_BRIDGES)
        used_terms = len(report.env_terms_used) + len(report.outcome_terms_used)
        if total_bridge_terms > 0:
            report.sc_bridge_util = used_terms / total_bridge_terms

    finally:
        conn.close()

    return report


# ============================================================================
# Success Conditions
# ============================================================================

def check_success_conditions(report: ExtractionReport) -> List[Dict[str, Any]]:
    """
    Evaluate success conditions for env/outcome extraction health.

    Returns a list of success condition results.
    """
    conditions = []

    # SC-FTR-1: Overall coverage — at least 30% of beliefs should get env OR outcome
    coverage_pct = report.sc_coverage * 100
    conditions.append({
        "id": "SC-FTR-1",
        "name": "Extraction Coverage",
        "description": "At least 30% of beliefs have extracted env_id or outcome_id",
        "target": "≥30%",
        "actual": f"{coverage_pct:.1f}%",
        "passed": coverage_pct >= 30.0,
        "value": report.sc_coverage,
    })

    # SC-FTR-2: Precision — of writable matches, >50% should be HIGH confidence
    precision_pct = report.sc_precision * 100
    conditions.append({
        "id": "SC-FTR-2",
        "name": "Extraction Precision",
        "description": "Of matches meeting write threshold, >50% are HIGH confidence",
        "target": ">50%",
        "actual": f"{precision_pct:.1f}%",
        "passed": precision_pct > 50.0,
        "value": report.sc_precision,
    })

    # SC-FTR-3: Env coverage — at least 20% of beliefs get an env_id
    env_pct = report.sc_env_coverage * 100
    conditions.append({
        "id": "SC-FTR-3",
        "name": "Environment ID Coverage",
        "description": "At least 20% of beliefs get an extracted environment_id",
        "target": "≥20%",
        "actual": f"{env_pct:.1f}%",
        "passed": env_pct >= 20.0,
        "value": report.sc_env_coverage,
    })

    # SC-FTR-4: Outcome coverage — at least 25% of beliefs get an outcome_id
    out_pct = report.sc_out_coverage * 100
    conditions.append({
        "id": "SC-FTR-4",
        "name": "Outcome ID Coverage",
        "description": "At least 25% of beliefs get an extracted outcome_id",
        "target": "≥25%",
        "actual": f"{out_pct:.1f}%",
        "passed": out_pct >= 25.0,
        "value": report.sc_out_coverage,
    })

    # SC-FTR-5: Bridge utilization — at least 40% of bridge vocab is activated
    bridge_pct = report.sc_bridge_util * 100
    conditions.append({
        "id": "SC-FTR-5",
        "name": "Bridge Vocabulary Utilization",
        "description": "At least 40% of ENV_BRIDGES + OUTCOME_BRIDGES keys are used",
        "target": "≥40%",
        "actual": f"{bridge_pct:.1f}%",
        "passed": bridge_pct >= 40.0,
        "value": report.sc_bridge_util,
    })

    # SC-FTR-6: Low confidence ratio — <20% of total extractions are LOW confidence
    total_extractions = (
        report.high_confidence_env + report.medium_confidence_env + report.low_confidence_env
        + report.high_confidence_outcome + report.medium_confidence_outcome + report.low_confidence_outcome
    )
    low_total = report.low_confidence_env + report.low_confidence_outcome
    low_ratio = (low_total / total_extractions * 100) if total_extractions > 0 else 0
    conditions.append({
        "id": "SC-FTR-6",
        "name": "Low Confidence Ratio",
        "description": "Less than 20% of all extractions are LOW confidence (uncertain matches)",
        "target": "<20%",
        "actual": f"{low_ratio:.1f}%",
        "passed": low_ratio < 20.0,
        "value": low_ratio / 100.0,
    })

    return conditions


def print_report(report: ExtractionReport) -> None:
    """Pretty-print the extraction report."""
    print("\n" + "=" * 60)
    print("  ENV/OUTCOME EXTRACTION REPORT")
    print("=" * 60)
    print(f"  Total beliefs: {report.total_beliefs}")
    print(f"  With env_id (MEDIUM+): {report.beliefs_with_env} ({report.sc_env_coverage*100:.1f}%)")
    print(f"  With outcome_id (MEDIUM+): {report.beliefs_with_outcome} ({report.sc_out_coverage*100:.1f}%)")
    print(f"  With BOTH: {report.beliefs_with_both}")
    print(f"  Writable (env OR outcome): {report.beliefs_writable}")

    print(f"\n  Confidence breakdown (Env):")
    print(f"    HIGH:   {report.high_confidence_env}")
    print(f"    MEDIUM: {report.medium_confidence_env}")
    print(f"    LOW:    {report.low_confidence_env}")

    print(f"\n  Confidence breakdown (Outcome):")
    print(f"    HIGH:   {report.high_confidence_outcome}")
    print(f"    MEDIUM: {report.medium_confidence_outcome}")
    print(f"    LOW:    {report.low_confidence_outcome}")

    print(f"\n  Env terms used: {sorted(report.env_terms_used)}")
    print(f"  Outcome terms used: {sorted(report.outcome_terms_used)}")

    # Success conditions
    conditions = check_success_conditions(report)
    print("\n" + "-" * 60)
    print("  SUCCESS CONDITIONS")
    print("-" * 60)
    passed = 0
    for sc in conditions:
        status = "✅" if sc["passed"] else "❌"
        print(f"  {status} {sc['id']}: {sc['name']}")
        print(f"     Target: {sc['target']}, Actual: {sc['actual']}")
        if sc["passed"]:
            passed += 1

    print(f"\n  Score: {passed}/{len(conditions)} conditions passed")
    grade = "GREEN" if passed >= 5 else "YELLOW" if passed >= 3 else "RED"
    print(f"  Grade: {grade}")


# ============================================================================
# CLI
# ============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract env/outcome IDs from belief content with confidence grading"
    )
    parser.add_argument(
        "--db", type=str, default=None,
        help="Path to web persistence DB (uses db_locator if not specified)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=True,
        help="Don't write to DB, just report (default: True)"
    )
    parser.add_argument(
        "--write", action="store_true",
        help="Actually write extracted values to DB"
    )
    parser.add_argument(
        "--threshold", type=float, default=WRITE_THRESHOLD,
        help=f"Minimum confidence to write (default {WRITE_THRESHOLD})"
    )
    parser.add_argument(
        "--sample", type=int, default=0,
        help="Process only N beliefs (for testing)"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Resolve DB path
    if args.db:
        db_path = Path(args.db)
    else:
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
            from src.services.db_locator import get_web_db
            db_path = Path(get_web_db())
        except Exception as e:
            print(f"❌ Cannot resolve DB: {e}")
            print("  Use --db to specify path explicitly")
            return

    if not db_path.exists():
        print(f"❌ DB not found: {db_path}")
        return

    print(f"  DB: {db_path}")

    dry_run = not args.write
    if dry_run:
        print("  Mode: DRY RUN (use --write to actually update DB)")
    else:
        print("  Mode: WRITE (will update env_id and outcome_id)")

    report = process_beliefs_from_db(
        db_path,
        dry_run=dry_run,
        write_threshold=args.threshold,
    )

    if args.json:
        # Serialize for overseer integration
        result = {
            "report": {
                k: v for k, v in asdict(report).items()
                if k not in ("env_terms_used", "outcome_terms_used")
            },
            "env_terms_used": sorted(report.env_terms_used),
            "outcome_terms_used": sorted(report.outcome_terms_used),
            "success_conditions": check_success_conditions(report),
        }
        # Sets aren't JSON serializable from asdict, clean up
        print(json.dumps(result, indent=2, default=str))
    else:
        print_report(report)


if __name__ == "__main__":
    main()
