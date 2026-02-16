
import { MechanisticTemplate } from '../types/template';
import { ReductionClaim } from '../types/reduction';
import { MechanisticClaim, ReductionEdge } from '../types/claim';
import * as crypto from 'crypto';

/**
 * Generates a MechanisticClaim from a Template instantiation.
 * @param template The template being instantiated.
 * @param targetId The ID of the finding or object being evaluated.
 * @param description Description of the instantiation condition.
 * @param direction Predicted direction of the outcome.
 */
export function createClaimFromTemplate(
    template: MechanisticTemplate,
    targetId: string,
    description: string,
    direction: "positive" | "negative" | "null"
): MechanisticClaim {
    const claimId = `CLM_${crypto.randomBytes(4).toString('hex').toUpperCase()}`;

    // Determine bridging quality from the causal chain (taking the minimum or representative value)
    // For simplicity, we take the overall bridging quality if available, or derive it.
    // The template has 'overall_maturity'.

    return {
        claim_id: claimId,
        source_template_id: template.id,
        target_id: targetId,
        instantiation_description: description,
        predicted_outcome: template.causal_chain[template.causal_chain.length - 1]?.change_produced || "Unknown Outcome",
        predicted_direction: direction,
        prior_maturity: template.overall_maturity,
        prior_bridging: "MEDIUM", // Default, should be derived from template analysis
    };
}

/**
 * Generates ReductionEdges from a ReductionClaim.
 * @param reduction The reduction claim to process.
 */
export function createEdgesFromReduction(reduction: ReductionClaim): ReductionEdge[] {
    return reduction.reducing_templates.map(rt => ({
        reduction_id: reduction.reduction_id,
        from_construct: reduction.tier2_construct,
        to_template: rt.template_id,
        edge_type: rt.edge_type,
        confidence: reduction.confidence
    }));
}
