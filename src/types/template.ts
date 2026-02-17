/**
 * @file template.ts
 * @description Defines the core data structures for Article Eater's Theory Tier templates.
 * Based on the schema in Doc 35 (CX-1).
 */

/**
 * Maturity level of a template or causal link.
 * @see Doc 35, Line 267
 */
export type Maturity =
  | "established"
  | "supported"
  | "preliminary"
  | "theoretical";

/**
 * Quality of the bridge between levels.
 * @see Doc 35, Line 268
 */
export type BridgingQuality =
  | "strong"
  | "moderate"
  | "weak"
  | "speculative";

/**
 * Level taxonomy for causal links.
 * @see Doc 35, Line 270
 */
export type Level =
  | "environmental"
  | "ecological"
  | "sensory"
  | "perceptual"
  | "neural"
  | "subcortical"
  | "neuroendocrine"
  | "cellular"
  | "circuit"
  | "computational"
  | "cognitive"
  | "affective"
  | "behavioral"
  | "motor"
  | "physiological"
  | "psychological"
  | "phenomenological"
  | "memorial"
  | "systems"
  | "subpersonal"
  | "molecular"
  | "personal_epistemic"
  | "biophysical";

/**
 * The nature of the causal relationship.
 */
export type Activity =
  | "enhances"
  | "inhibits"
  | "modulates";

/**
 * Structural organization of causal links in a template.
 */
export type CausalTopology =
  | "serial"
  | "parallel"
  | "hybrid";

/**
 * How parallel channels combine at convergence.
 */
export type ConvergenceRule =
  | "additive"
  | "multiplicative"
  | "super_additive"
  | "competitive"
  | "unknown";

/**
 * Timescale used by temporal mechanisms.
 */
export type TemporalScale =
  | "seconds"
  | "minutes"
  | "hours"
  | "circadian_24h"
  | "days"
  | "weeks"
  | "months"
  | "years";

/**
 * Type of temporal variable used in a causal link.
 */
export type TemporalVariableType =
  | "state"
  | "rate_of_change"
  | "phase"
  | "duration";

/**
 * A reference to a scholarly work.
 */
export interface Reference {
  citation: string;
  google_scholar_count: number;
}

/**
 * The core causal unit of a template.
 * Represents a directed link between two variables at specified levels.
 */
export interface CausalLink {
  from_variable: string;    // e.g., "fractal_dimension_D"
  to_variable: string;      // e.g., "processing_fluency"
  activity: Activity;       // e.g., "enhances"
  from_level: Level;        // e.g., "environmental"
  to_level: Level;          // e.g., "cognitive"
  bridging_quality: BridgingQuality;
  maturity: Maturity;
  /** Optional channel identifier for parallel-channel templates. */
  channel_id?: string;
  /** Optional convergence target variable for parallel channels. */
  converges_on?: string;
  /** Optional temporal metadata for slow or dynamic mechanisms. */
  temporal?: {
    scale: TemporalScale;
    variable_type?: TemporalVariableType;
    notes?: string;
  };
}

/**
 * A Mechanistic Template.
 * Represents a reusable causal pattern that explains architectural effects.
 */
export interface Template {
  /** Unique identifier, e.g., "PP_SPECTRAL_MATCH_001" */
  template_id: string;

  /** Human-readable short ID, e.g., "T1" */
  display_id: string;

  /** Descriptive name */
  name: string;

  /** Prose description of the causal pattern */
  structural_pattern: string;

  /** The general principle this instantiates */
  higher_order_principle: string;

  /** Which theoretical frameworks it belongs to */
  framework_ids: string[];

  /** The core causal links (2-8 per template) */
  causal_links: CausalLink[];

  /** Whether links are serial, parallel, or mixed. */
  causal_topology?: CausalTopology;

  /** Optional aggregation rule when multiple channels converge. */
  convergence_rule?: ConvergenceRule;

  /** Conditions under which this template applies */
  scope_conditions: string[];

  /** Factors that change the effect size/direction */
  moderators: string[];

  /** IDs of other templates this interacts with */
  interactions: string[];

  /** Overall maturity of the template logic */
  overall_maturity: Maturity;

  /** Supporting literature */
  key_references: Reference[];

  /** Version of the template definition */
  version?: string;

  /**
   * Backward-compatible calibration payload used by several calibration test fixtures.
   * Field shape varies by template family.
   */
  calibration_data?: Record<string, any>;
}
