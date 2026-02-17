import { CausalLink, Maturity } from "./template";

/**
 * @file reduction.ts
 * @description Defines the data structures for ReductionClaims that map Tier 2 theories to Tier 1 mechanisms.
 * Based on the schema in Doc 35 (CX-1) and updated via Panel D1 (Doc 18).
 */

export type ConfidenceLevel = "HIGH" | "MEDIUM" | "LOW";

/**
 * 4-dimensional confidence assessment as per Mitchell (2020) & Panel D1.
 */
export interface ConfidenceStack {
  extraction_confidence: number;  // 0.0 - 1.0 (PDF extraction quality)
  statistical_confidence: number; // 0.0 - 1.0 (p-values, effect sizes)
  mechanism_confidence: number;   // 0.0 - 1.0 (detail of causal chain)
  epistemic_confidence: number;   // 0.0 - 1.0 (consensus, replication)
}

export type GapType =
  | "MISSING_NODE"             // A required mechanism is completely unknown
  | "MISSING_EDGE"             // Connection between known nodes is unproven
  | "AMBIGUOUS_DIRECTION"      // Correlation exists, direction unknown
  | "UNKNOWN_INTERACTION"      // How two mechanisms combine is unknown
  | "LACK_OF_ECOLOGICAL_VALIDITY" // Lab results may not transfer to field
  | "MEASUREMENT_LATENCY"      // Temporal resolution issues
  | "INDIVIDUAL_VARIANCE"      // Mechanism highly dependent on subject traits
  | "PHENOMENOLOGICAL_RESIDUAL"; // Qualia not captured by function

/**
 * A gap in the reduction schema — future research target.
 */
export interface SchemaGap {
  gap_id: string;
  location: string;            // Edge ID or Node ID where gap exists
  gap_type: GapType;
  description: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  suggested_investigation?: string;
}

export type EvidenceClassification =
  | "EDGE_SUPPORTING"
  | "CLAIM_COHERENT"
  | "EDGE_CONTRADICTING"
  | "UNACCOUNTED";

/**
 * Link between a staging theory-link row and this reduction claim.
 */
export interface EvidenceLink {
  staging_row_id: string;      // FK to staging theory-link table
  classification: EvidenceClassification;
  linked_edge_id?: string;     // which edge in the DAG this supports/contradicts
  notes?: string;
}

export interface RevisionEntry {
  date: string;
  author: string;
  change_summary: string;
  affected_nodes?: string[];
}

export type CompositionalAdequacy =
  | "FULLY_DECOMPOSABLE"
  | "INTERACTION_DEPENDENT"
  | "EMERGENT_RESIDUAL"
  | "PARTIALLY_DECOMPOSABLE";

export type ReducibilityJudgment =
  | "FULLY_REDUCIBLE"
  | "PARTIALLY_REDUCIBLE"
  | "AUTONOMOUSLY_EXPLANATORY";

export type EdgeType = "PRODUCES" | "INHIBITS" | "CONSTITUTES" | "MODULATES";

export type Testability = "DIRECTLY_TESTABLE" | "INDIRECTLY_TESTABLE" | "NOT_YET_TESTABLE";

/**
 * A reduction edge in the DAG.
 * Represents a causal or constitutive relationship between templates or constructs.
 */
export interface ReductionEdge {
  edge_id: string;
  from_node: string;           // template_id or tie2_construct (if recursive)
  to_node: string;             // template_id or tie2_construct
  edge_type: EdgeType;

  // Causal details
  causal_link?: CausalLink;    // Re-use standard causal link structure if applicable

  // Constitutive details
  mutual_manipulability_evidence?: string; // For CONSTITUTES edges

  // Confidence & Verification
  edge_confidence: ConfidenceStack;
  testability: Testability;
  intervention_method?: string; // Proposed experiment

  // Gaps
  gap_type?: GapType;
  gap_description?: string;

  // Evidence
  key_evidence: string[];      // Citations
  staging_row_ids: string[];   // Links to staging data
}

/**
 * A Reduction Claim.
 * Maps a high-level Tier 2 construct (like "Fascination") to a graph of Tier 1 mechanisms.
 * Updated to match Panel D1 Decision (Doc 18).
 */
export interface ReductionClaim {
  // Identity
  claim_id: string;            // e.g., "RC_ART_SOFT_FASCINATION_002"
  version: string;             // SemVer "1.0.0"
  created_date: string;
  created_by: string;          // "Panel T2-A", "CMR_pipeline", etc.
  revision_history: RevisionEntry[];

  // Construct Definition
  tier2_theory: string;        // "ART", "SRT", "Biophilia"
  tier2_construct: string;     // "soft_fascination", "immediate_affect"
  construct_definition: string;
  construct_validity: ConfidenceLevel;
  construct_validity_justification: string;

  // The Reduction DAG
  template_nodes: string[];    // IDs of participating templates: ["T27", "T68"]
  reduction_edges: ReductionEdge[];

  // Assessment
  compositional_adequacy: CompositionalAdequacy;
  compositional_notes?: string;

  // Residuals & Gaps
  schema_gaps: SchemaGap[];
  irreducible_residual?: string;
  reducibility_judgment: ReducibilityJudgment;

  // Narrative
  mechanism_narrative: string;

  // Evidence & Context
  supporting_evidence: EvidenceLink[];
  boundary_variables: string[]; // Markov blanket definition

  // Metadata
  valid_as_of_template_count: number; // e.g. 77 templates existing when created
  overall_confidence: ConfidenceLevel;
  overall_maturity: "how-possibly" | "how-plausibly" | "how-actually";
  panel_source: string;
  key_references: string[];
}


