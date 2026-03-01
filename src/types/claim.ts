/**
 * @file claim.ts
 * @description Defines the Claim types that bridge the Theory Tier to the Epistemic Core.
 * Based on the schema in Doc 35 (CX-1).
 */

import { Maturity, BridgingQuality } from './template';
import { EdgeType, ConfidenceLevel } from './reduction';

/**
 * Concrete instantiation of a template's prediction.
 * "This building's facade has D = 1.35, therefore processing fluency is predicted."
 * @see Doc 35, Line 274
 */
export interface MechanisticClaim {
  /** Unique ID for this specific claim instance */
  claim_id: string;

  /** The template that generated this claim */
  source_template_id: string;

  /** The specific finding or object being evaluated */
  target_id: string; // e.g., finding_id or building_id

  /** Description of the specific condition (e.g., "D = 1.35") */
  instantiation_description: string;

  /** The predicted outcome variable */
  predicted_outcome: string;

  /** The direction of the prediction */
  predicted_direction: "positive" | "negative" | "null";

  /** Prior confidence derived from the template's maturity */
  prior_maturity: Maturity;

  /** Prior confidence derived from bridging quality */
  prior_bridging: BridgingQuality;

  /** Slot for empirical evidence that confirms or disconfirms */
  empirical_evidence?: {
    finding_id: string;
    support_level: "supports" | "refutes" | "mixed" | "neutral";
    notes: string;
  };
}

/**
 * A reduction edge in the Epistemic Core graph.
 * Represents a "supports" or "explains" relationship between a Tier 2 node and Tier 1 nodes.
 */
export interface ReductionEdge {
  /** The ReductionClaim ID this edge is derived from */
  reduction_id: string;

  /** The Tier 2 construct (source) */
  from_construct: string;

  /** The Tier 1 template (target) */
  to_template: string;

  /** The nature of the relationship */
  edge_type: EdgeType;

  /** Confidence in this specific edge */
  confidence: ConfidenceLevel;
}
