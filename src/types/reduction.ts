/**
 * @file reduction.ts
 * @description Defines the data structures for ReductionClaims that map Tier 2 theories to Tier 1 mechanisms.
 * Based on the schema in Doc 35 (CX-1).
 */

/**
 * Role of a template in a reduction.
 */
export type ReductionRole = string; // Open-ended description, e.g., "primary mechanism"

/**
 * Necessity of a template for the reduction.
 */
export type Necessity =
  | "required"
  | "typical"
  | "occasional";

/**
 * How the template relates to the Tier 2 construct.
 * @see Doc 35, Line 271
 */
export type EdgeType =
  | "implements"
  | "enables"
  | "modulates"
  | "partially_implements";

/**
 * Confidence level in the reduction.
 */
export type Confidence = "high" | "moderate" | "low";

/**
 * A template's contribution to a reduction.
 */
export interface ReducingTemplate {
  /** Reference to the template registry */
  template_id: string;

  /** How this template contributes */
  role: ReductionRole;

  /** How necessary this template is */
  necessity: Necessity;

  /** The nature of the relationship */
  edge_type: EdgeType;
}

/**
 * An edge in the DAG of template interactions.
 */
export interface DAGEdge {
  from: string; // template_id
  to: string;   // template_id
  type: string; // Description of the interaction
}

/**
 * The Directed Acyclic Graph structure of the reduction.
 */
export interface DAGStructure {
  nodes: string[]; // List of template_ids
  edges: DAGEdge[];
}

/**
 * A Reduction Claim.
 * Maps a high-level Tier 2 construct (like "Fascination") to a graph of Tier 1 mechanisms.
 */
export interface ReductionClaim {
  /** Unique ID, e.g., "RC_ART_FASCINATION_001" */
  reduction_id: string;

  /** The Tier 2 theory, e.g., "ART" */
  tier2_theory: string;

  /** The specific construct, e.g., "Fascination" */
  tier2_construct: string;

  /** Definition of the construct */
  tier2_construct_definition: string;

  /** The Tier 1 templates that explain this construct */
  reducing_templates: ReducingTemplate[];

  /** The interaction graph between these templates */
  dag_structure: DAGStructure;

  /** What the Tier 2 construct captures that the reduction does NOT */
  residual: string;

  /** Confidence in this reduction */
  confidence: Confidence;

  /** Citations supporting the reduction */
  key_evidence: string[];
}
