
import fs from 'fs';
import path from 'path';

// --- Types (Mocked/Simplified for Test) ---

interface CulturalProxemicZone {
    cluster: string;
    stranger_distance_cm: number;
    close_friend_cm: number;
    intimate_cm: number;
}

interface Soc1Calibration {
    cultural_cluster_enum: string[];
    zone_boundaries: CulturalProxemicZone[];
    cultural_privacy_parameter: { cluster: string; cpp: number }[];
}

interface Soc2Calibration {
    privacy_encounter_ratio: {
        satisfaction_formula: string;
        optimal_ratio: number;
        cost_knee: number;
    };
    encounter_paradox: {
        threshold: number;
    };
}

interface DunbarLayer {
    layer_size: number;
    physical_distance_m: { min: number; max: number } | null;
    floor_tax_applies?: boolean;
}

interface Soc3Calibration {
    dunbar_layers: DunbarLayer[];
    interaction_decay: {
        lambda_m: number;
    };
    floor_tax: {
        multiplier: number;
    };
}

// --- Helper Functions ---

function loadTemplate(filename: string): any {
    const filePath = path.resolve(__dirname, '../data/templates', filename);
    if (!fs.existsSync(filePath)) {
        throw new Error(`Template file not found: ${filePath}`);
    }
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
}

// --- Tests ---

function testSoc1Calibration() {
    console.log('Testing SOC1 (Proxemics)...');
    const soc1 = loadTemplate('SOC1_proxemic_pe.json');
    const cal = soc1.calibration_soc_ii as Soc1Calibration;

    if (!cal) throw new Error('SOC1 missing calibration_soc_ii');

    // 1. Verify 5 clusters
    const clusters = cal.cultural_cluster_enum;
    if (clusters.length !== 5) throw new Error(`Expected 5 clusters, found ${clusters.length}`);
    console.log('  Cluster count: OK');

    // 2. Verify Proxemic Ordering: Latin < North American < Northern European
    const zones = cal.zone_boundaries;
    const latin = zones.find(z => z.cluster === 'latin_american')!;
    const na = zones.find(z => z.cluster === 'north_american')!;
    const ne = zones.find(z => z.cluster === 'northern_european')!;

    if (latin.stranger_distance_cm >= na.stranger_distance_cm) {
        throw new Error(`Latin stranger distance (${latin.stranger_distance_cm}) not < NA (${na.stranger_distance_cm})`);
    }
    if (na.stranger_distance_cm >= ne.stranger_distance_cm) {
        throw new Error(`NA stranger distance (${na.stranger_distance_cm}) not < NE (${ne.stranger_distance_cm})`);
    }
    console.log('  Cultural ordering (Latin < NA < NE): OK');
}

function testSoc2Calibration() {
    console.log('Testing SOC2 (Privacy)...');
    const soc2 = loadTemplate('SOC2_privacy_gradient.json');
    const cal = soc2.calibration_soc_ii as Soc2Calibration;

    if (!cal) throw new Error('SOC2 missing calibration_soc_ii');

    // 1. Verify Satisfaction Formula Parameters
    const formula = cal.privacy_encounter_ratio.satisfaction_formula;
    if (!formula.includes('5.8')) throw new Error('Formula missing scaling factor 5.8');
    if (!formula.includes('0.50')) throw new Error('Formula missing optimal ratio 0.50');
    console.log('  Formula structure: OK');

    // 2. Verify Knee
    if (cal.privacy_encounter_ratio.cost_knee !== 0.70) {
        throw new Error(`Expected cost knee 0.70, found ${cal.privacy_encounter_ratio.cost_knee}`);
    }
    console.log('  Cost knee: OK');

    // 3. Verify Paradox Threshold
    if (cal.encounter_paradox.threshold !== 0.80) {
        throw new Error(`Expected paradox threshold 0.80, found ${cal.encounter_paradox.threshold}`);
    }
    console.log('  Paradox threshold: OK');
}

function calculateDecay(dist: number, lambda: number): number {
    return Math.exp(-dist / lambda);
}

function testSoc3Calibration() {
    console.log('Testing SOC3 (Dunbar/Territory)...');
    const soc3 = loadTemplate('SOC3_territorial_affordance.json');
    const cal = soc3.calibration_soc_ii as Soc3Calibration;

    if (!cal) throw new Error('SOC3 missing calibration_soc_ii');

    // 1. Verify Dunbar Layers
    const layers = cal.dunbar_layers;
    const layer5 = layers.find(l => l.layer_size === 5);
    const layer150 = layers.find(l => l.layer_size === 150);

    if (!layer5 || !layer150) throw new Error('Missing Dunbar layers 5 or 150');
    if (layer5.physical_distance_m?.max !== 6) throw new Error('Layer 5 max distance should be 6m');
    console.log('  Dunbar layers: OK');

    // 2. Verify Decay Function
    const lambda = cal.interaction_decay.lambda_m;
    if (lambda !== 8) throw new Error(`Expected lambda 8, found ${lambda}`);

    const prob8m = calculateDecay(8, lambda);
    if (Math.abs(prob8m - 0.367) > 0.01) throw new Error(`Decay at 8m should be ~0.37, got ${prob8m}`);

    const prob16m = calculateDecay(16, lambda);
    if (Math.abs(prob16m - 0.135) > 0.01) throw new Error(`Decay at 16m should be ~0.14, got ${prob16m}`);

    console.log('  Decay function (lambda=8): OK');

    // 3. Verify Floor Tax
    if (cal.floor_tax.multiplier !== 8) throw new Error(`Expected floor tax 8, found ${cal.floor_tax.multiplier}`);
    console.log('  Floor tax: OK');
}

// --- Main Runner ---

try {
    testSoc1Calibration();
    testSoc2Calibration();
    testSoc3Calibration();
    console.log('\nSUCCESS: All SOC-II calibration tests passed.');
    process.exit(0);
} catch (err) {
    console.error('\nFAILURE:', err);
    process.exit(1);
}
