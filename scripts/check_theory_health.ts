
import { TheoryAPI } from '../src/api/index';
import { Template } from '../src/types/template';

async function checkHealth() {
    console.log("Starting Theory Health Check...");
    const api = new TheoryAPI();
    await api.initialize();
    const templates = api.getAllTemplates();

    const errors: string[] = [];
    const warnings: string[] = [];

    const templateIds = new Set(templates.map(t => t.template_id));
    const displayIds = new Set(templates.map(t => t.display_id));

    // 1. Check Interaction Integrity
    console.log("\nChecking Interaction Integrity...");
    templates.forEach(t => {
        if (t.interactions) {
            t.interactions.forEach(targetId => {
                let targetStr = "";
                if (typeof targetId === 'string') {
                    targetStr = targetId;
                } else if (typeof targetId === 'object' && targetId.template) {
                    targetStr = targetId.template;
                }

                if (!targetStr) return;

                // Extract potential ID from string (e.g., "T38 (CROSS_COGNITIVE_LOAD_001)")
                const match = targetStr.match(/(T\d+|[A-Z_]+_\d+)/);
                if (match) {
                    const extracted = match[0];
                    // Check if extracted matches a display_id or template_id
                    if (!templateIds.has(extracted) && !displayIds.has(extracted)) {
                        // It might be a valid ID but text is "T46 (THALAMIC_FILTER)" - we need to see if T46 exists
                        // If "T46" exists in displayIds, it is valid.
                        if (!displayIds.has(extracted) && !templateIds.has(extracted)) {
                            warnings.push(`[${t.display_id}] References unknown template in interaction: "${targetStr}" (extracted: ${extracted})`);
                        }
                    }
                } else {
                    // If we can't extract an ID, is it a raw ID?
                    if (!templateIds.has(targetStr) && !displayIds.has(targetStr)) {
                        warnings.push(`[${t.display_id}] Unresolvable interaction reference: "${targetStr}"`);
                    }
                }
            });
        }
    });

    // 2. Check Variable Consistency (Typos)
    console.log("\nChecking Variable Consistency...");
    const variables = new Map<string, number>();
    templates.forEach(t => {
        t.causal_links.forEach(link => {
            if (link.from_entity) variables.set(link.from_entity, (variables.get(link.from_entity) || 0) + 1);
            if (link.to_entity) variables.set(link.to_entity, (variables.get(link.to_entity) || 0) + 1);
        });
    });

    // Find singleton variables (used only once) - potential typos
    const singletons = Array.from(variables.entries()).filter(([v, count]) => count === 1).map(x => x[0]);
    if (singletons.length > 0) {
        console.log(`Found ${singletons.length} variables used only once (potential typos or isolates). Top 10:`);
        singletons.slice(0, 10).forEach(v => console.log(`- ${v}`));
    }

    // 3. Validation of short_description existence
    console.log("\nChecking Schema Completeness...");
    let missingDesc = 0;
    templates.forEach(t => {
        if (!t.short_description) {
            missingDesc++;
            // Uncomment to see which ones
            // console.log(`- Missing short_description: ${t.display_id}`);
        }
    });
    console.log(`Templates missing 'short_description': ${missingDesc} / ${templates.length}`);

    // Summary
    console.log("\n--- Health Check Summary ---");
    console.log(`Errors: ${errors.length}`);
    console.log(`Warnings: ${warnings.length}`);

    if (warnings.length > 0) {
        console.log("\nWarnings Details:");
        warnings.forEach(w => console.log(w));
    }

    if (errors.length > 0) {
        process.exit(1);
    }
}

checkHealth().catch(console.error);
