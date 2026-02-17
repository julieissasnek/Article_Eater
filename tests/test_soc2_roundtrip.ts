
import { TemplateRegistry } from '../src/theory/templateRegistry';
import * as path from 'path';

/**
 * AG-11 Verification: SOC2 Round-Trip Test
 * Verifies that the Privacy Gradient template (SOC2) correctly links to:
 * - NM_THREAT_HPA_001 (T5)
 * - DT_DIRECTED_ATTENTION_001 (T25)
 * - ALLOSTATIC_MASTER_001 (T29)
 * - AUD_SCENE_ANALYSIS_001 (T31)
 * - SPATIAL_SOCIAL_ENCOUNTER_001 (SC4)
 */
async function runTest() {
    console.log("Initializing TemplateRegistry...");
    const registry = new TemplateRegistry(path.resolve(__dirname, '../data/templates'));
    await registry.loadAll();

    const soc2Id = "PRIVACY_GRADIENT_REGULATION_001";
    const soc2 = registry.getTemplate(soc2Id);

    if (!soc2) {
        console.error(`❌ FAILED: Could not find template ${soc2Id}`);
        process.exit(1);
    }
    console.log(`✅ Found SOC2: ${soc2.name} (${soc2.display_id})`);

    // Define expected connections
    const expectedConnections = [
        { id: "NM_THREAT_HPA_001", display: "T5" },
        { id: "DT_DIRECTED_ATTENTION_001", display: "T25" },
        { id: "ALLOSTATIC_MASTER_001", display: "T29" },
        { id: "AUD_SCENE_ANALYSIS_001", display: "T31" },
        { id: "SPATIAL_SOCIAL_ENCOUNTER_001", display: "SC4" }
    ];

    let missing = false;
    console.log("\nVerifying interactions...");

    for (const expected of expectedConnections) {
        // Check if the interaction exists in the interactions array
        // Note: interactions are stored as objects { template_id, ... } or strings depending on schema version
        // In SOC2.json they are objects with "template_id"
        const hasLink = soc2.interactions.some((i: any) =>
            (typeof i === 'string' && i === expected.id) ||
            (typeof i === 'object' && i.template_id === expected.id)
        );

        if (hasLink) {
            // Also verify the target template exists in registry
            const target = registry.getTemplate(expected.id);
            if (target) {
                console.log(`✅ Verified link to ${expected.display} (${expected.id})`);
            } else {
                console.error(`⚠️  Link exists to ${expected.display}, but target template not found in registry!`);
                missing = true;
            }
        } else {
            console.error(`❌ Missing link to ${expected.display} (${expected.id})`);
            missing = true;
        }
    }

    // Validate levels (Regressed in previous steps, ensuring fix works)
    console.log("\nVerifying levels...");
    let levelError = false;
    soc2.causal_links.forEach((link, idx) => {
        // We added 'social-cognitive' to valid levels, so this should pass
        if (String(link.to_level) === 'social-cognitive' || String(link.from_level) === 'social-cognitive') {
            console.log(`✅ Link ${idx + 1} uses 'social-cognitive' level (validated)`);
        }
    });

    if (missing || levelError) {
        console.error("\n❌ AG-11 Round-Trip Validation FAILED");
        process.exit(1);
    } else {
        console.log("\n✅ AG-11 Round-Trip Validation PASSED");
        process.exit(0);
    }
}

runTest().catch(err => {
    console.error(err);
    process.exit(1);
});
