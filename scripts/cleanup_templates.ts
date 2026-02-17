
import * as fs from "fs";
import * as path from "path";

const templatesDir = path.join(process.cwd(), "data/templates");
const apply = process.argv.includes("--apply");
const now = new Date().toISOString().replace(/[:.]/g, "-");
const archiveDir = path.join(process.cwd(), "_archive", "template_hygiene", now);

type Rec = {
  file: string;
  fullPath: string;
  json: any;
  raw: string;
  displayId: string | null;
  templateId: string | null;
};

const REQUIRED_V14 = [
  "age_band_modifiers",
  "vulnerability_index",
  "universal_design_thresholds",
  "challenge_gradient_available",
  "lifespan_sensitivity_multiplier",
  "developmental_challenge_benefit",
  "context_modes",
];

const PREFERRED_DISPLAY_IDS = new Set([
  "L3",
  "L4",
  "MAT1",
  "MAT3",
  "MAT4",
  "MAT5",
  "VIEW1",
  "TP1",
  "TP2",
  "SOC1",
  "SOC2",
  "CREA3",
]);

function hasV14(r: Rec): boolean {
  return REQUIRED_V14.every((k) => k in r.json);
}

function readTemplates(): Rec[] {
  return fs
    .readdirSync(templatesDir)
    .filter((f) => f.endsWith(".json"))
    .sort()
    .map((file) => {
      const fullPath = path.join(templatesDir, file);
      const raw = fs.readFileSync(fullPath, "utf-8");
      const json = JSON.parse(raw);
      const templateId =
        typeof json.template_id === "string"
          ? json.template_id
          : typeof json.id === "string"
          ? json.id
          : null;
      return {
        file,
        fullPath,
        json,
        raw,
        displayId: typeof json.display_id === "string" ? json.display_id : null,
        templateId,
      };
    });
}

function groupBy(records: Rec[], field: "displayId" | "templateId"): Map<string, Rec[]> {
  const m = new Map<string, Rec[]>();
  for (const r of records) {
    const v = r[field];
    if (!v) continue;
    const arr = m.get(v) || [];
    arr.push(r);
    m.set(v, arr);
  }
  return m;
}

function score(r: Rec): number {
  let s = 0;
  if (r.displayId && PREFERRED_DISPLAY_IDS.has(r.displayId)) s += 400;
  if (r.displayId && r.file === `${r.displayId}.json`) s += 1000;
  if (/^[A-Z]+\d+\.json$/.test(r.file)) s += 100;
  if (hasV14(r)) s += 20;
  if (!r.file.includes("_")) s += 5;
  s -= Math.floor(r.file.length / 8);
  return s;
}

function pickKeeper(records: Rec[]): Rec {
  return [...records].sort((a, b) => {
    const ds = score(b) - score(a);
    if (ds !== 0) return ds;
    return a.file.localeCompare(b.file);
  })[0];
}

function archiveAndRemove(file: string) {
  const src = path.join(templatesDir, file);
  const dst = path.join(archiveDir, file);
  fs.mkdirSync(path.dirname(dst), { recursive: true });
  fs.renameSync(src, dst);
}

function main() {
  console.log("Starting Template Deduplication...");
  console.log(`Mode: ${apply ? "APPLY" : "DRY-RUN"} (${apply ? "files will be moved to archive" : "no changes"})`);
  if (apply) {
    fs.mkdirSync(archiveDir, { recursive: true });
    console.log(`Archive dir: ${path.relative(process.cwd(), archiveDir)}`);
  }

  const records = readTemplates();
  const byDisplay = groupBy(records, "displayId");
  const byTemplate = groupBy(records, "templateId");
  const losers = new Set<string>();
  const renames: Array<{ from: string; to: string }> = [];

  for (const [displayId, group] of byDisplay.entries()) {
    if (group.length < 2) continue;
    const active = group.filter((r) => !losers.has(r.file));
    if (active.length < 2) continue;
    const keeper = pickKeeper(active);
    console.log(`\n[display_id=${displayId}] keep ${keeper.file}`);
    for (const r of active) {
      if (r.file !== keeper.file) {
        losers.add(r.file);
        console.log(`  archive/remove ${r.file}`);
      }
    }
  }

  for (const [templateId, group] of byTemplate.entries()) {
    if (group.length < 2) continue;
    const active = group.filter((r) => !losers.has(r.file));
    if (active.length < 2) continue;
    const keeper = pickKeeper(active);
    console.log(`\n[template_id=${templateId}] keep ${keeper.file}`);
    for (const r of active) {
      if (r.file !== keeper.file) {
        losers.add(r.file);
        console.log(`  archive/remove ${r.file}`);
      }
    }
  }

  for (const displayId of ["COL1", "COL2"]) {
    const group = (byDisplay.get(displayId) || []).filter((r) => !losers.has(r.file));
    if (group.length !== 1) continue;
    const current = group[0].file;
    const target = `${displayId}.json`;
    if (current !== target && !fs.existsSync(path.join(templatesDir, target))) {
      renames.push({ from: current, to: target });
      console.log(`\n[standardize] ${current} -> ${target}`);
    }
  }

  if (!apply) {
    console.log(`\nSummary (dry-run): archive/remove ${losers.size}, rename ${renames.length}`);
    console.log("Re-run with --apply to execute.");
    return;
  }

  let removed = 0;
  for (const file of losers) {
    if (fs.existsSync(path.join(templatesDir, file))) {
      archiveAndRemove(file);
      removed += 1;
    }
  }

  let renamed = 0;
  for (const r of renames) {
    const src = path.join(templatesDir, r.from);
    const dst = path.join(templatesDir, r.to);
    if (fs.existsSync(src) && !fs.existsSync(dst)) {
      fs.renameSync(src, dst);
      renamed += 1;
    }
  }

  console.log(`\nSummary: archived/removed ${removed} files, renamed ${renamed} files.`);
}

main();
