
import { TheoryAPI } from '../src/api/index';
import * as fs from 'fs';
import * as path from 'path';

async function analyze() {
    console.log("Starting Gap Analysis...");
    const api = new TheoryAPI();
    await api.initialize();

    const templates = api.getAllTemplates();
    const reductions = api.getAllReductions();

    console.log(`Loaded ${templates.length} templates.`);
    console.log(`Loaded ${reductions.length} reductions.`);

    // 1. Audit Reductions vs Task List / Preliminary Map
    const reductionMap = new Map<string, any>();
    reductions.forEach(r => reductionMap.set(r.claim_id, r));

    console.log("\n--- Reduction Inventory ---");
    reductions.forEach(r => {
        console.log(`[${r.claim_id}] Theory: '${r.tier2_theory}' -> Construct: '${r.tier2_construct}'`);
    });

    // 2. Identify Orphaned Templates (Not used in any reduction)
    const usedTemplateIds = new Set<string>();
    reductions.forEach(r => {
        r.template_nodes.forEach(tid => usedTemplateIds.add(tid));
    });

    const orphaned = templates.filter(t => !usedTemplateIds.has(t.template_id));
    console.log(`\n--- Orphaned Templates (${orphaned.length}) ---`);
    console.log("Templates not linked to any Reduction Claim:");
    orphaned.forEach(t => console.log(`- ${t.template_id} (${t.name})`));

    // 3. Expected vs Actual (Based on Preliminary Map logic hardcoded for check)
    // We expect: ART (4), SRT (3), Biophilia (4)
    // We have: RC1-RC6?

    // Check specific critical Tier 2 constructs
    const criticalConstructs = [
        { theory: "ART", construct: "soft fascination" },
        { theory: "ART", construct: "being away" },
        { theory: "ART", construct: "extent" },
        { theory: "ART", construct: "compatibility" },
        { theory: "SRT", construct: "parasympathetic" }, // Matches "Parasympathetic Dominance" or similar
        { theory: "SRT", construct: "recovery" }, // Matches "Stress Recovery"
        { theory: "Biophilia", construct: "prospect" } // Matches "Prospect-Refuge"
    ];

    console.log("\n--- Critical Construct Coverage ---");
    criticalConstructs.forEach(c => {
        const found = reductions.find(r => {
            const theoryMatch = r.tier2_theory.toLowerCase().includes(c.theory.toLowerCase());
            const constructMatch = r.tier2_construct.toLowerCase().includes(c.construct.toLowerCase());
            if (c.construct === "soft fascination") { // Debug specific case
                console.log(`Checking [${r.claim_id}]: TheoryMatch=${theoryMatch} ('${r.tier2_theory}' vs '${c.theory}'), ConstructMatch=${constructMatch} ('${r.tier2_construct}' vs '${c.construct}')`);
            }
            return theoryMatch && constructMatch;
        });
        if (found) {
            console.log(`[OK] ${c.theory} - ${c.construct} found in ${found.claim_id}`);
        } else {
            console.log(`[MISSING] ${c.theory} - ${c.construct}`);
        }
    });

}

analyze().catch(err => console.error(err));
