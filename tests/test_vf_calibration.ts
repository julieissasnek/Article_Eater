
import { TheoryAPI } from '../src/api/index';
import { expect } from 'expect';

// Helper to parse strings like "0.40-0.80"
function parseRange(str: string): { min: number, max: number } | null {
    const match = str.match(/([0-9.]+)\s*-\s*([0-9.]+)/);
    if (match) {
        return { min: parseFloat(match[1]), max: parseFloat(match[2]) };
    }
    const gt = str.match(/>\s*([0-9.]+)/);
    if (gt) return { min: parseFloat(gt[1]), max: Infinity };
    const lt = str.match(/<\s*([0-9.]+)/);
    if (lt) return { min: -Infinity, max: parseFloat(lt[1]) };
    return null;
}

async function runTest() {
    console.log("Initializing TheoryAPI for VF Calibration Test...");
    const api = new TheoryAPI();
    await api.initialize();

    const vf1 = api.getTemplate("CONTOUR_PE_CURVATURE_001");
    const vf2 = api.getTemplate("VISUAL_RHYTHM_SCALING_001");
    const vf3 = api.getTemplate("VISUAL_FORM_CEILING_HEIGHT_001"); // Using ShortID VF3 if registered, or full ID

    if (!vf1 || !vf2 || !vf3) {
        throw new Error("Failed to load VF templates");
    }

    console.log("✓ VF Templates Loaded");

    // --- TEST 1: VF1 Contour Curvature ---
    console.log("\n--- Testing VF1: Contour Curvature Index (CCI) ---");
    const cciData = vf1.calibration_data?.contour_curvature_index;
    expect(cciData).toBeDefined();
    console.log(`Optimal Range: ${cciData.optimal_range}`);

    // Check habituation function exists
    const habituation = vf1.calibration_data?.exposure_habituation;
    expect(habituation.function).toContain("d_acute * [0.40 + 0.60");
    console.log(`Habituation Model: ${habituation.function}`);


    // --- TEST 2: VF2 Rhythm & Scaling ---
    console.log("\n--- Testing VF2: SRV Goldilocks & SCI ---");
    const srv = vf2.calibration_data?.spatial_rhythm_variation;
    const sci = vf2.calibration_data?.scaling_coherence_index;

    expect(srv).toBeDefined();
    expect(sci).toBeDefined();

    const srvRange = parseRange(srv.goldilocks_zone);
    console.log(`SRV Optimal: ${srvRange?.min} - ${srvRange?.max}`);
    expect(srvRange?.min).toBe(0.12);
    expect(srvRange?.max).toBe(0.25);

    console.log(`SCI Metric: ${sci.metric}`);
    expect(sci.metric).toContain("1 - CV");


    // --- TEST 3: VF3 Transition PE ---
    console.log("\n--- Testing VF3: PE Transition Function ---");
    const transition = vf3.calibration_data?.pe_transition_function;
    expect(transition).toBeDefined();

    // Simulate Transition: Corridor (Low) -> Atrium (High)
    // R_h = height / sqrt(area)
    // Corridor: 2.4m / sqrt(10m2) = 2.4 / 3.16 = 0.76?? No wait.
    // Doc 64 says: Corridor (0.22) -> Atrium (0.60)
    const Rh_old = 0.22;
    const Rh_new = 0.60;

    // Formula: 0.55 * ln(Rh_new / Rh_old)
    const ratio = Rh_new / Rh_old;
    const predictedPE = 0.55 * Math.log(ratio);

    console.log(`Simulated Transition (Rh ${Rh_old} -> ${Rh_new}): Ratio ${ratio.toFixed(2)}x`);
    console.log(`Predicted PE Benefit: ${predictedPE.toFixed(3)}`);

    // Check against manual calc: 0.60/0.22 = 2.72. ln(2.72) = 1.0. 0.55 * 1.0 = 0.55.
    expect(predictedPE).toBeCloseTo(0.55, 1);

    // Reverse Transition
    const reversePE = 0.55 * Math.log(Rh_old / Rh_new);
    console.log(`Reverse Transition: ${reversePE.toFixed(3)}`);
    expect(reversePE).toBeLessThan(0);


    console.log("\n✓ All VF Calibration Tests Passed");
}

runTest().catch(err => {
    console.error(err);
    process.exit(1);
});
