# CX-5 Light Template Encoder Guide (L1-L5)

Date: 2026-02-16
Scope: Encoding Panel L-I templates using the current `src/types/template.ts` contract.

## Purpose

This guide shows how to encode Light templates (L1-L5) with the CX-5 schema extensions:
- `Level` additions: `subcortical`, `neuroendocrine`
- Parallel channel support: `causal_topology`, `convergence_rule`, `channel_id`, `converges_on`
- Temporal support: `temporal.scale`, `temporal.variable_type`

## Minimum required fields

Every template JSON still needs:
- `template_id`, `display_id`, `name`
- `structural_pattern`, `higher_order_principle`
- `framework_ids`, `causal_links`
- `scope_conditions`, `moderators`, `interactions`
- `overall_maturity`, `key_references`

## L2 encoding pattern (ipRGC -> SCN -> pineal)

Use the new level taxonomy for non-cortical and endocrine links.

```json
{
  "template_id": "CIRCADIAN_ARCH_REG_001",
  "display_id": "L2",
  "causal_topology": "serial",
  "causal_links": [
    {
      "from_variable": "melanopic_irradiance_at_eye",
      "to_variable": "ipRGC_activation",
      "activity": "modulates",
      "from_level": "environmental",
      "to_level": "sensory",
      "bridging_quality": "strong",
      "maturity": "established",
      "temporal": { "scale": "hours", "variable_type": "state" }
    },
    {
      "from_variable": "ipRGC_activation",
      "to_variable": "SCN_phase_signal",
      "activity": "modulates",
      "from_level": "sensory",
      "to_level": "subcortical",
      "bridging_quality": "strong",
      "maturity": "established",
      "temporal": { "scale": "circadian_24h", "variable_type": "phase" }
    },
    {
      "from_variable": "SCN_phase_signal",
      "to_variable": "melatonin_cortisol_profile",
      "activity": "modulates",
      "from_level": "subcortical",
      "to_level": "neuroendocrine",
      "bridging_quality": "strong",
      "maturity": "established",
      "temporal": { "scale": "circadian_24h", "variable_type": "phase" }
    }
  ]
}
```

## L3 encoding pattern (parallel channel convergence)

Represent daylight convergence as parallel channels with explicit convergence metadata.

```json
{
  "template_id": "DAYLIGHT_MULTICHANNEL_001",
  "display_id": "L3",
  "causal_topology": "parallel",
  "convergence_rule": "super_additive",
  "causal_links": [
    {
      "channel_id": "circadian",
      "from_variable": "daylight_spectral_profile",
      "to_variable": "circadian_alignment_signal",
      "converges_on": "daylight_wellbeing_index",
      "activity": "enhances",
      "from_level": "environmental",
      "to_level": "physiological",
      "bridging_quality": "moderate",
      "maturity": "supported"
    },
    {
      "channel_id": "view",
      "from_variable": "outdoor_view_information",
      "to_variable": "restoration_signal",
      "converges_on": "daylight_wellbeing_index",
      "activity": "enhances",
      "from_level": "environmental",
      "to_level": "affective",
      "bridging_quality": "moderate",
      "maturity": "supported"
    },
    {
      "channel_id": "dynamic_variation",
      "from_variable": "daylight_temporal_variability",
      "to_variable": "engagement_signal",
      "converges_on": "daylight_wellbeing_index",
      "activity": "enhances",
      "from_level": "environmental",
      "to_level": "cognitive",
      "bridging_quality": "moderate",
      "maturity": "supported"
    }
  ]
}
```

## L5 encoding pattern (rate-of-change / temporal dynamics)

Use `temporal.variable_type: rate_of_change` on links where dynamic light change is mechanistically central.

```json
{
  "template_id": "DYNAMIC_LIGHT_TEMPORAL_001",
  "display_id": "L5",
  "causal_topology": "hybrid",
  "causal_links": [
    {
      "from_variable": "illuminance_change_rate_lux_per_min",
      "to_variable": "temporal_prediction_update",
      "activity": "modulates",
      "from_level": "environmental",
      "to_level": "cognitive",
      "bridging_quality": "weak",
      "maturity": "preliminary",
      "temporal": {
        "scale": "minutes",
        "variable_type": "rate_of_change",
        "notes": "Distinguish dynamic-daylight-like ramps from static lighting"
      }
    },
    {
      "from_variable": "temporal_prediction_update",
      "to_variable": "sustained_engagement",
      "activity": "enhances",
      "from_level": "cognitive",
      "to_level": "behavioral",
      "bridging_quality": "weak",
      "maturity": "preliminary",
      "temporal": { "scale": "hours", "variable_type": "duration" }
    }
  ]
}
```

## Encoder checklist

1. Use lower-case canonical enums for `maturity` and `bridging_quality`.
2. For L2, use `subcortical`/`neuroendocrine` where biologically appropriate.
3. For L3, include `causal_topology` and `convergence_rule`.
4. For L3 parallel channels, assign `channel_id` and shared `converges_on` target.
5. For L5 dynamics, encode temporal metadata and `rate_of_change` where relevant.
6. Avoid legacy link keys (`from_entity`, `to_entity`, `level`) in new Light templates.

## Validation commands

Run compatibility and enum checks after encoding:

```bash
node scripts/check_template_contract_compatibility.js
node scripts/check_template_enum_drift.js
```
