# CX-5 Template Contract Compatibility Report

- Scan date (UTC): 2026-02-16T13:11:55.546Z
- Template directory: `data/templates`
- Files scanned: **88**

## Shape Summary
- Legacy-only causal link shape files: **59**
- Canonical-only causal link shape files: **4**
- Mixed-shape files: **0**
- Unknown-shape files: **25**
- Files using new `causal_topology`: **0**
- Links using new `temporal` metadata: **0**

## Key Gaps
- Activity drift in 209 entries (many domain-specific verbs outside canonical activity enum).
- No files yet use CX-5 Light-template extension fields (`causal_topology`, `convergence_rule`, `channel_id`, `converges_on`, `temporal.*`).

## Most Common Activity Values
- determines: 21
- modulates: 13
- generates: 9
- amplifies: 7
- produces: 7
- couples: 5
- biases: 5
- melatonin_suppression: 2
- modulates_inverted_U: 2
- drives: 2
- calibrates: 2
- supports: 2
- enhances: 2
- contributes_to: 2
- promotes: 2

## Most Common Level Values
- environmental: 116
- cognitive: 71
- neural: 64
- affective: 29
- physiological: 23
- behavioral: 12
- sensory: 6
- phenomenological: 4
- motor: 4
- perceptual: 3
- subcortical: 2
- memorial: 2

## Most Common Link Maturity Values
- established: 106
- supported: 85
- preliminary: 21

## Most Common Link Bridging Quality Values
- strong: 82
- moderate: 41
- weak: 1

## Files Missing Required Top-Level Fields
- none

## Sample Invalid Link-Level Values (first 40)
- AUD_REVERBERATION_SPACE_003.json: causal_links[0].activity=generate_acoustic_signature
- AUD_REVERBERATION_SPACE_003.json: causal_links[1].activity=infer_spatial_properties
- AUD_REVERBERATION_SPACE_003.json: causal_links[2].activity=modulate_affective_response
- AUD_SCENE_ANALYSIS_001.json: causal_links[0].activity=impose_segregation_load
- AUD_SCENE_ANALYSIS_001.json: causal_links[1].activity=recruit_neural_resources
- AUD_SCENE_ANALYSIS_001.json: causal_links[2].activity=divert_attentional_resources
- AX1.json: causal_links[0].activity=couples
- AX1.json: causal_links[1].activity=amplifies
- AX1.json: causal_links[2].activity=biases
- AX10.json: causal_links[0].activity=attention_capture
- AX10.json: causal_links[1].activity=effect_amplification
- AX11.json: causal_links[0].activity=pathway_differentiation
- AX11.json: causal_links[1].activity=outcome_production
- AX12.json: causal_links[0].activity=channel_stripping
- AX12.json: causal_links[1].activity=altered_processing
- AX2.json: causal_links[0].activity=adaptation_process
- AX3.json: causal_links[0].activity=couples
- AX3.json: causal_links[1].activity=couples
- AX3.json: causal_links[2].activity=amplifies
- AX4.json: causal_links[0].activity=appraisal_modification
- AX5.json: causal_links[0].activity=couples
- AX5.json: causal_links[1].activity=biases
- AX5.json: causal_links[2].activity=biases
- AX6.json: causal_links[0].activity=couples
- AX6.json: causal_links[1].activity=amplifies
- AX6.json: causal_links[2].activity=biases
- AX7.json: causal_links[0].activity=cumulative_impact
- AX8.json: causal_links[0].activity=sensitivity_modulation
- AX9.json: causal_links[0].activity=schema_application
- CB2.json: causal_links[0].activity=melatonin_suppression
- CB2.json: causal_links[1].activity=sleep_architecture_disruption
- CROSS_PROACTIVE_REACTIVE_CONTROL_001.json: causal_links[0].activity=bias_toward_proactive_or_reactive
- CROSS_PROACTIVE_REACTIVE_CONTROL_001.json: causal_links[1].activity=determine_energy_expenditure_pattern
- CROSS_PROACTIVE_REACTIVE_CONTROL_001.json: causal_links[2].activity=modulate_mode_accessibility
- CROSS_THALAMIC_ENVIRONMENTAL_FILTER_001.json: causal_links[0].activity=select_attentional_mode
- CROSS_THALAMIC_ENVIRONMENTAL_FILTER_001.json: causal_links[1].activity=gate_sensory_throughput
- CROSS_THALAMIC_ENVIRONMENTAL_FILTER_001.json: causal_links[2].activity=shape_perceptual_experience
- DP2.json: causal_links[0].activity=conflict_detection
- DP2.json: causal_links[1].activity=cognitive_control
- DT1.json: causal_links[0].activity=salience_detection
