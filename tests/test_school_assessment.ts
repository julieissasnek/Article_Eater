
import fs from 'fs';
import path from 'path';

// --- Simulation Data ---

// School Context: "Primary 5-9"
const context = "school";
const ageBand = "primary_5_9"; // age_6_9

// 3 Classroom Profiles based on HEAD criteria / V14 Prompt
// Excellent: High Daylight, Good Acoustics, Nature View, Flexible
// Average: Code Minimums
// Poor: Glare/Dark, Noise, No View, Crowded

const classrooms = [
    {
        id: "class_excellent",
        label: "Excellent (HEAD)",
        params: {
            daylight_vqi: 80, // > 50
            illuminance_lux: 450, // 300-500
            rt60_s: 0.35, // <= 0.4
            bg_noise_dba: 30, // <= 35
            nature_view_quality: "HIGH", // Essential
            ceiling_height_m: 3.0, // 2.7-3.0
            spatial_clarity: "maximum",
            display_area_ratio: 0.5
        }
    },
    {
        id: "class_average",
        label: "Average (Standard)",
        params: {
            daylight_vqi: 40,
            illuminance_lux: 300,
            rt60_s: 0.6,
            bg_noise_dba: 45,
            nature_view_quality: "LOW", // Minimal
            ceiling_height_m: 2.7,
            spatial_clarity: "moderate",
            display_area_ratio: 0.2
        }
    },
    {
        id: "class_poor",
        label: "Poor (Deficient)",
        params: {
            daylight_vqi: 10,
            illuminance_lux: 150, // Dim
            rt60_s: 1.2, // Echoey
            bg_noise_dba: 65, // Noisy
            nature_view_quality: "NEGATIVE", // None/Wall
            ceiling_height_m: 2.4, // Oppressive
            spatial_clarity: "confusing",
            display_area_ratio: 0.8 // Cluttered
        }
    }
];

// --- Load Templates ---

function loadTemplate(filename: string): any {
    const filePath = path.resolve(__dirname, '../data/templates', filename);
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
}

const tp2 = loadTemplate('TP2_threshold_episodic_boundary.json');
const view1 = loadTemplate('VIEW1_nature_view_convergence.json');
const crea1 = loadTemplate('CREA1_creative_network_dynamics.json'); // Maybe?

// --- Validation Logic ---

console.log('--- School Assessment Validation (Context: Primary 5-9) ---');

// Check TP2 School Context Parameters
console.log('\nChecking TP2 School Context Parameters:');
const schoolParams = tp2.context_modes?.school?.classroom_parameters;
if (!schoolParams) {
    console.error("FAILURE: TP2 missing context_modes.school.classroom_parameters");
    process.exit(1);
}

// Validate Thresholds (Reference from V14 Prompt)
const thresholds = {
    daylight: schoolParams.daylight_vqi_min[ageBand],
    rt60: schoolParams.acoustic_rt60_s_max[ageBand],
    noise: schoolParams.background_noise_dba_max[ageBand]
};

console.log(`Reference Thresholds for ${ageBand}:`);
console.log(`  Daylight VQI Min: ${thresholds.daylight}`);
console.log(`  RT60 Max: ${thresholds.rt60}s`);
console.log(`  Noise Max: ${thresholds.noise}dBA`);

// Evaluate Models
console.log('\nEvaluating Classrooms:');

classrooms.forEach(c => {
    console.log(`\n[${c.label}]`);
    let score = 0;

    // Daylight
    if (c.params.daylight_vqi >= thresholds.daylight) {
        console.log(`  PASS Daylight (${c.params.daylight_vqi} >= ${thresholds.daylight})`);
        score++;
    } else {
        console.log(`  FAIL Daylight (${c.params.daylight_vqi} < ${thresholds.daylight})`);
    }

    // Acoustics
    if (c.params.rt60_s <= thresholds.rt60) {
        console.log(`  PASS RT60 (${c.params.rt60_s} <= ${thresholds.rt60})`);
        score++;
    } else {
        console.log(`  FAIL RT60 (${c.params.rt60_s} > ${thresholds.rt60})`);
    }

    // Noise
    if (c.params.bg_noise_dba <= thresholds.noise) {
        console.log(`  PASS Noise (${c.params.bg_noise_dba} <= ${thresholds.noise})`);
        score++;
    } else {
        console.log(`  FAIL Noise (${c.params.bg_noise_dba} > ${thresholds.noise})`);
    }

    // Check VIEW1 Multiplier applied?
    // In V14 Prompt: VIEW1 has dev_restoration_multiplier.
    // If nature_view_quality is High, does it interact with age?
    // "dev_restoration_multiplier: {age_3_6: 1.5...}"
    // For age 6-9 (primary), mult is 1.4.
    // So impact of view is magnified.

    if (c.params.nature_view_quality === 'HIGH') {
        const mult = view1.dev_restoration_multiplier?.['age_6_9'] || 1.0;
        console.log(`  VIEW1 Impact: High (Multiplier x${mult}) -> Super-Restorative`);
    } else {
        console.log(`  VIEW1 Impact: ${c.params.nature_view_quality} (No multiplier benefit)`);
    }

    console.log(`  Score: ${score}/3 Core Metrics`);
});

console.log('\n--- Conclusion ---');
// Simple assertion: Excellent should pass all, Poor should fail all.
const excellent = classrooms.find(c => c.id === 'class_excellent');
if (excellent && excellent.params.daylight_vqi >= thresholds.daylight && excellent.params.rt60_s <= thresholds.rt60 && excellent.params.bg_noise_dba <= thresholds.noise) {
    console.log("PASS: Excellent profile meets all developmental criteria.");
} else {
    console.error("FAIL: Excellent profile failed some criteria.");
    process.exit(1);
}

const poor = classrooms.find(c => c.id === 'class_poor');
if (poor && poor.params.daylight_vqi < thresholds.daylight && poor.params.rt60_s > thresholds.rt60) {
    console.log("PASS: Poor profile correctly flagged as deficient.");
} else {
    console.error("FAIL: Poor profile not flagged correctly.");
    process.exit(1);
}

