#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const TEMPLATE_DIR = path.join(ROOT, 'data', 'templates');

const VALID_LEVEL = new Set([
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

const VALID_TOPOLOGY = new Set(['serial', 'parallel', 'hybrid']);
const VALID_CONVERGENCE = new Set([
  'additive',
  'multiplicative',
  'super_additive',
  'competitive',
  'unknown',
]);
const VALID_TEMPORAL_SCALE = new Set([
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
const VALID_TEMPORAL_VAR_TYPE = new Set([
  'state',
  'rate_of_change',
  'phase',
  'duration',
]);

function templateFiles() {
  if (!fs.existsSync(TEMPLATE_DIR)) {
    throw new Error(`Missing template directory: ${TEMPLATE_DIR}`);
  }
  return fs.readdirSync(TEMPLATE_DIR).filter((f) => f.endsWith('.json')).sort();
}

function main() {
  const files = templateFiles();
  const errors = [];

  let usesSubcortical = 0;
  let usesNeuroendocrine = 0;
  let usesTopology = 0;
  let usesConvergence = 0;
  let usesTemporal = 0;
  let checksRunOnCanonicalLevelFields = 0;

  for (const name of files) {
    const full = path.join(TEMPLATE_DIR, name);
    const obj = JSON.parse(fs.readFileSync(full, 'utf8'));

    if (obj.causal_topology !== undefined) {
      usesTopology += 1;
      if (!VALID_TOPOLOGY.has(obj.causal_topology)) {
        errors.push(`${name}: invalid causal_topology=${obj.causal_topology}`);
      }
    }

    if (obj.convergence_rule !== undefined) {
      usesConvergence += 1;
      if (!VALID_CONVERGENCE.has(obj.convergence_rule)) {
        errors.push(`${name}: invalid convergence_rule=${obj.convergence_rule}`);
      }
    }

    const links = Array.isArray(obj.causal_links) ? obj.causal_links : [];
    links.forEach((link, idx) => {
      ['from_level', 'to_level'].forEach((field) => {
        if (typeof link[field] === 'string') {
          checksRunOnCanonicalLevelFields += 1;
          const value = link[field];
          if (value === 'subcortical') usesSubcortical += 1;
          if (value === 'neuroendocrine') usesNeuroendocrine += 1;
          if (!VALID_LEVEL.has(value)) {
            errors.push(`${name}: causal_links[${idx}].${field} invalid level=${value}`);
          }
        }
      });

      if (link.temporal !== undefined) {
        usesTemporal += 1;
        if (typeof link.temporal.scale === 'string' && !VALID_TEMPORAL_SCALE.has(link.temporal.scale)) {
          errors.push(`${name}: causal_links[${idx}].temporal.scale invalid=${link.temporal.scale}`);
        }
        if (
          typeof link.temporal.variable_type === 'string' &&
          !VALID_TEMPORAL_VAR_TYPE.has(link.temporal.variable_type)
        ) {
          errors.push(`${name}: causal_links[${idx}].temporal.variable_type invalid=${link.temporal.variable_type}`);
        }
      }
    });
  }

  console.log(`Scanned ${files.length} template files.`);
  console.log(
    `Usage: subcortical=${usesSubcortical}, neuroendocrine=${usesNeuroendocrine}, topology=${usesTopology}, convergence=${usesConvergence}, temporal=${usesTemporal}`,
  );
  console.log(`Canonical level field checks run: ${checksRunOnCanonicalLevelFields}`);

  if (errors.length > 0) {
    console.error('Enum drift detected:');
    errors.slice(0, 200).forEach((err) => console.error(`- ${err}`));
    if (errors.length > 200) {
      console.error(`... ${errors.length - 200} additional errors`);
    }
    process.exit(1);
  }

  console.log('No enum drift detected for CX-5 extension fields.');

  if (usesTopology === 0 && usesTemporal === 0) {
    console.log('Note: no templates currently use the new CX-5 extension fields yet.');
  }
}

main();
