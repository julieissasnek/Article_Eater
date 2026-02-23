python3 scripts/gap_tracker.py --mark-calibrated PP_SPECTRAL_MATCH_001 --panel VISUAL-I
python3 scripts/gap_tracker.py --mark-calibrated PP_COMPLEXITY_GOLDILOCKS_002 --panel VISUAL-I
python3 scripts/gap_tracker.py --mark-calibrated PP_RAPID_GIST_004 --panel VISUAL-I
python3 scripts/gap_tracker.py --mark-calibrated LUM_CONTRAST_PE_001 --panel VISUAL-I
python3 scripts/gap_tracker.py --mark-calibrated NATURE_VIEW_CONVERGENCE_001 --panel VISUAL-I
python3 scripts/gap_tracker.py --mark-calibrated VF1_CONTOUR_PE_001 --panel VISUAL-I
python3 scripts/gap_tracker.py --mark-calibrated VF2_VISUAL_RHYTHM_001 --panel VISUAL-I
python3 scripts/gap_tracker.py --mark-calibrated VF3_SPATIAL_PROPORTIONS_001 --panel VISUAL-I

python3 scripts/gap_tracker.py --assign LUM_CONTRAST_PE_001_T1_dapple_convergence --panel LIGHT-I
python3 scripts/gap_tracker.py --assign PP_RAPID_GIST_004_SC1_integration_overlap --panel SPATIAL-II
python3 scripts/gap_tracker.py --assign PP_RAPID_GIST_004_VF3_temporal_dependency --panel VF-III
python3 scripts/gap_tracker.py --assign T2_VF1_VF2_VF3_domain_decomposition --panel VF-III
python3 scripts/gap_tracker.py --assign VF3_SC3_promenade_R_h_sequence --panel SC-III
python3 scripts/gap_tracker.py --assign VF2_SC3_nested_temporal_hierarchy --panel SC-III
python3 scripts/gap_tracker.py --assign T1_SC3_fractal_convergence_bonus --panel SC-III
python3 scripts/gap_tracker.py --assign L1_AX3_luminance_awe_trigger --panel AWE-I
python3 scripts/gap_tracker.py --assign VF3_AX3_high_R_h_awe_contributing_cause --panel AWE-I
python3 scripts/gap_tracker.py --assign VIEW1_T29_allostatic_restoration --panel NEUROMOD-I
python3 scripts/gap_tracker.py --assign VF1_IC2_cognitive_load_CCI_interaction --panel NEUROMOD-I
python3 scripts/gap_tracker.py --assign PP_RAPID_GIST_004_AESTHETIC_ANCHORING_T1_5_candidate --panel THEORY-REVIEW

python3 scripts/gap_tracker.py --report | grep -i "total open pipeline tasks"
