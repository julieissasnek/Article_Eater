
export interface Attribute {
  id: string;
  name: string;
  description: string;
}

export type AttributeDomainID = string;

/**
 * Coverage rating for a template's mapping to an attribute.
 * 0=None, 1=Minimal, 2=Partial, 3=Moderate, 4=Strong
 */
export type CoverageRating = 0 | 1 | 2 | 3 | 4;

export interface TemplateMapping {
  template_id: string;
  coverage: CoverageRating;
  notes?: string;
}

export interface AttributeDomain {
  domain_id: string;
  name: string;
  description: string;
  attributes: Attribute[];
  mapped_templates: TemplateMapping[];
}
