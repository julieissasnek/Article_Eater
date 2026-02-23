python3 scripts/gap_tracker.py --mark-calibrated DAYLIGHT_MULTICHANNEL_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated CIRCADIAN_ARCH_REG_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated NM_CIRCADIAN_ENTRAINMENT_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated CCT_TEMPORAL_ECOLOGICAL_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated DYNAMIC_LIGHT_TEMPORAL_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated CHRONO_LIGHT_ENTRAINMENT_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated CIRCADIAN_ARCH_REGULATION_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated CB_SLEEP_ARCHITECTURE_002 --panel LIGHT-I
python3 scripts/gap_tracker.py --assign LUM_CONTRAST_PE_001 --panel VISUAL-I
python3 scripts/gap_tracker.py --assign ALLOSTATIC_MASTER_001 --panel NEUROMOD-I
python3 scripts/gap_tracker.py --assign NM_NORADRENERGIC_EXPLORE_006 --panel NEUROMOD-I
python3 scripts/gap_tracker.py --assign ED_HIPPOCAMPAL_ENCODING_001 --panel MEMORY-I
python3 scripts/gap_tracker.py --assign T6 --panel STRESS-I-ADDENDUM-UPDATE
python3 scripts/gap_tracker.py --report
python3 scripts/gap_tracker.py --mark-calibrated SPATIAL_INTEGRATION_PE_001 --panel SPATIAL-I
python3 scripts/gap_tracker.py --mark-calibrated ISOVIST_VISUAL_PREDICTION_001 --panel SPATIAL-I
python3 scripts/gap_tracker.py --mark-calibrated ARCH_PROMENADE_TEMPORAL_PE_001 --panel SPATIAL-I
python3 scripts/gap_tracker.py --mark-calibrated SPATIAL_SOCIAL_ENCOUNTER_001 --panel SPATIAL-I
python3 scripts/gap_tracker.py --assign LUM_CONTRAST_PE_001 --panel VISUAL-I
python3 scripts/gap_tracker.py --assign IC2_BODY_BUDGET_INTEGRATION --panel NEUROMOD-I
python3 scripts/gap_tracker.py --assign T5_THREAT_HPA_001 --panel NEUROMOD-I  # isovist-area as primary environmental predictor
python3 scripts/gap_tracker.py --assign ED_HIPPOCAMPAL_ENCODING_001 --panel MEMORY-I  # SC3 threshold events as input
python3 scripts/gap_tracker.py --assign AX3_AWE_HIGH_PE_001 --panel AWE-I  # promenade compositional context required
python3 scripts/gap_tracker.py --assign T48_SOCIAL_BRAIN_001 --panel SOCIAL-I  # SC4 encounter parameters as upstream input
python3 scripts/gap_tracker.py --assign AX4_PERCEIVED_CONTROL_001 --panel AX-I  # edge condition density as primary input
python3 scripts/gap_tracker.py --assign PROXEMICS_T1_5_REDUCTION --panel THEORY-REDUCTION  # new T1.5 candidate
python3 scripts/gap_tracker.py --report
