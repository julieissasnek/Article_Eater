#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const DATE_TAG = new Date().toISOString().slice(0, 10);
const DEFAULT_MD_OUT = path.join(
  ROOT,
  "docs",
  `cx_v15_vf_crea_chain_validation_report_${DATE_TAG}.md`,
);
const DEFAULT_JSON_OUT = path.join(
  ROOT,
  "data",
  "review",
  `cx_v15_vf_crea_chain_validation_${DATE_TAG}.json`,
);

const VF3_FILE = path.join(ROOT, "data", "templates", "VF3.json");
const CREA2_FILE = path.join(
  ROOT,
  "data",
  "templates",
  "CREA2_processing_style_modulation.json",
);

const MATRIX_KEYS = [
  "A_noise_only",
  "B_ceiling_only",
  "C_light_only",
  "A_plus_B",
  "A_plus_C",
  "B_plus_C",
  "A_plus_B_plus_C",
];

const EXPECTED_SUB_ADDITIVITY = {
  A_noise_only: 1.0,
  B_ceiling_only: 1.0,
  C_light_only: 1.0,
  A_plus_B: 0.84,
  A_plus_C: 0.76,
  B_plus_C: 0.80,
  A_plus_B_plus_C: 0.70,
};

function toIsoNow() {
  return new Date().toISOString();
}

function ensureDirFor(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function normalizeInteractionRef(interaction) {
  if (typeof interaction === "string") {
    return interaction;
  }
  if (interaction && typeof interaction === "object") {
    return `${interaction.template_id || ""} ${interaction.display_id || ""}`.trim();
  }
  return "";
}

function canonicalMatrixKey(activePathways) {
  const set = new Set(activePathways);
  const hasA = set.has("A");
  const hasB = set.has("B");
  const hasC = set.has("C");

  if (hasA && hasB && hasC) return "A_plus_B_plus_C";
  if (hasA && hasB) return "A_plus_B";
  if (hasA && hasC) return "A_plus_C";
  if (hasB && hasC) return "B_plus_C";
  if (hasA) return "A_noise_only";
  if (hasB) return "B_ceiling_only";
  if (hasC) return "C_light_only";
  return null;
}

function sameNumber(a, b, tol = 1e-9) {
  return typeof a === "number" && typeof b === "number" && Math.abs(a - b) <= tol;
}

function buildMarkdown(report, mdOut, jsonOut) {
  const lines = [];
  lines.push("# CX V15 VF->CREA Chain Validation Report");
  lines.push("");
  lines.push(`- Generated: ${report.generated_at}`);
  lines.push(`- Pass: ${report.summary.pass}`);
  lines.push(`- Checks passed: ${report.summary.checks_passed}/${report.summary.checks_total}`);
  lines.push("");
  lines.push("## Summary");
  lines.push("");
  lines.push(`- VF3 chain path: \`${report.vf3_chain_path || "missing"}\``);
  lines.push(`- Direct VF3->CREA2 interaction present: ${report.direct_vf3_to_crea2_found}`);
  lines.push(
    `- Interaction matrix keys present: ${report.summary.matrix_keys_present}/${MATRIX_KEYS.length}`,
  );
  lines.push("");
  lines.push("## Findings");
  lines.push("");
  if (report.issues.length === 0) {
    lines.push("- No issues found.");
  } else {
    for (const issue of report.issues) {
      lines.push(`- ${issue}`);
    }
  }
  lines.push("");
  lines.push("## Artifacts");
  lines.push("");
  lines.push(`- JSON: \`${path.relative(ROOT, jsonOut)}\``);
  lines.push(`- Markdown: \`${path.relative(ROOT, mdOut)}\``);
  lines.push("");
  return `${lines.join("\n")}\n`;
}

function main() {
  const mdOut = process.argv[2] || DEFAULT_MD_OUT;
  const jsonOut = process.argv[3] || DEFAULT_JSON_OUT;

  const vf3 = readJson(VF3_FILE);
  const crea2 = readJson(CREA2_FILE);
  const issues = [];

  let checksTotal = 0;
  let checksPassed = 0;

  const chainPath = vf3?.calibration_data?.crea2b_linkage?.pathway;
  checksTotal += 1;
  if (
    typeof chainPath === "string" &&
    chainPath.includes("VF3 -> Affect -> CREA2B -> Divergent Thinking")
  ) {
    checksPassed += 1;
  } else {
    issues.push("VF3 CREA2B chain path missing or changed.");
  }

  const directLinkFound = Array.isArray(vf3.interactions)
    ? vf3.interactions.some((item) => /\bCREA2\b/i.test(normalizeInteractionRef(item)))
    : false;
  checksTotal += 1;
  if (!directLinkFound) {
    checksPassed += 1;
  } else {
    issues.push("Direct VF3->CREA2 interaction detected; may cause double-counting.");
  }

  const matrix = crea2?.calibration_data?.interaction_matrix;
  let matrixKeysPresent = 0;
  for (const key of MATRIX_KEYS) {
    checksTotal += 1;
    if (matrix && Object.prototype.hasOwnProperty.call(matrix, key)) {
      matrixKeysPresent += 1;
      checksPassed += 1;
    } else {
      issues.push(`Missing interaction matrix key: ${key}`);
    }
  }

  for (const [key, expected] of Object.entries(EXPECTED_SUB_ADDITIVITY)) {
    checksTotal += 1;
    const got = matrix?.[key]?.sub_additivity;
    if (sameNumber(got, expected)) {
      checksPassed += 1;
    } else {
      issues.push(
        `Sub-additivity mismatch for ${key}: expected ${expected}, got ${String(got)}.`,
      );
    }
  }

  const lookupProbes = [
    { active: ["A"], expected: "A_noise_only" },
    { active: ["B"], expected: "B_ceiling_only" },
    { active: ["C"], expected: "C_light_only" },
    { active: ["A", "B"], expected: "A_plus_B" },
    { active: ["A", "C"], expected: "A_plus_C" },
    { active: ["B", "C"], expected: "B_plus_C" },
    { active: ["A", "B", "C"], expected: "A_plus_B_plus_C" },
  ];
  for (const probe of lookupProbes) {
    checksTotal += 1;
    const key = canonicalMatrixKey(probe.active);
    if (key === probe.expected) {
      checksPassed += 1;
    } else {
      issues.push(
        `Lookup mapping mismatch for ${probe.active.join("+")}: expected ${probe.expected}, got ${String(key)}.`,
      );
    }
  }

  const report = {
    generated_at: toIsoNow(),
    vf3_chain_path: chainPath || null,
    direct_vf3_to_crea2_found: directLinkFound,
    expected_sub_additivity: EXPECTED_SUB_ADDITIVITY,
    summary: {
      checks_total: checksTotal,
      checks_passed: checksPassed,
      matrix_keys_present: matrixKeysPresent,
      pass: issues.length === 0,
    },
    issues,
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
