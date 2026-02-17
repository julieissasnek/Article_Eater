#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const TEMPLATE_DIR = path.join(ROOT, "data", "templates");
const DEFAULT_MD_OUT = path.join(
  ROOT,
  "docs",
  "cx_v10_bidirectional_audit_report_2026-02-17.md",
);
const DEFAULT_JSON_OUT = path.join(
  ROOT,
  "data",
  "review",
  "cx_v10_bidirectional_audit_2026-02-17.json",
);

// Source template set derived from Docs 55, 56, and 57.
const SOURCE_TEMPLATE_IDS = [
  "CROSS_CREATIVE_NETWORK_DYNAMICS_001",
  "CROSS_ENVIRONMENTAL_PROCESSING_STYLE_001",
  "CROSS_INCUBATION_ARCHITECTURE_001",
  "MOTOR_PREDICTION_ARCH_001",
  "THRESHOLD_EPISODIC_BOUNDARY_001",
  "MATERIAL_AGING_TEMPORAL_DEPTH_001",
  "TEMPORAL_HIERARCHY_ARCH_PE_001",
  "PROXEMIC_PE_ARCH_001",
  "PRIVACY_GRADIENT_REGULATION_001",
  "TERRITORIAL_AFFORDANCE_SOCIAL_001",
];

function ensureDirFor(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function toIsoNow() {
  return new Date().toISOString();
}

function readTemplates() {
  const files = fs
    .readdirSync(TEMPLATE_DIR)
    .filter((f) => f.endsWith(".json"))
    .sort();

  const templates = [];
  for (const name of files) {
    const fullPath = path.join(TEMPLATE_DIR, name);
    const raw = fs.readFileSync(fullPath, "utf8");
    let data;
    try {
      data = JSON.parse(raw);
    } catch {
      continue;
    }
    templates.push({
      file: name,
      data,
      templateId: data.template_id || data.id || null,
      displayId: data.display_id || null,
    });
  }
  return templates;
}

function getDisplayIdCandidates(text) {
  if (typeof text !== "string") {
    return [];
  }
  const matches = text.match(/\b(?:SOC|TP|SC|AX|VF|VIEW|COL|OLF|MAT|L|M|E|T)\d+\b/g);
  return matches ? [...new Set(matches)] : [];
}

function getTemplateIdCandidates(text) {
  if (typeof text !== "string") {
    return [];
  }
  const matches = text.match(/\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+_\d{3}\b/g);
  return matches ? [...new Set(matches)] : [];
}

function parseInteractionRefs(interaction) {
  const refs = [];
  if (typeof interaction === "string") {
    const templateIds = getTemplateIdCandidates(interaction);
    const displayIds = getDisplayIdCandidates(interaction);
    if (templateIds.length === 0 && displayIds.length === 0) {
      return refs;
    }
    refs.push({
      templateIds,
      displayIds,
      raw: interaction,
    });
    return refs;
  }

  if (!interaction || typeof interaction !== "object") {
    return refs;
  }

  const templateIds = [];
  const displayIds = [];

  if (typeof interaction.template_id === "string") {
    templateIds.push(interaction.template_id);
  }
  if (typeof interaction.display_id === "string") {
    displayIds.push(interaction.display_id);
  }
  if (typeof interaction.template === "string") {
    templateIds.push(...getTemplateIdCandidates(interaction.template));
    displayIds.push(...getDisplayIdCandidates(interaction.template));
  }

  if (templateIds.length > 0 || displayIds.length > 0) {
    refs.push({
      templateIds: [...new Set(templateIds)],
      displayIds: [...new Set(displayIds)],
      raw: interaction,
    });
  }
  return refs;
}

function resolveTarget(ref, byTemplateId, byDisplayId) {
  for (const tid of ref.templateIds) {
    const t = byTemplateId.get(tid);
    if (t) {
      return { target: t, reason: null };
    }
  }
  for (const did of ref.displayIds) {
    const arr = byDisplayId.get(did);
    if (!arr || arr.length === 0) {
      continue;
    }
    if (arr.length === 1) {
      return { target: arr[0], reason: null };
    }
    return {
      target: null,
      reason: `ambiguous display_id '${did}' resolves to ${arr.length} templates`,
    };
  }
  if (ref.templateIds.length > 0) {
    return {
      target: null,
      reason: `no template_id match for ${JSON.stringify(ref.templateIds)}`,
    };
  }
  return { target: null, reason: "no target match from parsed references" };
}

function hasReverseLink(targetTemplate, sourceTemplate, byTemplateId, byDisplayId) {
  const interactions = Array.isArray(targetTemplate.data.interactions)
    ? targetTemplate.data.interactions
    : [];
  for (const ix of interactions) {
    const refs = parseInteractionRefs(ix);
    for (const ref of refs) {
      if (sourceTemplate.templateId && ref.templateIds.includes(sourceTemplate.templateId)) {
        return true;
      }
      if (sourceTemplate.displayId && ref.displayIds.includes(sourceTemplate.displayId)) {
        return true;
      }

      const { target: resolved } = resolveTarget(ref, byTemplateId, byDisplayId);
      if (!resolved) {
        continue;
      }
      if (
        sourceTemplate.templateId &&
        resolved.templateId &&
        resolved.templateId === sourceTemplate.templateId
      ) {
        return true;
      }
      if (
        sourceTemplate.displayId &&
        resolved.displayId &&
        resolved.displayId === sourceTemplate.displayId
      ) {
        return true;
      }
    }
  }
  return false;
}

function main() {
  const mdOut = process.argv[2] || DEFAULT_MD_OUT;
  const jsonOut = process.argv[3] || DEFAULT_JSON_OUT;

  const templates = readTemplates();
  const byTemplateId = new Map();
  const byDisplayId = new Map();
  for (const t of templates) {
    if (t.templateId) {
      byTemplateId.set(t.templateId, t);
    }
    if (t.displayId) {
      if (!byDisplayId.has(t.displayId)) {
        byDisplayId.set(t.displayId, []);
      }
      byDisplayId.get(t.displayId).push(t);
    }
  }

  const missingSourceTemplates = [];
  const unresolvedTargets = [];
  const missingReverseLinks = [];
  const reciprocalLinks = [];

  let sourceTemplatesFound = 0;
  let sourceEdgesScanned = 0;

  for (const sourceId of SOURCE_TEMPLATE_IDS) {
    const source = byTemplateId.get(sourceId);
    if (!source) {
      missingSourceTemplates.push(sourceId);
      continue;
    }
    sourceTemplatesFound += 1;

    const interactions = Array.isArray(source.data.interactions)
      ? source.data.interactions
      : [];
    for (let idx = 0; idx < interactions.length; idx += 1) {
      const ix = interactions[idx];
      const refs = parseInteractionRefs(ix);
      if (refs.length === 0) {
        unresolvedTargets.push({
          source_template_id: source.templateId,
          source_display_id: source.displayId,
          source_file: source.file,
          interaction_index: idx,
          reason: "interaction has no parseable template/display reference",
        });
        continue;
      }

      for (const ref of refs) {
        const { target, reason } = resolveTarget(ref, byTemplateId, byDisplayId);
        sourceEdgesScanned += 1;
        if (!target) {
          unresolvedTargets.push({
            source_template_id: source.templateId,
            source_display_id: source.displayId,
            source_file: source.file,
            interaction_index: idx,
            reason: reason || "target template could not be resolved",
            parsed_template_ids: ref.templateIds,
            parsed_display_ids: ref.displayIds,
          });
          continue;
        }

        const isReciprocal = hasReverseLink(target, source, byTemplateId, byDisplayId);
        if (isReciprocal) {
          reciprocalLinks.push({
            source_template_id: source.templateId,
            source_display_id: source.displayId,
            target_template_id: target.templateId,
            target_display_id: target.displayId,
          });
        } else {
          missingReverseLinks.push({
            source_template_id: source.templateId,
            source_display_id: source.displayId,
            source_file: source.file,
            target_template_id: target.templateId,
            target_display_id: target.displayId,
            target_file: target.file,
          });
        }
      }
    }
  }

  const report = {
    generated_at: toIsoNow(),
    source_scope: {
      docs: ["55", "56", "57"],
      source_template_ids: SOURCE_TEMPLATE_IDS,
      source_templates_found: sourceTemplatesFound,
      source_templates_missing: missingSourceTemplates,
    },
    summary: {
      source_edges_scanned: sourceEdgesScanned,
      reciprocal_links: reciprocalLinks.length,
      missing_reverse_links: missingReverseLinks.length,
      unresolved_targets: unresolvedTargets.length,
    },
    missing_reverse_links: missingReverseLinks,
    unresolved_targets: unresolvedTargets,
  };

  const md = [];
  md.push("# CX V10 Bidirectional Interaction Audit");
  md.push("");
  md.push(`- Generated: ${report.generated_at}`);
  md.push("- Source docs: 55 (CREA-I), 56 (TP-II), 57 (SOC-II)");
  md.push(`- Source templates found: ${sourceTemplatesFound}/${SOURCE_TEMPLATE_IDS.length}`);
  md.push(`- Source edges scanned: ${report.summary.source_edges_scanned}`);
  md.push(`- Reciprocal links: ${report.summary.reciprocal_links}`);
  md.push(`- Missing reverse links: ${report.summary.missing_reverse_links}`);
  md.push(`- Unresolved targets: ${report.summary.unresolved_targets}`);
  md.push("");

  if (missingSourceTemplates.length > 0) {
    md.push("## Missing Source Templates");
    md.push("");
    for (const tid of missingSourceTemplates) {
      md.push(`- ${tid}`);
    }
    md.push("");
  }

  if (missingReverseLinks.length > 0) {
    md.push("## Missing Reverse Links");
    md.push("");
    md.push("| Source | Target | Source File | Target File |");
    md.push("|---|---|---|---|");
    for (const row of missingReverseLinks) {
      const source = `${row.source_display_id || "n/a"} (${row.source_template_id || "n/a"})`;
      const target = `${row.target_display_id || "n/a"} (${row.target_template_id || "n/a"})`;
      md.push(`| ${source} | ${target} | \`${row.source_file}\` | \`${row.target_file}\` |`);
    }
    md.push("");
  }

  if (unresolvedTargets.length > 0) {
    md.push("## Unresolved References");
    md.push("");
    for (const row of unresolvedTargets) {
      md.push(
        `- ${row.source_display_id || "n/a"} (${row.source_template_id || "n/a"}) ` +
          `interaction[${row.interaction_index}] in \`${row.source_file}\`: ${row.reason}.`,
      );
    }
    md.push("");
  }

  md.push("## Artifacts");
  md.push("");
  md.push(`- JSON: \`${path.relative(ROOT, jsonOut)}\``);
  md.push(`- Markdown: \`${path.relative(ROOT, mdOut)}\``);
  md.push("");

  ensureDirFor(jsonOut);
  ensureDirFor(mdOut);
  fs.writeFileSync(jsonOut, JSON.stringify(report, null, 2) + "\n", "utf8");
  fs.writeFileSync(mdOut, md.join("\n") + "\n", "utf8");

  console.log(`Wrote ${path.relative(ROOT, jsonOut)}`);
  console.log(`Wrote ${path.relative(ROOT, mdOut)}`);
  console.log(
    `Summary: edges=${report.summary.source_edges_scanned}, reciprocal=${report.summary.reciprocal_links}, missing_reverse=${report.summary.missing_reverse_links}, unresolved=${report.summary.unresolved_targets}`,
  );
}

main();
