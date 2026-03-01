import { TheoryAPI } from '../src/api';

/**
 * AG-36: Panel CREA-III Deepening Verification
 * Testing:
 * 1. CREA2 Interaction Matrix (Sub-additivity)
 * 2. CREA1 Tightened Phase-Environment Mapping
 * 3. CREA4 Collaborative Creativity Architecture (New Template)
 */

async function testCreaDeepening() {
    console.log("Initializing TheoryAPI for CREA-III Verification...");
    const api = new TheoryAPI();
    await api.initialize();

    // Load Templates
    const crea1 = api.getTemplate("CREATIVE_NETWORK_DYNAMICS_001");
    const crea2 = api.getTemplate("PROCESSING_STYLE_MODULATION_001");
    const crea4 = api.getTemplate("COLLABORATIVE_CREATIVITY_ARCHITECTURE_001"); // Validating alias mapping

    if (!crea1 || !crea2 || !crea4) {
        console.error("FAILED to load one or more CREA templates.");
        console.log("CREA1:", !!crea1);
        console.log("CREA2:", !!crea2);
        console.log("CREA4:", !!crea4);
        process.exit(1);
    }

    console.log("✓ CREA Templates Loaded (including new CREA4)");

    // --- TEST 1: CREA2 Interaction Matrix ---
    console.log("\n--- Testing CREA2: Interaction Matrix ---");
    const matrix = crea2.calibration_data?.interaction_matrix;
    const designRules = crea2.calibration_data?.design_rules;

    expect(matrix).toBeDefined();
    expect(designRules).toBeDefined();

    // Test Sub-additivity Values
    console.log("Validating Sub-additivity Coefficients:");

    // A+B (Noise + Ceiling) - The "Efficient" Combo
    const ab = matrix["A_plus_B"];
    console.log(`A+B (Noise+Ceiling): sub_additivity = ${ab.sub_additivity} (Expected ~0.84)`);
    expect(ab.sub_additivity).toBeCloseTo(0.84, 2);
    expect(ab.d_divergent).toBe(0.65);

    // A+C (Noise + Dim) - The "Redundant" Combo (Mehta 2024)
    const ac = matrix["A_plus_C"];
    console.log(`A+C (Noise+Dim): sub_additivity = ${ac.sub_additivity} (Expected ~0.76)`);
    expect(ac.sub_additivity).toBeCloseTo(0.76, 2);

    // Design Rule Check
    console.log(`Design Rule (Generative): ${designRules["generative_only"]}`);
    expect(designRules["generative_only"]).toContain("Noise + Ceiling");


    // --- TEST 2: CREA1 Tightened Phase Mapping ---
    console.log("\n--- Testing CREA1: Phase-Environment Mapping ---");
    const phases = (crea1 as any).phase_appropriate_architecture;
    expect(phases).toBeDefined();

    // Generative Zone Parameters
    console.log("Generative Zone Spec:");
    console.log(`- Noise: ${phases.generative_zone.noise}`);
    console.log(`- Ceiling: ${phases.generative_zone.ceiling}`);
    console.log(`- Light: ${phases.generative_zone.light}`);

    expect(phases.generative_zone.ceiling).toContain("> 0.35");
    expect(phases.generative_zone.light).toContain("100-200 lux");

    // Evaluative Zone Parameters
    console.log("Evaluative Zone Spec:");
    console.log(`- Noise: ${phases.evaluative_zone.noise}`);

    expect(phases.evaluative_zone.noise).toContain("<45 dBA");


    // --- TEST 3: CREA4 Structure and Logic ---
    console.log("\n--- Testing CREA4: Collaborative Architecture ---");
    expect(crea4.display_id).toBe("CREA4");

    // Check Causal Links for Production Blocking
    const productionBlockingLink = crea4.causal_links.find(
        link => link.to_variable === "production_blocking_reduction"
    );
    expect(productionBlockingLink).toBeDefined();
    console.log("✓ Found Causal Link: Spatial Alternation -> Production Blocking Reduction");

    // Check Calibration Data
    const cal = crea4.calibration_data;
    console.log(`Optimal Group Size: ${cal?.optimal_group_size}`);
    expect(cal?.optimal_group_size).toContain("3-6");

    console.log("\n✓ All CREA-III Deepening Tests Passed");
}

testCreaDeepening().catch(err => {
    console.error("Test Failed:", err);
    process.exit(1);
});
