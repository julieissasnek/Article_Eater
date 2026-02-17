#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const TEMPLATE_DIR = path.join(ROOT, "data", "templates");
const AUDIT_JSON = path.join(
  ROOT,
  "data",
  "review",
  "cx_v10_bidirectional_audit_2026-02-17.json",
);

const AMBIGUOUS_FIXES = [
  {
    file: "data/templates/T59.json",
    find: {
      display_id: "T27",
      template_id: "DMN_TPN_SWITCHING_001",
    },
    replace_template_id: "DT_DMN_MAINTENANCE_002",
  },
  {
    file: "data/templates/T60.json",
    find: {
      display_id: "T38",
      template_id: "COGNITIVE_LOAD_MASTER_001",
    },
    replace_template_id: "HC_HIERARCHICAL_CONTROL_002",
  },
  {
    file: "data/templates/TP1_motor_prediction_proprioceptive.json",
    find: {
      display_id: "T12",
      template_id: "INTEROCEPTIVE_AFFECT_001",
    },
    replace_template_id: "IC_INTEROCEPTIVE_AFFECT_CONSTRUCTION_001",
  },
  {
    file: "data/templates/TP1.json",
    find: {
      display_id: "T12",
      template_id: "INTEROCEPTIVE_AFFECT_001",
    },
    replace_template_id: "IC_INTEROCEPTIVE_AFFECT_CONSTRUCTION_001",
  },
];

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function detectIndent(text) {
  const m = text.match(/\n( +)"/);
  if (!m) {
    return 2;
  }
  return m[1].length;
}

function writeJson(filePath, obj, indent = 2) {
  fs.writeFileSync(filePath, `${JSON.stringify(obj, null, indent)}\n`, "utf8");
}

function parseInteractionRefs(ix) {
  const refs = { templateIds: new Set(), displayIds: new Set() };
  if (typeof ix === "string") {
    for (const m of ix.match(/\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+_\d{3}\b/g) || []) {
      refs.templateIds.add(m);
    }
    for (const m of ix.match(/\b(?:SOC|TP|SC|AX|VF|VIEW|COL|OLF|MAT|L|M|E|T)\d+\b/g) || []) {
      refs.displayIds.add(m);
    }
    return refs;
  }
  if (!ix || typeof ix !== "object") {
    return refs;
  }
  if (typeof ix.template_id === "string") {
    refs.templateIds.add(ix.template_id);
  }
  if (typeof ix.display_id === "string") {
    refs.displayIds.add(ix.display_id);
  }
  if (typeof ix.template === "string") {
    for (const m of ix.template.match(/\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+_\d{3}\b/g) || []) {
      refs.templateIds.add(m);
    }
    for (const m of ix.template.match(/\b(?:SOC|TP|SC|AX|VF|VIEW|COL|OLF|MAT|L|M|E|T)\d+\b/g) || []) {
      refs.displayIds.add(m);
    }
  }
  return refs;
}

function hasInteraction(interactions, sourceTemplateId, sourceDisplayId) {
  for (const ix of interactions || []) {
    const refs = parseInteractionRefs(ix);
    if (refs.templateIds.has(sourceTemplateId) || refs.displayIds.has(sourceDisplayId)) {
      return true;
    }
  }
  return false;
}

function applyAmbiguousIdFixes() {
  let changed = 0;
  for (const fix of AMBIGUOUS_FIXES) {
    const fullPath = path.join(ROOT, fix.file);
    if (!fs.existsSync(fullPath)) {
      continue;
    }
    const raw = fs.readFileSync(fullPath, "utf8");
    const indent = detectIndent(raw);
    const doc = JSON.parse(raw);
    if (!Array.isArray(doc.interactions)) {
      continue;
    }
    let localChanged = false;
    for (const ix of doc.interactions) {
      if (!ix || typeof ix !== "object") {
        continue;
      }
      if (
        ix.display_id === fix.find.display_id &&
        ix.template_id === fix.find.template_id
      ) {
        ix.template_id = fix.replace_template_id;
        localChanged = true;
      }
    }
    if (localChanged) {
      writeJson(fullPath, doc, indent);
      changed += 1;
      console.log(`fixed ambiguous reference in ${fix.file}`);
    }
  }
  return changed;
}

function applyReverseLinksFromAudit() {
  const audit = readJson(AUDIT_JSON);
  const missing = Array.isArray(audit.missing_reverse_links)
    ? audit.missing_reverse_links
    : [];
  let filesChanged = 0;
  let linksAdded = 0;

  const byTarget = new Map();
  for (const row of missing) {
    if (!row.target_file) {
      continue;
    }
    if (!byTarget.has(row.target_file)) {
      byTarget.set(row.target_file, []);
    }
    byTarget.get(row.target_file).push(row);
  }

  for (const [targetFile, rows] of byTarget.entries()) {
    const fullPath = path.join(TEMPLATE_DIR, targetFile);
    if (!fs.existsSync(fullPath)) {
      continue;
    }
    const raw = fs.readFileSync(fullPath, "utf8");
    const indent = detectIndent(raw);
    const doc = JSON.parse(raw);
    if (!Array.isArray(doc.interactions)) {
      doc.interactions = [];
    }
    let touched = false;
    for (const row of rows) {
      if (
        hasInteraction(
          doc.interactions,
          row.source_template_id,
          row.source_display_id,
        )
      ) {
        continue;
      }
      doc.interactions.push({
        template_id: row.source_template_id,
        display_id: row.source_display_id,
        nature:
          "Reverse link added by CX V10 S4 remediation to satisfy bidirectional interaction encoding.",
      });
      linksAdded += 1;
      touched = true;
    }
    if (touched) {
      writeJson(fullPath, doc, indent);
      filesChanged += 1;
      console.log(`added reverse links in data/templates/${targetFile}`);
    }
  }
  return { filesChanged, linksAdded };
}

function main() {
  const fixesChanged = applyAmbiguousIdFixes();
  const { filesChanged, linksAdded } = applyReverseLinksFromAudit();
  console.log(
    `summary: ambiguous_fix_files=${fixesChanged}, reverse_link_files=${filesChanged}, reverse_links_added=${linksAdded}`,
  );
}

main();
