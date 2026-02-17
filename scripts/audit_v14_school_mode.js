#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const TEMPLATE_DIR = path.join(ROOT, "data", "templates");
const DEFAULT_MD_OUT = path.join(
  ROOT,
  "docs",
  "cx_v14_school_mode_audit_report_2026-02-17.md",
);
const DEFAULT_JSON_OUT = path.join(
  ROOT,
  "data",
  "review",
  "cx_v14_school_mode_audit_2026-02-17.json",
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

const REQUIRED_CLASSROOM_KEYS = [
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

function validateClassroomParams(params) {
  if (!params || typeof params !== "object") {
    return { ok: false, reason: "missing classroom_parameters object", missing_keys: REQUIRED_CLASSROOM_KEYS };
  }

  const missing = [];
  for (const key of REQUIRED_CLASSROOM_KEYS) {
    if (!(key in params)) {
      missing.push(key);
    }
  }

  if (missing.length > 0) {
    return { ok: false, reason: "missing classroom parameter keys", missing_keys: missing };
  }

  const issues = [];

  const daylight = params.daylight_vqi_min;
  if (!daylight || typeof daylight !== "object" || !isNum(daylight.primary_5_9)) {
    issues.push("daylight_vqi_min.primary_5_9 missing/non-numeric");
  }

  const lux = params.illuminance_lux;
  if (!lux || typeof lux !== "object" || !isNum(lux.min) || !isNum(lux.max) || lux.min > lux.max) {
    issues.push("illuminance_lux invalid");
  }

  const rt60 = params.acoustic_rt60_s_max;
  if (!rt60 || typeof rt60 !== "object" || !isNum(rt60.primary_5_9)) {
    issues.push("acoustic_rt60_s_max.primary_5_9 missing/non-numeric");
  }

  const noise = params.background_noise_dba_max;
  if (!noise || typeof noise !== "object" || !isNum(noise.primary_5_9)) {
    issues.push("background_noise_dba_max.primary_5_9 missing/non-numeric");
  }

  const clarity = params.spatial_clarity;
  if (!clarity || typeof clarity !== "object" || typeof clarity.primary_5_9 !== "string") {
    issues.push("spatial_clarity.primary_5_9 missing/non-string");
  }

  return issues.length === 0
    ? { ok: true, reason: null, missing_keys: [] }
    : { ok: false, reason: issues.join("; "), missing_keys: [] };
}

function main() {
  const mdOut = process.argv[2] || DEFAULT_MD_OUT;
  const jsonOut = process.argv[3] || DEFAULT_JSON_OUT;

  const templates = readTemplates();
  const { canonical, duplicates } = pickCanonicalByDisplay(templates);
  const duplicatesInScope = duplicates.filter((d) => TARGET_DISPLAY_IDS.includes(d.display_id));

  const rows = [];
  let missingTemplates = 0;
  let missingSchoolMode = 0;
  let invalidContext = 0;
  let missingOrInvalidParams = 0;
  let activationOk = 0;

  for (const displayId of TARGET_DISPLAY_IDS) {
    const t = canonical.get(displayId);
    if (!t) {
      rows.push({ display_id: displayId, status: "missing_template" });
      missingTemplates += 1;
      continue;
    }

    const contextModes = t.data.context_modes;
    const schoolMode = contextModes && typeof contextModes === "object" ? contextModes.school : null;

    if (!schoolMode || typeof schoolMode !== "object") {
      rows.push({
        display_id: displayId,
        file: t.name,
        template_id: t.templateId,
        status: "missing_school_mode",
      });
      missingSchoolMode += 1;
      continue;
    }

    const contextOk = schoolMode.context === "school";
    if (!contextOk) {
      invalidContext += 1;
    }

    const paramsCheck = validateClassroomParams(schoolMode.classroom_parameters);
    if (!paramsCheck.ok) {
      missingOrInvalidParams += 1;
    }

    const rowStatus = contextOk && paramsCheck.ok ? "activation_ok" : "activation_incomplete";
    if (rowStatus === "activation_ok") {
      activationOk += 1;
    }

    rows.push({
      display_id: displayId,
      file: t.name,
      template_id: t.templateId,
      status: rowStatus,
      checks: {
        context_is_school: contextOk,
        classroom_parameters: paramsCheck,
      },
    });
  }

  const report = {
    generated_at: toIsoNow(),
    template_files_scanned: templates.length,
    scope: {
      target_display_ids: TARGET_DISPLAY_IDS,
      duplicate_display_ids_in_scope: duplicatesInScope,
      required_classroom_keys: REQUIRED_CLASSROOM_KEYS,
    },
    summary: {
      missing_templates: missingTemplates,
      missing_school_mode_blocks: missingSchoolMode,
      invalid_school_context_values: invalidContext,
      missing_or_invalid_classroom_parameters: missingOrInvalidParams,
      activation_ok_templates: activationOk,
    },
    rows,
  };

  ensureDirFor(jsonOut);
  fs.writeFileSync(jsonOut, `${JSON.stringify(report, null, 2)}\n`, "utf8");

  const md = [];
  md.push("# CX V14 School Mode Activation Audit");
  md.push("");
  md.push(`- Generated: ${report.generated_at}`);
  md.push(`- Template files scanned: ${report.template_files_scanned}`);
  md.push(`- Target templates: ${TARGET_DISPLAY_IDS.join(", ")}`);
  md.push(`- Duplicate display IDs in scope: ${duplicatesInScope.length}`);
  md.push(`- Missing school mode blocks: ${missingSchoolMode}`);
  md.push(`- Invalid school context values: ${invalidContext}`);
  md.push(`- Missing/invalid classroom parameter sets: ${missingOrInvalidParams}`);
  md.push(`- Activation OK templates: ${activationOk}`);
  md.push("");

  md.push("## Per-Template Results");
  md.push("");
  md.push("| Display | Status | Notes |");
  md.push("|---|---|---|");

  for (const row of rows) {
    if (row.status === "missing_template") {
      md.push(`| ${row.display_id} | missing_template | template not found |`);
      continue;
    }

    if (row.status === "missing_school_mode") {
      md.push(`| ${row.display_id} | missing_school_mode | no context_modes.school block |`);
      continue;
    }

    if (row.status === "activation_ok") {
      md.push(`| ${row.display_id} | activation_ok | context='school' and all 11 classroom keys present |`);
      continue;
    }

    const notes = [];
    if (!row.checks.context_is_school) {
      notes.push("context != 'school'");
    }
    if (!row.checks.classroom_parameters.ok) {
      notes.push(row.checks.classroom_parameters.reason);
      if (row.checks.classroom_parameters.missing_keys.length > 0) {
        notes.push(`missing keys: ${row.checks.classroom_parameters.missing_keys.join(", ")}`);
      }
    }
    md.push(`| ${row.display_id} | activation_incomplete | ${notes.join("; ")} |`);
  }
  md.push("");

  md.push("## Findings");
  md.push("");
  if (missingSchoolMode === 0 && invalidContext === 0 && missingOrInvalidParams === 0) {
    md.push("- School mode activation is valid across the V14 target template set.");
  } else {
    if (missingSchoolMode > 0) {
      md.push(`- ${missingSchoolMode} templates do not yet expose a \`context_modes.school\` block.`);
    }
    if (invalidContext > 0) {
      md.push(`- ${invalidContext} templates have a school block but \`context\` is not \`"school"\`.`);
    }
    if (missingOrInvalidParams > 0) {
      md.push(`- ${missingOrInvalidParams} templates have school mode but missing/invalid classroom parameters.`);
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
