#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const TEMPLATE_DIR = path.join(ROOT, 'data', 'templates');

const REQUIRED_TOP_LEVEL = [
  'template_id',
  'display_id',
  'name',
  'overall_maturity',
  'causal_links',
  'key_references',
];

const CANONICAL_MATURITY = new Set([
  'established',
  'supported',
  'preliminary',
  'theoretical',
]);

const CANONICAL_BRIDGING_QUALITY = new Set([
  'strong',
  'moderate',
  'weak',
  'speculative',
]);

const CANONICAL_LEVEL = new Set([
  'environmental',
  'sensory',
  'perceptual',
  'somatosensory',
  'motor',
  'neural',
  'subcortical',
  'interoceptive-insular',
  'neuroendocrine',
  'cognitive',
  'memorial',
  'phenomenological',
  'affective',
  'behavioral',
  'physiological',
]);

const CANONICAL_ACTIVITY = new Set([
  'enhances',
  'inhibits',
  'modulates',
]);

const CANONICAL_TOPOLOGY = new Set(['serial', 'parallel', 'hybrid']);
const CANONICAL_CONVERGENCE = new Set([
  'additive',
  'multiplicative',
  'super_additive',
  'competitive',
  'unknown',
]);

const CANONICAL_TEMPORAL_SCALE = new Set([
  'milliseconds',
  'seconds',
  'minutes',
  'hours',
  'circadian_24h',
  'days',
  'weeks',
  'months',
  'years',
  'decades',
  'centuries',
]);

const CANONICAL_TEMPORAL_VAR_TYPE = new Set([
  'state',
  'rate_of_change',
  'phase',
  'duration',
]);

function readTemplates() {
  if (!fs.existsSync(TEMPLATE_DIR)) {
    throw new Error(`Template directory not found: ${TEMPLATE_DIR}`);
  }

  return fs
    .readdirSync(TEMPLATE_DIR)
    .filter((name) => name.endsWith('.json'))
    .sort()
    .map((name) => {
      const fullPath = path.join(TEMPLATE_DIR, name);
      const raw = fs.readFileSync(fullPath, 'utf8');
      try {
        return { name, data: JSON.parse(raw) };
      } catch (err) {
        return { name, parseError: String(err) };
      }
    });
}

function addCount(map, key) {
  map.set(key, (map.get(key) || 0) + 1);
}

function toLines(title, values) {
  const lines = [`## ${title}`];
  if (values.length === 0) {
    lines.push('- none');
    return lines;
  }
  for (const value of values) {
    lines.push(`- ${value}`);
  }
  return lines;
}

function run() {
  const templates = readTemplates();

  const findings = {
    parseErrors: [],
    missingRequiredByFile: [],
    emptyCausalLinks: [],
    legacyLinkShapeByFile: [],
    canonicalLinkShapeByFile: [],
    mixedLinkShapeByFile: [],
    unknownLinkShapeByFile: [],
    invalidTopMaturity: [],
    invalidCausalTopology: [],
    invalidConvergenceRule: [],
    invalidLinkLevel: [],
    invalidLinkActivity: [],
    invalidLinkMaturity: [],
    invalidLinkBridging: [],
    invalidTemporalScale: [],
    invalidTemporalVarType: [],
  };

  const stats = {
    total: templates.length,
    legacyOnly: 0,
    canonicalOnly: 0,
    mixed: 0,
    unknown: 0,
    withNewTopologyField: 0,
    withNewTemporalField: 0,
  };

  const activityCounts = new Map();
  const levelCounts = new Map();
  const maturityCounts = new Map();
  const bridgingCounts = new Map();

  for (const entry of templates) {
    const { name, data, parseError } = entry;
    if (parseError) {
      findings.parseErrors.push(`${name}: ${parseError}`);
      continue;
    }

    const missingRequired = REQUIRED_TOP_LEVEL.filter((field) => !(field in data));
    if (missingRequired.length > 0) {
      findings.missingRequiredByFile.push(`${name}: ${missingRequired.join(', ')}`);
    }

    if (data.overall_maturity && !CANONICAL_MATURITY.has(data.overall_maturity)) {
      findings.invalidTopMaturity.push(`${name}: overall_maturity=${data.overall_maturity}`);
    }

    if (data.causal_topology !== undefined) {
      stats.withNewTopologyField += 1;
      if (!CANONICAL_TOPOLOGY.has(data.causal_topology)) {
        findings.invalidCausalTopology.push(`${name}: causal_topology=${data.causal_topology}`);
      }
    }

    if (data.convergence_rule !== undefined) {
      if (!CANONICAL_CONVERGENCE.has(data.convergence_rule)) {
        findings.invalidConvergenceRule.push(`${name}: convergence_rule=${data.convergence_rule}`);
      }
    }

    if (!Array.isArray(data.causal_links) || data.causal_links.length === 0) {
      findings.emptyCausalLinks.push(name);
      continue;
    }

    let hasLegacy = false;
    let hasCanonical = false;
    let hasUnknown = false;

    for (const [idx, link] of data.causal_links.entries()) {
      const legacyShape = Boolean(link && link.from_entity && link.to_entity && link.level);
      const canonicalShape = Boolean(link && link.from_variable && link.to_variable && link.from_level && link.to_level);

      if (legacyShape) hasLegacy = true;
      if (canonicalShape) hasCanonical = true;
      if (!legacyShape && !canonicalShape) {
        hasUnknown = true;
        findings.unknownLinkShapeByFile.push(`${name}: causal_links[${idx}] has neither legacy nor canonical shape`);
      }

      if (typeof link.activity === 'string') {
        addCount(activityCounts, link.activity);
        if (!CANONICAL_ACTIVITY.has(link.activity)) {
          findings.invalidLinkActivity.push(`${name}: causal_links[${idx}].activity=${link.activity}`);
        }
      }

      if (typeof link.level === 'string') {
        addCount(levelCounts, link.level);
        if (!CANONICAL_LEVEL.has(link.level)) {
          findings.invalidLinkLevel.push(`${name}: causal_links[${idx}].level=${link.level}`);
        }
      }

      if (typeof link.from_level === 'string') {
        addCount(levelCounts, link.from_level);
        if (!CANONICAL_LEVEL.has(link.from_level)) {
          findings.invalidLinkLevel.push(`${name}: causal_links[${idx}].from_level=${link.from_level}`);
        }
      }

      if (typeof link.to_level === 'string') {
        addCount(levelCounts, link.to_level);
        if (!CANONICAL_LEVEL.has(link.to_level)) {
          findings.invalidLinkLevel.push(`${name}: causal_links[${idx}].to_level=${link.to_level}`);
        }
      }

      if (typeof link.maturity === 'string') {
        addCount(maturityCounts, link.maturity);
        if (!CANONICAL_MATURITY.has(link.maturity)) {
          findings.invalidLinkMaturity.push(`${name}: causal_links[${idx}].maturity=${link.maturity}`);
        }
      }

      if (typeof link.bridging_quality === 'string') {
        addCount(bridgingCounts, link.bridging_quality);
        if (!CANONICAL_BRIDGING_QUALITY.has(link.bridging_quality)) {
          findings.invalidLinkBridging.push(`${name}: causal_links[${idx}].bridging_quality=${link.bridging_quality}`);
        }
      }

      if (link.temporal !== undefined) {
        stats.withNewTemporalField += 1;
        if (link.temporal && typeof link.temporal.scale === 'string' && !CANONICAL_TEMPORAL_SCALE.has(link.temporal.scale)) {
          findings.invalidTemporalScale.push(`${name}: causal_links[${idx}].temporal.scale=${link.temporal.scale}`);
        }
        if (
          link.temporal &&
          typeof link.temporal.variable_type === 'string' &&
          !CANONICAL_TEMPORAL_VAR_TYPE.has(link.temporal.variable_type)
        ) {
          findings.invalidTemporalVarType.push(`${name}: causal_links[${idx}].temporal.variable_type=${link.temporal.variable_type}`);
        }
      }
    }

    if (hasLegacy && hasCanonical) {
      stats.mixed += 1;
      findings.mixedLinkShapeByFile.push(name);
    } else if (hasLegacy) {
      stats.legacyOnly += 1;
      findings.legacyLinkShapeByFile.push(name);
    } else if (hasCanonical) {
      stats.canonicalOnly += 1;
      findings.canonicalLinkShapeByFile.push(name);
    } else if (hasUnknown) {
      stats.unknown += 1;
    }
  }

  const reportLines = [];
  reportLines.push('# CX-5 Template Contract Compatibility Report');
  reportLines.push('');
  reportLines.push(`- Scan date (UTC): ${new Date().toISOString()}`);
  reportLines.push(`- Template directory: \`data/templates\``);
  reportLines.push(`- Files scanned: **${stats.total}**`);
  reportLines.push('');
  reportLines.push('## Shape Summary');
  reportLines.push(`- Legacy-only causal link shape files: **${stats.legacyOnly}**`);
  reportLines.push(`- Canonical-only causal link shape files: **${stats.canonicalOnly}**`);
  reportLines.push(`- Mixed-shape files: **${stats.mixed}**`);
  reportLines.push(`- Unknown-shape files: **${stats.unknown}**`);
  reportLines.push(`- Files using new \`causal_topology\`: **${stats.withNewTopologyField}**`);
  reportLines.push(`- Links using new \`temporal\` metadata: **${stats.withNewTemporalField}**`);
  reportLines.push('');

  const keyFindings = [];
  if (findings.invalidTopMaturity.length > 0) {
    keyFindings.push(
      `Top-level maturity drift in ${findings.invalidTopMaturity.length} files (non-canonical values like \`how-actually\`, \`how-plausibly\`).`,
    );
  }
  if (findings.invalidLinkMaturity.length > 0) {
    keyFindings.push(
      `Link-level maturity drift in ${findings.invalidLinkMaturity.length} links (legacy maturity taxonomy).`,
    );
  }
  if (findings.invalidLinkBridging.length > 0) {
    keyFindings.push(
      `Link-level bridging-quality drift in ${findings.invalidLinkBridging.length} links (legacy values like \`HIGH\`, \`MEDIUM\`).`,
    );
  }
  if (findings.invalidLinkLevel.length > 0) {
    keyFindings.push(
      `Level drift in ${findings.invalidLinkLevel.length} entries (legacy levels like \`circuit\`, \`computational\`, \`molecular\`).`,
    );
  }
  if (findings.invalidLinkActivity.length > 0) {
    keyFindings.push(
      `Activity drift in ${findings.invalidLinkActivity.length} entries (many domain-specific verbs outside canonical activity enum).`,
    );
  }
  if (stats.withNewTopologyField === 0 && stats.withNewTemporalField === 0) {
    keyFindings.push(
      'No files yet use CX-5 Light-template extension fields (`causal_topology`, `convergence_rule`, `channel_id`, `converges_on`, `temporal.*`).',
    );
  }

  reportLines.push('## Key Gaps');
  if (keyFindings.length === 0) {
    reportLines.push('- No compatibility gaps detected.');
  } else {
    keyFindings.forEach((line) => reportLines.push(`- ${line}`));
  }
  reportLines.push('');

  const topN = (map, n = 12) =>
    Array.from(map.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, n)
      .map(([k, v]) => `${k}: ${v}`);

  reportLines.push(...toLines('Most Common Activity Values', topN(activityCounts, 15)));
  reportLines.push('');
  reportLines.push(...toLines('Most Common Level Values', topN(levelCounts, 15)));
  reportLines.push('');
  reportLines.push(...toLines('Most Common Link Maturity Values', topN(maturityCounts, 10)));
  reportLines.push('');
  reportLines.push(...toLines('Most Common Link Bridging Quality Values', topN(bridgingCounts, 10)));
  reportLines.push('');

  reportLines.push(...toLines('Files Missing Required Top-Level Fields', findings.missingRequiredByFile.slice(0, 30)));
  reportLines.push('');
  reportLines.push(...toLines('Sample Invalid Link-Level Values (first 40)', [
    ...findings.invalidLinkActivity,
    ...findings.invalidLinkLevel,
    ...findings.invalidLinkMaturity,
    ...findings.invalidLinkBridging,
  ].slice(0, 40)));

  const reportPath = path.join(ROOT, 'docs', 'cx5_template_compatibility_report.md');
  fs.writeFileSync(reportPath, reportLines.join('\n') + '\n', 'utf8');

  console.log(`Wrote compatibility report: ${path.relative(ROOT, reportPath)}`);
  console.log(`Templates scanned: ${stats.total}`);
  console.log(`Legacy-only files: ${stats.legacyOnly}`);
  console.log(`Canonical-only files: ${stats.canonicalOnly}`);
  console.log(`Mixed files: ${stats.mixed}`);
  console.log(`Unknown shape files: ${stats.unknown}`);
  console.log(`Files with new topology field: ${stats.withNewTopologyField}`);
  console.log(`Links with temporal metadata: ${stats.withNewTemporalField}`);

  const hardFailures =
    findings.parseErrors.length +
    findings.missingRequiredByFile.length +
    findings.emptyCausalLinks.length;

  if (hardFailures > 0) {
    console.error(`Hard-compat failures: ${hardFailures}`);
    process.exitCode = 1;
  }
}

run();
