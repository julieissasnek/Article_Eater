#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const TEMPLATE_DIR = path.join(ROOT, "data", "templates");
const DEFAULT_MD_OUT = path.join(
  ROOT,
  "docs",
  "cx_v14_runtime_checks_report_2026-02-17.md",
);
const DEFAULT_JSON_OUT = path.join(
  ROOT,
  "data",
  "review",
  "cx_v14_runtime_checks_2026-02-17.json",
);

const REQUIRED_DISPLAYS = ["VIEW1", "TP1", "TP2", "SOC1"];

const DISPLAY_FIELDS = {
  VIEW1: "dev_restoration_multiplier",
  TP1: "dev_mfi_baseline",
  TP2: "dev_channel_capacity",
  SOC1: "dev_personal_space_cm",
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
  for (const [displayId, candidates] of byDisplay.entries()) {
    const ranked = candidates
      .map((c) => ({ c, score: scoreCanonicalCandidate(c) }))
      .sort((a, b) => b.score - a.score || a.c.name.localeCompare(b.c.name));
    canonical.set(displayId, ranked[0].c);
  }
  return canonical;
}

function expectedInterpolated(v16, v25, age) {
  if (age <= 16) return v16;
  if (age >= 25) return v25;
  const ratio = (age - 16) / (25 - 16);
  return v16 + (v25 - v16) * ratio;
}

function closeEnough(a, b, tol = 1e-9) {
  return Math.abs(a - b) <= tol;
}

function buildMarkdown(report, mdOut, jsonOut) {
  const md = [];
  md.push("# CX V14 Runtime Checks Report");
  md.push("");
  md.push(`- Generated: ${report.generated_at}`);
  md.push(`- Templates scanned: ${report.template_files_scanned}`);
  md.push(`- Required displays resolved: ${report.summary.resolved_displays}/${report.summary.required_displays}`);
  md.push(`- Interpolation checks: ${report.summary.interpolation_checks_passed}/${report.summary.interpolation_checks_total}`);
  md.push(`- School-mode checks: ${report.summary.school_checks_passed}/${report.summary.school_checks_total}`);
  md.push(`- Template-specific dev-field checks: ${report.summary.dev_field_checks_passed}/${report.summary.dev_field_checks_total}`);
  md.push(`- Pass: ${report.summary.pass}`);
  md.push("");
  md.push("## Findings");
  md.push("");
  if (report.issues.length === 0) {
    md.push("- No runtime issues found.");
  } else {
    for (const issue of report.issues) {
      md.push(`- ${issue.display_id || "unknown"} (${issue.file || "n/a"}): ${issue.message}`);
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
  const canonical = pickCanonicalByDisplay(templates);
  const issues = [];

  const interpolationSamples = [];
  let interpolationChecksTotal = 0;
  let interpolationChecksPassed = 0;
  let schoolChecksTotal = 0;
  let schoolChecksPassed = 0;
  let devChecksTotal = 0;
  let devChecksPassed = 0;
  let resolvedDisplays = 0;

  for (const did of REQUIRED_DISPLAYS) {
    const t = canonical.get(did);
    if (!t) {
      issues.push({ display_id: did, file: null, message: "canonical template missing" });
      continue;
    }
    resolvedDisplays += 1;

    const lsm = t.data.lifespan_sensitivity_multiplier;
    const byAge = lsm && lsm.by_age_range;
    if (!byAge || !isNum(byAge.age_12_25) || !isNum(byAge.age_25_50)) {
      issues.push({ display_id: did, file: t.name, message: "missing numeric lifespan anchors age_12_25 and age_25_50" });
    } else {
      const v16 = byAge.age_12_25;
      const v25 = byAge.age_25_50;
      const expected = {
        age16: expectedInterpolated(v16, v25, 16),
        age20: expectedInterpolated(v16, v25, 20),
        age25: expectedInterpolated(v16, v25, 25),
      };

      interpolationSamples.push({
        display_id: did,
        file: t.name,
        anchors: { age_16: v16, age_25: v25 },
        expected,
      });

      interpolationChecksTotal += 3;
      if (closeEnough(expected.age16, v16)) interpolationChecksPassed += 1;
      else issues.push({ display_id: did, file: t.name, message: "age 16 interpolation check failed" });

      if (expected.age20 < v16 && expected.age20 > v25) interpolationChecksPassed += 1;
      else issues.push({ display_id: did, file: t.name, message: "age 20 interpolation monotonicity check failed" });

      if (closeEnough(expected.age25, v25)) interpolationChecksPassed += 1;
      else issues.push({ display_id: did, file: t.name, message: "age 25 interpolation check failed" });

      if (!lsm.boundary_rule || lsm.boundary_rule.range !== "16-25") {
        issues.push({ display_id: did, file: t.name, message: "boundary_rule.range must be '16-25'" });
      }
    }

    schoolChecksTotal += 1;
    const school = t.data.context_modes && t.data.context_modes.school;
    const params = school && school.classroom_parameters;
    if (
      school &&
      school.context === "school" &&
      params &&
      typeof params === "object"
    ) {
      schoolChecksPassed += 1;
    } else {
      issues.push({ display_id: did, file: t.name, message: "school mode activation missing/incomplete" });
    }

    devChecksTotal += 1;
    const field = DISPLAY_FIELDS[did];
    if (field in t.data) {
      devChecksPassed += 1;
    } else {
      issues.push({ display_id: did, file: t.name, message: `missing expected dev field ${field}` });
    }
  }

  const report = {
    generated_at: toIsoNow(),
    template_files_scanned: templates.length,
    required_displays: REQUIRED_DISPLAYS,
    interpolation_samples: interpolationSamples,
    issues,
    summary: {
      required_displays: REQUIRED_DISPLAYS.length,
      resolved_displays: resolvedDisplays,
      interpolation_checks_total: interpolationChecksTotal,
      interpolation_checks_passed: interpolationChecksPassed,
      school_checks_total: schoolChecksTotal,
      school_checks_passed: schoolChecksPassed,
      dev_field_checks_total: devChecksTotal,
      dev_field_checks_passed: devChecksPassed,
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
