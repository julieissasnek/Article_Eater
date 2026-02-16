import {
    ExtractedFinding,
    TheoryMatchInput
} from '../types/extraction';
import { AttributeDomainID } from '../types/attribute';
import { Level } from '../types/template';

/**
 * Maps an ExtractedFinding to a TheoryMatchInput.
 * @param finding The raw finding from the extraction pipeline.
 * @returns TheoryMatchInput ready for the Theory API.
 */
export function mapFindingToTheory(
    finding: ExtractedFinding
): TheoryMatchInput {

    // 1. Determine Attribute Domain
    let domainId: AttributeDomainID = "AD_SPATIAL"; // Default fallback
    let subAttr: string | undefined = undefined;

    if (finding.architectural_variable && finding.architectural_variable.attribute_domain) {
        domainId = finding.architectural_variable.attribute_domain;
        subAttr = finding.architectural_variable.sub_attribute;
    } else if (finding.architectural_variable?.raw_text) {
        // Fallback: Infer from raw text
        const inferred = inferAttributesFromText(finding.architectural_variable.raw_text);
        if (inferred.length > 0) {
            domainId = inferred[0].domain_id; // Pick highest confidence
            subAttr = inferred[0].attribute_name;
        }
    } else if (finding.intervention_text) {
        const inferred = inferAttributesFromText(finding.intervention_text);
        if (inferred.length > 0) {
            domainId = inferred[0].domain_id;
            subAttr = inferred[0].attribute_name;
        }
    }

    // 2. Construct TheoryMatchInput
    const input: TheoryMatchInput = {
        attribute_domain_id: domainId,
        sub_attribute_id: subAttr,
        outcome_domain: finding.outcome_variable.domain || "environmental", // Default to environmenal if missing
        direction: finding.effect?.direction,
        magnitude: finding.effect?.magnitude,
        effect_pathway: finding.effect_pathway
    };

    return input;
}

interface InferredAttribute {
    domain_id: AttributeDomainID;
    attribute_name: string;
    confidence: number;
}

/**
 * MOCK LLM Fallback: Infers attributes from text.
 */
function inferAttributesFromText(text: string): InferredAttribute[] {
    const mappings: InferredAttribute[] = [];
    const lower = text.toLowerCase();

    // Heuristic rules for demo
    if (lower.includes("ceiling") || lower.includes("height") || lower.includes("dimension")) {
        mappings.push({ domain_id: "AD_SPATIAL", attribute_name: "ceiling_height", confidence: 0.6 });
    }
    if (lower.includes("light") || lower.includes("sun") || lower.includes("window")) {
        mappings.push({ domain_id: "AD_VISUAL", attribute_name: "light", confidence: 0.6 });
    }
    if (lower.includes("wood") || lower.includes("stone") || lower.includes("material") || lower.includes("paneling")) {
        mappings.push({ domain_id: "AD_CONTENT", attribute_name: "material", confidence: 0.6 });
    }
    if (lower.includes("noise") || lower.includes("sound") || lower.includes("quiet")) {
        mappings.push({ domain_id: "AD_SENSORY_NON_VISUAL", attribute_name: "acoustic", confidence: 0.6 });
    }

    return mappings;
}
