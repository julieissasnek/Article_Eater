import type {
  AttributeDomainID,
  CoverageRating,
  TemplateMapping,
} from "../types/attribute";
import type { GapReport } from "../types/crossReference";
import type { ReductionClaim } from "../types/reduction";
import type { BridgingQuality, Level, Maturity, Template } from "../types/template";

/**
 * Query filters for template search.
 */
export interface TemplateSearchQuery {
  fromLevel?: Level;
  toLevel?: Level;
  activity?: string;
  minMaturity?: Maturity;
  frameworkId?: string;
}

/**
 * Attribute mapping used for reverse lookup.
 */
export interface AttributeMapping {
  template_id: string;
  domain_id: AttributeDomainID;
  sub_attribute_id?: string;
  coverage_rating: CoverageRating;
}

/**
 * Template mapping enriched with domain identifiers for attribute-first lookup.
 */
export interface DomainTemplateMapping extends TemplateMapping {
  domain_id: AttributeDomainID;
  sub_attribute_id?: string;
  coverage_rating: CoverageRating;
}

/**
 * Result of the compound expert workflow query.
 */
export interface EvaluateFindingResult {
  relevantTemplates: DomainTemplateMapping[];
  predictions: string[];
  critiques: string[];
  extensions: string[];
}

/**
 * API errors surfaced by theory module calls.
 */
export class TheoryApiError extends Error {
  readonly code: "NOT_FOUND" | "INVALID_ARGUMENT" | "INVARIANT_VIOLATION";

  constructor(
    code: "NOT_FOUND" | "INVALID_ARGUMENT" | "INVARIANT_VIOLATION",
    message: string,
  ) {
    super(message);
    this.name = "TheoryApiError";
    this.code = code;
  }
}

/**
 * In-memory registries consumed by the module API.
 */
export interface TheoryRegistry {
  templatesById: Readonly<Record<string, Template>>;
  templateMappings: readonly DomainTemplateMapping[];
  attributeMappings: readonly AttributeMapping[];
  reductionClaims: readonly ReductionClaim[];
  gapReports: readonly GapReport[];
}

/**
 * Public API surface for theory-tier queries.
 */
export interface TheoryTierApi {
  getTemplatesForAttribute(
    domainId: AttributeDomainID,
    subAttributeId?: string,
  ): DomainTemplateMapping[];
  getAttributesForTemplate(templateId: string): AttributeMapping[];
  getCoverage(templateId: string, domainId: AttributeDomainID): number;
  getGaps(maxCoverage?: number): GapReport[];
  getReductionForConstruct(theory: string, construct: string): ReductionClaim;
  getConstructsUsingTemplate(templateId: string): ReductionClaim[];
  searchTemplates(query: TemplateSearchQuery): Template[];
  evaluateFinding(attributeDomainIds: AttributeDomainID[]): EvaluateFindingResult;
}

/**
 * Factory for a synchronous, in-memory theory API implementation.
 */
export function createTheoryApi(registry: TheoryRegistry): TheoryTierApi {
  return {
    getTemplatesForAttribute(domainId, subAttributeId) {
      return registry.templateMappings.filter(
        (mapping) =>
          mapping.domain_id === domainId &&
          (subAttributeId === undefined || mapping.sub_attribute_id === subAttributeId),
      );
    },

    getAttributesForTemplate(templateId) {
      return registry.attributeMappings.filter(
        (mapping) => mapping.template_id === templateId,
      );
    },

    getCoverage(templateId, domainId) {
      const mapping = registry.attributeMappings.find(
        (item) => item.template_id === templateId && item.domain_id === domainId,
      );
      return mapping?.coverage_rating ?? 0;
    },

    getGaps(maxCoverage = 1) {
      if (!Number.isInteger(maxCoverage) || maxCoverage < 0 || maxCoverage > 4) {
        throw new TheoryApiError(
          "INVALID_ARGUMENT",
          "maxCoverage must be an integer from 0 to 4",
        );
      }
      return registry.gapReports.filter((gap) => gap.current_coverage <= maxCoverage);
    },

    getReductionForConstruct(theory, construct) {
      const match = registry.reductionClaims.find(
        (claim) => claim.tier2_theory === theory && claim.tier2_construct === construct,
      );
      if (!match) {
        throw new TheoryApiError(
          "NOT_FOUND",
          `Reduction claim not found for theory=${theory}, construct=${construct}`,
        );
      }
      return match;
    },

    getConstructsUsingTemplate(templateId) {
      return registry.reductionClaims.filter((claim) => {
        const viaLegacy =
          claim.reducing_templates?.some((item) => item.template_id === templateId) ?? false;
        const viaNodes = claim.template_nodes.includes(templateId);
        return viaLegacy || viaNodes;
      });
    },

    searchTemplates(query) {
      const maturityOrder: Record<Maturity, number> = {
        theoretical: 0,
        preliminary: 1,
        supported: 2,
        established: 3,
      };

      return Object.values(registry.templatesById).filter((template) => {
        const matchesMaturity =
          query.minMaturity === undefined ||
          maturityOrder[template.overall_maturity] >= maturityOrder[query.minMaturity];

        const matchesFramework =
          query.frameworkId === undefined ||
          template.framework_ids.includes(query.frameworkId);

        const matchesLink =
          query.fromLevel === undefined &&
          query.toLevel === undefined &&
          query.activity === undefined
            ? true
            : template.causal_links.some((link) => {
                const fromOk =
                  query.fromLevel === undefined || link.from_level === query.fromLevel;
                const toOk =
                  query.toLevel === undefined || link.to_level === query.toLevel;
                const activityOk =
                  query.activity === undefined || link.activity === query.activity;
                return fromOk && toOk && activityOk;
              });

        return matchesMaturity && matchesFramework && matchesLink;
      });
    },

    evaluateFinding(attributeDomainIds) {
      if (attributeDomainIds.length === 0) {
        throw new TheoryApiError(
          "INVALID_ARGUMENT",
          "evaluateFinding requires at least one attribute domain ID",
        );
      }

      const uniqueDomainIds = [...new Set(attributeDomainIds)];
      const relevantTemplates = registry.templateMappings.filter((mapping) =>
        uniqueDomainIds.includes(mapping.domain_id),
      );

      const predictions = relevantTemplates
        .map((mapping) => {
          const template = registry.templatesById[mapping.template_id];
          if (!template) {
            return "";
          }
          return `${template.display_id}: ${template.structural_pattern}`;
        })
        .filter((line) => line.length > 0);

      const critiques = [
        "Potential confounds should be checked for modality blocking and demand characteristics.",
        "Coverage asymmetry can lower confidence for weakly-mapped domains.",
      ];

      const extensions = [
        "Test whether effects strengthen when multiple modalities are jointly active.",
        "Run subgroup analyses to isolate domain-specific versus convergence effects.",
      ];

      return {
        relevantTemplates,
        predictions,
        critiques,
        extensions,
      };
    },
  };
}

/**
 * Optional helper for converting bridge quality to a numeric prior.
 */
export function bridgingQualityToPrior(quality: BridgingQuality): number {
  switch (quality) {
    case "strong":
      return 0.85;
    case "moderate":
      return 0.7;
    case "weak":
      return 0.5;
    case "speculative":
      return 0.35;
  }
}
