Given (1) rule candidates and (2) seven-panel items, infer potential LINKS:
- chaining: A->B and B->C
- synergy: A1->C, A2->C, (A1&A2)->C with d12 > d1+d2
- antagonism: d12 < d1+d2
Return JSON:
{
  "links":[
    {"type":"chaining","from":"wayfinding_legibility","to":"stress↓","evidence_idx":[5,9]},
    {"type":"synergy","a1":"natural_light","a2":"plants","target":"stress↓","evidence_idx":[4,8,12]}
  ]
}
Strict JSON only.