Web metrics:
  beliefs: 12628
  constraints: 36625
  bridges: 1898
  supports_count: 12763
  explains_count: 21134
  contradicts_count: 373
  supports_share_pct: 34.84778156996587
  explains_share_pct: 57.703754266211604
  contradicts_share_pct: 1.0184300341296928
  isolated_count: 2838
  isolated_pct: 22.473867595818817
  both_sides_count: 5441
  both_sides_pct: 43.08679125752297
  avg_indeg: 2.9003009185936017
  avg_outdeg: 2.9003009185936017
  bridge_with_source_pct: 100.0
BN metrics:
  nodes: 11846
  edges: 12024
  dangling_edges: 0
  has_cycle: 0
  isolated_count: 69
  isolated_pct: 0.5824750970791829
  largest_component_count: 7763
  largest_component_pct: 65.53266925544487
  unresolved_count: 5506
  unresolved_pct: 46.479824413304065
minimum_viable: PASS (12 passed, 0 failed)
target: FAIL (4 passed, 3 failed)
  TARGET MISS web.isolated_pct <= 10.0 (actual=22.473867595818817)
  TARGET MISS web.contradicts_share_pct >= 2.0 (actual=1.0184300341296928)
  TARGET MISS bn.unresolved_pct <= 30.0 (actual=46.479824413304065)
