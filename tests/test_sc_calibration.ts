
import { TheoryAPI } from '../src/api/index';
import { expect } from 'expect';
import * as fs from 'fs';
import * as path from 'path';

// Helper to parse "1.5x to 2.5x" strings into usable numbers
function parseMultiplier(str: string): number {
    const match = str.match(/(\d+\.?\d*)x/);
    return match ? parseFloat(match[1]) : 1.0;
}

// Helper to parse range "20-45"
function parseRange(str: string): { min: number, max: number } {
    const parts = str.split('-').map(s => parseFloat(s));
    return { min: parts[0], max: parts[1] };
}

async function runTest() {
    console.log("Initializing TheoryAPI for SC Calibration Test...");
    const api = new TheoryAPI();
    await api.initialize();

    const sc1 = api.getTemplate("SPATIAL_INTEGRATION_NAV_PE_001");
    const sc2 = api.getTemplate("ISOVIST_VISUAL_PREDICTION_001");
    const sc3 = api.getTemplate("ARCH_PROMENADE_PE_ORCHESTRATION_001");

    if (!sc1 || !sc2 || !sc3) {
        throw new Error("Failed to load SC templates");
    }

    console.log("✓ SC Templates Loaded");

    // --- TEST 1: SC1 Vertical PE ---
    console.log("\n--- Testing SC1: Vertical PE Multiplier ---");
    const vertMultStr = sc1.calibration_data?.vertical_pe_multiplier; // "1.5x to 2.5x"
    const atriumFactorStr = sc1.calibration_data?.atrium_mitigation_factor; // "0.30 to 0.50 reduction"

    expect(vertMultStr).toBeDefined();
    expect(atriumFactorStr).toBeDefined();

    const baseMult = parseMultiplier(vertMultStr); // Should pick ~1.5
    const atriumRed = parseFloat(atriumFactorStr.match(/0\.(\d+)/)[0]); // ~0.30

    console.log(`Base Vertical Multiplier extracted: ${baseMult}`);
    console.log(`Atrium Mitigation extracted: ${atriumFactorStr}`);

    // Simulation: Calculate cost for 2 floors up
    const horizontalCost = 10; // arbitrary units
    const floors = 2;
    // Simple model: Cost = Horizontal * (BaseMult ^ Floors)
    // Or linear per floor? Doc says "per floor change".
    // Doc 62: "Vertical PE multiplier: 1.5-2.5x per floor"
    // Let's assume linear accumulation of penalty for simplicity or multiplicative?
    // "navigating to a destination 3 floors away produces 4-6x the PE" -> Suggests multiplicative or additive accumulation.
    // 1 floor = 1.5x. 2 floors = 1.5 * 1.5? Or 1 + (0.5 * 2)?
    // Doc: "Three+ floors: 4.0-6.0x".
    // 1 floor (1.5) -> 2 floors (3.0?) -> 3 floors (4.5?). 
    // Linear adder: 1 + 0.5*N? -> 1+0.5=1.5. 1+1.0=2.0. 1+1.5=2.5. Too low.
    // Multiplicative: 1.5^1=1.5. 1.5^2=2.25. 1.5^3=3.375.
    // Upper bound 2.5: 2.5^1=2.5. 2.5^2=6.25. 2.5^3=15.
    // The doc says "Two floors: 3.0-4.0x". "Three+ floors: 4.0-6.0x".
    // This matches roughly a multiplicative model around 1.8x - 2.0x.
    // We just verify the data exists and is parsable.

    expect(baseMult).toBeGreaterThan(1.0);
    expect(atriumFactorStr).toContain("reduction");


    // --- TEST 2: SC2 Isovist Asymmetry ---
    console.log("\n--- Testing SC2: Isovist Asymmetry ---");
    const asymmetry = sc2.calibration_data?.reveal_compression_asymmetry;
    expect(asymmetry).toContain("1.5x");
    expect(asymmetry).toContain("Compression");
    console.log(`Asymmetry Rule: ${asymmetry}`);


    // --- TEST 3: SC3 Threshold Density ---
    console.log("\n--- Testing SC3: Threshold Density Goldilocks ---");
    const optimalIntervalStr = sc3.calibration_data?.optimal_threshold_interval_s; // "20-45"
    const optimalRange = parseRange(optimalIntervalStr);

    console.log(`Optimal Interval: ${optimalRange.min}-${optimalRange.max}s`);

    // Simulation: Check engagement for different intervals
    const testIntervals = [10, 30, 90];
    testIntervals.forEach(interval => {
        let status = " suboptimal";
        if (interval >= optimalRange.min && interval <= optimalRange.max) {
            status = " OPTIMAL";
        } else if (interval < optimalRange.min) {
            status = " (Risk of Fatigue)";
        } else {
            status = " (Risk of Habituation)";
        }
        console.log(`Interval ${interval}s: ${status}`);
    });

    expect(optimalRange.min).toBe(20);
    expect(optimalRange.max).toBe(45);


    // --- TEST 4: SC3 Bonus Values ---
    console.log("\n--- Testing SC3: Multistimulus Bonus ---");
    const bonus = sc3.calibration_data?.multistimulus_bonus_values;
    expect(bonus).toBeDefined();
    expect(bonus.plus_light).toBe(0.25);
    expect(bonus.full_convergence).toBe(0.70);
    console.log(`Full Convergence Bonus: ${bonus.full_convergence}`);

    console.log("\n✓ All SC Calibration Tests Passed");
}

runTest().catch(err => {
    console.error(err);
    process.exit(1);
});
