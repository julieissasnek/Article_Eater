
import { Template, BridgingQuality } from '../types/template';
import { ReductionClaim, ConfidenceLevel, EdgeType } from '../types/reduction';
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
    template: Template,
    targetId: string,
    description: string,
    direction: "positive" | "negative" | "null"
): MechanisticClaim {
    const claimId = `CLM_${crypto.randomBytes(4).toString('hex').toUpperCase()}`;
    const predictedOutcome =
        template.causal_links[template.causal_links.length - 1]?.to_variable || "Unknown Outcome";

    return {
        claim_id: claimId,
        source_template_id: template.template_id,
        target_id: targetId,
        instantiation_description: description,
        predicted_outcome: predictedOutcome,
        predicted_direction: direction,
        prior_maturity: template.overall_maturity,
        prior_bridging: derivePriorBridging(template),
    };
}

function derivePriorBridging(template: Template): BridgingQuality {
    if (!template.causal_links.length) return "speculative";

    const rank: Record<BridgingQuality, number> = {
        strong: 3,
        moderate: 2,
        weak: 1,
        speculative: 0
    };

    // Conservative prior: use weakest link bridging quality in the chain.
    return template.causal_links.reduce<BridgingQuality>((current, link) => {
        return rank[link.bridging_quality] < rank[current] ? link.bridging_quality : current;
    }, "strong");
}

/**
 * Generates ReductionEdges from a ReductionClaim.
 * @param reduction The reduction claim to process.
 */
export function createEdgesFromReduction(reduction: ReductionClaim): ReductionEdge[] {
    const reductionId = reduction.claim_id;
    const confidence = normalizeConfidence(reduction);

    return reduction.template_nodes.map(templateId => ({
        reduction_id: reductionId,
        from_construct: reduction.tier2_construct,
        to_template: templateId,
        edge_type: "MODULATES",
        confidence
    }));
}

function normalizeEdgeType(value: unknown): EdgeType {
    const v = String(value).toUpperCase();
    return v === "IMPLEMENTS" ||
        v === "ENABLES" ||
        v === "MODULATES" ||
        v === "PARTIALLY_IMPLEMENTS"
        ? v as EdgeType
        : "MODULATES";
}

function normalizeConfidence(reduction: ReductionClaim): ConfidenceLevel {
    const legacy = (reduction as { confidence?: unknown }).confidence;
    if (legacy === "HIGH" || legacy === "MEDIUM" || legacy === "LOW") {
        return legacy as ConfidenceLevel;
    }

    switch (reduction.overall_confidence) {
        case "HIGH":
            return "HIGH";
        case "LOW":
            return "LOW";
        case "MEDIUM":
        default:
            return "MEDIUM";
    }
}
