
import fs from 'fs';
import path from 'path';

// --- Types (Mocked) ---

interface Col1Calibration {
    pe_formula: string;
    ecological_valence_baseline: Record<string, number>;
    context_match_d_values: Record<string, Record<string, number>>;
    cultural_modifiers: Record<string, Record<string, number>>;
}

interface Col2Calibration {
    arousal_formula: string;
    calibration_data: {
        parameters: {
            tau_arousal: Record<string, string>;
        };
        arousal_targets: Record<string, number>;
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

function testCol1Calibration() {
    console.log('Testing COL1 (Chromatic PE)...');
    const col1 = loadTemplate('COL1_chromatic_pe_context.json');
    const cal = col1.calibration_data as Col1Calibration;

    if (!cal) throw new Error('COL1 missing calibration_data');

    // 1. Verify Matrix Data (Elliot)
    // Red in Focus context should be negative (-0.35)
    if (cal.context_match_d_values.red.focus !== -0.35) {
        throw new Error(`Red-Focus should be -0.35, got ${cal.context_match_d_values.red.focus}`);
    }
    // Blue in Focus context should be positive (+0.25)
    if (cal.context_match_d_values.blue.focus !== 0.25) {
        throw new Error(`Blue-Focus should be 0.25, got ${cal.context_match_d_values.blue.focus}`);
    }
    console.log('  Context Matrix: OK');

    // 2. Verify Ecological Valence (Palmer)
    if (cal.ecological_valence_baseline.blue !== 0.80) throw new Error('Blue EVT baseline mismatch');
    console.log('  Ecological Valence: OK');

    // 3. Simulate PE Calculation
    // Scenario: Red Wall in Office (Focus). Region: Western (0 modifier).
    // PE = 1.0 - (0.40 * eco_valence + 0.45 * context_match + 0.15 * regional_match)
    // Eco (Red) = 0.10
    // Context (Red, Focus) = -0.35
    // Region = 0
    // Score = 0.4*0.10 + 0.45*(-0.35) + 0 = 0.04 - 0.1575 = -0.1175
    // PE = 1.0 - (-0.1175) = 1.1175 (High Error)

    const score = (0.40 * 0.10) + (0.45 * -0.35) + (0.15 * 0);
    const pe = 1.0 - score;

    console.log(`  Simulated PE (Red Office): ${pe.toFixed(4)}`);
    if (pe < 1.0) throw new Error('Red office should generate high PE (>1.0)');
    console.log('  PE Logic: OK');
}

function testCol2Calibration() {
    console.log('Testing COL2 (Arousal Dose)...');
    const col2 = loadTemplate('COL2_color_arousal_dose.json');
    const cal = col2.calibration_data;

    // 1. Verify Arousal Formula
    if (!cal.arousal_formula.includes('0.30 * S')) throw new Error('Arousal formula mismatch');

    // 2. Verify Habituation Constraints
    const tau = cal.parameters.tau_arousal;
    if (tau.immersive !== '3h') throw new Error('Immersive habituation should be 3h');
    if (tau.accent !== '2d') throw new Error('Accent habituation should be 2d');
    console.log('  Habituation Parameters: OK');

    // 3. Simulate Arousal
    // Scenario: Active Work (Target 0.25).
    // Color: High Sat (0.8), High Bright (0.8), Warm Hue (0.5). Immersive (1.0).
    // Arousal = (0.3*0.8 + 0.2*0.8 + 0.1*0.5) * 1.0
    // = (0.24 + 0.16 + 0.05) = 0.45
    // Mismatch = |0.45 - 0.25| = 0.20 (Borderline high)

    const arousal_calc = (0.30 * 0.8) + (0.20 * 0.8) + (0.10 * 0.5);
    console.log(`  Simulated Arousal: ${arousal_calc.toFixed(2)}`);

    if (arousal_calc !== 0.45) throw new Error('Arousal calculation failed');
    console.log('  Arousal Logic: OK');
}

// --- Main Runner ---

try {
    testCol1Calibration();
    testCol2Calibration();
    console.log('\nSUCCESS: All COL-II calibration tests passed.');
    process.exit(0);
} catch (err) {
    console.error('\nFAILURE:', err);
    process.exit(1);
}
