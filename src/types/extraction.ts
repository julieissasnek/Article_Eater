/**
 * @file extraction.ts
 * @description Extraction-to-theory bridge types, adapted to CC-5 audit reality.
 */

import { AttributeDomainID } from './attribute';
import { Level } from './template';

/**
 * The source location of a finding within a paper.
 */
export type SourceLocation =
  | "abstract"
  | "results_table"
  | "results_text"
  | "discussion";

/**
 * Outcome domains map to template causal-link levels.
 */
export type OutcomeDomain = Level;

/**
 * Direction of the reported effect.
 */
export type EffectDirection =
  | "positive"
  | "negative"
  | "null"
  | "curvilinear"
  | "unclear";

/**
 * Coarse effect-size magnitude bucket.
 */
export type EffectMagnitude = "small" | "medium" | "large" | "unknown";

/**
 * Coarse effect pathway class.
 */
export type EffectPathway =
  | "subpersonal"
  | "personal_epistemic"
  | "mixed"
  | "unknown";

/**
 * Study design classification.
 */
export type StudyDesign =
  | "RCT"
  | "quasi-experimental"
  | "correlational"
  | "qualitative"
  | "review"
  | "meta-analysis"
  | "unknown";

/**
 * Raw/semi-structured finding from extraction.
 *
 * CX-4b: `architectural_variable` and `direction` are optional to match CC-5 findings.
 */
export interface ExtractedFinding {
  /** Unique ID of the paper. */
  paper_id: string;

  /** Unique ID of this specific finding. */
  finding_id: string;

  /** Where in the paper this was found. */
  source_location: SourceLocation;

  /**
   * Architectural variable block.
   * Optional because CC-5 reports it can be entirely missing.
   */
  architectural_variable?: {
    /** Raw text from the paper, e.g., "ceiling height", "open plan". */
    raw_text?: string;

    /** Normalized name if extraction succeeded. */
    normalized_name?: string;

    /** Mapped domain ID if extraction succeeded. */
    attribute_domain?: AttributeDomainID;

    /** Mapped sub-attribute ID if extraction succeeded. */
    sub_attribute?: string;

    /** Confidence in mapping (0..1). */
    mapping_confidence?: number;
  };

  /**
   * Optional intervention fallback text for mapping when architectural variable is missing.
   */
  intervention_text?: string;

  /**
   * Outcome variable.
   * CC-5 reports this is often present but may be partially normalized.
   */
  outcome_variable: {
    /** Raw text from paper, e.g., "stress", "focus". */
    raw_text: string;

    /** Standardized name key if available. */
    normalized_name?: string;

    /** Domain classification if available. */
    domain?: OutcomeDomain;
  };

  /**
   * Observed effect block.
   * CX-4b: `direction` is optional to match CC-5 partial availability.
   */
  effect?: {
    direction?: EffectDirection;

    significance?: {
      p_value?: number;
      is_significant: boolean;
      confidence_interval?: string;
    };

    effect_size?: {
      type: string;
      value: number;
    };

    /** Optional coarse magnitude when extraction or post-processing provides it. */
    magnitude?: EffectMagnitude;
  };

  /**
   * Optional pathway classification (CC-5 reports missing in current pipeline).
   */
  effect_pathway?: EffectPathway;

  /** Study-quality metadata. */
  study_metadata: {
    design: StudyDesign;
    sample_size?: number;
    control_condition?: string;
    demographics?: string;
  };
}

/**
 * Clean input consumed by theory-tier matching.
 */
export interface TheoryMatchInput {
  /** Primary attribute domain to query. */
  attribute_domain_id: AttributeDomainID;

  /** Specific sub-attribute if known. */
  sub_attribute_id?: string;

  /** Outcome domain used to filter/template-match. */
  outcome_domain: OutcomeDomain;

  /** Optional observed direction. */
  direction?: EffectDirection;

  /** Optional coarse effect magnitude for richer evaluation. */
  magnitude?: EffectMagnitude;

  /** Optional pathway signal for richer evaluation. */
  effect_pathway?: EffectPathway;
}

/**
 * Structured mapper output for epistemically honest degradation.
 */
export interface ExtractionToTheoryMapResult {
  /** Mapper output; null only when no viable mapping can be produced. */
  result: TheoryMatchInput | null;

  /** Mapper confidence in [0,1]. */
  confidence: number;

  /** Non-fatal warnings (missing fields, low-confidence mapping, etc.). */
  warnings: string[];
}

/**
 * Function signature for the bridge mapper (CC-6).
 */
export type ExtractionToTheoryMapper = (
  finding: ExtractedFinding,
) => Promise<ExtractionToTheoryMapResult>;
