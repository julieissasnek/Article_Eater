
import { TheoryAPI } from '../src/api/index';
import { Template } from '../src/types/template';

async function auditConnectivity() {
    const api = new TheoryAPI();
    await api.initialize();
    const templates = api.getAllTemplates();

    const outboundCounts = new Map<string, number>();
    const inboundCounts = new Map<string, number>();
    const idMap = new Map<string, string>(); // display_id -> template_id

    // Initialize counts
    templates.forEach(t => {
        outboundCounts.set(t.display_id, 0);
        inboundCounts.set(t.display_id, 0);
        idMap.set(t.template_id, t.display_id);
    });

    // Populate counts
    templates.forEach(t => {
        const interactions = t.interactions || [];
        outboundCounts.set(t.display_id, interactions.length);

        interactions.forEach(target => {
            let targetId = "";
            if (typeof target === 'string') {
                targetId = target;
            } else if (typeof target === 'object' && target !== null && 'template' in target) {
                targetId = (target as any).template;
            }

            if (!targetId) return;
            // Clean ID (remove comments like " (stress)")
            targetId = targetId.split(' ')[0];

            // Resolve template_id to display_id if needed
            if (idMap.has(targetId)) {
                targetId = idMap.get(targetId)!;
            }

            if (inboundCounts.has(targetId)) {
                inboundCounts.set(targetId, inboundCounts.get(targetId)! + 1);
            }
        });
    });

    console.log("\n--- Connectivity Audit ---");

    // 1. Silent Nodes (No Outbound)
    const silent = templates.filter(t => outboundCounts.get(t.display_id) === 0);
    console.log(`\nSilent Nodes (0 Outbound Links): ${silent.length}`);
    silent.slice(0, 10).forEach(t => console.log(`- ${t.display_id} (${t.template_id})`));

    // 2. Orphan Nodes (No Inbound)
    const orphans = templates.filter(t => inboundCounts.get(t.display_id) === 0);
    console.log(`\nOrphan Nodes (0 Inbound Links): ${orphans.length}`);
    orphans.slice(0, 10).forEach(t => console.log(`- ${t.display_id} (${t.template_id})`));

    // 2a. T1-T30 Orphans
    const coreOrphans = orphans.filter(t => {
        const numId = parseInt(t.display_id.replace('T', ''));
        return !isNaN(numId) && numId >= 1 && numId <= 30;
    });
    console.log(`\nCore T1-T30 Orphans (0 Inbound Links): ${coreOrphans.length}`);
    coreOrphans.forEach(t => console.log(`- ${t.display_id} (${t.template_id})`));

    // 3. True Islands (0 In + 0 Out)
    const islands = templates.filter(t =>
        outboundCounts.get(t.display_id) === 0 &&
        inboundCounts.get(t.display_id) === 0
    );
    console.log(`\nTrue Islands (Isolated): ${islands.length}`);
    islands.forEach(t => console.log(`- ${t.display_id}`));
}

auditConnectivity().catch(console.error);
