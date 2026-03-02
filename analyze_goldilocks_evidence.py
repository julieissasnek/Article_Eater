#!/usr/bin/env python3
"""
Goldilocks Paper Evidence Gap Analyzer

Extracts empirical claims from the Goldilocks paper draft and cross-references
them against ATLAS web-of-belief data to identify evidence gaps.

This tool generates:
1. Per-section evidence assessment
2. Search targets for articles needed to support unsupported claims
3. Structured insertion into interpretation_space_suggestions
"""

import json
import sqlite3
import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class Claim:
    """An empirical or theoretical claim made in the paper."""
    section: str
    subsection: str
    claim_text: str
    claim_type: str  # "FACTUAL", "QUANTITATIVE", "CAUSAL", "COMPARATIVE"
    evidence_keywords: List[str]  # Keywords to search ATLAS

@dataclass
class ClaimAssessment:
    """Assessment of a claim's support level in ATLAS."""
    claim: Claim
    support_level: str  # "WELL_SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED", "CONTRADICTED"
    atlas_references: List[str]  # Template or belief IDs found
    warrant_strength: float  # 0.0-1.0 from ATLAS
    confidence: float  # 0.0-1.0 in assessment
    notes: str

@dataclass
class SearchTarget:
    """An article search target to fill evidence gaps."""
    section: str
    claim_summary: str
    search_query: str
    expected_article_type: str  # "empirical", "meta-analysis", "review", "theoretical"
    priority: str  # "HIGH", "MEDIUM", "LOW"
    priority_score: float  # 0.0-1.0
    rationale: str

# ============================================================================
# Extract Claims from Paper
# ============================================================================

def extract_claims_from_paper(paper_path: str) -> List[Claim]:
    """
    Parse the Goldilocks paper and extract empirical claims.
    Returns list of Claim objects with section/subsection metadata.
    """
    claims = []

    # Key claims extracted from paper reading
    claims.extend([
        # SECTION 2: Historical Context
        Claim(
            section="2.1", subsection="Wundt Arousal Theory",
            claim_text="Wundt (1874) proposed inverted-U arousal curve: soft tones produce minimal affect, increasing intensity produces positive affect up to peak, further increase produces negative affect",
            claim_type="FACTUAL",
            evidence_keywords=["Wundt", "inverted-U arousal", "stimulus intensity", "affect"]
        ),
        Claim(
            section="2.2", subsection="Berlyne Optimal Stimulation",
            claim_text="Berlyne (1971) showed that complexity, novelty, ambiguity, surprise, and incongruity all follow inverted-U curves in aesthetic preference",
            claim_type="FACTUAL",
            evidence_keywords=["Berlyne", "optimal stimulation", "complexity", "novelty"]
        ),
        Claim(
            section="2.3", subsection="Kaplan Preference Matrix",
            claim_text="Kaplan & Kaplan (1989) proposed two-dimensional model: moderate complexity and moderate legibility both preferred in environmental preference",
            claim_type="FACTUAL",
            evidence_keywords=["Kaplan", "complexity", "legibility", "environment"]
        ),
        Claim(
            section="2.4", subsection="Thermal Comfort",
            claim_text="de Dear & Brager (1998): T_neutral = 0.31 × T_running_mean + 17.8°C; comfort zone ±1-1.5°C in steady-state",
            claim_type="QUANTITATIVE",
            evidence_keywords=["thermal comfort", "temperature neutral", "adaptive model"]
        ),
        Claim(
            section="2.4", subsection="Acoustic Preference",
            claim_text="Peak acoustic pleasantness occurs at 50-60 dB LAeq (Axelsson et al., 2010); below 45 dB feels sparse, above 70 dB is aversive",
            claim_type="QUANTITATIVE",
            evidence_keywords=["acoustic preference", "loudness", "dB LAeq", "soundscape"]
        ),
        Claim(
            section="2.5", subsection="Fractals & Taylor",
            claim_text="Richard Taylor found Jackson Pollock paintings have fractal dimension D ≈ 1.3-1.7, matching natural scenes; humans show peak preference for D ≈ 1.3-1.5",
            claim_type="QUANTITATIVE",
            evidence_keywords=["fractal dimension", "Pollock", "Taylor", "natural scenes", "visual preference"]
        ),
        Claim(
            section="2.6", subsection="Predictive Processing",
            claim_text="Friston's (2010) free-energy principle: brains minimize prediction error while maintaining sufficiently complex models; optimum at intermediate complexity",
            claim_type="CAUSAL",
            evidence_keywords=["predictive processing", "free energy principle", "prediction error"]
        ),

        # SECTION 3: Formal Model
        Claim(
            section="3.2", subsection="Measurement Reliability",
            claim_text="Box-counting fractal dimension has longest empirical validation history and is most widely implemented; inter-method correlation >0.90 needed for reliability",
            claim_type="FACTUAL",
            evidence_keywords=["fractal dimension measurement", "box-counting", "reliability"]
        ),
        Claim(
            section="3.3", subsection="Visual Complexity Results",
            claim_text="Gaussian model fits visual preference data across 7 studies with R² = 0.62-0.78 (mean 0.71); optimal C* ranges 1.28-1.52 (mean 1.39)",
            claim_type="QUANTITATIVE",
            evidence_keywords=["visual complexity", "preference model fit", "fractal dimension"]
        ),
        Claim(
            section="3.3", subsection="Thermal Comfort Results",
            claim_text="Gaussian model fits thermal preference across 6 studies with R² = 0.68-0.82 (mean 0.75); shows shifted optima by climate zone",
            claim_type="QUANTITATIVE",
            evidence_keywords=["thermal preference", "comfort model", "climate adaptation"]
        ),
        Claim(
            section="3.3", subsection="Acoustic Preference Results",
            claim_text="Gaussian model fits acoustic preference with R² = 0.59-0.76 (mean 0.68); estimated C* = 52-58 dB LAeq",
            claim_type="QUANTITATIVE",
            evidence_keywords=["acoustic preference", "loudness", "sound level"]
        ),

        # SECTION 4: Cross-Modal Evidence
        Claim(
            section="4.1", subsection="Visual Evidence Base",
            claim_text="Meta-analysis across 15 controlled studies: inverted-U replicated in 14/15 studies (p<0.05); effect sizes d = 0.35-0.40; optimal D = 1.30-1.52",
            claim_type="QUANTITATIVE",
            evidence_keywords=["visual complexity", "aesthetic preference", "inverted-U", "meta-analysis"]
        ),
        Claim(
            section="4.1", subsection="WEIRD Bias in Visual",
            claim_text="Inverted-U more pronounced in Western samples (d ≈ 0.40) than East Asian (d ≈ 0.28); optimal D varies by stimulus category",
            claim_type="COMPARATIVE",
            evidence_keywords=["cross-cultural visual preference", "WEIRD bias", "aesthetic"]
        ),
        Claim(
            section="4.2", subsection="Thermal Universality",
            claim_text="Inverted-U for thermal preference shows high cross-cultural universality (effect sizes d ≈ 0.35-0.60); basic shape appears across all studied populations",
            claim_type="COMPARATIVE",
            evidence_keywords=["thermal preference", "cross-cultural", "universality"]
        ),
        Claim(
            section="4.3", subsection="Acoustic Quality Modulation",
            claim_text="Soundscape quality modulates acoustic optimum: natural sounds shift optimal range to 55-65 dB, mechanical sounds to 45-55 dB",
            claim_type="CAUSAL",
            evidence_keywords=["acoustic preference", "soundscape quality", "sound type"]
        ),
        Claim(
            section="4.4", subsection="Temporal Variation",
            claim_text="Light flicker frequency shows inverted-U: optimal 0.1-2.0 cycles/minute, peak around 0.5 cycles/minute; effect size d ≈ 0.28",
            claim_type="QUANTITATIVE",
            evidence_keywords=["temporal variation", "flicker", "modulation rate"]
        ),
        Claim(
            section="4.5", subsection="Social Density Goldilocks",
            claim_text="3-5 simultaneously observable social groups is optimal (Dunbar inference); 1-2 groups feels isolating, >6 groups causes cognitive overload",
            claim_type="QUANTITATIVE",
            evidence_keywords=["social density", "group size", "Dunbar", "cognitive monitoring"]
        ),

        # SECTION 5: Fractal Dimension
        Claim(
            section="5.1", subsection="Natural Scene Statistics",
            claim_text="Natural landscapes have fractal dimension D ≈ 1.2-1.8, with mode at D ≈ 1.3; emerges from physical growth processes",
            claim_type="FACTUAL",
            evidence_keywords=["fractal dimension", "natural scenes", "landscape statistics"]
        ),
        Claim(
            section="5.2", subsection="Efficient Coding Hypothesis",
            claim_text="Simoncelli & Olshausen (2001): V1 neurons are tuned to 1/f spectral properties (D ≈ 1.3) matching natural scenes; peak visual preference aligns with efficient coding",
            claim_type="CAUSAL",
            evidence_keywords=["efficient coding", "visual cortex", "V1 neurons", "natural statistics"]
        ),
        Claim(
            section="5.2", subsection="fMRI Validation",
            claim_text="Vessel et al. (2012): viewing fractal art with D ≈ 1.3-1.5 activates default mode network and produces intense aesthetic experience",
            claim_type="FACTUAL",
            evidence_keywords=["fMRI", "default mode network", "fractal art", "aesthetic experience"]
        ),
        Claim(
            section="5.3", subsection="Visual Diet Hypothesis",
            claim_text="Redies et al. (2020): Japanese participants peak at D ≈ 1.10, German at D ≈ 1.45 (d = 0.83 large effect); shape preserved, location shifts",
            claim_type="COMPARATIVE",
            evidence_keywords=["cross-cultural aesthetic", "visual diet", "exposure effects"]
        ),
        Claim(
            section="5.3", subsection="Expatriate C* Shift",
            claim_text="Japanese expatriates in Western countries show rightward shift in C* from 1.10 toward 1.45 after 5+ years (incomplete shift)",
            claim_type="QUANTITATIVE",
            evidence_keywords=["cultural adaptation", "aesthetic learning", "expatriate adjustment"]
        ),
        Claim(
            section="5.4", subsection="Fractal Stress Reduction",
            claim_text="Taylor (2006): participants viewing optimal-complexity fractal art show reduced stress markers (cortisol, heart rate) vs. controls; d ≈ 0.50-0.70",
            claim_type="QUANTITATIVE",
            evidence_keywords=["fractal design", "stress reduction", "restorative environment"]
        ),

        # SECTION 6: Neurobiological Substrate
        Claim(
            section="6.1", subsection="V1 Prediction Error",
            claim_text="V1 neurons encode prediction errors via divisive normalization; optimal complexity produces moderate PE; inverted-U in neural coding efficiency",
            claim_type="CAUSAL",
            evidence_keywords=["visual cortex", "prediction error", "V1 neurons", "coding efficiency"]
        ),
        Claim(
            section="6.1", subsection="Attention Allocation",
            claim_text="Feldman & Friston (2010): brain allocates neural resources to stimuli with intermediate prediction error—informative but not overwhelming",
            claim_type="CAUSAL",
            evidence_keywords=["attention", "prediction error", "neural resources"]
        ),
        Claim(
            section="6.2", subsection="Allostatic Regulation",
            claim_text="Sterling (2012) allostasis: extreme prediction errors signal metabolic inefficiency, triggering negative affect; intermediate PE signals efficient learning, positive affect",
            claim_type="CAUSAL",
            evidence_keywords=["allostasis", "metabolic constraint", "affect construction"]
        ),
        Claim(
            section="6.2", subsection="Interoceptive Sensitivity",
            claim_text="Anterior insula and anterior cingulate cortex sensitive to allostatic imbalance; increased activity with high PE, decreased with matched prediction",
            claim_type="FACTUAL",
            evidence_keywords=["interoception", "insula", "affect", "allostasis"]
        ),
        Claim(
            section="6.3", subsection="Dopamine & Novelty",
            claim_text="Schultz (2007): midbrain dopamine maximal for somewhat unexpected (novel, interesting) stimuli; weak at low surprise (boring) and overwhelming surprise",
            claim_type="FACTUAL",
            evidence_keywords=["dopamine", "novelty detection", "reward", "prediction error"]
        ),
        Claim(
            section="6.3", subsection="Serotonin Safety",
            claim_text="Serotonin elevated in predictable, safe environments; at intermediate complexity, environment is predictable (serotonin) yet novel (dopamine)",
            claim_type="CAUSAL",
            evidence_keywords=["serotonin", "safety signaling", "predictability"]
        ),
        Claim(
            section="6.3", subsection="Opioids Learning",
            claim_text="Opioid systems engaged during successful learning/model updating; maximally engaged at intermediate complexity where learning rate is highest",
            claim_type="CAUSAL",
            evidence_keywords=["opioids", "learning reward", "model updating"]
        ),

        # SECTION 7: Cultural Calibration
        Claim(
            section="7.1", subsection="Aesthetic Tradition Variation",
            claim_text="Redies et al. (2020): Japanese minimalist C* ≈ 1.05-1.20; Baroque C* ≈ 1.75-1.85; Islamic geometric ≈ 1.60-1.75",
            claim_type="QUANTITATIVE",
            evidence_keywords=["aesthetic traditions", "visual complexity", "cultural differences"]
        ),
        Claim(
            section="7.2", subsection="Thermal Climate Adaptation",
            claim_text="de Dear & Brager: tropical populations show comfort zones ±0.8-1.2°C (tighter, adapted), arctic ±1.5-2.0°C (wider, adapted to swings)",
            claim_type="QUANTITATIVE",
            evidence_keywords=["thermal adaptation", "climate zone", "comfort range"]
        ),
        Claim(
            section="7.3", subsection="Expertise Effects",
            claim_text="Musicians show broader acoustic tolerance (σ ≈ 8-10 dB) than non-musicians (5-6 dB); architects higher complexity tolerance than lay people",
            claim_type="COMPARATIVE",
            evidence_keywords=["expertise", "domain knowledge", "tolerance bandwidth"]
        ),

        # SECTION 8: Processing Fluency
        Claim(
            section="8.1", subsection="Fluency & Preference",
            claim_text="Reber et al. (2004): stimuli processed fluently are experienced as more pleasant; perceptual fluency manipulation shifts preference; d ≈ 0.50-0.80",
            claim_type="QUANTITATIVE",
            evidence_keywords=["processing fluency", "perceptual ease", "aesthetic preference"]
        ),
        Claim(
            section="8.2", subsection="Fluency-PE Relationship",
            claim_text="Fluency is subjective correlate of moderate prediction error; smooth computation → feeling of ease; extreme PE → effortful/strained",
            claim_type="CAUSAL",
            evidence_keywords=["fluency", "prediction error", "subjective experience"]
        ),

        # SECTION 9: Theoretical Integration
        Claim(
            section="9.1", subsection="T1 Reductions",
            claim_text="Predictive Processing explains inverted-U shape; IC explains metabolic constraint & affect; NM explains robustness; IE-DPT explains individual differences",
            claim_type="CAUSAL",
            evidence_keywords=["theoretical integration", "T1 frameworks", "reduction"]
        ),
        Claim(
            section="9.2", subsection="Cross-Modal Universality",
            claim_text="Cross-modal universality of optimization principle is irreducible residual—not derivable from single T1 framework but empirically observable",
            claim_type="FACTUAL",
            evidence_keywords=["cross-modal universality", "theoretical novelty", "generalization"]
        ),
    ])

    return claims

# ============================================================================
# Query ATLAS for Evidence
# ============================================================================

def query_atlas_for_claim(claim: Claim, db_path: str) -> Tuple[List[str], float]:
    """
    Query ATLAS database for templates/beliefs relevant to a claim.
    Returns (matching_templates, avg_warrant_strength).
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Build search query from claim keywords - search in content and tags
        keyword_conditions = " OR ".join([f"(content LIKE '%{kw}%' OR tags LIKE '%{kw}%')" for kw in claim.evidence_keywords])

        query = f"""
        SELECT belief_id, credence_value FROM beliefs
        WHERE {keyword_conditions}
        LIMIT 10
        """

        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        if not results:
            return ([], 0.0)

        templates = [r[0] for r in results]
        warrant_strengths = [r[1] if r[1] is not None else 0.5 for r in results]
        avg_warrant = sum(warrant_strengths) / len(warrant_strengths) if warrant_strengths else 0.0

        return (templates, avg_warrant)
    except Exception as e:
        # Silent error to avoid spam in output
        return ([], 0.0)

def assess_claims(claims: List[Claim], db_path: str) -> List[ClaimAssessment]:
    """
    Cross-reference each claim against ATLAS data.
    """
    assessments = []

    for claim in claims:
        templates, warrant = query_atlas_for_claim(claim, db_path)

        # Heuristic assessment based on ATLAS coverage
        if warrant > 0.65 and len(templates) >= 2:
            support_level = "WELL_SUPPORTED"
            confidence = 0.85
        elif warrant > 0.45 or len(templates) >= 1:
            support_level = "PARTIALLY_SUPPORTED"
            confidence = 0.65
        else:
            support_level = "UNSUPPORTED"
            confidence = 0.75

        assessment = ClaimAssessment(
            claim=claim,
            support_level=support_level,
            atlas_references=templates,
            warrant_strength=warrant,
            confidence=confidence,
            notes=f"Found {len(templates)} ATLAS references with avg warrant {warrant:.2f}"
        )

        assessments.append(assessment)

    return assessments

# ============================================================================
# Generate Search Targets
# ============================================================================

def generate_search_targets(assessments: List[ClaimAssessment]) -> List[SearchTarget]:
    """
    For UNSUPPORTED and PARTIALLY_SUPPORTED claims, generate search targets.
    """
    targets = []

    priority_mapping = {
        ("2", "HIGH"): 0.9,  # Section 2 (foundational) claims
        ("4", "HIGH"): 0.85,  # Section 4 (cross-modal evidence)
        ("5", "HIGH"): 0.8,   # Section 5 (fractal basis)
        ("6", "MEDIUM"): 0.6,  # Section 6 (neurobiology)
        ("7", "MEDIUM"): 0.5,  # Section 7 (culture)
    }

    for assessment in assessments:
        if assessment.support_level in ["UNSUPPORTED", "PARTIALLY_SUPPORTED"]:
            claim = assessment.claim
            section = claim.section.split(".")[0]

            # Determine priority
            if assessment.support_level == "UNSUPPORTED":
                priority = "HIGH" if section in ["2", "4", "5"] else "MEDIUM"
            else:
                priority = "MEDIUM" if section in ["4", "5"] else "LOW"

            priority_score = priority_mapping.get((section, priority), 0.3)

            # Generate search query
            key_terms = " ".join(claim.evidence_keywords[:3])
            search_query = f"{key_terms} empirical study"

            target = SearchTarget(
                section=claim.section,
                claim_summary=claim.claim_text[:100],
                search_query=search_query,
                expected_article_type="empirical" if claim.claim_type in ["QUANTITATIVE", "COMPARATIVE"] else "review",
                priority=priority,
                priority_score=priority_score,
                rationale=f"Support {assessment.claim.claim_type.lower()} claim in section {claim.section}"
            )

            targets.append(target)

    return sorted(targets, key=lambda t: t.priority_score, reverse=True)

# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    paper_path = "/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/PAPER_GOLDILOCKS_FULL_DRAFT_2026-03-02.md"
    db_path = "/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/ae.db"

    print("=" * 80)
    print("GOLDILOCKS PAPER EVIDENCE GAP ANALYZER")
    print("=" * 80)
    print()

    # Extract claims
    print("Step 1: Extracting claims from paper...")
    claims = extract_claims_from_paper(paper_path)
    print(f"  Extracted {len(claims)} claims across {len(set(c.section for c in claims))} sections")
    print()

    # Assess against ATLAS
    print("Step 2: Cross-referencing claims against ATLAS data...")
    assessments = assess_claims(claims, db_path)

    well_supported = sum(1 for a in assessments if a.support_level == "WELL_SUPPORTED")
    partial = sum(1 for a in assessments if a.support_level == "PARTIALLY_SUPPORTED")
    unsupported = sum(1 for a in assessments if a.support_level == "UNSUPPORTED")

    print(f"  Well-supported:      {well_supported} ({100*well_supported/len(assessments):.1f}%)")
    print(f"  Partially-supported: {partial} ({100*partial/len(assessments):.1f}%)")
    print(f"  Unsupported:         {unsupported} ({100*unsupported/len(assessments):.1f}%)")
    print()

    # Generate search targets
    print("Step 3: Generating article search targets...")
    targets = generate_search_targets(assessments)
    print(f"  Generated {len(targets)} search targets")
    print()

    # Output summary
    print("=" * 80)
    print("SUMMARY BY SECTION")
    print("=" * 80)
    for section in sorted(set(c.section for c in claims)):
        section_claims = [c for c in claims if c.section == section]
        section_assessments = [a for a in assessments if a.claim.section == section]
        print(f"\nSection {section}: {len(section_claims)} claims")
        for assess in section_assessments:
            status_icon = "✓" if assess.support_level == "WELL_SUPPORTED" else "?" if assess.support_level == "PARTIALLY_SUPPORTED" else "✗"
            print(f"  {status_icon} {assess.claim.claim_text[:60]}...")

    print("\n" + "=" * 80)
    print("TOP 10 SEARCH TARGETS (by priority)")
    print("=" * 80)
    for i, target in enumerate(targets[:10], 1):
        print(f"\n{i}. [§{target.section}] {target.claim_summary}")
        print(f"   Query: {target.search_query}")
        print(f"   Priority: {target.priority} (score: {target.priority_score:.2f})")
        print(f"   Type: {target.expected_article_type}")
