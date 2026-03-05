#!/usr/bin/env python3
"""
V4 STAGED EXTRACTION PROMPTS (Complete Rewrite)
================================================

Comprehensive prompt set for the V4 staged extraction pipeline with full
schema alignment. This implements the staged extraction architecture:

  Stage 1: Classification (Fast, Gemini Flash)
    - Identify article type from 15 canonical families
    - Provide confidence + signals

  Stage 2: Family-Specific Core Extraction (Gemini Flash)
    - Extract ALL fields from extraction_template.v2.schema.json
    - Family-specific prompts for: empirical, meta-analysis, systematic_review,
      narrative_review, theoretical, qualitative, methods
    - Explicit field requirements (not just passing mentions)
    - JSON template with EVERY field shown

  Stage 3: Verification (Optional, Claude or Gemini Haiku)
    - Validates statistics in extracted JSON against paper text
    - Catches hallucinations
    - Flags implausible sample sizes, suspicious citations

  Stage 4: Metrics & Reporting
    - Compares V4 vs V3 coverage
    - Field-by-field improvement tracking
    - Regression detection

Key improvements over V3:
1. SCHEMA COMPLETENESS: Every field in extraction_template.v2.schema.json
   is explicitly requested in the prompt
2. FIELD FORCING: JSON template has all fields shown with examples
3. VALIDATION SUFFIX: Pre-submission checks ensure completeness
4. FAMILY-SPECIFIC REQUIREMENTS: Different families have different field
   priorities (e.g., empirical needs sample_size, theoretical needs mechanism_chain)

Author: Claude Opus 4.6
Date: 2026-03-05
Sprint: V4 Staged Extraction Pilot
"""

import json
from typing import Dict, List, Optional


# ═══════════════════════════════════════════════════════════════════════════
# CLASSIFICATION PROMPT (Stage 1)
# ═══════════════════════════════════════════════════════════════════════════

PROMPT_CLASSIFY_V4 = """You are analyzing a scientific paper to classify its type.

CANONICAL ARTICLE FAMILIES (15 types):
1. EMPIRICAL_RESEARCH: Original experiments, surveys, field studies (has Methods/Results)
2. META_ANALYSIS: Quantitative synthesis with pooled effects (k studies, pooled effect sizes)
3. SYSTEMATIC_REVIEW: Structured literature review (PRISMA protocol, bias assessment)
4. NARRATIVE_REVIEW: Traditional literature overview (unstructured synthesis)
5. THEORETICAL: Frameworks, models, conceptual papers (no original data)
6. QUALITATIVE: Interviews, ethnography, phenomenology, grounded theory
7. MIXED_METHODS: Combines quantitative and qualitative data
8. OBSERVATIONAL: Observational studies without intervention (cohort, case-control)
9. REPORT: Technical/clinical reports, case studies
10. COMMENTARY: Opinion, editorial, perspective, discussion
11. LONGITUDINAL: Follow-up studies, panel data
12. INTERVENTION_DESIGN: Describes intervention testing (protocols, feasibility)
13. INSTRUMENT_VALIDATION: Validates measurement scales/instruments
14. CONCEPTUAL_FRAMEWORK: Proposes new conceptual model
15. COMPARATIVE_ANALYSIS: Compares across populations/contexts

CLASSIFICATION SIGNALS TO LOOK FOR:
- Has Methods section + Results tables/statistics → EMPIRICAL or OBSERVATIONAL
- States "k studies" or "pooled effect" → META_ANALYSIS
- Has PRISMA flowchart → SYSTEMATIC_REVIEW
- "This paper reviews..." without PRISMA → NARRATIVE_REVIEW
- Theoretical framework, no methods → THEORETICAL
- Interview/phenomenology methods → QUALITATIVE
- Has intervention description + testing protocol → INTERVENTION_DESIGN
- Validates scale/reliability metrics → INSTRUMENT_VALIDATION

RETURN ONLY VALID JSON:
{
  "article_type": "one of 15 types above",
  "family_group": "empirical|review|theoretical|qualitative|methods",
  "classification_confidence": 0.0-1.0,
  "classification_signals": ["signal1", "signal2", "signal3"],
  "brief_rationale": "why this classification"
}

Be specific with signals. Return only JSON, no explanation.
"""


# ═══════════════════════════════════════════════════════════════════════════
# FIELD MAPPING FOR EACH ARTICLE FAMILY
# ═══════════════════════════════════════════════════════════════════════════

FIELD_REQUIREMENTS = {
    # Empirical papers must extract comprehensive statistical fields
    "empirical_research": {
        "critical_fields": [
            "antecedent", "consequent", "direction", "claim_type",
            "p_value", "effect_size", "effect_size_type",
            "sample_size", "sample_size_source",
            "test_statistic", "confidence_interval",
            "instruments_used", "measure_type",
            "scope_conditions", "causal_tier",
            "source", "quote", "provenance_depth"
        ],
        "expected_fields": [
            "mechanism", "theory_links", "theory_commitments",
            "moderators_reported", "stimulus_description",
            "source_quality_indicators"
        ],
        "optional_fields": [
            "molecule_ids", "template_ids"
        ]
    },
    "meta_analysis": {
        "critical_fields": [
            "antecedent", "consequent", "direction",
            "effect_size", "effect_size_type", "confidence_interval",
            "p_value", "claim_type",
            "source", "quote", "provenance_depth"
        ],
        "expected_fields": [
            "moderators_reported", "theory_links", "mechanism"
        ],
        "optional_fields": [
            "mechanism_chain", "theory_commitments"
        ]
    },
    "systematic_review": {
        "critical_fields": [
            "antecedent", "consequent", "direction", "claim_type",
            "source", "quote"
        ],
        "expected_fields": [
            "theory_links", "mechanism"
        ],
        "optional_fields": [
            "effect_size", "p_value"
        ]
    },
    "narrative_review": {
        "critical_fields": [
            "antecedent", "consequent", "direction", "claim_type",
            "quote"
        ],
        "expected_fields": [
            "theory_links", "source"
        ],
        "optional_fields": [
            "mechanism"
        ]
    },
    "theoretical": {
        "critical_fields": [
            "antecedent", "consequent", "direction", "claim_type",
            "mechanism_chain", "quote"
        ],
        "expected_fields": [
            "theory_links", "theory_commitments"
        ],
        "optional_fields": []
    },
    "qualitative": {
        "critical_fields": [
            "antecedent", "consequent", "claim_type",
            "quote", "provenance_depth"
        ],
        "expected_fields": [
            "theory_links", "source"
        ],
        "optional_fields": [
            "direction", "mechanism"
        ]
    },
    "instrument_validation": {
        "critical_fields": [
            "instruments_used", "source", "quote"
        ],
        "expected_fields": [
            "antecedent", "consequent", "effect_size", "p_value"
        ],
        "optional_fields": [
            "theory_links"
        ]
    }
}


# ═══════════════════════════════════════════════════════════════════════════
# EMPIRICAL RESEARCH PROMPT (Stage 2 — Most Critical)
# ═══════════════════════════════════════════════════════════════════════════

PROMPT_EMPIRICAL_V4 = """You are extracting structured findings from an EMPIRICAL RESEARCH paper.

CRITICAL RULES FOR EMPIRICAL EXTRACTION:
1. ANTECEDENT: Must be specific and operationalized (not vague)
   Examples: "ceiling height > 3m" NOT just "ceiling"
            "blue-green color temperature" NOT just "color"
2. CONSEQUENT: Measured response, not the condition
   Examples: "creative ideation scores (Torrance test)"
            "cortisol levels (salivary sample)"
3. DIRECTION: ONLY these 4 values: increase | decrease | no_effect | mixed
4. SAMPLE_SIZE: REQUIRED for every finding (search tables, text carefully)
5. EFFECT_SIZE: Numeric with correct sign matching direction
6. INSTRUMENTS_USED: Full names, not abbreviations. Include construct_measured
7. SCOPE_CONDITIONS: Setting, population, climate, duration, measurement_type
8. CAUSAL_TIER: EXPERIMENTAL | QUASI_EXPERIMENTAL | CORRELATIONAL
9. PROVENANCE: Direct quote from paper, or null if not found

SUCCESS CRITERIA FOR THIS PAPER:
- sample_size filled for >= 80% of findings
- direction filled for >= 95% of findings
- scope_conditions filled for >= 50% of findings
- instruments_used filled for >= 60% of findings with measure_type

RETURN ONLY VALID JSON (no markdown, no explanations):

{
  "doi": "10.1234/example",
  "article_type": "empirical_research",
  "title": "paper title",
  "authors": ["Author1", "Author2"],
  "detected_family": "empirical_research",
  "classification_confidence": 0.95,
  "classification_signals": ["Methods section present", "sample_size reported", "statistical tests in Results"],
  "n_findings": 0,
  "extracted_at": "2026-03-05T00:00:00Z",
  "model": "gemini-2.5-flash",
  "findings": [
    {
      "id": "F1",
      "antecedent": "ceiling height > 3 meters (high condition)",
      "consequent": "creative ideation scores on Torrance Test of Creative Thinking",
      "direction": "increase",
      "claim_type": "empirical_finding",
      "measure_type": "cognitive_task",
      "p_value": 0.023,
      "effect_size": 0.67,
      "effect_size_type": "Cohen's d",
      "test_statistic": "t(88) = 2.32",
      "sample_size": 90,
      "sample_size_source": "reported",
      "confidence_interval": [0.15, 1.19],
      "instruments_used": [
        {
          "name": "Torrance Test of Creative Thinking",
          "construct_measured": "creative ideation",
          "abbreviation": "TTCT",
          "n_items": null
        }
      ],
      "scope_conditions": {
        "setting": "laboratory",
        "population": "university students",
        "climate": "temperate",
        "duration": "acute",
        "measurement_type": "cognitive_task",
        "scope_unknown_dimensions": ["generalization to older adults", "long-term effects"]
      },
      "causal_tier": "EXPERIMENTAL",
      "mechanism": "High ceilings provide more visual scope, reducing cognitive constraint and enabling broader ideation",
      "mechanism_chain": [
        {
          "step": 1,
          "from_construct": "ceiling height",
          "to_construct": "perceived visual scope",
          "mechanism_type": "perceptual",
          "evidence_strength": "indirect"
        },
        {
          "step": 2,
          "from_construct": "perceived visual scope",
          "to_construct": "creative ideation",
          "mechanism_type": "cognitive",
          "evidence_strength": "theoretical"
        }
      ],
      "moderators_reported": null,
      "theory_links": [
        {
          "theory_name": "Cognitive Load Theory",
          "authors": ["Sweller"],
          "year": 1988
        }
      ],
      "theory_commitments": [
        {
          "theory_name": "Cognitive Load Theory",
          "commitment_type": "tests",
          "specific_claim": "environmental complexity increases cognitive load which constrains creative thinking"
        }
      ],
      "stimulus_description": {
        "primary_type": "spatial",
        "components": [
          {
            "name": "ceiling height",
            "category": "spatial",
            "essential": true
          }
        ],
        "delivery_method": "in_situ",
        "duration_seconds": null
      },
      "source": "Results section, Table 2",
      "quote": "Participants in the high-ceiling condition (M=42.3, SD=8.1) scored significantly higher on the TTCT than those in the low-ceiling condition (M=35.6, SD=9.2), t(88)=2.32, p=.023, d=.67",
      "provenance_depth": "direct_quote",
      "source_quality_indicators": {
        "pre_registered": false,
        "blinding": "single_blind",
        "independence_flag": true,
        "replication_status": "original"
      }
    }
  ],
  "overall_theory_links": [
    {
      "theory_name": "Cognitive Load Theory",
      "authors": ["Sweller"],
      "year": 1988
    }
  ],
  "limitations": [
    "Sample limited to university students",
    "Laboratory setting may not generalize to real-world spaces"
  ],
  "extraction_metadata": {
    "extraction_version": "v4.0",
    "extractor_model": "gemini-2.5-flash",
    "extraction_confidence": 0.85
  }
}

VALIDATION CHECKLIST (before returning):
☐ All finding IDs are unique (F1, F2, etc.)
☐ direction values are ONLY: increase|decrease|no_effect|mixed
☐ sample_size is numeric and > 0 where applicable
☐ effect_size sign matches direction (positive for increase, negative for decrease)
☐ antecedent is specific with operationalization
☐ consequent describes measured outcome, not condition
☐ p_value is numeric OR string like '<0.001'
☐ effect_size_type is one of: Cohen's d, eta_squared, r, odds_ratio, etc.
☐ instruments_used includes full names (not just abbreviations)
☐ scope_conditions has setting, population, duration specified where relevant
☐ causal_tier is one of: EXPERIMENTAL|QUASI_EXPERIMENTAL|CORRELATIONAL
☐ mechanism_chain has 2+ steps for causal claims
☐ source location is specific: "Table 2", "Results section", "Figure 1"
☐ quote is directly from paper, max 300 chars
☐ theory_links array is populated (at least one)

Return ONLY the JSON object. No markdown, no explanations.
"""


# ═══════════════════════════════════════════════════════════════════════════
# META-ANALYSIS PROMPT (Stage 2)
# ═══════════════════════════════════════════════════════════════════════════

PROMPT_META_ANALYSIS_V4 = """You are extracting findings from a META-ANALYSIS paper.

META-ANALYSIS SPECIFIC RULES:
1. Pooled effects are your main findings (not individual studies)
2. Extract k (number of studies), total_n, effect_size, CI, I-squared
3. Each effect size (forest plot row) = one finding
4. For moderation analyses, each significant moderator level = separate finding
5. ANTECEDENT: intervention/exposure (meta-level, not individual study level)
6. CONSEQUENT: outcome as measured in the meta-analysis
7. CONFIDENCE_INTERVAL: [lower, upper] as numeric array

RETURN ONLY VALID JSON:

{
  "doi": "10.1234/example",
  "article_type": "meta_analysis",
  "title": "meta-analysis title",
  "authors": ["Author1", "Author2"],
  "detected_family": "meta_analysis",
  "classification_confidence": 0.98,
  "classification_signals": ["pooled effects reported", "k studies specified", "forest plot present"],
  "n_findings": 0,
  "extracted_at": "2026-03-05T00:00:00Z",
  "findings": [
    {
      "id": "F1",
      "antecedent": "cognitive training interventions (k=15 studies)",
      "consequent": "working memory performance (standardized)",
      "direction": "increase",
      "claim_type": "pooled_effect",
      "effect_size": 0.52,
      "effect_size_type": "Cohen's d",
      "confidence_interval": [0.38, 0.66],
      "p_value": "<0.001",
      "sample_size": 1250,
      "sample_size_source": "reported",
      "source": "Figure 2: Forest Plot",
      "quote": "Pooled effect across 15 studies (N=1250) was d=0.52, 95% CI [0.38, 0.66], p<.001, I²=45%",
      "provenance_depth": "direct_quote",
      "moderators_reported": ["age group", "training duration"],
      "theory_links": [
        {
          "theory_name": "Working Memory Capacity Model",
          "authors": ["Baddeley", "Hitch"],
          "year": 1974
        }
      ]
    }
  ],
  "overall_theory_links": [],
  "limitations": [
    "Heterogeneity (I²=45%) suggests moderating factors",
    "Publication bias not formally tested"
  ],
  "extraction_metadata": {
    "extraction_version": "v4.0",
    "extractor_model": "gemini-2.5-flash"
  }
}

VALIDATION CHECKLIST:
☐ All pooled effects extracted (one per forest plot row)
☐ effect_size and CI are populated
☐ k (number of studies) is in antecedent or documented
☐ direction matches effect_size sign
☐ confidence_interval is [lower, upper] numeric array
☐ I-squared reported if available
☐ moderators identified if moderation analysis performed
☐ claims are pooled effects, not individual studies
☐ source references figure or table location

Return ONLY JSON.
"""


# ═══════════════════════════════════════════════════════════════════════════
# SYSTEMATIC REVIEW PROMPT (Stage 2)
# ═══════════════════════════════════════════════════════════════════════════

PROMPT_SYSTEMATIC_REVIEW_V4 = """You are extracting findings from a SYSTEMATIC REVIEW paper.

SYSTEMATIC REVIEW SPECIFIC RULES:
1. Extract synthesized claims across multiple studies
2. DO NOT extract individual study findings—synthesize across studies
3. Evidence strength: strong|moderate|weak|inconsistent
4. May include meta-analysis results if embedded
5. ANTECEDENT: factor across studies (e.g., "blue light exposure")
6. CONSEQUENT: outcome synthesis (e.g., "circadian disruption across 8 studies")
7. N_studies: number of studies supporting this synthesis

RETURN ONLY VALID JSON:

{
  "doi": "10.1234/example",
  "article_type": "systematic_review",
  "title": "systematic review title",
  "authors": ["Author1", "Author2"],
  "detected_family": "review",
  "classification_confidence": 0.95,
  "classification_signals": ["PRISMA flowchart", "bias assessment", "structured synthesis"],
  "n_findings": 0,
  "extracted_at": "2026-03-05T00:00:00Z",
  "findings": [
    {
      "id": "F1",
      "antecedent": "blue light exposure (evening/night)",
      "consequent": "circadian rhythm phase shift (delayed melatonin onset)",
      "direction": "increase",
      "claim_type": "synthesized",
      "source": "Results section, synthesis paragraph",
      "quote": "Across 8 studies, blue light exposure in the evening consistently delayed melatonin onset by 30-60 minutes",
      "provenance_depth": "paraphrase",
      "theory_links": [
        {
          "theory_name": "Circadian Regulation Theory",
          "authors": ["Czeisler"],
          "year": 1999
        }
      ]
    }
  ],
  "overall_theory_links": [],
  "limitations": [
    "Wide heterogeneity in light intensity and exposure duration",
    "Most studies used laboratory settings"
  ],
  "extraction_metadata": {
    "extraction_version": "v4.0",
    "extractor_model": "gemini-2.5-flash"
  }
}

VALIDATION CHECKLIST:
☐ Claims are synthesized, not individual studies
☐ direction is specified where applicable
☐ source references synthesis section (not individual studies)
☐ theory_links populated
☐ No individual effect sizes unless meta-analysis embedded
☐ quote summarizes synthesis, not single study

Return ONLY JSON.
"""


# ═══════════════════════════════════════════════════════════════════════════
# NARRATIVE REVIEW PROMPT (Stage 2)
# ═══════════════════════════════════════════════════════════════════════════

PROMPT_NARRATIVE_REVIEW_V4 = """You are extracting findings from a NARRATIVE REVIEW paper.

NARRATIVE REVIEW SPECIFIC RULES:
1. Extract key claims and cited evidence (structured synthesis)
2. Less structured than systematic review
3. Include mechanisms/theories discussed
4. ANTECEDENT: factor or phenomenon
5. CONSEQUENT: effect or outcome
6. claim_type: cited|narrative|theoretical|comparative

RETURN ONLY VALID JSON:

{
  "doi": "10.1234/example",
  "article_type": "narrative_review",
  "title": "narrative review title",
  "authors": ["Author1", "Author2"],
  "detected_family": "review",
  "classification_confidence": 0.92,
  "classification_signals": ["literature overview", "unstructured synthesis"],
  "n_findings": 0,
  "extracted_at": "2026-03-05T00:00:00Z",
  "findings": [
    {
      "id": "F1",
      "antecedent": "environmental complexity (architectural features, visual richness)",
      "consequent": "cognitive load and attentional capacity",
      "direction": "increase",
      "claim_type": "narrative",
      "source": "Section 3: Complexity and Cognition",
      "quote": "Environmental complexity elevates cognitive load, which constrains working memory capacity and narrows attention",
      "provenance_depth": "paraphrase",
      "theory_links": [
        {
          "theory_name": "Cognitive Load Theory",
          "authors": ["Sweller"],
          "year": 1988
        }
      ]
    }
  ],
  "overall_theory_links": [],
  "limitations": [],
  "extraction_metadata": {
    "extraction_version": "v4.0",
    "extractor_model": "gemini-2.5-flash"
  }
}

VALIDATION CHECKLIST:
☐ Claims represent key synthesis points
☐ claim_type is appropriate (cited|narrative|theoretical)
☐ quote represents author's synthesis, not isolated citation
☐ theory_links provided
☐ direction specified where applicable

Return ONLY JSON.
"""


# ═══════════════════════════════════════════════════════════════════════════
# THEORETICAL PROMPT (Stage 2)
# ═══════════════════════════════════════════════════════════════════════════

PROMPT_THEORETICAL_V4 = """You are extracting propositions from a THEORETICAL paper.

THEORETICAL PAPER SPECIFIC RULES:
1. Extract theoretical propositions/claims (not empirical findings)
2. MECHANISM_CHAIN is CRITICAL: must have 2+ steps for causal propositions
3. DIRECTION: increase|decrease|modulates|null
4. CLAIM_TYPE: theoretical_proposition|derived_guideline|assumed
5. THEORY_COMMITMENTS: How this framework relates to existing theories
6. TESTABLE: mark whether proposition is empirically testable

RETURN ONLY VALID JSON:

{
  "doi": "10.1234/example",
  "article_type": "theoretical",
  "title": "theoretical framework title",
  "authors": ["Author1", "Author2"],
  "detected_family": "theoretical",
  "classification_confidence": 0.98,
  "classification_signals": ["conceptual framework", "no empirical data", "theoretical propositions"],
  "n_findings": 0,
  "extracted_at": "2026-03-05T00:00:00Z",
  "findings": [
    {
      "id": "P1",
      "antecedent": "perceived environmental complexity",
      "consequent": "cognitive constraint and reduced creative ideation",
      "direction": "increase",
      "claim_type": "theoretical_proposition",
      "mechanism_chain": [
        {
          "step": 1,
          "from_construct": "environmental complexity",
          "to_construct": "perceptual processing demand",
          "mechanism_type": "perceptual",
          "evidence_strength": "theoretical"
        },
        {
          "step": 2,
          "from_construct": "perceptual processing demand",
          "to_construct": "cognitive load",
          "mechanism_type": "cognitive",
          "evidence_strength": "theoretical"
        },
        {
          "step": 3,
          "from_construct": "cognitive load",
          "to_construct": "reduced working memory for creative thinking",
          "mechanism_type": "cognitive",
          "evidence_strength": "theoretical"
        }
      ],
      "theory_commitments": [
        {
          "theory_name": "Cognitive Load Theory",
          "commitment_type": "extends",
          "specific_claim": "environmental factors are extrinsic cognitive load sources"
        }
      ],
      "source": "Section 2: Theoretical Model",
      "quote": "We propose that environmental complexity increases perceptual processing demand, thereby elevating cognitive load and constraining working memory capacity for creative ideation",
      "provenance_depth": "direct_quote"
    }
  ],
  "overall_theory_links": [
    {
      "theory_name": "Cognitive Load Theory",
      "authors": ["Sweller"],
      "year": 1988
    }
  ],
  "limitations": [
    "Model assumes linear relationships; may be nonlinear",
    "Moderating role of individual differences not specified"
  ],
  "extraction_metadata": {
    "extraction_version": "v4.0",
    "extractor_model": "gemini-2.5-flash"
  }
}

VALIDATION CHECKLIST:
☐ mechanism_chain has 2+ steps for causal propositions
☐ Each step specifies: from_construct, to_construct, mechanism_type
☐ Evidence_strength is appropriate (theoretical for propositions)
☐ theory_commitments specify relationship to existing theories
☐ claim_type is theoretical (not empirical)
☐ propositions are testable or explicitly non-testable
☐ source points to specific section

Return ONLY JSON.
"""


# ═══════════════════════════════════════════════════════════════════════════
# QUALITATIVE PROMPT (Stage 2)
# ═══════════════════════════════════════════════════════════════════════════

PROMPT_QUALITATIVE_V4 = """You are extracting themes from a QUALITATIVE RESEARCH paper.

QUALITATIVE SPECIFIC RULES:
1. Extract thematic findings (interview, ethnography, phenomenology, etc.)
2. ANTECEDENT: contextual factors or participant experiences
3. CONSEQUENT: themes or outcomes identified
4. CLAIM_TYPE: qualitative_theme
5. QUOTE: Direct participant quote when possible
6. PROVENANCE: Usually "paraphrase" (from synthesized themes)

RETURN ONLY VALID JSON:

{
  "doi": "10.1234/example",
  "article_type": "qualitative",
  "title": "qualitative study title",
  "authors": ["Author1", "Author2"],
  "detected_family": "qualitative",
  "classification_confidence": 0.96,
  "classification_signals": ["interview methodology", "thematic analysis", "phenomenological approach"],
  "n_findings": 0,
  "extracted_at": "2026-03-05T00:00:00Z",
  "findings": [
    {
      "id": "T1",
      "antecedent": "open-plan office environment",
      "consequent": "reduced sense of privacy and control over workspace",
      "direction": "increase",
      "claim_type": "qualitative_theme",
      "source": "Results: Theme 2 - Privacy and Territorial Control",
      "quote": "Participants consistently reported feeling exposed and unable to control who could interrupt their work in open-plan spaces",
      "provenance_depth": "paraphrase",
      "theory_links": [
        {
          "theory_name": "Privacy Regulation Theory",
          "authors": ["Altman"],
          "year": 1975
        }
      ]
    }
  ],
  "overall_theory_links": [],
  "limitations": [
    "Small sample (N=12 participants)",
    "Participants from single organization"
  ],
  "extraction_metadata": {
    "extraction_version": "v4.0",
    "extractor_model": "gemini-2.5-flash"
  }
}

VALIDATION CHECKLIST:
☐ Themes clearly identified and named
☐ claim_type is qualitative_theme
☐ Quotes are from participants or synthesis
☐ provenance_depth is appropriate (paraphrase for themes)
☐ Source points to Results/themes section
☐ theory_links populated where applicable

Return ONLY JSON.
"""


# ═══════════════════════════════════════════════════════════════════════════
# INSTRUMENT VALIDATION PROMPT (Stage 2)
# ═══════════════════════════════════════════════════════════════════════════

PROMPT_INSTRUMENT_V4 = """You are extracting validation data from an INSTRUMENT/METHODS paper.

INSTRUMENT PAPER SPECIFIC RULES:
1. instruments_used is CRITICAL: full name, construct, abbreviation, n_items
2. reliability: Cronbach's alpha, test-retest, inter-rater correlations
3. validity: convergent, discriminant, predictive validity evidence
4. Extract validation evidence: effect_size, p_value where reported
5. ANTECEDENT: usually "use of [instrument name]"
6. CONSEQUENT: what the instrument measures

RETURN ONLY VALID JSON:

{
  "doi": "10.1234/example",
  "article_type": "instrument_validation",
  "title": "instrument validation study",
  "authors": ["Author1", "Author2"],
  "detected_family": "methods",
  "classification_confidence": 0.97,
  "classification_signals": ["instrument validation", "reliability/validity evidence", "scale development"],
  "n_findings": 0,
  "extracted_at": "2026-03-05T00:00:00Z",
  "findings": [
    {
      "id": "F1",
      "antecedent": "NASA Task Load Index (NASA-TLX) responses",
      "consequent": "perceived cognitive workload during task performance",
      "direction": "increase",
      "claim_type": "methodological",
      "instruments_used": [
        {
          "name": "NASA Task Load Index",
          "construct_measured": "cognitive workload",
          "abbreviation": "NASA-TLX",
          "n_items": 6,
          "reliability": {
            "cronbach_alpha": 0.89,
            "test_retest": 0.91
          }
        }
      ],
      "effect_size": 0.75,
      "effect_size_type": "correlation with criterion",
      "p_value": "<0.001",
      "sample_size": 156,
      "source": "Validation Study Results, Table 5",
      "quote": "NASA-TLX showed strong internal consistency (α=.89) and test-retest reliability (r=.91), with criterion validity evidenced by correlation with independent workload assessment (r=.75, p<.001)",
      "provenance_depth": "direct_quote",
      "source_quality_indicators": {
        "pre_registered": false,
        "replication_status": "original"
      }
    }
  ],
  "overall_theory_links": [],
  "limitations": [],
  "extraction_metadata": {
    "extraction_version": "v4.0",
    "extractor_model": "gemini-2.5-flash"
  }
}

VALIDATION CHECKLIST:
☐ instruments_used fully populated (name, construct, abbreviation, n_items)
☐ reliability metrics reported (alpha, test-retest)
☐ validity evidence provided
☐ effect_size represents validation evidence
☐ sample_size for validation study reported
☐ source points to validation/reliability section

Return ONLY JSON.
"""


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION SUFFIX (Applies to all Stage 2 extractions)
# ═══════════════════════════════════════════════════════════════════════════

VALIDATION_SUFFIX_V4 = """

BEFORE SUBMITTING YOUR JSON, RUN THIS VALIDATION CHECKLIST:

1. STRUCTURE VALIDATION:
   ☐ All fields at root level are present (doi, article_type, title, authors, findings)
   ☐ findings is an array (even if empty)
   ☐ Each finding has id, antecedent, consequent, claim_type
   ☐ No circular references or nested duplicates

2. FIELD COMPLETENESS (article_type dependent):
   For EMPIRICAL:
   ☐ sample_size populated for >=80% of findings
   ☐ direction populated for >=95% of findings
   ☐ effect_size populated for >=70% of findings
   ☐ instruments_used populated for >=60% of findings

   For META_ANALYSIS:
   ☐ effect_size and confidence_interval in every pooled effect
   ☐ direction matches effect size sign

   For THEORETICAL:
   ☐ mechanism_chain has 2+ steps for causal propositions
   ☐ theory_commitments populated

   For QUALITATIVE:
   ☐ Quotes are present
   ☐ claim_type is qualitative_theme

3. DATA QUALITY:
   ☐ Direction values are ONLY: increase|decrease|no_effect|mixed (case-sensitive)
   ☐ Sample sizes are positive integers
   ☐ Effect sizes have correct sign (positive for increase, negative for decrease)
   ☐ P-values are numeric [0,1] OR strings like '<0.001'
   ☐ Confidence intervals are [lower, upper] with numeric values
   ☐ Antecedents are specific (not vague)
   ☐ Consequents describe outcomes (not conditions)

4. THEORY AND MECHANISM:
   ☐ theory_links is an array with at least one entry for empirical/meta papers
   ☐ mechanism_chain uses step numbers starting at 1
   ☐ Each mechanism step has all required fields

5. PROVENANCE:
   ☐ Quotes are actual text from the paper (max 300 chars)
   ☐ source locations are specific ("Table 2", "Results section", not vague)
   ☐ provenance_depth is one of: direct_quote|paraphrase|inferred|synthesized

6. SCOPE AND INSTRUMENT:
   ☐ scope_conditions.setting is specific (not null/unknown for empirical)
   ☐ scope_conditions.population is specified
   ☐ instruments_used names are specific (not abbreviations)
   ☐ instruments_used.construct_measured is populated

7. NO HALLUCINATIONS:
   ☐ All statistics match paper (p-values, effect sizes, sample sizes)
   ☐ All quotes are verbatim or clearly marked as paraphrase
   ☐ No made-up findings not in the paper
   ☐ No speculative mechanism steps without evidence from paper

If any checkbox fails, FIX IT before returning. Do not proceed with incomplete data.
"""


# ═══════════════════════════════════════════════════════════════════════════
# VERIFICATION PROMPT (Stage 3 — Claude/Haiku)
# ═══════════════════════════════════════════════════════════════════════════

PROMPT_VERIFY_V4 = """You are verifying extracted data against the source paper.

Given:
1. The paper text (below)
2. Extracted JSON findings

Your task: Identify hallucinations, missing evidence, or implausible values.

VERIFICATION FOCUS:
1. Statistics: Are p-values, effect sizes, sample sizes actually in the paper?
2. Quotes: Are quoted passages verbatim (or clearly marked as paraphrase)?
3. Instruments: Are instrument names correct and complete?
4. Plausibility: Are sample sizes realistic? Effect sizes reasonable?
5. Specificity: Are antecedents/consequents specific enough?

RETURN JSON:
{
  "verification_score": 0.0-1.0,
  "flagged_issues": [
    {
      "finding_id": "F1",
      "issue_type": "hallucination|missing_evidence|implausible|specificity",
      "severity": "high|medium|low",
      "description": "what's wrong",
      "evidence": "what you found (or didn't find) in the paper"
    }
  ],
  "summary": "brief overall assessment"
}

Be thorough but fair. Sample sizes may be inferred; that's OK if marked as "inferred".
Mechanism chains may be theoretical; that's OK if clearly labeled.
Return ONLY JSON.
"""


# ═══════════════════════════════════════════════════════════════════════════
# PROMPT MAPPING AND UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

PROMPT_MAP_V4 = {
    "classify": PROMPT_CLASSIFY_V4,
    "empirical_research": PROMPT_EMPIRICAL_V4,
    "meta_analysis": PROMPT_META_ANALYSIS_V4,
    "systematic_review": PROMPT_SYSTEMATIC_REVIEW_V4,
    "narrative_review": PROMPT_NARRATIVE_REVIEW_V4,
    "theoretical": PROMPT_THEORETICAL_V4,
    "qualitative": PROMPT_QUALITATIVE_V4,
    "instrument_validation": PROMPT_INSTRUMENT_V4,
}


def get_family_prompt(article_type: str) -> str:
    """Get the V4 prompt for a given article type."""
    return PROMPT_MAP_V4.get(article_type, "")


def get_validation_suffix() -> str:
    """Get the validation suffix that applies to all extractions."""
    return VALIDATION_SUFFIX_V4


def get_verification_prompt() -> str:
    """Get the verification prompt for Stage 3."""
    return PROMPT_VERIFY_V4


def get_field_requirements(article_type: str) -> Dict[str, List[str]]:
    """Get field requirements for an article type."""
    return FIELD_REQUIREMENTS.get(article_type, {})
