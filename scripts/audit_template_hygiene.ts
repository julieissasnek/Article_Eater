
import * as fs from "fs";
import * as path from "path";

const templatesDir = path.join(process.cwd(), "data/templates");

const REQUIRED_V14_FIELDS = [
  "age_band_modifiers",
  "vulnerability_index",
  "universal_design_thresholds",
  "challenge_gradient_available",
  "lifespan_sensitivity_multiplier",
  "developmental_challenge_benefit",
  "context_modes",
];

type TemplateRec = {
  file: string;
  displayId: string | null;
  templateId: string | null;
  json: any;
};

function loadRawTemplates(): TemplateRec[] {
  return fs
    .readdirSync(templatesDir)
    .filter((f) => f.endsWith(".json"))
    .sort()
    .map((file) => {
      const json = JSON.parse(fs.readFileSync(path.join(templatesDir, file), "utf8"));
      const templateId =
        typeof json.template_id === "string"
          ? json.template_id
          : typeof json.id === "string"
          ? json.id
          : null;
      return {
        file,
        displayId: typeof json.display_id === "string" ? json.display_id : null,
        templateId,
        json,
      };
    });
}

function findDuplicates(records: TemplateRec[], key: "displayId" | "templateId") {
  const m = new Map<string, string[]>();
  for (const r of records) {
    const v = r[key];
    if (!v) continue;
    const arr = m.get(v) || [];
    arr.push(r.file);
    m.set(v, arr);
  }
  return [...m.entries()].filter(([, files]) => files.length > 1);
}

function main() {
  console.log("Starting Template Hygiene Audit...");
  const records = loadRawTemplates();
  console.log(`Scanned ${records.length} raw template files.`);

  const displayDups = findDuplicates(records, "displayId");
  const templateDups = findDuplicates(records, "templateId");

  console.log("\n--- Duplicate ID Check ---");
  console.log(`Duplicate display_id groups: ${displayDups.length}`);
  for (const [id, files] of displayDups) {
    console.log(`[DUPLICATE display_id] ${id}: ${files.join(", ")}`);
  }
  console.log(`Duplicate template_id groups: ${templateDups.length}`);
  for (const [id, files] of templateDups) {
    console.log(`[DUPLICATE template_id] ${id}: ${files.join(", ")}`);
  }

  console.log("\n--- V14 Lifespan Field Check ---");
  let missingCount = 0;
  for (const r of records) {
    const missing = REQUIRED_V14_FIELDS.filter((f) => !(f in r.json));
    if (missing.length > 0) {
      console.log(`[MISSING V14] ${r.file}: ${missing.join(", ")}`);
      missingCount += 1;
    }
  }
  if (missingCount === 0) {
    console.log("All templates have required V14 fields.");
  } else {
    console.log(`Templates missing V14 fields: ${missingCount}`);
  }

  const pass = displayDups.length === 0 && templateDups.length === 0 && missingCount === 0;
  console.log("\n--- Summary ---");
  console.log(`Pass: ${pass}`);
  if (!pass) {
    process.exit(1);
  }
}

main();
