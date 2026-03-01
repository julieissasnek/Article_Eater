
import { TheoryAPI } from '../src/api/index';

async function validate() {
    console.log("Starting Theory Validation...");

    const api = new TheoryAPI();
    await api.initialize();

    const templates = api.getAllTemplates();
    const reductions = api.getAllReductions();
    const domains = api.getAllAttributeDomains();

    console.log(`Loaded ${templates.length} templates.`);
    console.log(`Loaded ${reductions.length} reductions.`);
    console.log(`Loaded ${domains.length} attribute domains.`);

    const errors: string[] = [];

    // 1. Validate Reductions -> Templates
    reductions.forEach(reduction => {
        const reductionId = reduction.claim_id || "UNKNOWN_REDUCTION";
        const templateIds = reduction.template_nodes || [];

        templateIds.forEach(tid => {
            if (!api.getTemplate(tid)) {
                errors.push(`Reduction ${reductionId} references missing template: ${tid}`);
            }
        });
    });

    // 2. Validate Attribute Domains -> Templates
    domains.forEach(domain => {
        let domainCoverage = 0;
        domain.mapped_templates.forEach(mapping => {
            if (!api.getTemplate(mapping.template_id)) {
                errors.push(`Attribute Domain ${domain.domain_id} references missing template: ${mapping.template_id}`);
            } else {
                domainCoverage++;
            }
        });
        if (domainCoverage === 0) {
            errors.push(`Attribute Domain ${domain.domain_id} has no valid mapped templates.`);
        }
    });

    // 3. Check for specific Core Templates (just a sample check)
    const coreTemplates = [
        // Legacy (Mapped manually from template_id_mapping_master.json)
        'PP_SPECTRAL_MATCH_001', 'PP_COMPLEXITY_GOLDILOCKS_002', 'PP_FRACTAL_FLUENCY_003', 'SN_SPATIAL_LEGIBILITY_004', 'NM_THREAT_HPA_001',
        'NM_NATURE_RESTORATION_006', 'DT_DMN_TPN_TOGGLE_007', 'EC_AFFORDANCE_POSTURAL_001', 'DP_IMPLICIT_EVALUATION_001', 'EC_EMBODIED_SPACE_010',
        'CB_LIGHT_CIRCADIAN_011', 'IC_INTEROCEPTIVE_AFFECT_CONSTRUCTION_001',
        'CROWDING_STRESS_023', 'ALLOSTATIC_MASTER_001', 'ENCLOSURE_SAFETY_030',
        // New
        'LUM_CONTRAST_PE_001', 'CIRCADIAN_ARCH_REG_001', 'DAYLIGHT_MULTICHANNEL_001', 'CCT_TEMPORAL_ECOLOGICAL_001', 'DYNAMIC_LIGHT_TEMPORAL_001',
        'CT_AFFECTIVE_TOUCH_001', 'THERMAL_ADAPTIVE_PE_001', 'MATERIAL_IDENTITY_INTEGRATION_001', 'NATURAL_MATERIAL_CONVERGENCE_001', 'MATERIAL_CULTURAL_CONDITIONING_001'
    ];
    coreTemplates.forEach(tid => {
        if (!api.getTemplate(tid)) {
            errors.push(`Core Template missing: ${tid}`);
        }
    });

    if (errors.length > 0) {
        console.error("\nValidation FAILED with errors:");
        errors.forEach(e => console.error(`- ${e}`));
        process.exit(1);
    } else {
        console.log("\nValidation PASSED. Theory completeness verified.");
        process.exit(0);
    }
}

validate().catch(err => {
    console.error("Validation crashed:", err);
    process.exit(1);
});
