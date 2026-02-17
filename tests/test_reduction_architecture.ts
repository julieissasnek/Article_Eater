
import { TemplateRegistry } from '../src/theory/templateRegistry';
import { ReductionRegistry } from '../src/theory/reductionRegistry';
import { strict as assert } from 'node:assert';

async function runTest() {
    console.log("Initializing Registries for AG-37 Validation...");
    const templateRegistry = new TemplateRegistry();
    const reductionRegistry = new ReductionRegistry();

    await templateRegistry.loadAll();
    await reductionRegistry.loadAll();

    console.log("✓ Registries Initialized");

    // Test 1: ReductionRegistry
    assert.ok(reductionRegistry, "ReductionRegistry should be initialized");
    console.log("✓ ReductionRegistry exists");

    // Test 2: T1 (Biophilia/Fractals)
    const t1 = templateRegistry.getTemplate('PP_SPECTRAL_MATCH_001');
    assert.ok(t1, "T1 should exist");
    assert.ok(t1.calibration_data, "T1 should have calibration_data");
    assert.ok(t1.calibration_data.biophilia_fractal_d, "T1 should have biophilia_fractal_d");
    assert.equal(t1.calibration_data.biophilia_fractal_d.optimal_range, '1.3-1.5');
    console.log("✓ T1 Calibration Validated");

    // Test 3: T2 (Complexity)
    const t2 = templateRegistry.getTemplate('PP_COMPLEXITY_GOLDILOCKS_002');
    assert.ok(t2, "T2 should exist");
    assert.ok(t2.calibration_data, "T2 should have calibration_data");
    assert.ok(t2.calibration_data.biophilia_mystery, "T2 should have biophilia_mystery");
    console.log("✓ T2 Calibration Validated");

    // Test 4: T5 (Threat/Cortisol)
    const t5 = templateRegistry.getTemplate('NM_THREAT_HPA_001');
    assert.ok(t5, "T5 should exist");
    assert.ok(t5.calibration_data, "T5 should have calibration_data");
    assert.ok(t5.calibration_data.cortisol_recovery, "T5 should have cortisol_recovery");
    console.log("✓ T5 Calibration Validated");

    // Test 5: T13 (Nature Multipath)
    const t13 = templateRegistry.getTemplate('XF_NATURE_VIEW_MULTIPATH_001');
    assert.ok(t13, "T13 should exist");
    assert.ok(t13.calibration_data, "T13 should have calibration_data");
    assert.ok(t13.calibration_data.pathway_dominance, "T13 should have pathway_dominance");
    console.log("✓ T13 Calibration Validated");

    // Test 6: T16 (Restoration Timecourse)
    const t16 = templateRegistry.getTemplate('DT_RESTORATION_TIMECOURSE_001');
    assert.ok(t16, "T16 should exist");
    assert.ok(t16.calibration_data, "T16 should have calibration_data");
    assert.ok(t16.calibration_data.temporal_stages, "T16 should have temporal_stages");
    console.log("✓ T16 Calibration Validated");

    // Test 7: T25 (Ripple Replay)
    const t25 = templateRegistry.getTemplate('MS_RIPPLE_REPLAY_002');
    assert.ok(t25, "T25 should exist");
    assert.ok(t25.calibration_data, "T25 should have calibration_data");
    assert.ok(t25.calibration_data.replay_requirements, "T25 should have replay_requirements");
    console.log("✓ T25 Calibration Validated");

    // Test 8: T27 (DMN Maintenance)
    const t27 = templateRegistry.getTemplate('DT_DMN_MAINTENANCE_002');
    assert.ok(t27, "T27 should exist");
    assert.ok(t27.calibration_data, "T27 should have calibration_data");
    assert.ok(t27.calibration_data.dmn_activation_threshold, "T27 should have dmn_activation_threshold");
    console.log("✓ T27 Calibration Validated");

    console.log("\nAll AG-37 Validation Tests Passed!");
}

runTest().catch(err => {
    console.error("Test Failed:", err);
    process.exit(1);
});
