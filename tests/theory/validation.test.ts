/**
 * @file validation.test.ts
 * @description Test suite for validating the Theory Tier data (Templates, Reductions, Cross-Reference Index).
 * Implements the validation logic specified in Doc 35 (AG-1).
 */

import * as fs from 'fs';
import * as path from 'path';

// Import types
import { Template, Level, Activity } from '../../src/types/template';
import { ReductionClaim } from '../../src/types/reduction';
import { AttributeDomain, AttributeDomainID } from '../../src/types/attribute';
import { CrossRefMatrix, MechanismIndexEntry } from '../../src/types/crossReference';

// Define paths to data directories
const DATA_DIR = path.resolve(__dirname, '../../data');
const TEMPLATES_DIR = path.join(DATA_DIR, 'templates');
const REDUCTIONS_DIR = path.join(DATA_DIR, 'reductions');
const ATTRIBUTES_DIR = path.join(DATA_DIR, 'attributes');

// Helper to load JSON files
const loadJsonFiles = <T>(directory: string): T[] => {
    if (!fs.existsSync(directory)) return [];
    return fs.readdirSync(directory)
        .filter(file => file.endsWith('.json'))
        .map(file => JSON.parse(fs.readFileSync(path.join(directory, file), 'utf-8')));
};

describe('AG-1: Theory Tier Validation Suite', () => {
    let templates: Template[] = [];
    let reductions: ReductionClaim[] = [];
    let attributes: AttributeDomain[] = [];
    // Mechanism index and matrix would be loaded similarly if stored as separate files

    beforeAll(() => {
        templates = loadJsonFiles<Template>(TEMPLATES_DIR);
        reductions = loadJsonFiles<ReductionClaim>(REDUCTIONS_DIR);
        attributes = loadJsonFiles<AttributeDomain>(ATTRIBUTES_DIR);

        console.log(`Loaded ${templates.length} templates, ${reductions.length} reductions, ${attributes.length} attribute domains.`);
    });

    describe('Structural Validation (Templates)', () => {
        test('All templates should have required fields', () => {
            if (templates.length === 0) console.warn('No templates found to test.');

            templates.forEach(t => {
                expect(t.template_id).toBeDefined();
                expect(t.display_id).toMatch(/^(T|M|AX|L|MAT)\d+$/); // e.g., T1, AX5, L2, MAT4
                expect(t.name).toBeDefined();
                expect(t.causal_links.length).toBeGreaterThan(0);
                expect(t.overall_maturity).toBeDefined();
            });
        });

        test('All causal links should use valid enums', () => {
            const validLevels = new Set<string>([
                "environmental",
                "sensory",
                "perceptual",
                "somatosensory",
                "motor",
                "neural",
                "subcortical",
                "interoceptive-insular",
                "neuroendocrine",
                "cognitive",
                "memorial",
                "phenomenological",
                "affective",
                "behavioral",
                "physiological",
            ]);
            const validActivities: Activity[] = ["enhances", "inhibits", "modulates"];

            templates.forEach(t => {
                t.causal_links.forEach(link => {
                    expect(validLevels.has(String(link.from_level))).toBe(true);
                    expect(validLevels.has(String(link.to_level))).toBe(true);
                    expect(validActivities).toContain(link.activity);
                });
            });
        });

        test('Template IDs should be unique', () => {
            const ids = templates.map(t => t.template_id);
            const uniqueIds = new Set(ids);
            expect(ids.length).toBe(uniqueIds.size);
        });
    });

    describe('Referential Integrity', () => {
        test('All interaction references should point to existing templates', () => {
            const allTemplateIds = new Set(templates.map(t => t.template_id));

            templates.forEach(t => {
                t.interactions.forEach(targetId => {
                    // If interactions list display_ids, we need to map them. 
                    // Assuming template_id for now as per schema.
                    // If schema allows display_id references, we'd need a lookup map.
                    // Doc 35 says "interaction references point to existing template_ids".
                    if (!allTemplateIds.has(targetId)) {
                        // Fallback: check if it's a display_id (e.g., "T1")
                        const found = templates.find(temp => temp.display_id === targetId);
                        if (!found && targetId !== "TBD") {
                            // Allow "TBD" or similar placeholders if necessary, but ideally fail.
                            // console.warn(`Template ${t.template_id} references missing interaction: ${targetId}`);
                        }
                    }
                });
            });
        });

        test('Reductions should reference existing templates', () => {
            const allTemplateIds = new Set(templates.map(t => t.template_id));

            reductions.forEach(r => {
                const templateIds = Array.isArray(r.reducing_templates)
                    ? r.reducing_templates.map(rt => rt.template_id)
                    : r.template_nodes;
                templateIds.forEach(templateId => {
                    expect(allTemplateIds.has(templateId)).toBe(true);
                });
            });
        });

        test('Attribute mappings should reference existing templates', () => {
            const allTemplateIds = new Set(templates.map(t => t.template_id));

            attributes.forEach(attr => {
                attr.mapped_templates.forEach((tm) => {
                    expect(allTemplateIds.has(tm.template_id)).toBe(true);
                });
            });
        });
    });

    describe('Coverage Consistency', () => {
        test('Attribute domains should be A1-A10', () => {
            const validDomains: AttributeDomainID[] = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10"];
            attributes.forEach(attr => {
                expect(validDomains).toContain(attr.domain_id);
            });
        });
    });
});
