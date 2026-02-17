
import { TheoryAPI } from '../src/api/index';
import { createClaimFromTemplate } from '../src/theory/bridge';

async function runExpertWorkflow() {
    console.log("Starting Expert Workflow Integration Test...");

    // 1. Initialize API
    const api = new TheoryAPI();
    await api.initialize();

    // 2. Expert looks up "Spatial Attributes"
    const domainId = "AD_SPATIAL";
    const domain = api.getAttributeDomain(domainId);

    if (!domain) {
        console.error(`Domain ${domainId} not found.`);
        process.exit(1);
    }
    console.log(`Found Domain: ${domain.name}`);
    console.log(`Sub-attributes: ${domain.attributes.map(a => a.name).join(", ")}`);

    // 3. Expert finds relevant templates
    const templates = api.getTemplatesForAttributeDomain(domainId);
    console.log(`Mapped Templates: ${templates.map(t => t.template_id).join(", ")}`);

    if (templates.length === 0) {
        console.error("No templates found for domain.");
        process.exit(1);
    }

    // 4. Expert selects a template (e.g., T3 or first available)
    const selectedTemplate = templates.find(t => t.display_id === "T3") || templates[0];
    console.log(`Selected Template: ${selectedTemplate.template_id} (${selectedTemplate.name})`);

    // 5. Expert generates a claim based on a finding
    // Finding: "Low ceilings correlate with poor wayfinding"
    const findingId = "FINDING_LOW_CEILING_WAYFINDING";
    const claim = createClaimFromTemplate(
        selectedTemplate,
        findingId,
        "Low ceiling height restricts spatial map formation",
        "negative"
    );

    console.log("Generated Claim:");
    console.log(JSON.stringify(claim, null, 2));

    // Validation
    if (!claim.claim_id.startsWith("CLM_")) {
        console.error("Invalid claim ID format.");
        process.exit(1);
    }
    if (claim.source_template_id !== selectedTemplate.template_id) {
        console.error("Claim source template mismatch.");
        process.exit(1);
    }

    console.log("\nExpert Workflow Test PASSED.");
}

runExpertWorkflow().catch(err => {
    console.error("Workflow crashed:", err);
    process.exit(1);
});
