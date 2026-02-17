#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const TEMPLATE_DIR = path.join(ROOT, "data", "templates");
const DEFAULT_MD_OUT = path.join(
  ROOT,
  "docs",
  "cx_v10_schema_validation_report_2026-02-17.md",
);
const DEFAULT_JSON_OUT = path.join(
  ROOT,
  "data",
  "review",
  "cx_v10_schema_validation_2026-02-17.json",
);

const CULTURAL_CLUSTERS = new Set([
  "latin_american",
  "north_american",
  "northern_european",
  "east_asian",
  "middle_eastern",
]);
const CREATIVE_PHASES = new Set([
  "generative",
  "evaluative",
  "incubation",
  "phase_neutral",
]);
const DUNBAR_LAYERS = new Set([5, 15, 50, 150]);

const EXPECTED_BY_FIELD = {
  cultural_cluster: ["SOC1", "SOC3", "SC4"],
  privacy_encounter_ratio: ["SOC2"],
  dunbar_layer: ["SOC3", "SC4"],
  floor_tax_multiplier: ["SOC3"],
  creative_phase_affinity: ["T59", "T60", "T61"],
  mfi_range: ["TP1"],
  aging_trajectory: ["TP3"],
  threshold_channel_count: ["TP2", "SC3", "AX3", "AX6"],
};

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

function isNum(v) {
  return typeof v === "number" && Number.isFinite(v);
}

function validateEnumOrEnumArray(value, allowed) {
  if (typeof value === "string") {
    return allowed.has(value)
      ? { ok: true }
      : { ok: false, reason: `invalid enum value '${value}'` };
  }
  if (Array.isArray(value)) {
    const invalid = value.filter((x) => typeof x !== "string" || !allowed.has(x));
    return invalid.length === 0
      ? { ok: true }
      : { ok: false, reason: `invalid array values: ${JSON.stringify(invalid)}` };
  }
  return { ok: false, reason: "value must be string or string[]" };
}

function validateMfiRange(value) {
  let min;
  let max;
  if (Array.isArray(value) && value.length === 2) {
    min = value[0];
    max = value[1];
  } else if (value && typeof value === "object") {
    min = value.min;
    max = value.max;
  } else {
    return { ok: false, reason: "mfi_range must be {min,max} or [min,max]" };
  }

  if (!isNum(min) || !isNum(max)) {
    return { ok: false, reason: "mfi_range min/max must be numeric" };
  }
  if (min < 0 || max > 1 || min > max) {
    return { ok: false, reason: "mfi_range must satisfy 0 <= min <= max <= 1" };
  }
  return { ok: true };
}

function collectAgingParamBlocks(value, pathPrefix, out) {
  if (!value || typeof value !== "object") {
    return;
  }

  const entries = Object.entries(value);
  const dVals = [];
  const tauVals = [];

  for (const [k, v] of entries) {
    const lk = k.toLowerCase();
    if (isNum(v) && (lk === "d_0" || lk === "d0" || lk === "d_initial" || lk === "dmax" || lk === "d_max")) {
      dVals.push({ key: `${pathPrefix}${k}`, value: v });
    }
    if (isNum(v) && (lk === "tau" || lk === "tau_years" || lk === "tau_yr")) {
      tauVals.push({ key: `${pathPrefix}${k}`, value: v });
    }
  }

  if (dVals.length > 0 || tauVals.length > 0) {
    out.push({ dVals, tauVals, path: pathPrefix || "(root)" });
  }

  for (const [k, v] of entries) {
    if (v && typeof v === "object") {
      collectAgingParamBlocks(v, `${pathPrefix}${k}.`, out);
    }
  }
}

function validateAgingTrajectory(value) {
  if (!value || typeof value !== "object") {
    return { ok: false, reason: "aging_trajectory must be an object" };
  }

  const blocks = [];
  collectAgingParamBlocks(value, "", blocks);
  if (blocks.length === 0) {
    return {
      ok: false,
      reason: "aging_trajectory has no recognizable D/tau fields",
    };
  }

  const issues = [];
  for (const block of blocks) {
    for (const d of block.dVals) {
      if (d.value < 1.0 || d.value > 2.0) {
        issues.push(`${d.key}=${d.value} outside [1.0,2.0]`);
      }
    }
    for (const tau of block.tauVals) {
      if (tau.value <= 0) {
        issues.push(`${tau.key}=${tau.value} must be > 0`);
      }
    }
  }

  return issues.length === 0
    ? { ok: true }
    : { ok: false, reason: issues.join("; ") };
}

function buildFieldChecks() {
  return {
    cultural_cluster: (v) => validateEnumOrEnumArray(v, CULTURAL_CLUSTERS),
    privacy_encounter_ratio: (v) => {
      if (!isNum(v)) {
        return { ok: false, reason: "privacy_encounter_ratio must be numeric" };
      }
      return v >= 0 && v <= 1
        ? { ok: true }
        : { ok: false, reason: "privacy_encounter_ratio must be within [0,1]" };
    },
    dunbar_layer: (v) => {
      if (!Number.isInteger(v)) {
        return { ok: false, reason: "dunbar_layer must be an integer" };
      }
      return DUNBAR_LAYERS.has(v)
        ? { ok: true }
        : { ok: false, reason: "dunbar_layer must be one of 5,15,50,150" };
    },
    floor_tax_multiplier: (v) => {
      if (!Number.isInteger(v)) {
        return { ok: false, reason: "floor_tax_multiplier must be an integer" };
      }
      return v > 0
        ? { ok: true }
        : { ok: false, reason: "floor_tax_multiplier must be > 0" };
    },
    creative_phase_affinity: (v) => validateEnumOrEnumArray(v, CREATIVE_PHASES),
    mfi_range: validateMfiRange,
    aging_trajectory: validateAgingTrajectory,
    threshold_channel_count: (v) => {
      if (!Number.isInteger(v)) {
        return { ok: false, reason: "threshold_channel_count must be an integer" };
      }
      return v >= 0 && v <= 7
        ? { ok: true }
        : { ok: false, reason: "threshold_channel_count must be within [0,7]" };
    },
  };
}

function ensureDirFor(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function toIsoNow() {
  return new Date().toISOString();
}

function main() {
  const mdOut = process.argv[2] || DEFAULT_MD_OUT;
  const jsonOut = process.argv[3] || DEFAULT_JSON_OUT;

  const templates = readTemplates();
  const validators = buildFieldChecks();
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

  const report = {
    generated_at: toIsoNow(),
    template_files_scanned: templates.length,
    fields: {},
    summary: {
      missing_expected_total: 0,
      invalid_values_total: 0,
    },
  };

  for (const [field, expectedDisplayIds] of Object.entries(EXPECTED_BY_FIELD)) {
    const invalidEntries = [];
    let presentCount = 0;
    let validCount = 0;
    let invalidCount = 0;

    for (const t of templates) {
      if (!(field in t.data)) {
        continue;
      }
      presentCount += 1;
      const result = validators[field](t.data[field]);
      if (result.ok) {
        validCount += 1;
      } else {
        invalidCount += 1;
        invalidEntries.push({
          file: t.name,
          display_id: t.displayId,
          template_id: t.templateId,
          reason: result.reason,
          value: t.data[field],
        });
      }
    }

    const missingExpected = [];
    for (const displayId of expectedDisplayIds) {
      const matches = byDisplay.get(displayId) || [];
      const hasField = matches.some((t) => field in t.data);
      if (!hasField) {
        missingExpected.push(displayId);
      }
    }

    report.fields[field] = {
      present_count: presentCount,
      valid_count: validCount,
      invalid_count: invalidCount,
      expected_display_ids: expectedDisplayIds,
      missing_expected_display_ids: missingExpected,
      invalid_entries: invalidEntries,
    };

    report.summary.missing_expected_total += missingExpected.length;
    report.summary.invalid_values_total += invalidCount;
  }

  const mdLines = [];
  mdLines.push("# CX V10 Schema Validation Report");
  mdLines.push("");
  mdLines.push(`- Generated: ${report.generated_at}`);
  mdLines.push(`- Template files scanned: ${report.template_files_scanned}`);
  mdLines.push(`- Missing expected field assignments: ${report.summary.missing_expected_total}`);
  mdLines.push(`- Invalid field values: ${report.summary.invalid_values_total}`);
  mdLines.push("");
  mdLines.push("## Field Results");
  mdLines.push("");
  mdLines.push("| Field | Present | Valid | Invalid | Missing Expected Display IDs |");
  mdLines.push("|---|---:|---:|---:|---|");
  for (const [field, stats] of Object.entries(report.fields)) {
    const missing = stats.missing_expected_display_ids.join(", ") || "none";
    mdLines.push(
      `| \`${field}\` | ${stats.present_count} | ${stats.valid_count} | ${stats.invalid_count} | ${missing} |`,
    );
  }
  mdLines.push("");

  const fieldsWithIssues = Object.entries(report.fields).filter(
    ([, stats]) =>
      stats.invalid_count > 0 || stats.missing_expected_display_ids.length > 0,
  );

  if (fieldsWithIssues.length > 0) {
    mdLines.push("## Findings");
    mdLines.push("");
    for (const [field, stats] of fieldsWithIssues) {
      if (stats.missing_expected_display_ids.length > 0) {
        mdLines.push(
          `- \`${field}\`: missing on expected templates ${stats.missing_expected_display_ids.join(", ")}.`,
        );
      }
      for (const entry of stats.invalid_entries) {
        mdLines.push(
          `- \`${field}\`: ${entry.file} (${entry.display_id || "n/a"}) invalid: ${entry.reason}.`,
        );
      }
    }
    mdLines.push("");
  }

  mdLines.push("## Artifacts");
  mdLines.push("");
  mdLines.push(`- JSON: \`${path.relative(ROOT, jsonOut)}\``);
  mdLines.push(`- Markdown: \`${path.relative(ROOT, mdOut)}\``);
  mdLines.push("");

  ensureDirFor(jsonOut);
  ensureDirFor(mdOut);
  fs.writeFileSync(jsonOut, JSON.stringify(report, null, 2) + "\n", "utf8");
  fs.writeFileSync(mdOut, mdLines.join("\n") + "\n", "utf8");

  console.log(`Wrote ${path.relative(ROOT, jsonOut)}`);
  console.log(`Wrote ${path.relative(ROOT, mdOut)}`);
  console.log(
    `Summary: missing_expected=${report.summary.missing_expected_total}, invalid_values=${report.summary.invalid_values_total}`,
  );
}

main();
