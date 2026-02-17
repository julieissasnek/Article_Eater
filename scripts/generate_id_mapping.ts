
import * as fs from 'fs';
import * as path from 'path';

const TEMPLATES_DIR = path.join(process.cwd(), 'data', 'templates');
const OUTPUT_FILE = path.join(process.cwd(), 'docs', 'template_id_mapping_master.json');

interface TemplateMinimal {
    template_id: string;
    display_id: string;
    id?: string; // For new ones that use id as template_id
}

async function generateMapping() {
    console.log(`Scanning templates in ${TEMPLATES_DIR}...`);

    if (!fs.existsSync(TEMPLATES_DIR)) {
        console.error(`Directory not found: ${TEMPLATES_DIR}`);
        process.exit(1);
    }

    const files = fs.readdirSync(TEMPLATES_DIR).filter(f => f.endsWith('.json'));
    const mapping: Record<string, string> = {};
    const conflictLog: string[] = [];

    files.forEach(file => {
        try {
            const content = fs.readFileSync(path.join(TEMPLATES_DIR, file), 'utf-8');
            const data = JSON.parse(content) as TemplateMinimal;

            // Handle ID aliasing: new files use 'id' as 'template_id'
            const longId = data.template_id || data.id;
            const shortId = data.display_id;

            if (!longId || !shortId) {
                console.warn(`Skipping ${file}: Missing template_id/id or display_id`);
                return;
            }

            if (mapping[shortId] && mapping[shortId] !== longId) {
                conflictLog.push(`CONFLICT: Short ID ${shortId} maps to both ${mapping[shortId]} and ${longId}`);
            } else {
                mapping[shortId] = longId;
            }

        } catch (err) {
            console.error(`Error processing ${file}:`, err);
        }
    });

    // Also ingest from docs/template_id_aliases.json to catch templates without files
    const ALIASES_FILE = path.join(process.cwd(), 'docs', 'template_id_aliases.json');
    if (fs.existsSync(ALIASES_FILE)) {
        console.log(`Loading aliases from ${ALIASES_FILE}...`);
        try {
            const aliases = JSON.parse(fs.readFileSync(ALIASES_FILE, 'utf-8'));
            aliases.forEach((a: any) => {
                // Construct Short ID from number? e.g. T45
                // alias entries have "id" (Long) and "number" (Int).
                // They don't explicitly list "T45" as a display_id usually, but let's assume T{number}.
                const shortId = `T${a.number}`;
                const longId = a.id;

                if (!mapping[shortId]) {
                    mapping[shortId] = longId;
                    // console.log(`Added missing mapping: ${shortId} -> ${longId}`);
                }
            });
        } catch (err) {
            console.error("Error reading aliases:", err);
        }
    }

    if (conflictLog.length > 0) {
        console.error("Conflicts found:");
        conflictLog.forEach(c => console.error(c));
        // We might want to abort, but for now let's write what we have
    }

    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(mapping, null, 2));
    console.log(`Mapping generated with ${Object.keys(mapping).length} entries.`);
    console.log(`Saved to ${OUTPUT_FILE}`);
}

generateMapping().catch(console.error);
