#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const TEMPLATE_DIR = path.join(ROOT, "data", "templates");
const DEFAULT_MD_OUT = path.join(
  ROOT,
  "docs",
  "cx_v14_lifespan_validation_report_2026-02-17.md",
);
const DEFAULT_JSON_OUT = path.join(
  ROOT,
  "data",
  "review",
  "cx_v14_lifespan_validation_2026-02-17.json",
);

const REQUIRED_ROOT_FIELDS = [
  "age_band_modifiers",
  "vulnerability_index",
  "universal_design_thresholds",
  "challenge_gradient_available",
  "lifespan_sensitivity_multiplier",
  "developmental_challenge_benefit",
  "context_modes",
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

const REQUIRED_AGE_FACTORS = ["speed", "vision", "hearing", "motor", "olfaction"];

const REQUIRED_UCURVE_RANGES = [
  "age_0_6",
  "age_6_12",
  "age_12_25",
  "age_25_50",
  "age_50_65",
  "age_65_80",
  "age_80_plus",
];

const REQUIRED_SCHOOL_PARAMS = [
  "daylight_vqi_min",
  "illuminance_lux",
  "cct_k",
  "acoustic_rt60_s_max",
  "background_noise_dba_max",
  "visual_complexity_target",
  "display_area_m2_per_child",
  "nature_view_priority",
  "movement_break_min",
  "ceiling_height_m",
  "spatial_clarity",
];

const EXPECTED_BY_DISPLAY = {
  L2: ["medi_age_multiplier"],
  L3: ["glare_tolerance_cd_m2"],
  VIEW1: ["restoration_multiplier", "dev_restoration_multiplier"],
  TP1: ["attentional_cost_multiplier", "dev_mfi_baseline"],
  TP2: ["threshold_recovery_strides", "dev_channel_capacity"],
  SOC1: ["dev_personal_space_cm"],
  SOC2: ["optimal_privacy_ratio"],
  CREA3: ["walk_duration_optimal"],
};

function ensureDirFor(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function isNum(v) {
  return typeof v === "number" && Number.isFinite(v);
}

function toIsoNow() {
  return new Date().toISOString();
}

function readTemplates() {
  const files = fs
    .readdirSync(TEMPLATE_DIR)
    .filter((f) => f.endsWith(".json"))
    .sort();
  return files.map((name) => {
    const full = path.join(TEMPLATE_DIR, name);
    const data = JSON.parse(fs.readFileSync(full, "utf8"));
    return {
      name,
      data,
      templateId: data.template_id || data.id || null,
      displayId: data.display_id || null,
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
    t.data.calibration_parameters
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
    if (!t.displayId) continue;
    if (!byDisplay.has(t.displayId)) byDisplay.set(t.displayId, []);
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
        candidates: ranked.map((r) => ({ file: r.c.name, score: r.score })),
      });
    }
  }
  return { canonical, duplicates };
}

function pushIssue(issues, file, displayId, field, reason) {
  issues.push({ file, display_id: displayId || null, field, reason });
}

function validateTemplate(record, issues) {
  const { data, name, displayId } = record;

  for (const field of REQUIRED_ROOT_FIELDS) {
    if (!(field in data)) {
      pushIssue(issues, name, displayId, field, "missing required root field");
    }
  }

  if (data.age_band_modifiers && typeof data.age_band_modifiers === "object") {
    for (const band of REQUIRED_AGE_BANDS) {
      const v = data.age_band_modifiers[band];
      if (!v || typeof v !== "object") {
        pushIssue(issues, name, displayId, "age_band_modifiers", `missing band ${band}`);
        continue;
      }
      for (const factor of REQUIRED_AGE_FACTORS) {
        if (!isNum(v[factor])) {
          pushIssue(issues, name, displayId, "age_band_modifiers", `${band}.${factor} must be numeric`);
        }
      }
    }
  } else if ("age_band_modifiers" in data) {
    pushIssue(issues, name, displayId, "age_band_modifiers", "must be object");
  }

  if (data.vulnerability_index && typeof data.vulnerability_index === "object") {
    if (typeof data.vulnerability_index.formula !== "string" || !data.vulnerability_index.formula.trim()) {
      pushIssue(issues, name, displayId, "vulnerability_index", "formula must be non-empty string");
    }
    if (typeof data.vulnerability_index.reference_band !== "string" || !data.vulnerability_index.reference_band.trim()) {
      pushIssue(issues, name, displayId, "vulnerability_index", "reference_band must be non-empty string");
    }
  } else if ("vulnerability_index" in data) {
    pushIssue(issues, name, displayId, "vulnerability_index", "must be object");
  }

  if (data.universal_design_thresholds && typeof data.universal_design_thresholds === "object") {
    const u = data.universal_design_thresholds;
    const numericKeys = [
      "min_ambient_illuminance_lux",
      "max_rt60_speech_s",
      "min_snr_db",
      "min_cof",
      "max_riser_mm",
      "min_contrast_ratio",
      "min_wayfinding_channels",
    ];
    for (const key of numericKeys) {
      if (!isNum(u[key])) {
        pushIssue(issues, name, displayId, "universal_design_thresholds", `${key} must be numeric`);
      }
    }
  } else if ("universal_design_thresholds" in data) {
    pushIssue(issues, name, displayId, "universal_design_thresholds", "must be object");
  }

  if ("challenge_gradient_available" in data && typeof data.challenge_gradient_available !== "boolean") {
    pushIssue(issues, name, displayId, "challenge_gradient_available", "must be boolean");
  }
  if ("developmental_challenge_benefit" in data && typeof data.developmental_challenge_benefit !== "boolean") {
    pushIssue(issues, name, displayId, "developmental_challenge_benefit", "must be boolean");
  }

  if (data.lifespan_sensitivity_multiplier && typeof data.lifespan_sensitivity_multiplier === "object") {
    const l = data.lifespan_sensitivity_multiplier;
    const byAge = l.by_age_range;
    if (!byAge || typeof byAge !== "object") {
      pushIssue(issues, name, displayId, "lifespan_sensitivity_multiplier", "by_age_range must be object");
    } else {
      for (const k of REQUIRED_UCURVE_RANGES) {
        if (!isNum(byAge[k])) {
          pushIssue(issues, name, displayId, "lifespan_sensitivity_multiplier", `${k} must be numeric`);
        }
      }
      if (
        isNum(byAge.age_0_6) &&
        isNum(byAge.age_6_12) &&
        isNum(byAge.age_12_25) &&
        isNum(byAge.age_25_50) &&
        !(byAge.age_0_6 > byAge.age_6_12 && byAge.age_6_12 >= byAge.age_12_25 && byAge.age_12_25 >= byAge.age_25_50)
      ) {
        pushIssue(issues, name, displayId, "lifespan_sensitivity_multiplier", "invalid developmental side of U-curve");
      }
      if (
        isNum(byAge.age_80_plus) &&
        isNum(byAge.age_65_80) &&
        isNum(byAge.age_50_65) &&
        isNum(byAge.age_25_50) &&
        !(byAge.age_80_plus > byAge.age_65_80 && byAge.age_65_80 > byAge.age_50_65 && byAge.age_50_65 > byAge.age_25_50)
      ) {
        pushIssue(issues, name, displayId, "lifespan_sensitivity_multiplier", "invalid aging side of U-curve");
      }
    }
    const br = l.boundary_rule;
    if (!br || typeof br !== "object") {
      pushIssue(issues, name, displayId, "lifespan_sensitivity_multiplier", "boundary_rule must be object");
    } else if (br.range !== "16-25") {
      pushIssue(issues, name, displayId, "lifespan_sensitivity_multiplier", "boundary_rule.range must be '16-25'");
    }
  } else if ("lifespan_sensitivity_multiplier" in data) {
    pushIssue(issues, name, displayId, "lifespan_sensitivity_multiplier", "must be object");
  }

  if (data.context_modes && typeof data.context_modes === "object") {
    const school = data.context_modes.school;
    if (!school || typeof school !== "object") {
      pushIssue(issues, name, displayId, "context_modes", "context_modes.school must be object");
    } else {
      if (school.context !== "school") {
        pushIssue(issues, name, displayId, "context_modes", "context_modes.school.context must be 'school'");
      }
      const params = school.classroom_parameters;
      if (!params || typeof params !== "object") {
        pushIssue(issues, name, displayId, "context_modes", "context_modes.school.classroom_parameters must be object");
      } else {
        for (const key of REQUIRED_SCHOOL_PARAMS) {
          if (!(key in params)) {
            pushIssue(issues, name, displayId, "context_modes", `missing school parameter ${key}`);
          }
        }
      }
    }
  } else if ("context_modes" in data) {
    pushIssue(issues, name, displayId, "context_modes", "must be object");
  }
}

function validateExpectedDisplaySpecific(canonicalByDisplay) {
  const issues = [];
  for (const [displayId, fields] of Object.entries(EXPECTED_BY_DISPLAY)) {
    const t = canonicalByDisplay.get(displayId);
    if (!t) {
      issues.push({
        display_id: displayId,
        field: "(template)",
        reason: "canonical template missing",
      });
      continue;
    }
    for (const field of fields) {
      if (!(field in t.data)) {
        issues.push({
          file: t.name,
          display_id: displayId,
          field,
          reason: "missing expected display-specific field",
        });
      }
    }
  }
  return issues;
}

function buildMarkdown(report, mdOut, jsonOut) {
  const md = [];
  md.push("# CX V14 Lifespan Validation Report");
  md.push("");
  md.push(`- Generated: ${report.generated_at}`);
  md.push(`- Template files scanned: ${report.template_files_scanned}`);
  md.push(`- Missing required root fields: ${report.summary.missing_required_root_fields}`);
  md.push(`- Structural validation issues: ${report.summary.structural_issues}`);
  md.push(`- Display-specific expectation issues: ${report.summary.display_specific_issues}`);
  md.push(`- Duplicate display IDs: ${report.summary.duplicate_display_id_count}`);
  md.push("");
  md.push("## Findings");
  md.push("");

  if (report.summary.total_issues === 0) {
    md.push("- No V14 lifespan issues found.");
  } else {
    for (const issue of report.issues.slice(0, 200)) {
      const prefix = issue.display_id ? `${issue.display_id} (${issue.file})` : `${issue.file}`;
      md.push(`- ${prefix}: \`${issue.field}\` ${issue.reason}.`);
    }
    if (report.issues.length > 200) {
      md.push(`- ... plus ${report.issues.length - 200} additional issues (see JSON artifact).`);
    }
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
  const issues = [];

  for (const record of templates) {
    validateTemplate(record, issues);
  }

  const missingRoot = issues.filter((i) => i.reason === "missing required root field").length;
  const structuralIssues = issues.length - missingRoot;

  const { canonical, duplicates } = pickCanonicalByDisplay(templates);
  const displayIssues = validateExpectedDisplaySpecific(canonical);
  for (const item of displayIssues) {
    issues.push(item);
  }

  const report = {
    generated_at: toIsoNow(),
    template_files_scanned: templates.length,
    expected_display_specific_fields: EXPECTED_BY_DISPLAY,
    issues,
    summary: {
      missing_required_root_fields: missingRoot,
      structural_issues: structuralIssues,
      display_specific_issues: displayIssues.length,
      duplicate_display_id_count: duplicates.length,
      total_issues: issues.length,
      pass: issues.length === 0,
    },
  };

  ensureDirFor(jsonOut);
  fs.writeFileSync(jsonOut, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  const md = buildMarkdown(report, mdOut, jsonOut);
  ensureDirFor(mdOut);
  fs.writeFileSync(mdOut, md, "utf8");

  console.log(`wrote ${path.relative(ROOT, jsonOut)}`);
  console.log(`wrote ${path.relative(ROOT, mdOut)}`);

  if (!report.summary.pass) {
    process.exit(1);
  }
}

main();
