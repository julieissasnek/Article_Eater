
import { Template, BridgingQuality } from '../types/template';
import { ReductionClaim, Confidence, EdgeType } from '../types/reduction';
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
    const reductionId = reduction.reduction_id || reduction.claim_id;
    const confidence = normalizeConfidence(reduction);
    const legacyTemplates = Array.isArray(reduction.reducing_templates)
        ? reduction.reducing_templates.filter(rt => typeof rt?.template_id === "string")
        : [];

    if (legacyTemplates.length > 0) {
        return legacyTemplates.map(rt => ({
            reduction_id: reductionId,
            from_construct: reduction.tier2_construct,
            to_template: rt.template_id,
            edge_type: normalizeEdgeType(rt.edge_type),
            confidence
        }));
    }

    return reduction.template_nodes.map(templateId => ({
        reduction_id: reductionId,
        from_construct: reduction.tier2_construct,
        to_template: templateId,
        edge_type: "modulates",
        confidence
    }));
}

function normalizeEdgeType(value: unknown): EdgeType {
    return value === "implements" ||
        value === "enables" ||
        value === "modulates" ||
        value === "partially_implements"
        ? value
        : "modulates";
}

function normalizeConfidence(reduction: ReductionClaim): Confidence {
    const legacy = (reduction as { confidence?: unknown }).confidence;
    if (legacy === "high" || legacy === "moderate" || legacy === "low") {
        return legacy;
    }

    switch (reduction.overall_confidence) {
        case "HIGH":
            return "high";
        case "LOW":
            return "low";
        case "MEDIUM":
        default:
            return "moderate";
    }
}
