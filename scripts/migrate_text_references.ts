
import * as fs from 'fs';
import * as path from 'path';

const DATA_DIR = path.join(process.cwd(), 'data');
const MAPPING_FILE = path.join(process.cwd(), 'docs', 'template_id_mapping_master.json');

async function migrate() {
    console.log("Starting Short ID -> Long ID Migration (v2)...");

    if (!fs.existsSync(MAPPING_FILE)) {
        console.error("Mapping file not found.");
        process.exit(1);
    }

    const mapping = JSON.parse(fs.readFileSync(MAPPING_FILE, 'utf-8')) as Record<string, string>;
    console.log(`Loaded ${Object.keys(mapping).length} ID mappings.`);

    // Recursively find all JSON files in data/
    const getAllFiles = (dir: string, files: string[] = []) => {
        fs.readdirSync(dir).forEach(file => {
            const fullPath = path.join(dir, file);
            if (fs.statSync(fullPath).isDirectory()) {
                getAllFiles(fullPath, files);
            } else if (file.endsWith('.json')) {
                files.push(fullPath);
            }
        });
        return files;
    };

    const files = getAllFiles(DATA_DIR);
    console.log(`Found ${files.length} JSON files to scan.`);

    let totalReplacements = 0;
    let filesModified = 0;

    files.forEach(file => {
        let content = fs.readFileSync(file, 'utf-8');
        let modified = false;

        // 1. Rename "id" -> "template_id" in Template files if mapping matches
        // Only valid for files in data/templates/
        if (file.includes('/data/templates/')) {
            for (const longId of Object.values(mapping)) {
                // Match "id": "LONG_ID"
                // Use regex strictness to avoid partial matches
                const regexKey = new RegExp(`"id"\\s*:\\s*"${longId}"`);
                if (regexKey.test(content)) {
                    content = content.replace(regexKey, `"template_id": "${longId}"`);
                    modified = true;
                    console.log(`[${path.basename(file)}] Renamed 'id' to 'template_id' for ${longId}`);
                }
            }
        }

        // 2. Replace Short IDs with Long IDs in reference fields
        for (const [shortId, longId] of Object.entries(mapping)) {
            // Field: "template_id"
            const regexId = new RegExp(`("template_id"\\s*:\\s*)"${shortId}"`, 'g');
            if (regexId.test(content)) {
                content = content.replace(regexId, `$1"${longId}"`);
                modified = true;
                totalReplacements++;
            }

            // Field: "template_link" (used in MAT4)
            const regexLink = new RegExp(`("template_link"\\s*:\\s*)"${shortId}"`, 'g');
            if (regexLink.test(content)) {
                content = content.replace(regexLink, `$1"${longId}"`);
                modified = true;
                totalReplacements++;
            }
        }

        if (modified) {
            fs.writeFileSync(file, content);
            filesModified++;
        }
    });

    console.log(`Migration Complete.`);
    console.log(`Modified ${filesModified} files.`);
    console.log(`Total replacements: ${totalReplacements}`);
}

migrate().catch(console.error);
