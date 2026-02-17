
import { TheoryAPI } from '../src/api/index';

/**
 * CI Drift Check Script
 * Enforces referential integrity and data validity.
 * Exit code 1 on any failure.
 */
async function runDriftCheck() {
    console.log("Starting Theory Drift Check (CI Mode)...");

    const api = new TheoryAPI();
    await api.initialize();

    const errors: string[] = [];

    // Data Loading
    const templates = api.getAllTemplates();
    const reductions = api.getAllReductions();
    const domains = api.getAllAttributeDomains();

    console.log(`Checking ${templates.length} templates...`);
    console.log(`Checking ${reductions.length} reductions...`);
    console.log(`Checking ${domains.length} domains...`);

    // 1. Template Integrity
    const templateIds = new Set(templates.map(t => t.template_id));
    templates.forEach(t => {
        if (!t.template_id) errors.push(`Template missing ID: ${t.name}`);
        if (!t.overall_maturity) errors.push(`Template ${t.template_id} missing maturity rating.`);
        // Check causal chain
        if (!t.causal_links || t.causal_links.length === 0) {
            console.warn(`Warning: Template ${t.template_id} has empty causal links.`);
        }
    });

    // 2. Reduction Integrity
    reductions.forEach(r => {
        r.reducing_templates.forEach(rt => {
            if (!templateIds.has(rt.template_id)) {
                errors.push(`[Referential Integrity] Reduction ${r.reduction_id} -> Missing Template ${rt.template_id}`);
            }
        });
    });

    // 3. Domain Integrity
    const validDomainIds = new Set(['AD_SPATIAL', 'AD_VISUAL', 'AD_SENSORY_NON_VISUAL', 'AD_CONTENT', 'AD_AFFORDANCE']);
    const loadedDomainIds = new Set(domains.map(d => d.domain_id));

    for (const domainId of validDomainIds) {
        if (!loadedDomainIds.has(domainId)) {
            console.warn(`Warning: expected core domain missing: ${domainId}`);
        }
    }

    // Check that all core domains are present (if we expect them)
    // checks for mapped templates
    domains.forEach(d => {
        d.mapped_templates.forEach(mapping => {
            if (!templateIds.has(mapping.template_id)) {
                errors.push(`[Referential Integrity] Domain ${d.domain_id} -> Missing Template ${mapping.template_id}`);
            }
        });
    });

    // 4. Report
    if (errors.length > 0) {
        console.error("\nDrift Detect detected ERRORS:");
        errors.forEach(e => console.error(`❌ ${e}`));
        console.log("\n❌ DRIFT CHECK FAILED");
        process.exit(1);
    } else {
        console.log("\n✅ DRIFT CHECK PASSED - Theory Integrity Verified.");
        process.exit(0);
    }
}

runDriftCheck().catch(console.error);
