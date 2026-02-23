# ⚠️ SUPERSEDED — See (newer version exists) for current version

# SPRINT VERIFICATION & END-TO-END PROVENANCE TEST SUITE
## February 17, 2026

---

## PURPOSE

Two problems this document solves:

1. **Sprint tasks get marked DONE but aren't working.** Sprint 10 was declared complete, but the building eval returned WIS 50.0 for every building. Unit tests passed because they tested components in isolation — nobody tested whether the components were CONNECTED. This suite verifies each sprint deliverable actually functions in the integrated system.

2. **We can't trace from answer back to data.** When the system says "this building scores WIS 72," we need to verify: which templates contributed? What data did each template use? Did the template apply the correct parameters? Did the theory (PE framework, Goldilocks boundaries) actually influence the result, or did the system bypass it? These provenance tests verify the full chain from input data to final answer.

---

## PART 1: SPRINT DELIVERABLE VERIFICATION

### How to run

These tests should be run AFTER each sprint is declared complete, BEFORE starting the next sprint. Any failure means the sprint is NOT actually complete.

```bash
python -m pytest tests/test_sprint_verification.py -v
```

### Sprint 10 Verification

```python
"""tests/test_sprint_verification.py — Sprint 10"""

import json
import os
import sqlite3

# ============================================================
# S10-V01: Template DB actually populated
# ============================================================
def test_s10_template_db_exists_and_populated():
    """Template DB has records, not just an empty table."""
    from src.theory.templateRegistry import get_all_templates  # or equivalent
    templates = get_all_templates()
    assert len(templates) >= 150, f"Expected 150+ templates, got {len(templates)}"

def test_s10_template_db_has_classifications():
    """Every template has dedup_status, pe_contribution, accessibility."""
    templates = get_all_templates()
    for t in templates:
        assert t.dedup_status in ("active", "superseded", "residual", 
                                   "reference", "gap"), \
            f"{t.display_id}: bad dedup_status '{t.dedup_status}'"
        assert t.pe_contribution in ("predictive", "explanatory", 
                                      "organizational"), \
            f"{t.display_id}: bad pe_contribution '{t.pe_contribution}'"
        assert t.practical_accessibility in ("A", "B", "C", "D"), \
            f"{t.display_id}: bad accessibility '{t.practical_accessibility}'"

def test_s10_no_orphan_json_files():
    """Every JSON file in data/templates/ has a DB record."""
    json_files = os.listdir("data/templates/")
    json_files = [f for f in json_files if f.endswith(".json")]
    templates = {t.json_path for t in get_all_templates()}
    for f in json_files:
        assert f in templates or f"data/templates/{f}" in templates, \
            f"JSON file {f} has no DB record"

# ============================================================
# S10-V02: Staging theory-links actually loaded
# ============================================================
def test_s10_staging_links_loaded():
    """1,361 theory links exist in web of belief."""
    from src.services.web_persistence import get_constraints_for_web
    links = get_constraints_for_web(constraint_type="tier2_theory_link")
    assert len(links) >= 1361, f"Expected 1361 theory links, got {len(links)}"

def test_s10_staging_links_have_theory_ids():
    """Every theory link has a valid theory_id."""
    links = get_constraints_for_web(constraint_type="tier2_theory_link")
    theory_ids = {getattr(l, 'theory_id', None) for l in links}
    assert "ART" in theory_ids, "No ART theory links found"
    assert "Biophilia" in theory_ids, "No Biophilia theory links found"

# ============================================================
# S10-V03: WIS module produces correct values
# ============================================================
def test_s10_wis_not_always_50():
    """WIS conversion never returns 50 for non-zero d values."""
    from src.cmr.wis import cohens_d_to_wis
    for d in [0.1, 0.2, 0.3, 0.5, 0.8, -0.3, -0.5]:
        wis = cohens_d_to_wis(d)
        assert wis != 50.0, f"cohens_d_to_wis({d}) returned exactly 50.0"

def test_s10_wis_monotonic():
    """Larger d → larger WIS."""
    from src.cmr.wis import cohens_d_to_wis
    d_values = [-1.0, -0.5, 0, 0.2, 0.5, 0.8, 1.0]
    wis_values = [cohens_d_to_wis(d) for d in d_values]
    for i in range(len(wis_values) - 1):
        assert wis_values[i] < wis_values[i+1], \
            f"WIS not monotonic: d={d_values[i]}→{wis_values[i]}, d={d_values[i+1]}→{wis_values[i+1]}"

# ============================================================
# S10-V04: Compute functions produce non-placeholder values
# ============================================================
def test_s10_compute_functions_exist():
    """At least 12 core compute functions exist."""
    from src.cmr import template_computations as tc
    expected = ["VF3", "L1", "L2", "L3", "MAT1", "MAT2", "MAT4", 
                "SOC2", "SC1", "SC4", "VIEW1", "CREA2"]
    dispatch = getattr(tc, 'TEMPLATE_DISPATCH', None) or \
               getattr(tc, 'DISPATCH', None) or \
               {name.replace("compute_", "").upper(): getattr(tc, name) 
                for name in dir(tc) if name.startswith("compute_")}
    for template_id in expected:
        assert template_id in dispatch or template_id.lower() in dispatch, \
            f"No compute function for {template_id}"

def test_s10_compute_functions_return_real_values():
    """Compute functions return values other than 50."""
    from src.cmr.template_computations import compute_vf3  # or equivalent
    result = compute_vf3(ceiling_height_m=2.75, floor_area_m2=18.0)
    wis = result.get("wis_raw", result.get("wis", None))
    assert wis is not None, "VF3 returned no WIS value"
    assert wis != 50.0, "VF3 returned placeholder 50.0"

# ============================================================
# S10-V05: Building eval orchestrator is CONNECTED
# ============================================================
def test_s10_orchestrator_calls_real_functions():
    """The orchestrator produces different scores for different buildings."""
    from src.cmr.building_eval import evaluate_building
    
    salk = evaluate_building(
        building_context={"building_type": "research_institute"},
        measured_features={"ceiling_height_m": 2.75, "floor_area_m2": 18.0,
                          "illuminance_lux": 350, "ambient_noise_dba": 38,
                          "has_nature_view": True, "view_content": "ocean"},
        occupant_profile={"age": 35}
    )
    openplan = evaluate_building(
        building_context={"building_type": "office"},
        measured_features={"ceiling_height_m": 2.7, "floor_area_m2": 500.0,
                          "illuminance_lux": 500, "ambient_noise_dba": 62,
                          "has_nature_view": False, "privacy_visual": "none",
                          "privacy_acoustic": "none"},
        occupant_profile={"age": 35}
    )
    
    salk_wis = salk.get("overall_wis", salk.get("wis_geometric_mean"))
    open_wis = openplan.get("overall_wis", openplan.get("wis_geometric_mean"))
    
    assert salk_wis != open_wis, \
        f"Salk ({salk_wis}) and open-plan ({open_wis}) scored identically — orchestrator disconnected"
    assert salk_wis != 50.0, f"Salk scored exactly 50.0 — likely placeholder"
    assert open_wis != 50.0, f"Open-plan scored exactly 50.0 — likely placeholder"

def test_s10_orchestrator_lifespan_works():
    """Same building, different ages → different scores."""
    from src.cmr.building_eval import evaluate_building
    
    features = {"ceiling_height_m": 3.0, "floor_area_m2": 25.0,
                "illuminance_lux": 400, "ambient_noise_dba": 40}
    
    young = evaluate_building(
        building_context={}, measured_features=features,
        occupant_profile={"age": 25}
    )
    old = evaluate_building(
        building_context={}, measured_features=features,
        occupant_profile={"age": 70}
    )
    
    young_wis = young.get("overall_wis", young.get("wis_geometric_mean"))
    old_wis = old.get("overall_wis", old.get("wis_geometric_mean"))
    
    assert young_wis != old_wis, \
        f"Age 25 ({young_wis}) and age 70 ({old_wis}) scored identically — lifespan not wired"


### Sprint 11 Verification

# ============================================================
# S11-V01: Building eval wiring fixed (Round 1)
# ============================================================
def test_s11_salk_scores_well():
    """Salk Institute overall WIS > 55."""
    result = evaluate_building(
        building_context={"building_type": "research_institute"},
        measured_features={"ceiling_height_m": 2.75, "floor_area_m2": 18.0,
                          "illuminance_lux": 350, "ambient_noise_dba": 38,
                          "has_nature_view": True, "view_content": "ocean"},
        occupant_profile={"age": 35}
    )
    wis = result.get("overall_wis", result.get("wis_geometric_mean"))
    assert wis > 55, f"Salk scored {wis} — expected > 55 for excellent building"

def test_s11_openplan_scores_badly():
    """Open-plan office overall WIS < 50."""
    result = evaluate_building(
        building_context={"building_type": "office"},
        measured_features={"ceiling_height_m": 2.7, "floor_area_m2": 500.0,
                          "illuminance_lux": 500, "ambient_noise_dba": 62,
                          "has_nature_view": False, "privacy_visual": "none",
                          "privacy_acoustic": "none",
                          "density_m2_per_person": 8.0},
        occupant_profile={"age": 35}
    )
    wis = result.get("overall_wis", result.get("wis_geometric_mean"))
    assert wis < 50, f"Open-plan scored {wis} — expected < 50 for poor environment"

def test_s11_salk_beats_openplan():
    """Salk WIS > open-plan WIS (fundamental face-validity)."""
    salk = evaluate_building(
        building_context={"building_type": "research_institute"},
        measured_features={"ceiling_height_m": 2.75, "floor_area_m2": 18.0,
                          "illuminance_lux": 350, "ambient_noise_dba": 38,
                          "has_nature_view": True, "view_content": "ocean"},
        occupant_profile={"age": 35}
    )
    openplan = evaluate_building(
        building_context={"building_type": "office"},
        measured_features={"ceiling_height_m": 2.7, "floor_area_m2": 500.0,
                          "illuminance_lux": 500, "ambient_noise_dba": 62,
                          "has_nature_view": False, "privacy_visual": "none"},
        occupant_profile={"age": 35}
    )
    assert salk["overall_wis"] > openplan["overall_wis"], \
        "Salk should beat open-plan — face-validity failure"

# ============================================================
# S11-V02: Paper eval pipeline runs
# ============================================================
def test_s11_paper_eval_runs():
    """Paper eval produces output, not an error."""
    from src.cmr.paper_eval import evaluate_paper
    result = evaluate_paper(structured_claims=[
        {"iv": "nature_view", "dv": "restoration", 
         "direction": "increase", "d": 0.5}
    ])
    assert result is not None
    assert "findings" in result or "n_claims_matched" in result

def test_s11_paper_eval_finds_view1():
    """Nature view claim matches VIEW1 template."""
    result = evaluate_paper(structured_claims=[
        {"iv": "nature_view", "dv": "restoration", 
         "direction": "increase", "d": 0.5}
    ])
    findings = result.get("findings", [])
    template_ids = str(findings)
    assert "VIEW1" in template_ids, \
        "Nature view claim didn't match VIEW1 — template matching broken"

def test_s11_paper_eval_sensitive_to_direction():
    """Contradicting claim produces different output than confirming."""
    confirm = evaluate_paper(structured_claims=[
        {"iv": "nature_view", "dv": "restoration", 
         "direction": "increase", "d": 0.5}
    ])
    contradict = evaluate_paper(structured_claims=[
        {"iv": "nature_view", "dv": "restoration", 
         "direction": "decrease", "d": -0.5}
    ])
    assert str(confirm) != str(contradict), \
        "Confirming and contradicting claims produced identical output — data-insensitive"
```

---

## PART 2: END-TO-END PROVENANCE TESTS

These tests verify that the system's answers are TRACEABLE back to specific data, templates, and theory. The question is not "does it produce a number?" but "can we explain WHERE that number came from?"

### Test Suite: Building Evaluation Provenance

```python
"""tests/test_provenance_building.py"""

# ============================================================
# PROV-B01: Score decomposition — every WIS score traceable to template
# ============================================================
def test_overall_wis_decomposes_to_domains():
    """Overall WIS must be the geometric mean of domain scores — 
    not an independent calculation."""
    from src.cmr.building_eval import evaluate_building
    from src.cmr.wis import aggregate_overall_wis
    import math
    
    result = evaluate_building(
        building_context={},
        measured_features={"ceiling_height_m": 3.0, "floor_area_m2": 25.0,
                          "illuminance_lux": 400, "ambient_noise_dba": 40,
                          "has_nature_view": True},
        occupant_profile={"age": 35}
    )
    
    # Extract domain scores
    domain_scores = result.get("domain_scores", [])
    assert len(domain_scores) > 0, "No domain scores in result"
    
    # Recompute geometric mean manually
    wis_values = [d["wis"] for d in domain_scores if d.get("wis")]
    if wis_values:
        manual_geomean = math.exp(sum(math.log(max(w, 0.01)) for w in wis_values) / len(wis_values))
        reported = result.get("overall_wis", result.get("wis_geometric_mean"))
        assert abs(manual_geomean - reported) < 1.0, \
            f"Overall WIS {reported} doesn't match geometric mean of domains {manual_geomean}"

def test_domain_wis_decomposes_to_templates():
    """Each domain score must be traceable to specific template activations."""
    result = evaluate_building(
        building_context={},
        measured_features={"ceiling_height_m": 3.0, "floor_area_m2": 25.0},
        occupant_profile={"age": 35}
    )
    
    domain_scores = result.get("domain_scores", [])
    activations = result.get("template_activations", [])
    
    for domain in domain_scores:
        domain_name = domain.get("domain")
        domain_templates = domain.get("template_ids", "")
        assert domain_templates, f"Domain {domain_name} has no template_ids — score untraceable"

def test_template_wis_decomposes_to_inputs():
    """Each template activation must record which inputs it used 
    and what raw output it produced before WIS conversion."""
    result = evaluate_building(
        building_context={},
        measured_features={"ceiling_height_m": 3.0, "floor_area_m2": 25.0},
        occupant_profile={"age": 35}
    )
    
    activations = result.get("template_activations", [])
    for act in activations:
        template_id = act.get("template", act.get("template_display_id"))
        # Must have inputs recorded
        inputs = act.get("inputs", {})
        assert inputs or act.get("needs_computation"), \
            f"{template_id}: no inputs recorded — can't trace score to data"
        # Must have raw output before WIS conversion
        raw = act.get("raw_output", act.get("outputs", {}))
        wis = act.get("wis_score", act.get("wis"))
        if wis and wis != 50.0:
            assert raw, f"{template_id}: WIS={wis} but no raw output recorded"

# ============================================================
# PROV-B02: Parameters come from calibration, not hardcoded
# ============================================================
def test_vf3_uses_json_boundaries():
    """VF3's Goldilocks zone boundaries must come from its JSON file, 
    not be hardcoded in the compute function."""
    import json
    
    # Load the VF3 JSON template
    vf3_json = None
    for f in os.listdir("data/templates/"):
        if "VF3" in f.upper() or "vf3" in f.lower() or "visual_form_3" in f.lower():
            with open(f"data/templates/{f}") as fh:
                vf3_json = json.load(fh)
            break
    
    assert vf3_json is not None, "VF3 JSON template not found"
    
    # Extract boundaries from JSON
    json_params = vf3_json.get("parameters", [])
    json_boundaries = {p["name"]: p["value"] for p in json_params 
                       if "boundary" in p.get("name", "").lower() or 
                          "zone" in p.get("name", "").lower() or
                          "threshold" in p.get("name", "").lower()}
    
    # If the JSON has boundaries, the compute function should use them
    # (This test documents whether parameters are data-driven or hardcoded)
    if json_boundaries:
        print(f"VF3 JSON has boundary parameters: {json_boundaries}")
        # The compute function should reference these, not magic numbers
    else:
        print("WARNING: VF3 JSON has no explicit boundary parameters — "
              "compute function may use hardcoded values")

def test_template_params_match_source_docs():
    """Spot-check: template parameter values should match what the 
    calibration panels documented."""
    import json
    
    # L2: circadian threshold should be ~250 lux melanopic EDI (from Doc 57)
    # This is a specific check that the right number made it through
    for f in os.listdir("data/templates/"):
        with open(f"data/templates/{f}") as fh:
            data = json.load(fh)
        display_id = data.get("display_id", "")
        if display_id == "L2":
            params = {p["name"]: p for p in data.get("parameters", [])}
            # Should have an M-EDI threshold around 200-300 lux
            threshold_params = {k: v for k, v in params.items() 
                               if "threshold" in k.lower() or "medi" in k.lower() 
                               or "melanopic" in k.lower()}
            if threshold_params:
                for name, param in threshold_params.items():
                    val = param.get("value")
                    if isinstance(val, (int, float)):
                        assert 100 < val < 500, \
                            f"L2 {name}={val} outside plausible range"
            break

# ============================================================
# PROV-B03: Lifespan moderation traceable
# ============================================================
def test_lifespan_moderation_recorded():
    """When lifespan moderation is applied, the result must record 
    WHAT was modified and by HOW MUCH."""
    result_young = evaluate_building(
        building_context={},
        measured_features={"ceiling_height_m": 3.0, "floor_area_m2": 25.0,
                          "illuminance_lux": 400},
        occupant_profile={"age": 25}
    )
    result_old = evaluate_building(
        building_context={},
        measured_features={"ceiling_height_m": 3.0, "floor_area_m2": 25.0,
                          "illuminance_lux": 400},
        occupant_profile={"age": 70}
    )
    
    # At least one template activation should show different values
    young_activations = {a.get("template"): a.get("wis_score") 
                        for a in result_young.get("template_activations", [])}
    old_activations = {a.get("template"): a.get("wis_score") 
                      for a in result_old.get("template_activations", [])}
    
    common_templates = set(young_activations.keys()) & set(old_activations.keys())
    any_different = any(young_activations[t] != old_activations[t] 
                       for t in common_templates 
                       if young_activations[t] is not None)
    assert any_different, \
        "No template scores differ between age 25 and 70 — lifespan moderation not applied"

# ============================================================
# PROV-B04: Interaction adjustments traceable
# ============================================================
def test_interaction_adjustments_recorded():
    """When interaction adjustments are applied, the result must record 
    which templates interacted and what the adjustment was."""
    # Trigger convergence triad: L3 + MAT4 + VIEW1
    result = evaluate_building(
        building_context={},
        measured_features={"illuminance_lux": 500, "primary_material": "wood",
                          "has_nature_view": True, "view_content": "trees",
                          "ceiling_height_m": 3.0, "floor_area_m2": 30.0},
        occupant_profile={"age": 35}
    )
    
    # Check for interaction records
    interactions = result.get("interactions_applied", [])
    activations = result.get("template_activations", [])
    interaction_records = [a.get("interaction_adjustments") for a in activations 
                          if a.get("interaction_adjustments")]
    
    # At least document whether interactions were checked
    has_interaction_info = bool(interactions) or bool(interaction_records)
    if not has_interaction_info:
        print("WARNING: No interaction adjustment records in result — "
              "either no interactions triggered or interaction module not recording")
```

### Test Suite: Paper Evaluation Provenance

```python
"""tests/test_provenance_paper.py"""

# ============================================================
# PROV-P01: Claim-to-template matching is correct and traceable
# ============================================================
def test_claim_match_records_rationale():
    """Each claim-template match must explain WHY it matched."""
    from src.cmr.paper_eval import evaluate_paper
    
    result = evaluate_paper(structured_claims=[
        {"iv": "nature_view", "dv": "stress_reduction", 
         "direction": "decrease", "d": 0.5, "context": "hospital"}
    ])
    
    findings = result.get("findings", [])
    assert len(findings) > 0, "No findings produced"
    
    for finding in findings:
        matches = finding.get("template_matches", finding.get("matches", []))
        for match in (matches if isinstance(matches, list) else [matches]):
            if isinstance(match, dict):
                assert match.get("rationale") or match.get("match_type"), \
                    f"Match to {match.get('template_id')} has no rationale — untraceable"

def test_claim_direction_matters():
    """System must distinguish between 'X increases Y' and 'X decreases Y'.
    These should produce different assessments, not identical matches."""
    increases = evaluate_paper(structured_claims=[
        {"iv": "noise_65dba", "dv": "creative_performance", 
         "direction": "increase", "d": 0.4}
    ])
    decreases = evaluate_paper(structured_claims=[
        {"iv": "noise_65dba", "dv": "creative_performance", 
         "direction": "decrease", "d": -0.4}
    ])
    
    inc_findings = str(increases.get("findings", []))
    dec_findings = str(decreases.get("findings", []))
    
    assert inc_findings != dec_findings, \
        "System ignores claim direction — 'increases' and 'decreases' produced identical output"

def test_effect_size_matters():
    """d=0.1 and d=1.5 should produce different VOI or confidence assessments."""
    small = evaluate_paper(structured_claims=[
        {"iv": "ceiling_height", "dv": "creativity", 
         "direction": "increase", "d": 0.1}
    ])
    large = evaluate_paper(structured_claims=[
        {"iv": "ceiling_height", "dv": "creativity", 
         "direction": "increase", "d": 1.5}
    ])
    
    # At least one metric should differ
    small_str = json.dumps(small.get("findings", []), sort_keys=True)
    large_str = json.dumps(large.get("findings", []), sort_keys=True)
    assert small_str != large_str, \
        "d=0.1 and d=1.5 produced identical findings — system ignores effect size"

# ============================================================
# PROV-P02: Template theory actually constrains assessment
# ============================================================
def test_template_prediction_used_in_assessment():
    """When a claim matches a template, the template's predicted 
    direction/magnitude must be compared against the claim."""
    result = evaluate_paper(structured_claims=[
        {"iv": "nature_view", "dv": "restoration", 
         "direction": "increase", "d": 0.5}
    ])
    
    findings = result.get("findings", [])
    for finding in findings:
        # Should have an assessment that references what the template predicts
        assessment = str(finding)
        has_prediction_comparison = any(term in assessment.lower() for term in 
            ["confirms", "contradicts", "consistent", "inconsistent", 
             "supports", "challenges", "expected", "predicted"])
        if not has_prediction_comparison:
            print(f"WARNING: Finding has no prediction comparison: {finding.get('claim', {}).get('iv')}")

def test_contradiction_detected_correctly():
    """A claim that contradicts a template prediction must be flagged, 
    not treated as confirmation."""
    # CREA2 predicts: moderate noise (65-75 dBA) HELPS divergent creativity
    # This claim says noise HURTS creativity — should be flagged
    result = evaluate_paper(structured_claims=[
        {"iv": "ambient_noise_70dba", "dv": "divergent_creativity", 
         "direction": "decrease", "d": -0.6}
    ])
    
    findings = result.get("findings", [])
    assessment_text = str(findings).lower()
    
    assert any(term in assessment_text for term in 
        ["contradict", "inconsistent", "conflicts", "challenges", "unexpected"]), \
        "Noise hurting creativity should contradict CREA2 — not flagged as contradiction"

def test_gap_identified_for_unmapped_variables():
    """Claims about variables with no template should be flagged as gaps, 
    not silently ignored or force-matched."""
    result = evaluate_paper(structured_claims=[
        {"iv": "electromagnetic_field", "dv": "sleep_quality", 
         "direction": "decrease", "d": -0.4}
    ])
    
    # Should either be unmatched or flagged as gap
    n_unmatched = result.get("n_claims_unmatched", 0)
    findings_text = str(result.get("findings", []))
    
    assert n_unmatched > 0 or "gap" in findings_text.lower() or \
           "unmatched" in findings_text.lower() or "novel" in findings_text.lower(), \
        "EMF claim was not flagged as gap — system force-matched to wrong template or silently dropped it"

# ============================================================
# PROV-P03: The chain from data to theory to answer is complete
# ============================================================
def test_full_provenance_chain():
    """Trace a single claim through every boundary and verify 
    data flows correctly at each step."""
    
    claim = {"iv": "ceiling_height_3m", "dv": "spatial_openness", 
             "direction": "increase", "d": 0.6, 
             "sample_n": 80, "context": "office"}
    
    # Step 1: Claim extraction preserves data
    from src.cmr.claim_extraction import extract_claims_structured
    extracted = extract_claims_structured([claim])
    assert extracted[0]["d"] == 0.6, "Claim extraction lost effect size"
    assert extracted[0]["sample_n"] == 80, "Claim extraction lost sample size"
    
    # Step 2: Template matching finds VF3
    from src.cmr.template_matching import match_claims_to_templates
    templates = get_all_active_templates()
    matches = match_claims_to_templates(extracted, templates)
    matched_ids = [m.get("template_id") for match_set in matches 
                   for m in match_set.get("matches", [])]
    assert "VF3" in matched_ids, "VF3 not matched to ceiling height claim"
    
    # Step 3: Mechanism tracing checks the PE theory
    from src.cmr.mechanism_tracing import trace_mechanisms
    traced = trace_mechanisms(matches)
    vf3_trace = [t for t in traced if t.get("template") == "VF3"]
    assert len(vf3_trace) > 0, "VF3 not traced"
    
    # The trace should reference VF3's specific mechanism
    trace_text = str(vf3_trace[0])
    assert any(term in trace_text.lower() for term in 
        ["r_h", "ceiling", "enclosure", "spatial", "prediction error"]), \
        "VF3 trace doesn't reference its specific mechanism"
    
    # Step 4: Convergence assessment
    from src.cmr.convergence import assess_convergence
    convergence = assess_convergence(traced)
    assert len(convergence) > 0, "No convergence assessment produced"
    
    # Step 5: VOI scoring uses effect size
    from src.cmr.voi_scoring import score_voi
    scored = score_voi(convergence)
    assert scored[0].get("voi") is not None, "No VOI score"
    
    # Final: full pipeline produces complete report
    result = evaluate_paper(structured_claims=[claim])
    assert result.get("n_claims_matched", 0) >= 1
    
    # The report should mention VF3 and the effect size
    report_text = str(result)
    assert "VF3" in report_text, "Final report doesn't mention VF3"

# ============================================================
# PROV-P04: Cross-pipeline consistency
# ============================================================
def test_paper_and_building_agree():
    """If a paper says 'high ceilings help spatial cognition' and the 
    building has high ceilings, the building eval should show high 
    spatial scores."""
    
    # Paper says: high ceiling → spatial benefit
    paper_result = evaluate_paper(structured_claims=[
        {"iv": "ceiling_height_high", "dv": "spatial_openness", 
         "direction": "increase", "d": 0.5}
    ])
    
    # Building with high ceiling
    high_ceiling = evaluate_building(
        building_context={},
        measured_features={"ceiling_height_m": 4.5, "floor_area_m2": 30.0},
        occupant_profile={"age": 35}
    )
    # Building with low ceiling  
    low_ceiling = evaluate_building(
        building_context={},
        measured_features={"ceiling_height_m": 2.3, "floor_area_m2": 30.0},
        occupant_profile={"age": 35}
    )
    
    # Paper says high ceiling helps → high-ceiling building should score better
    high_wis = high_ceiling.get("overall_wis", 0)
    low_wis = low_ceiling.get("overall_wis", 0)
    
    # The direction should be consistent with the paper's claim
    assert high_wis >= low_wis, \
        "Paper says high ceiling helps, but building eval scores high ceiling lower — inconsistent"

def test_paper_contradiction_matches_building_eval():
    """If the paper eval flags a contradiction, the building eval 
    should show the EXPECTED direction (not the paper's claimed direction)."""
    
    # CREA2 says moderate noise helps divergent creativity
    # Feed a contradicting paper
    paper = evaluate_paper(structured_claims=[
        {"iv": "ambient_noise_70dba", "dv": "divergent_creativity", 
         "direction": "decrease", "d": -0.5}
    ])
    
    # Building eval with 70 dBA noise — what does the SYSTEM predict?
    noisy = evaluate_building(
        building_context={},
        measured_features={"ceiling_height_m": 3.0, "floor_area_m2": 25.0,
                          "ambient_noise_dba": 70},
        occupant_profile={"age": 35}
    )
    quiet = evaluate_building(
        building_context={},
        measured_features={"ceiling_height_m": 3.0, "floor_area_m2": 25.0,
                          "ambient_noise_dba": 35},
        occupant_profile={"age": 35}
    )
    
    # The system should follow its OWN templates, not the contradicting paper
    # CREA2 says moderate noise helps → noisy should score equal or better
    # on creativity domain (but may lose on other domains)
    # The point: the system has its own model and can explain disagreement
```

---

## PART 3: IMPLEMENTATION INSTRUCTIONS

### For agents implementing these tests

1. Create the test files:
   - `tests/test_sprint_verification.py` (Part 1)
   - `tests/test_provenance_building.py` (Part 2, building eval)
   - `tests/test_provenance_paper.py` (Part 2, paper eval)

2. **Adapt function calls to match actual codebase.** The function signatures above are APPROXIMATE. The real imports, function names, and return structures may differ. Read the actual code in src/cmr/ and adjust the test calls to match. Document any discrepancies in DECISIONS.md.

3. **Every failing test is a finding.** Don't just fix the test to make it pass — if the test reveals a real problem (placeholder returns, disconnected module, data-insensitive output), report the problem. The test caught what it was supposed to catch.

4. **Run the full suite together:**
```bash
python -m pytest tests/test_sprint_verification.py tests/test_provenance_building.py tests/test_provenance_paper.py -v --tb=short
```

Report: total passed, total failed, which specific tests failed and why.

---

*Sprint Verification & Provenance Test Suite — February 17, 2026*
*Part 1: Sprint deliverable verification (did each task actually work?)*
*Part 2: End-to-end provenance (can we trace from answer to data?)*
*Part 3: Implementation instructions*
*Core principle: The system must either compute a real answer traceable to specific data and theory, or explicitly refuse. Silent defaults are bugs.*
