
import * as fs from "fs";
import * as path from "path";

const templatesDir = path.join(process.cwd(), "data/templates");

function push(map: Map<string, string[]>, key: string, file: string) {
  const existing = map.get(key) || [];
  existing.push(file);
  map.set(key, existing);
}

function report(title: string, map: Map<string, string[]>) {
  let dupCount = 0;
  console.log(`\n${title}`);
  for (const [id, files] of map.entries()) {
    if (files.length > 1) {
      console.log(`[DUPLICATE] ${id}: [${files.join(", ")}]`);
      dupCount += 1;
    }
  }
  console.log(`Duplicate groups: ${dupCount}`);
  return dupCount;
}

function checkRawDuplicates() {
  console.log("Scanning raw JSON files for duplicate display_id/template_id...");
  const files = fs.readdirSync(templatesDir).filter((f) => f.endsWith(".json"));
  const byDisplay = new Map<string, string[]>();
  const byTemplateId = new Map<string, string[]>();

  for (const file of files) {
    try {
      const content = fs.readFileSync(path.join(templatesDir, file), "utf-8");
      const json = JSON.parse(content);
      if (typeof json.display_id === "string" && json.display_id.trim()) {
        push(byDisplay, json.display_id, file);
      }
      const tid = typeof json.template_id === "string" ? json.template_id : typeof json.id === "string" ? json.id : "";
      if (tid) {
        push(byTemplateId, tid, file);
      }
    } catch (e: any) {
      console.error(`Error reading ${file}: ${e?.message || String(e)}`);
    }
  }

  const displayDupCount = report("Duplicate display_id groups", byDisplay);
  const templateDupCount = report("Duplicate template_id groups", byTemplateId);

  if (displayDupCount === 0 && templateDupCount === 0) {
    console.log("\nNo raw duplicate IDs found.");
  } else {
    process.exitCode = 1;
  }
}

checkRawDuplicates();
