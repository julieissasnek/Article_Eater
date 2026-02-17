#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const TEMPLATE_DIR = path.join(ROOT, "data", "templates");
const DEFAULT_MD_OUT = path.join(
  ROOT,
  "docs",
  "cx_v12_schema_validation_report_2026-02-17.md",
);
const DEFAULT_JSON_OUT = path.join(
  ROOT,
  "data",
  "review",
  "cx_v12_schema_validation_2026-02-17.json",
);

const EXPECTED_DISPLAY_IDS = [
  "VIEW1",
  "CREA1",
  "CREA2",
  "CREA3",
  "TP1",
  "TP2",
  "TP3",
  "TP4",
  "SOC1",
  "SOC2",
  "SOC3",
];

const ROOT_METADATA_EXPECTATIONS = {
  vqi_score: ["VIEW1"],
  vqi_channel_scores: ["VIEW1"],
  synthetic_efficacy: ["VIEW1"],
  blue_space_present: ["VIEW1"],
  blue_bonus_multiplier: ["VIEW1"],
  creativity_goldilocks_ceiling: ["CREA1", "CREA2", "CREA3"],
  convergent_tradeoff_d: ["CREA1", "CREA2", "CREA3"],
  baseline_creativity_multiplier: ["CREA1", "CREA2", "CREA3"],
  mfi_range: ["TP1"],
  threshold_channel_count: ["TP2"],
  estimated_boundary_d: ["TP2"],
  aging_trajectory: ["TP3"],
  cultural_cluster: ["SOC1", "SOC3"],
};

function ensureDirFor(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function toIsoNow() {
  return new Date().toISOString();
}

function isNum(v) {
  return typeof v === "number" && Number.isFinite(v);
}

function getPath(obj, dottedPath) {
  if (!obj || typeof obj !== "object") {
    return undefined;
  }
  const parts = dottedPath.split(".");
  let cur = obj;
  for (const part of parts) {
    if (!cur || typeof cur !== "object" || !(part in cur)) {
      return undefined;
    }
    cur = cur[part];
  }
  return cur;
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
    t.data.calibration_soc_ii
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
  if (typeof t.templateId === "string" && t.templateId.startsWith("CROSS_")) {
    score -= 10;
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
        candidates: ranked.map((x) => ({
          file: x.c.name,
          template_id: x.c.templateId,
          score: x.score,
        })),
      });
    }
  }

  return { canonical, duplicates };
}

function validateRangePair(v, minAllowed, maxAllowed, label) {
  if (!Array.isArray(v) || v.length !== 2 || !isNum(v[0]) || !isNum(v[1])) {
    return { ok: false, reason: `${label} must be [min,max] numeric array` };
  }
  const [min, max] = v;
  if (min > max) {
    return { ok: false, reason: `${label} must satisfy min <= max` };
  }
  if (min < minAllowed || max > maxAllowed) {
    return {
      ok: false,
      reason: `${label} must stay within [${minAllowed},${maxAllowed}]`,
    };
  }
  return { ok: true };
}

function validateMinMaxObject(v, minAllowed, maxAllowed, label) {
  if (!v || typeof v !== "object" || !isNum(v.min) || !isNum(v.max)) {
    return { ok: false, reason: `${label} must be object {min,max}` };
  }
  if (v.min > v.max) {
    return { ok: false, reason: `${label} must satisfy min <= max` };
  }
  if (v.min < minAllowed || v.max > maxAllowed) {
    return {
      ok: false,
      reason: `${label} must stay within [${minAllowed},${maxAllowed}]`,
    };
  }
  return { ok: true };
}

const CALIBRATION_CHECKS = [
  {
    id: "view_channel_weights",
    expected: ["VIEW1"],
    get: (doc) => getPath(doc, "calibration_view_ii.channel_weights"),
    validate: (v) => {
      if (!v || typeof v !== "object") {
        return { ok: false, reason: "channel_weights must be an object" };
      }
      const keys = [
        "ch1_fractal",
        "ch2_prospect",
        "ch3_restoration",
        "ch4_temporal",
        "ch5_safety",
      ];
      const vals = [];
      for (const key of keys) {
        if (!isNum(v[key])) {
          return { ok: false, reason: `missing/non-numeric weight '${key}'` };
        }
        if (v[key] < 0 || v[key] > 1) {
          return { ok: false, reason: `weight '${key}' outside [0,1]` };
        }
        vals.push(v[key]);
      }
      const sum = vals.reduce((a, b) => a + b, 0);
      if (Math.abs(sum - 1) > 0.02) {
        return { ok: false, reason: `channel_weights sum must be ~1.0, got ${sum}` };
      }
      return { ok: true };
    },
  },
  {
    id: "view_ch5_gate_range",
    expected: ["VIEW1"],
    get: (doc) => getPath(doc, "calibration_view_ii.convergence_model.ch5_gate_range"),
    validate: (v) => validateRangePair(v, 0.2, 1.2, "ch5_gate_range"),
  },
  {
    id: "view_synthetic_efficacy",
    expected: ["VIEW1"],
    get: (doc) => getPath(doc, "calibration_view_ii.synthetic_efficacy"),
    validate: (v) => {
      if (!v || typeof v !== "object") {
        return { ok: false, reason: "synthetic_efficacy must be object" };
      }
      const entries = Object.entries(v);
      if (entries.length === 0) {
        return { ok: false, reason: "synthetic_efficacy cannot be empty" };
      }
      for (const [k, val] of entries) {
        if (!isNum(val)) {
          return { ok: false, reason: `synthetic_efficacy.${k} must be numeric` };
        }
        if (val < 0 || val > 1.2) {
          return { ok: false, reason: `synthetic_efficacy.${k} outside [0,1.2]` };
        }
      }
      return { ok: true };
    },
  },
  {
    id: "view_vqi_range",
    expected: ["VIEW1"],
    get: (doc) => getPath(doc, "calibration_view_ii.vqi_score"),
    validate: (v) => {
      if (!v || typeof v !== "object") {
        return { ok: false, reason: "vqi_score must be object" };
      }
      const rangeCheck = validateRangePair(v.range, 0, 100, "vqi_score.range");
      if (!rangeCheck.ok) {
        return rangeCheck;
      }
      const th = v.thresholds;
      if (!th || !isNum(th.excellent) || !isNum(th.good) || !isNum(th.adequate) || !isNum(th.poor)) {
        return { ok: false, reason: "vqi_score.thresholds incomplete" };
      }
      if (!(th.excellent > th.good && th.good > th.adequate && th.adequate > th.poor)) {
        return { ok: false, reason: "vqi thresholds must be strictly descending" };
      }
      return { ok: true };
    },
  },
  {
    id: "view_blue_bonus_multiplier",
    expected: ["VIEW1"],
    get: (doc) => getPath(doc, "calibration_view_ii.blue_space_bonus.multiplier"),
    validate: (v) => {
      if (!isNum(v)) {
        return { ok: false, reason: "blue_space_bonus.multiplier must be numeric" };
      }
      if (v < 1.0 || v > 1.3) {
        return { ok: false, reason: "blue_space_bonus.multiplier outside [1.0,1.3]" };
      }
      return { ok: true };
    },
  },
  {
    id: "crea1_phase_durations_s",
    expected: ["CREA1"],
    get: (doc) => getPath(doc, "calibration_crea_i.phase_durations_s"),
    validate: (v) => {
      if (!v || typeof v !== "object") {
        return { ok: false, reason: "phase_durations_s must be object" };
      }
      for (const phase of ["generation", "selective", "evaluation"]) {
        const p = v[phase];
        if (!p || !isNum(p.mean) || !isNum(p.sd) || p.mean <= 0 || p.sd <= 0) {
          return { ok: false, reason: `phase_durations_s.${phase} must contain positive mean/sd` };
        }
      }
      return { ok: true };
    },
  },
  {
    id: "crea1_generative_extension_pct",
    expected: ["CREA1"],
    get: (doc) => getPath(doc, "calibration_crea_i.generative_extension_pct"),
    validate: (v) => {
      if (!isNum(v)) {
        return { ok: false, reason: "generative_extension_pct must be numeric" };
      }
      if (v < 0 || v > 100) {
        return { ok: false, reason: "generative_extension_pct outside [0,100]" };
      }
      return { ok: true };
    },
  },
  {
    id: "crea1_alpha_phase_marker",
    expected: ["CREA1"],
    get: (doc) => getPath(doc, "calibration_crea_i.alpha_phase_marker.frequency_hz"),
    validate: (v) => validateRangePair(v, 0, 200, "alpha_phase_marker.frequency_hz"),
  },
  {
    id: "crea2_pathway_d_values",
    expected: ["CREA2"],
    get: (doc) => getPath(doc, "calibration_crea_i.pathway_independence.pathway_d_values"),
    validate: (v) => {
      if (!v || typeof v !== "object") {
        return { ok: false, reason: "pathway_d_values must be object" };
      }
      const required = ["A_noise", "B_ceiling", "B_light", "B_combined", "C_demand"];
      for (const key of required) {
        if (!isNum(v[key])) {
          return { ok: false, reason: `pathway_d_values.${key} must be numeric` };
        }
        if (v[key] < 0 || v[key] > 2.0) {
          return { ok: false, reason: `pathway_d_values.${key} outside [0,2.0]` };
        }
      }
      return { ok: true };
    },
  },
  {
    id: "crea2_goldilocks_ceiling",
    expected: ["CREA2"],
    get: (doc) => getPath(doc, "calibration_crea_i.pathway_independence.creativity_goldilocks_ceiling"),
    validate: (v) => {
      if (!isNum(v)) {
        return { ok: false, reason: "creativity_goldilocks_ceiling must be numeric" };
      }
      if (v < 0 || v > 1) {
        return { ok: false, reason: "creativity_goldilocks_ceiling outside [0,1]" };
      }
      return { ok: true };
    },
  },
  {
    id: "crea2_two_pathway_optimum",
    expected: ["CREA2"],
    get: (doc) => getPath(doc, "calibration_crea_i.pathway_independence.two_pathway_optimum"),
    validate: (v) => validateMinMaxObject(v, 0, 1, "two_pathway_optimum"),
  },
  {
    id: "crea2_convergent_tradeoff_d",
    expected: ["CREA2"],
    get: (doc) => getPath(doc, "calibration_crea_i.pathway_independence.convergent_tradeoff_d"),
    validate: (v) => {
      if (!v || typeof v !== "object") {
        return { ok: false, reason: "convergent_tradeoff_d must be object" };
      }
      for (const key of ["A", "B", "C"]) {
        if (!isNum(v[key])) {
          return { ok: false, reason: `convergent_tradeoff_d.${key} must be numeric` };
        }
        if (v[key] > 0 || v[key] < -1) {
          return { ok: false, reason: `convergent_tradeoff_d.${key} outside [-1,0]` };
        }
      }
      return { ok: true };
    },
  },
  {
    id: "crea3_walk_duration_optimal_min",
    expected: ["CREA3"],
    get: (doc) => getPath(doc, "calibration_crea_i.walk_duration_optimal_min"),
    validate: (v) => validateMinMaxObject(v, 0, 120, "walk_duration_optimal_min"),
  },
  {
    id: "crea3_post_walk_persistence_min",
    expected: ["CREA3"],
    get: (doc) => getPath(doc, "calibration_crea_i.post_walk_persistence_min"),
    validate: (v) => validateMinMaxObject(v, 0, 120, "post_walk_persistence_min"),
  },
];

function runCalibrationChecks(canonicalByDisplay) {
  const out = {};
  let missingExpectedTotal = 0;
  let invalidValuesTotal = 0;

  for (const spec of CALIBRATION_CHECKS) {
    const rows = [];
    const missing = [];
    let present = 0;
    let valid = 0;
    let invalid = 0;

    for (const did of spec.expected) {
      const t = canonicalByDisplay.get(did);
      if (!t) {
        missing.push({ display_id: did, reason: "template missing" });
        continue;
      }
      const value = spec.get(t.data);
      if (typeof value === "undefined") {
        missing.push({ display_id: did, file: t.name, reason: "field missing" });
        continue;
      }
      present += 1;
      const result = spec.validate(value, t);
      if (result.ok) {
        valid += 1;
      } else {
        invalid += 1;
        rows.push({
          display_id: did,
          file: t.name,
          reason: result.reason,
        });
      }
    }

    missingExpectedTotal += missing.length;
    invalidValuesTotal += invalid;

    out[spec.id] = {
      expected_display_ids: spec.expected,
      present_count: present,
      valid_count: valid,
      invalid_count: invalid,
      missing_expected: missing,
      invalid_entries: rows,
    };
  }

  return {
    checks: out,
    summary: {
      missing_expected_total: missingExpectedTotal,
      invalid_values_total: invalidValuesTotal,
    },
  };
}

function runRootMetadataProjectionChecks(canonicalByDisplay) {
  const fields = {};
  let missingAssignmentsTotal = 0;

  for (const [field, displayIds] of Object.entries(ROOT_METADATA_EXPECTATIONS)) {
    const missing = [];
    const present = [];

    for (const did of displayIds) {
      const t = canonicalByDisplay.get(did);
      if (!t) {
        missing.push({ display_id: did, reason: "template missing" });
        continue;
      }
      if (!(field in t.data)) {
        missing.push({ display_id: did, file: t.name, reason: "field missing at root" });
      } else {
        present.push({ display_id: did, file: t.name });
      }
    }

    missingAssignmentsTotal += missing.length;

    fields[field] = {
      expected_display_ids: displayIds,
      present_count: present.length,
      missing_count: missing.length,
      present,
      missing,
    };
  }

  return {
    fields,
    summary: {
      missing_root_assignments_total: missingAssignmentsTotal,
    },
  };
}

function buildMarkdown(report, mdOut, jsonOut) {
  const md = [];
  md.push("# CX V12 Schema Validation Report");
  md.push("");
  md.push(`- Generated: ${report.generated_at}`);
  md.push(`- Template files scanned: ${report.template_files_scanned}`);
  md.push(`- Canonical display IDs covered: ${report.scope.expected_display_ids.join(", ")}`);
  md.push(
    `- Duplicate display IDs in V12 scope: ${report.summary.duplicate_display_id_count_in_scope} (global duplicates: ${report.summary.duplicate_display_id_count_global})`,
  );
  md.push(`- Calibration checks missing expected fields: ${report.calibration_checks.summary.missing_expected_total}`);
  md.push(`- Calibration checks invalid values: ${report.calibration_checks.summary.invalid_values_total}`);
  md.push(`- Root metadata missing assignments: ${report.root_metadata_projection.summary.missing_root_assignments_total}`);
  md.push("");

  md.push("## Calibration Checks");
  md.push("");
  md.push("| Check | Present | Valid | Invalid | Missing Expected |");
  md.push("|---|---:|---:|---:|---:|");
  for (const [checkId, row] of Object.entries(report.calibration_checks.checks)) {
    md.push(
      `| \`${checkId}\` | ${row.present_count} | ${row.valid_count} | ${row.invalid_count} | ${row.missing_expected.length} |`,
    );
  }
  md.push("");

  md.push("## Root Metadata Projection Checks");
  md.push("");
  md.push("| Field | Present | Missing |");
  md.push("|---|---:|---:|");
  for (const [field, row] of Object.entries(report.root_metadata_projection.fields)) {
    md.push(`| \`${field}\` | ${row.present_count} | ${row.missing_count} |`);
  }
  md.push("");

  if (report.summary.duplicate_display_id_count_in_scope > 0) {
    md.push("## Duplicate Display IDs (V12 Scope)");
    md.push("");
    for (const dup of report.duplicate_display_ids_in_scope) {
      md.push(`- \`${dup.display_id}\`: canonical=\`${dup.canonical_file}\``);
    }
    md.push("");
  }

  md.push("## Findings");
  md.push("");

  let findings = 0;
  for (const [checkId, row] of Object.entries(report.calibration_checks.checks)) {
    if (row.invalid_entries.length > 0) {
      findings += 1;
      for (const bad of row.invalid_entries) {
        md.push(`- \`${checkId}\`: ${bad.display_id} (${bad.file}) invalid: ${bad.reason}.`);
      }
    }
    if (row.missing_expected.length > 0) {
      findings += 1;
      const displayIds = row.missing_expected.map((m) => m.display_id).join(", ");
      md.push(`- \`${checkId}\`: missing on expected templates ${displayIds}.`);
    }
  }

  for (const [field, row] of Object.entries(report.root_metadata_projection.fields)) {
    if (row.missing_count > 0) {
      findings += 1;
      const displayIds = row.missing.map((m) => m.display_id).join(", ");
      md.push(`- Root field \`${field}\` missing on expected templates ${displayIds}.`);
    }
  }

  if (findings === 0) {
    md.push("- No issues found for V12 calibration checks or root metadata projections.");
  }

  md.push("");
  md.push("## Artifacts");
  md.push("");
  md.push(`- JSON: \`${path.relative(ROOT, jsonOut)}\``);
  md.push(`- Markdown: \`${path.relative(ROOT, mdOut)}\``);
  md.push("");

  return `${md.join("\n")}\n`;
}

function main() {
  const mdOut = process.argv[2] || DEFAULT_MD_OUT;
  const jsonOut = process.argv[3] || DEFAULT_JSON_OUT;

  const templates = readTemplates();
  const { canonical, duplicates } = pickCanonicalByDisplay(templates);

  const canonical_scope = {};
  for (const did of EXPECTED_DISPLAY_IDS) {
    const t = canonical.get(did);
    canonical_scope[did] = t
      ? {
          file: t.name,
          template_id: t.templateId,
        }
      : null;
  }

  const calibrationChecks = runCalibrationChecks(canonical);
  const rootProjection = runRootMetadataProjectionChecks(canonical);
  const duplicatesInScope = duplicates.filter((d) =>
    EXPECTED_DISPLAY_IDS.includes(d.display_id),
  );

  const report = {
    generated_at: toIsoNow(),
    template_files_scanned: templates.length,
    scope: {
      expected_display_ids: EXPECTED_DISPLAY_IDS,
      canonical_templates: canonical_scope,
    },
    duplicate_display_ids_global: duplicates,
    duplicate_display_ids_in_scope: duplicatesInScope,
    calibration_checks: calibrationChecks,
    root_metadata_projection: rootProjection,
    summary: {
      duplicate_display_id_count_global: duplicates.length,
      duplicate_display_id_count_in_scope: duplicatesInScope.length,
      calibration_missing_expected_total: calibrationChecks.summary.missing_expected_total,
      calibration_invalid_values_total: calibrationChecks.summary.invalid_values_total,
      root_missing_assignments_total: rootProjection.summary.missing_root_assignments_total,
    },
  };

  ensureDirFor(jsonOut);
  fs.writeFileSync(jsonOut, `${JSON.stringify(report, null, 2)}\n`, "utf8");

  const md = buildMarkdown(report, mdOut, jsonOut);
  ensureDirFor(mdOut);
  fs.writeFileSync(mdOut, md, "utf8");

  console.log(`wrote ${path.relative(ROOT, jsonOut)}`);
  console.log(`wrote ${path.relative(ROOT, mdOut)}`);
}

main();
