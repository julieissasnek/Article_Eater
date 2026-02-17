#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const TEMPLATE_DIR = path.join(ROOT, "data", "templates");
const DEFAULT_MD_OUT = path.join(
  ROOT,
  "docs",
  "cx_v14_lifespan_ucurve_validation_report_2026-02-17.md",
);
const DEFAULT_JSON_OUT = path.join(
  ROOT,
  "data",
  "review",
  "cx_v14_lifespan_ucurve_validation_2026-02-17.json",
);

const TARGET_DISPLAY_IDS = [
  "L1",
  "L2",
  "L3",
  "L4",
  "L5",
  "MAT1",
  "MAT2",
  "MAT3",
  "MAT4",
  "MAT5",
  "TP1",
  "TP2",
  "TP3",
  "TP4",
  "SOC1",
  "SOC2",
  "SOC3",
  "CREA1",
  "CREA2",
  "CREA3",
  "VIEW1",
];

const REQUIRED_AGE_BANDS = [
  "toddler_0_3",
  "age_3_6",
  "age_6_9",
  "age_9_12",
  "age_12_16",
  "emerging_adult_16_25",
  "young_20_40",
  "middle_40_65",
  "older_65_80",
  "frail_80_plus",
];

const REQUIRED_FACTORS = ["speed", "vision", "hearing", "motor", "olfaction"];

const REQUIRED_UCURVE_BANDS = [
  "age_0_6",
  "age_6_12",
  "age_12_25",
  "age_25_50",
  "age_50_65",
  "age_65_80",
  "age_80_plus",
];

function toIsoNow() {
  return new Date().toISOString();
}

function ensureDirFor(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function isNum(v) {
  return typeof v === "number" && Number.isFinite(v);
}

function readTemplates() {
  const files = fs
    .readdirSync(TEMPLATE_DIR)
    .filter((f) => f.endsWith(".json"))
    .sort();

  return files.map((name) => {
    const fullPath = path.join(TEMPLATE_DIR, name);
    const raw = fs.readFileSync(fullPath, "utf8");
    const data = JSON.parse(raw);
    return {
      name,
      data,
      displayId: data.display_id || null,
      templateId: data.template_id || data.id || null,
    };
  });
}

function scoreCanonicalCandidate(t) {
  let score = 0;
  if (
    t.data.calibration_view_ii ||
    t.data.calibration_crea_i ||
    t.data.calibration_tp_ii ||
    t.data.calibration_soc_ii ||
    t.data.calibration_age_i ||
    t.data.calibration_dev_i
  ) {
    score += 100;
  }
  if (t.name.includes("_")) {
    score += 10;
  }
  if (/^T\d+\.json$/.test(t.name)) {
    score -= 50;
  }
  if (/^[A-Z]+\d+\.json$/.test(t.name)) {
    score -= 15;
  }
  return score;
}

function pickCanonicalByDisplay(templates) {
  const byDisplay = new Map();
  for (const t of templates) {
    if (!t.displayId) {
      continue;
    }
    if (!byDisplay.has(t.displayId)) {
      byDisplay.set(t.displayId, []);
    }
    byDisplay.get(t.displayId).push(t);
  }

  const canonical = new Map();
  const duplicates = [];

  for (const [displayId, candidates] of byDisplay.entries()) {
    const ranked = candidates
      .map((c) => ({ c, score: scoreCanonicalCandidate(c) }))
      .sort((a, b) => b.score - a.score || a.c.name.localeCompare(b.c.name));

    canonical.set(displayId, ranked[0].c);

    if (ranked.length > 1) {
      duplicates.push({
        display_id: displayId,
        canonical_file: ranked[0].c.name,
        canonical_template_id: ranked[0].c.templateId,
      });
    }
  }

  return { canonical, duplicates };
}

function findFirstObjectByKey(obj, keyName) {
  if (!obj || typeof obj !== "object") {
    return null;
  }
  if (Object.prototype.hasOwnProperty.call(obj, keyName)) {
    return obj[keyName];
  }
  for (const value of Object.values(obj)) {
    if (value && typeof value === "object") {
      const found = findFirstObjectByKey(value, keyName);
      if (found !== null) {
        return found;
      }
    }
  }
  return null;
}

function validateAgeBands(ageBands) {
  if (!ageBands || typeof ageBands !== "object") {
    return { ok: false, reason: "missing age_band_modifiers object" };
  }
  for (const band of REQUIRED_AGE_BANDS) {
    const block = ageBands[band];
    if (!block || typeof block !== "object") {
      return { ok: false, reason: `missing band '${band}'` };
    }
    for (const factor of REQUIRED_FACTORS) {
      const v = block[factor];
      if (!isNum(v)) {
        return { ok: false, reason: `missing/non-numeric '${band}.${factor}'` };
      }
      if (v <= 0 || v > 2) {
        return { ok: false, reason: `out-of-range '${band}.${factor}'` };
      }
    }
  }
  return { ok: true };
}

function validateUCurve(ucurve) {
  if (!ucurve || typeof ucurve !== "object") {
    return { ok: false, reason: "missing lifespan_sensitivity_multiplier object" };
  }
  if (ucurve.model !== "u_curve_piecewise") {
    return { ok: false, reason: "model must be 'u_curve_piecewise'" };
  }

  const byAge = ucurve.by_age_range;
  if (!byAge || typeof byAge !== "object") {
    return { ok: false, reason: "missing by_age_range" };
  }

  for (const key of REQUIRED_UCURVE_BANDS) {
    if (!isNum(byAge[key])) {
      return { ok: false, reason: `missing/non-numeric by_age_range.${key}` };
    }
    if (byAge[key] <= 0 || byAge[key] > 5) {
      return { ok: false, reason: `out-of-range by_age_range.${key}` };
    }
  }

  const boundaryRule = ucurve.boundary_rule;
  if (!boundaryRule || typeof boundaryRule !== "object") {
    return { ok: false, reason: "missing boundary_rule" };
  }

  const range = String(boundaryRule.range || "");
  const method = String(boundaryRule.method || "");

  if (!range.includes("16-25")) {
    return { ok: false, reason: "boundary_rule.range must include '16-25'" };
  }
  if (!method.includes("linear_interpolation")) {
    return { ok: false, reason: "boundary_rule.method must include 'linear_interpolation'" };
  }

  return { ok: true };
}

function productFactors(bandObj) {
  return REQUIRED_FACTORS.reduce((acc, k) => acc * bandObj[k], 1);
}

function computeBoundaryProbe(ageBands, ucurve) {
  const byAge = ucurve.by_age_range;

  const dev16 = byAge.age_12_25;
  const adult25 = byAge.age_25_50;
  const interp20 = dev16 + (adult25 - dev16) * ((20 - 16) / (25 - 16));

  const youngBaseline = productFactors(ageBands.young_20_40);
  const emergingBaseline = productFactors(ageBands.emerging_adult_16_25);

  const combined16 = dev16 * emergingBaseline;
  const combined20 = interp20 * emergingBaseline;
  const combined25 = adult25 * youngBaseline;

  const trendOk = combined16 >= combined20 && combined20 >= combined25;

  return {
    ages: {
      age_16: combined16,
      age_20: combined20,
      age_25: combined25,
    },
    components: {
      ucurve_age_12_25: dev16,
      ucurve_age_25_50: adult25,
      ucurve_age_20_interpolated: interp20,
      emerging_adult_cascade: emergingBaseline,
      young_adult_cascade: youngBaseline,
    },
    trend_ok: trendOk,
  };
}

function main() {
  const mdOut = process.argv[2] || DEFAULT_MD_OUT;
  const jsonOut = process.argv[3] || DEFAULT_JSON_OUT;

  const templates = readTemplates();
  const { canonical, duplicates } = pickCanonicalByDisplay(templates);
  const duplicatesInScope = duplicates.filter((d) => TARGET_DISPLAY_IDS.includes(d.display_id));

  const rows = [];
  let missingTemplates = 0;
  let invalidAgeBand = 0;
  let invalidUcurve = 0;
  let boundaryReady = 0;
  let boundaryTrendFailures = 0;

  for (const displayId of TARGET_DISPLAY_IDS) {
    const t = canonical.get(displayId);
    if (!t) {
      rows.push({ display_id: displayId, status: "missing_template" });
      missingTemplates += 1;
      continue;
    }

    const ageBands = findFirstObjectByKey(t.data, "age_band_modifiers");
    const ucurve = findFirstObjectByKey(t.data, "lifespan_sensitivity_multiplier");

    const ageBandCheck = validateAgeBands(ageBands);
    const ucurveCheck = validateUCurve(ucurve);

    if (!ageBandCheck.ok) {
      invalidAgeBand += 1;
    }
    if (!ucurveCheck.ok) {
      invalidUcurve += 1;
    }

    let boundaryProbe = null;
    if (ageBandCheck.ok && ucurveCheck.ok) {
      boundaryProbe = computeBoundaryProbe(ageBands, ucurve);
      boundaryReady += 1;
      if (!boundaryProbe.trend_ok) {
        boundaryTrendFailures += 1;
      }
    }

    rows.push({
      display_id: displayId,
      file: t.name,
      template_id: t.templateId,
      checks: {
        age_band_modifiers: ageBandCheck,
        lifespan_sensitivity_multiplier: ucurveCheck,
      },
      boundary_probe: boundaryProbe,
    });
  }

  const report = {
    generated_at: toIsoNow(),
    template_files_scanned: templates.length,
    scope: {
      target_display_ids: TARGET_DISPLAY_IDS,
      duplicate_display_ids_in_scope: duplicatesInScope,
    },
    summary: {
      missing_templates: missingTemplates,
      invalid_age_band_modifiers: invalidAgeBand,
      invalid_lifespan_multiplier_blocks: invalidUcurve,
      boundary_ready_templates: boundaryReady,
      boundary_trend_failures: boundaryTrendFailures,
    },
    rows,
  };

  ensureDirFor(jsonOut);
  fs.writeFileSync(jsonOut, `${JSON.stringify(report, null, 2)}\n`, "utf8");

  const md = [];
  md.push("# CX V14 Lifespan U-Curve Validation Report");
  md.push("");
  md.push(`- Generated: ${report.generated_at}`);
  md.push(`- Template files scanned: ${report.template_files_scanned}`);
  md.push(`- Target templates: ${TARGET_DISPLAY_IDS.join(", ")}`);
  md.push(`- Duplicate display IDs in scope: ${duplicatesInScope.length}`);
  md.push(`- Invalid age_band_modifiers: ${invalidAgeBand}`);
  md.push(`- Invalid lifespan_sensitivity_multiplier blocks: ${invalidUcurve}`);
  md.push(`- Boundary-ready templates (16/20/25): ${boundaryReady}`);
  md.push(`- Boundary trend failures: ${boundaryTrendFailures}`);
  md.push("");

  md.push("## Per-Template Results");
  md.push("");
  md.push("| Display | Age Bands | Lifespan Block | Boundary Probe (16/20/25) |");
  md.push("|---|---|---|---|");

  for (const row of rows) {
    if (row.status === "missing_template") {
      md.push(`| ${row.display_id} | missing template | missing template | missing template |`);
      continue;
    }

    const ageStatus = row.checks.age_band_modifiers.ok
      ? "ok"
      : `invalid (${row.checks.age_band_modifiers.reason})`;
    const lifeStatus = row.checks.lifespan_sensitivity_multiplier.ok
      ? "ok"
      : `invalid (${row.checks.lifespan_sensitivity_multiplier.reason})`;

    let probe = "not ready";
    if (row.boundary_probe) {
      const ages = row.boundary_probe.ages;
      probe = `ready [${ages.age_16.toFixed(4)}, ${ages.age_20.toFixed(4)}, ${ages.age_25.toFixed(4)}]`;
      if (!row.boundary_probe.trend_ok) {
        probe += " (trend fail)";
      }
    }

    md.push(`| ${row.display_id} | ${ageStatus} | ${lifeStatus} | ${probe} |`);
  }
  md.push("");

  md.push("## Findings");
  md.push("");
  if (invalidAgeBand === 0 && invalidUcurve === 0 && boundaryTrendFailures === 0) {
    md.push("- Lifespan U-curve configuration is structurally valid for the V14 target template set.");
    md.push("- Boundary-age handoff (16→20→25) is monotonic toward adult baseline in all boundary-ready templates.");
  } else {
    if (invalidAgeBand > 0) {
      md.push(`- ${invalidAgeBand} templates have invalid or missing age-band cascade configuration.`);
    }
    if (invalidUcurve > 0) {
      md.push(`- ${invalidUcurve} templates have invalid or missing lifespan U-curve blocks.`);
    }
    if (boundaryTrendFailures > 0) {
      md.push(`- ${boundaryTrendFailures} templates fail boundary-age monotonicity checks.`);
    }
  }
  md.push("");

  md.push("## Artifacts");
  md.push("");
  md.push(`- JSON: \`${path.relative(ROOT, jsonOut)}\``);
  md.push(`- Markdown: \`${path.relative(ROOT, mdOut)}\``);
  md.push("");

  ensureDirFor(mdOut);
  fs.writeFileSync(mdOut, `${md.join("\n")}\n`, "utf8");

  console.log(`wrote ${path.relative(ROOT, jsonOut)}`);
  console.log(`wrote ${path.relative(ROOT, mdOut)}`);
}

main();
