/**
 * @file crossReference.ts
 * @description Defines the data structures for the Cross-Reference Matrix and Gap Reports.
 * Based on the schema in Doc 35 (CX-1).
 */

import { AttributeDomainID, CoverageRating } from './attribute';

/**
 * The Cross-Reference Matrix.
 * A 2D lookup: matrix[template_id][domain_id] → coverage_rating
 * @see Doc 35, Line 183
 */
export interface CrossRefMatrix {
  [template_id: string]: {
    [domain_id in AttributeDomainID]?: CoverageRating;
  };
}

/**
 * A report on a coverage gap in the Theory Tier.
 */
export interface GapReport {
  domain_id: AttributeDomainID;
  current_coverage: CoverageRating;
  missing_mechanisms: string[]; // Descriptions of what logic is missing
  recommendation: string;
}

/**
 * Represents the full mechanism-first index entry.
 * @see Doc 35, Line 172
 */
export interface MechanismIndexEntry {
  template_id: string;
  architectural_attributes: {
    domain_id: AttributeDomainID;
    sub_attributes: string[]; // IDs
    coverage: CoverageRating;
  }[];
}
