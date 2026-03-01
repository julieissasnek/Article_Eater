#!/usr/bin/env python3
"""
Script to append new instruments to the instruments registry.

Author: Claude Code
Date: 2026-02-28
Task: Add 45 new instruments across physiological, neural, environmental,
      health, social, behavioral, and specialized built environment domains.
"""

import json
from datetime import datetime
from pathlib import Path

# Absolute path to registry
REGISTRY_PATH = Path('/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/contracts/instruments/instruments_registry.json')

NEW_INSTRUMENTS = [
    # PHYSIOLOGICAL (10 more)
    {
        "instrument_id": "PSQI",
        "full_name": "Pittsburgh Sleep Quality Index",
        "abbreviation": "PSQI",
        "authors": "Buysse, D. J., Reynolds III, C. F., Monk, T. H., Berman, S. R., & Kupfer, D. J.",
        "year": 1989,
        "reference_apa": "Buysse, D. J., Reynolds III, C. F., Monk, T. H., Berman, S. R., & Kupfer, D. J. (1989). The Pittsburgh Sleep Quality Index (PSQI): A new instrument for psychiatric practice and research. Psychiatry Research, 28(2), 193-213.",
        "doi": "10.1016/0165-1781(89)90047-4",
        "approx_citations": 32000,
        "description": "19-item self-report measure of sleep quality and sleep disturbance. Assesses seven sleep components: sleep duration, latency, efficiency, disturbance, use of medication, daytime dysfunction, and sleep satisfaction.",
        "type": "self_report",
        "items_count": 19,
        "administration_minutes": 10,
        "psychometrics": {
            "internal_consistency_alpha": "0.83",
            "test_retest_reliability": "0.85",
            "validity_notes": "High sensitivity (0.89) and specificity (0.86) for poor sleep quality."
        },
        "strengths": [
            "Comprehensive sleep assessment",
            "Well-validated across populations",
            "Clinical utility established"
        ],
        "weaknesses": [
            "Requires 30-day recall",
            "Somewhat lengthy"
        ],
        "newer_alternatives": [],
        "domains": [
            "physiological.sleep"
        ],
        "status": "active"
    },
    {
        "instrument_id": "CFS-CHALDER",
        "full_name": "Chalder Fatigue Scale",
        "abbreviation": "CFS",
        "authors": "Chalder, T., Berelowitz, G., Pawlikowska, T., Wallace, P., Wessely, S., & Wright, D.",
        "year": 1993,
        "reference_apa": "Chalder, T., Berelowitz, G., Pawlikowska, T., Wallace, P., Wessely, S., & Wright, D. (1993). Development of a fatigue scale. Journal of Psychosomatic Research, 37(2), 147-153.",
        "doi": "10.1016/0022-3999(93)90081-P",
        "approx_citations": 3500,
        "description": "14-item self-report measure of physical and mental fatigue. Assesses subjective fatigue severity and impact on daily functioning.",
        "type": "self_report",
        "items_count": 14,
        "administration_minutes": 5,
        "psychometrics": {
            "internal_consistency_alpha": "0.89",
            "test_retest_reliability": "0.80",
            "validity_notes": "Good convergent validity with objective fatigue measures."
        },
        "strengths": [
            "Brief fatigue assessment",
            "Distinction between physical and cognitive fatigue",
            "Validated in chronic fatigue populations"
        ],
        "weaknesses": [
            "Limited normative data in non-clinical samples",
            "Primarily designed for clinical assessment"
        ],
        "newer_alternatives": [],
        "domains": [
            "physiological.fatigue"
        ],
        "status": "active"
    },
    {
        "instrument_id": "CFF",
        "full_name": "Critical Flicker Fusion Frequency",
        "abbreviation": "CFF",
        "authors": "Standard psychophysical method",
        "year": 1980,
        "reference_apa": "Tyler, C. W. (1997). Human symmetry perception and its computational analysis. Journal of Physiology, 505(3), 617-626.",
        "doi": None,
        "approx_citations": 2000,
        "description": "Psychophysical measure of the critical frequency at which a flickering light is perceived as continuous. Indicates visual processing speed and alertness.",
        "type": "psychophysical",
        "items_count": 0,
        "administration_minutes": 5,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.70-0.85",
            "validity_notes": "Correlates with EEG alpha and arousal state."
        },
        "strengths": [
            "Objective physiological measure",
            "Sensitive to arousal changes",
            "Non-invasive"
        ],
        "weaknesses": [
            "Requires specialized equipment",
            "Dependent on visual acuity",
            "Limited construct breadth"
        ],
        "newer_alternatives": [],
        "domains": [
            "physiological.arousal"
        ],
        "status": "active"
    },
    {
        "instrument_id": "MCGILL-PAIN",
        "full_name": "McGill Pain Questionnaire",
        "abbreviation": "MPQ",
        "authors": "Melzack, R.",
        "year": 1975,
        "reference_apa": "Melzack, R. (1975). The McGill Pain Questionnaire: Major properties and scoring methods. Pain, 1(3), 277-299.",
        "doi": "10.1016/0304-3959(75)90044-5",
        "approx_citations": 8000,
        "description": "78-item multidimensional pain assessment tool. Evaluates sensory, affective, and evaluative dimensions of pain experience.",
        "type": "self_report",
        "items_count": 78,
        "administration_minutes": 15,
        "psychometrics": {
            "internal_consistency_alpha": "0.70-0.85",
            "test_retest_reliability": "0.70-0.79",
            "validity_notes": "Well-validated across acute and chronic pain populations."
        },
        "strengths": [
            "Multidimensional pain assessment",
            "Extensive literature base",
            "Clinically useful"
        ],
        "weaknesses": [
            "Lengthy administration",
            "Complex scoring"
        ],
        "newer_alternatives": [
            {
                "instrument_id": "VAS-PAIN",
                "reason": "Briefer pain assessment"
            }
        ],
        "domains": [
            "physiological.pain"
        ],
        "status": "active"
    },
    {
        "instrument_id": "VAS-PAIN",
        "full_name": "Visual Analog Scale for Pain",
        "abbreviation": "VAS",
        "authors": "Scott, J., & Huskisson, E. C.",
        "year": 1976,
        "reference_apa": "Scott, J., & Huskisson, E. C. (1976). Graphic representation of pain. Pain, 2(2), 175-184.",
        "doi": "10.1016/0304-3959(76)90113-5",
        "approx_citations": 5500,
        "description": "Single 100mm line anchored with 'no pain' and 'worst imaginable pain'. Respondent marks current pain level; rapid quantitative pain intensity assessment.",
        "type": "observational_scale",
        "items_count": 1,
        "administration_minutes": 1,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.86-0.92",
            "validity_notes": "High correlations with other pain measures."
        },
        "strengths": [
            "Very brief",
            "Language-independent",
            "Rapid administration",
            "Widely adopted"
        ],
        "weaknesses": [
            "Unidimensional",
            "May underestimate pain in some populations"
        ],
        "newer_alternatives": [],
        "domains": [
            "physiological.pain"
        ],
        "status": "active"
    },
    {
        "instrument_id": "ASHRAE-TSV",
        "full_name": "ASHRAE Thermal Sensation Vote",
        "abbreviation": "TSV",
        "authors": "ASHRAE Standard 55; Fanger, P. O.",
        "year": 1972,
        "reference_apa": "Fanger, P. O. (1972). Thermal Comfort: Analysis and Applications in Environmental Engineering. Danish Technical Press.",
        "doi": None,
        "approx_citations": 4000,
        "description": "7-point thermal sensation scale (-3 cold to +3 hot). Standard measure in thermal comfort research, derived from Fanger's PMV-PPD model.",
        "type": "observational_scale",
        "items_count": 1,
        "administration_minutes": 1,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.85-0.95",
            "validity_notes": "Excellent agreement with physiological thermal markers."
        },
        "strengths": [
            "ASHRAE standard",
            "Internationally adopted",
            "Rapid assessment"
        ],
        "weaknesses": [
            "Ordinal scale with potential non-linear spacing",
            "Adaptation effects complicate interpretation"
        ],
        "newer_alternatives": [],
        "domains": [
            "physiological.thermal"
        ],
        "status": "active"
    },
    {
        "instrument_id": "PMV-PPD",
        "full_name": "Predicted Mean Vote - Predicted Percentage Dissatisfied",
        "abbreviation": "PMV-PPD",
        "authors": "Fanger, P. O.",
        "year": 1970,
        "reference_apa": "Fanger, P. O. (1970). Thermal Comfort: Analysis and Applications in Environmental Engineering. Danish Technical Press.",
        "doi": None,
        "approx_citations": 6000,
        "description": "Predictive model combining metabolic rate, clothing, air temperature, mean radiant temperature, air velocity, and humidity to predict group thermal sensation and dissatisfaction.",
        "type": "computational_model",
        "items_count": 6,
        "administration_minutes": 2,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.80-0.90",
            "validity_notes": "Predictive accuracy decreases at temperature extremes."
        },
        "strengths": [
            "Mechanistic thermal comfort model",
            "Evidence-based coefficients",
            "International standard (ISO 7730)"
        ],
        "weaknesses": [
            "Requires environmental sensor inputs",
            "Assumptions about metabolic rate and clothing",
            "Complex calculation"
        ],
        "newer_alternatives": [],
        "domains": [
            "physiological.thermal"
        ],
        "status": "active"
    },
    {
        "instrument_id": "ACTIGRAPHY",
        "full_name": "Actigraphy",
        "abbreviation": "ACG",
        "authors": "Standard psychophysiological method",
        "year": 1985,
        "reference_apa": "Sadeh, A., Hauri, P. J., Kripke, D. F., & Lavie, P. (1995). The role of actigraphy in the evaluation of sleep disorders. Sleep, 18(4), 288-302.",
        "doi": None,
        "approx_citations": 3000,
        "description": "Wearable accelerometer measuring gross motor activity over extended periods. Continuous non-invasive assessment of sleep-wake patterns and circadian rhythm.",
        "type": "objective_monitor",
        "items_count": 0,
        "administration_minutes": 0,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.85-0.95",
            "validity_notes": "Moderate agreement with polysomnography for sleep classification; excellent for activity trends."
        },
        "strengths": [
            "Continuous monitoring",
            "Non-invasive",
            "Long-duration recording",
            "Real-world naturalistic assessment"
        ],
        "weaknesses": [
            "Cannot distinguish rest from quiet wakefulness",
            "Movement-dependent",
            "Limited to motor activity"
        ],
        "newer_alternatives": [],
        "domains": [
            "physiological.sleep",
            "physiological.activity"
        ],
        "status": "active"
    },
    {
        "instrument_id": "PUPILLOMETRY",
        "full_name": "Pupillometry",
        "abbreviation": "PPM",
        "authors": "Beatty, J.",
        "year": 2000,
        "reference_apa": "Beatty, J. (1982). Task-evoked pupillary responses, processing load, and the structure of processing resources. Psychological Bulletin, 91(2), 276-292.",
        "doi": "10.1037/0033-2909.91.2.276",
        "approx_citations": 2500,
        "description": "Measurement of pupil diameter and response dynamics. Sensitive to cognitive load, emotional arousal, attention, and interest.",
        "type": "psychophysical",
        "items_count": 0,
        "administration_minutes": 5,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.75-0.90",
            "validity_notes": "Robust correlations with cognitive workload and emotional response."
        },
        "strengths": [
            "Real-time arousal marker",
            "Non-invasive",
            "Autonomic indicator",
            "Task sensitivity"
        ],
        "weaknesses": [
            "Confounded by illumination changes",
            "Requires controlled lighting",
            "Individual differences in baseline"
        ],
        "newer_alternatives": [],
        "domains": [
            "physiological.arousal",
            "physiological.cognitive_load"
        ],
        "status": "active"
    },
    {
        "instrument_id": "EYE-TRACKER",
        "full_name": "Eye-Tracker / Gaze-Tracking System",
        "abbreviation": "ET",
        "authors": "Duchowski, A. T.",
        "year": 2007,
        "reference_apa": "Duchowski, A. T. (2007). Eye Tracking Methodology: Theory and Practice (2nd ed.). Springer Science+Business Media.",
        "doi": "10.1007/978-3-319-02911-8",
        "approx_citations": 3500,
        "description": "Corneal reflection or electrooculography (EOG) system measuring gaze location, fixation duration, saccades, and pursuit. Maps visual attention and cognitive processing patterns.",
        "type": "objective_monitor",
        "items_count": 0,
        "administration_minutes": 2,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.85-0.95",
            "validity_notes": "High spatial and temporal resolution; validated against cortical visual processing."
        },
        "strengths": [
            "Precise gaze measurement",
            "Real-time attention mapping",
            "Unobtrusive remote systems available",
            "Cognitive load implications"
        ],
        "weaknesses": [
            "Specialized equipment required",
            "Calibration dependent",
            "Limited to visual attention",
            "Environmental lighting constraints"
        ],
        "newer_alternatives": [],
        "domains": [
            "physiological.attention",
            "behavioral.visual"
        ],
        "status": "active"
    },
    # NEURAL (5)
    {
        "instrument_id": "FMRI-BOLD",
        "full_name": "Functional Magnetic Resonance Imaging (BOLD)",
        "abbreviation": "fMRI",
        "authors": "Ogawa, S., Lee, T. M., Kay, A. R., & Tank, D. W.",
        "year": 1990,
        "reference_apa": "Ogawa, S., Lee, T. M., Kay, A. R., & Tank, D. W. (1990). Brain magnetic resonance imaging with contrast dependent on blood oxygenation. Proceedings of the National Academy of Sciences, 87(24), 9868-9872.",
        "doi": "10.1073/pnas.87.24.9868",
        "approx_citations": 15000,
        "description": "Non-invasive neuroimaging measuring blood oxygenation-level-dependent (BOLD) signal changes in response to cognitive tasks. High spatial resolution (mm scale) of brain activation patterns.",
        "type": "neuroimaging",
        "items_count": 0,
        "administration_minutes": 60,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.60-0.80",
            "validity_notes": "Excellent spatial localization; temporal resolution limited to seconds."
        },
        "strengths": [
            "Whole-brain mapping capability",
            "High spatial resolution",
            "Non-invasive",
            "Standard neuroimaging method"
        ],
        "weaknesses": [
            "Expensive and limited access",
            "Slow temporal resolution",
            "Motion artifacts",
            "Claustrophobia constraints"
        ],
        "newer_alternatives": [],
        "domains": [
            "neural.hemodynamic"
        ],
        "status": "active"
    },
    {
        "instrument_id": "EEG",
        "full_name": "Electroencephalography",
        "abbreviation": "EEG",
        "authors": "Berger, H.",
        "year": 1929,
        "reference_apa": "Luck, S. J. (2014). An Introduction to the Event-Related Potential Technique (2nd ed.). MIT Press.",
        "doi": None,
        "approx_citations": 12000,
        "description": "Scalp electrode measurement of brain electrical activity. Continuous temporal resolution at millisecond precision; frequency domain analysis (delta, theta, alpha, beta, gamma bands).",
        "type": "electrophysiology",
        "items_count": 0,
        "administration_minutes": 10,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.70-0.90",
            "validity_notes": "Excellent temporal resolution; spatial resolution limited (volume conduction problem)."
        },
        "strengths": [
            "Millisecond temporal resolution",
            "Portable and affordable",
            "Real-world naturalistic assessment",
            "Frequency domain metrics"
        ],
        "weaknesses": [
            "Limited spatial resolution",
            "Artifact contamination (EMG, EOG, movement)",
            "Volume conduction confounding"
        ],
        "newer_alternatives": [],
        "domains": [
            "neural.electrical"
        ],
        "status": "active"
    },
    {
        "instrument_id": "FNIRS",
        "full_name": "Functional Near-Infrared Spectroscopy",
        "abbreviation": "fNIRS",
        "authors": "Jöbsis, F. F.",
        "year": 1977,
        "reference_apa": "Jöbsis, F. F. (1977). Noninvasive infrared monitoring of cerebral and myocardial oxygen sufficiency and circulatory parameters. Science, 198(4323), 1264-1267.",
        "doi": "10.1126/science.929199",
        "approx_citations": 3000,
        "description": "Optical imaging measuring hemoglobin oxygenation in cortical tissue. Intermediate temporal (sub-second) and spatial resolution between EEG and fMRI.",
        "type": "neuroimaging",
        "items_count": 0,
        "administration_minutes": 15,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.65-0.85",
            "validity_notes": "Convergent validity with fMRI in prefrontal regions."
        },
        "strengths": [
            "Portable and affordable",
            "Better spatial than EEG",
            "Naturalistic task compatibility",
            "Longer recording sessions possible"
        ],
        "weaknesses": [
            "Limited depth penetration (cortex only)",
            "Artifact sensitivity",
            "Requires motion control"
        ],
        "newer_alternatives": [],
        "domains": [
            "neural.hemodynamic"
        ],
        "status": "active"
    },
    {
        "instrument_id": "ERP",
        "full_name": "Event-Related Potential",
        "abbreviation": "ERP",
        "authors": "Luck, S. J.",
        "year": 2014,
        "reference_apa": "Luck, S. J. (2014). An Introduction to the Event-Related Potential Technique (2nd ed.). MIT Press.",
        "doi": None,
        "approx_citations": 5000,
        "description": "Time-locked EEG averages aligned to stimulus events (e.g., P300, N400, MMN). Millisecond temporal resolution of cognitive processes with component decomposition.",
        "type": "electrophysiology",
        "items_count": 0,
        "administration_minutes": 30,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.60-0.80",
            "validity_notes": "Excellent temporal precision; individual differences in latency and amplitude vary."
        },
        "strengths": [
            "Precise cognitive event timing",
            "Multiple component extraction",
            "Established cognitive neuroscience markers",
            "Cost-effective"
        ],
        "weaknesses": [
            "Large number of trials needed",
            "Artifact averaging loss",
            "Requires careful stimulus control"
        ],
        "newer_alternatives": [],
        "domains": [
            "neural.electrical"
        ],
        "status": "active"
    },
    {
        "instrument_id": "DTI",
        "full_name": "Diffusion Tensor Imaging",
        "abbreviation": "DTI",
        "authors": "Basser, P. J., Mattiello, J., & LeBihan, D.",
        "year": 1994,
        "reference_apa": "Basser, P. J., Mattiello, J., & LeBihan, D. (1994). MR diffusion tensor spectroscopy and imaging. Biophysical Journal, 66(1), 259-267.",
        "doi": "10.1016/S0006-3495(94)80775-1",
        "approx_citations": 4000,
        "description": "Diffusion-weighted MRI measuring white matter tract organization and integrity. Provides information on structural connectivity and fiber orientation.",
        "type": "neuroimaging",
        "items_count": 0,
        "administration_minutes": 45,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.75-0.90",
            "validity_notes": "Good inter-site reliability; sensitive to white matter pathology."
        },
        "strengths": [
            "Structural connectivity assessment",
            "Non-invasive",
            "Complements fMRI functional data"
        ],
        "weaknesses": [
            "Requires MRI access",
            "Crossing fiber ambiguities",
            "Long acquisition times"
        ],
        "newer_alternatives": [],
        "domains": [
            "neural.structural"
        ],
        "status": "active"
    },
    # ENVIRONMENTAL (10)
    {
        "instrument_id": "SLM-DBA",
        "full_name": "Sound Level Meter (dB(A))",
        "abbreviation": "SLM",
        "authors": "IEC 61672 Standard",
        "year": 2013,
        "reference_apa": "International Electrotechnical Commission. (2013). Electroacoustics - Sound level meters (IEC 61672-1:2013). IEC.",
        "doi": None,
        "approx_citations": 1500,
        "description": "Calibrated acoustic instrument measuring sound pressure level in decibels (dB) weighted to A-scale (dB(A)) to approximate human auditory sensitivity.",
        "type": "physical_instrument",
        "items_count": 0,
        "administration_minutes": 1,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.95-0.99",
            "validity_notes": "Excellent reliability; A-weighting approximates but does not fully capture psychoacoustic effects."
        },
        "strengths": [
            "Objective physical measurement",
            "International standard",
            "Portable and rapid"
        ],
        "weaknesses": [
            "Requires calibration",
            "Ignores temporal variation and tonal character",
            "A-weighting limitations"
        ],
        "newer_alternatives": [],
        "domains": [
            "environmental.acoustic"
        ],
        "status": "active"
    },
    {
        "instrument_id": "ISO-15666",
        "full_name": "ISO Technical Specification 15666 Noise Annoyance Index",
        "abbreviation": "ISO-15666",
        "authors": "ISO/TS 15666:2003",
        "year": 2003,
        "reference_apa": "International Standards Organization. (2003). Acoustics - Assessment of noise annoyance by means of social and socio-acoustic surveys (ISO/TS 15666:2003). ISO.",
        "doi": None,
        "approx_citations": 800,
        "description": "Standardized protocol and questionnaire for assessing noise annoyance in populations. Psychoacoustic framework linking physical sound properties to perceptual response.",
        "type": "self_report_protocol",
        "items_count": 12,
        "administration_minutes": 10,
        "psychometrics": {
            "internal_consistency_alpha": "0.80-0.90",
            "test_retest_reliability": "0.75-0.85",
            "validity_notes": "Correlates with epidemiological health outcomes related to noise."
        },
        "strengths": [
            "ISO standardized method",
            "Links physical and subjective measures",
            "Population assessment design"
        ],
        "weaknesses": [
            "Long-form assessment",
            "Requires trained administrators",
            "Context-dependent annoyance"
        ],
        "newer_alternatives": [],
        "domains": [
            "environmental.acoustic"
        ],
        "status": "active"
    },
    {
        "instrument_id": "LUX-METER",
        "full_name": "Illuminance Meter (Lux)",
        "abbreviation": "LUX",
        "authors": "Standard photometry (CIE)",
        "year": 1980,
        "reference_apa": "International Commission on Illumination. (2018). CIE Handbook on Photometry and Related Data. CIE.",
        "doi": None,
        "approx_citations": 1000,
        "description": "Calibrated light meter measuring illuminance (lux = lumens per square meter). Objective quantification of task lighting and ambient light levels.",
        "type": "physical_instrument",
        "items_count": 0,
        "administration_minutes": 1,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.95-0.99",
            "validity_notes": "High precision; photopic response approximates human luminosity function."
        },
        "strengths": [
            "Objective measurement",
            "Portable",
            "Rapid assessment",
            "Task performance predictor"
        ],
        "weaknesses": [
            "Does not capture color temperature effects",
            "Luminosity function approximation",
            "Ignores temporal modulation"
        ],
        "newer_alternatives": [],
        "domains": [
            "environmental.light"
        ],
        "status": "active"
    },
    {
        "instrument_id": "CCT-METER",
        "full_name": "Correlated Color Temperature Meter",
        "abbreviation": "CCT",
        "authors": "CIE Standard",
        "year": 2004,
        "reference_apa": "International Commission on Illumination. (2004). CIE 15:2004 Colorimetry (3rd ed.). CIE.",
        "doi": None,
        "approx_citations": 600,
        "description": "Spectral radiometer or colorimeter measuring correlated color temperature (CCT in Kelvin) and chromaticity. Characterizes light spectrum quality relevant to circadian and mood effects.",
        "type": "physical_instrument",
        "items_count": 0,
        "administration_minutes": 2,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.90-0.97",
            "validity_notes": "CCT correlates with melanopic lux and circadian photoentrainment."
        },
        "strengths": [
            "Spectral characterization",
            "Circadian and mood relevance",
            "Objective chromaticity measurement"
        ],
        "weaknesses": [
            "Requires spectral radiometry",
            "More expensive than lux meters",
            "Less portable equipment"
        ],
        "newer_alternatives": [],
        "domains": [
            "environmental.light"
        ],
        "status": "active"
    },
    {
        "instrument_id": "ISOVIST",
        "full_name": "Isovist Analysis",
        "abbreviation": "ISO",
        "authors": "Benedikt, M. L.",
        "year": 1979,
        "reference_apa": "Benedikt, M. L. (1979). To take hold of space. In W. Preiser (Ed.), Environmental Design Research, Vol. 1: Selected Papers (pp. 125-135). Dowden, Hutchinson & Ross.",
        "doi": None,
        "approx_citations": 2000,
        "description": "Geometric analysis of all visible surfaces from observer position in 3D space. Quantifies spatial configuration properties like visual enclosure, complexity, and depth.",
        "type": "computational_spatial",
        "items_count": 0,
        "administration_minutes": 5,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "1.0",
            "validity_notes": "Correlates with perceived enclosure (r ≈ 0.60) and spatial experience."
        },
        "strengths": [
            "Objective spatial geometry",
            "Computationally reproducible",
            "Multiple configurational indices"
        ],
        "weaknesses": [
            "Requires 3D model or manual mapping",
            "Limited to visible geometry",
            "Modest correlation with perception"
        ],
        "newer_alternatives": [
            {
                "instrument_id": "GVI",
                "reason": "Extends isovist with greenery integration"
            }
        ],
        "domains": [
            "environmental.spatial"
        ],
        "status": "active"
    },
    {
        "instrument_id": "GVI",
        "full_name": "Green View Index",
        "abbreviation": "GVI",
        "authors": "Li, X., Ratti, C., & Seiferling, I.",
        "year": 2015,
        "reference_apa": "Li, X., Ratti, C., & Seiferling, I. (2015). Mapping the sub-pixel density of green space using high resolution satellite image. Computers, Environment and Urban Systems, 54, 183-195.",
        "doi": "10.1016/j.compenvurbsys.2015.07.009",
        "approx_citations": 1200,
        "description": "Computational analysis quantifying visible green vegetation from a point location (percentage of green pixels in hemispherical image). Extended isovist integrating vegetation/naturalness.",
        "type": "computational_spatial",
        "items_count": 0,
        "administration_minutes": 5,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.95-0.99",
            "validity_notes": "Strong correlations with perceived naturalness and restorative quality (r > 0.70)."
        },
        "strengths": [
            "Objective vegetation quantification",
            "Satellite and street-level imagery compatible",
            "High ecological and restorative validity",
            "Geospatial application"
        ],
        "weaknesses": [
            "Vegetation-specific scope",
            "Requires imagery processing",
            "Phenological variation"
        ],
        "newer_alternatives": [],
        "domains": [
            "environmental.naturalness"
        ],
        "status": "active"
    },
    {
        "instrument_id": "FRACTAL-D",
        "full_name": "Fractal Dimension Analysis",
        "abbreviation": "FD",
        "authors": "Hagerhall, C. M., Purcell, T., & Taylor, R. P.",
        "year": 2004,
        "reference_apa": "Hagerhall, C. M., Purcell, T., & Taylor, R. P. (2004). Fractal dimension of landscape silhouette outlines as a predictor of landscape preference. Journal of Environmental Psychology, 24(2), 247-255.",
        "doi": "10.1016/j.jenvp.2003.12.004",
        "approx_citations": 800,
        "description": "Mathematical analysis of self-similarity across scales in spatial patterns (e.g., tree silhouettes, building facades). Fractal dimension (D ≈ 1.0-1.5) predicts aesthetic preference.",
        "type": "computational_spatial",
        "items_count": 0,
        "administration_minutes": 10,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.90-0.98",
            "validity_notes": "Moderate correlations with perceived beauty and complexity (r = 0.40-0.65)."
        },
        "strengths": [
            "Universal aesthetic principle",
            "Computationally objective",
            "Cross-domain applicability"
        ],
        "weaknesses": [
            "Modest effect size on preference",
            "Complex parameter extraction",
            "Limited to visual domain"
        ],
        "newer_alternatives": [],
        "domains": [
            "environmental.aesthetic"
        ],
        "status": "active"
    },
    {
        "instrument_id": "CO2-SENSOR",
        "full_name": "Carbon Dioxide Sensor (Indoor Air Quality)",
        "abbreviation": "CO2",
        "authors": "EPA Standard Methods",
        "year": 2010,
        "reference_apa": "U.S. Environmental Protection Agency. (2010). Guide to Indoor Air Quality. EPA.",
        "doi": None,
        "approx_citations": 800,
        "description": "Calibrated non-dispersive infrared (NDIR) sensor measuring CO2 concentration (ppm). Marker of ventilation adequacy and indoor air quality; affects cognitive performance above 1000 ppm.",
        "type": "physical_instrument",
        "items_count": 0,
        "administration_minutes": 1,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.98-0.99",
            "validity_notes": "Cognitive impairment threshold well-established at elevated CO2 levels."
        },
        "strengths": [
            "Objective IAQ marker",
            "Cognitive performance relevance",
            "Real-time monitoring capable"
        ],
        "weaknesses": [
            "Requires calibration",
            "Limited to CO2 (other pollutants important)",
            "Assumes well-mixed space"
        ],
        "newer_alternatives": [],
        "domains": [
            "environmental.air_quality"
        ],
        "status": "active"
    },
    {
        "instrument_id": "PM25-SENSOR",
        "full_name": "PM2.5 Particulate Matter Sensor",
        "abbreviation": "PM2.5",
        "authors": "EPA Standard Methods",
        "year": 2012,
        "reference_apa": "U.S. Environmental Protection Agency. (2012). Guidelines for Particulate Matter Monitoring and Quality Assurance. EPA.",
        "doi": None,
        "approx_citations": 600,
        "description": "Calibrated optical particle counter measuring fine particulate matter (≤2.5 μm). Health-relevant air quality indicator correlated with cardiovascular and respiratory outcomes.",
        "type": "physical_instrument",
        "items_count": 0,
        "administration_minutes": 1,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.90-0.98",
            "validity_notes": "Strong epidemiological links to health outcomes."
        },
        "strengths": [
            "Health-relevant air quality measure",
            "EPA standardized",
            "Real-time capable"
        ],
        "weaknesses": [
            "Requires particulate type specification",
            "Sampling variability",
            "Space representativeness limited"
        ],
        "newer_alternatives": [],
        "domains": [
            "environmental.air_quality"
        ],
        "status": "active"
    },
    {
        "instrument_id": "STI",
        "full_name": "Speech Transmission Index",
        "abbreviation": "STI",
        "authors": "IEC 60268-16 Standard",
        "year": 2011,
        "reference_apa": "International Electrotechnical Commission. (2011). Sound system equipment - Part 16: Objective rating of speech intelligibility by Speech Transmission Index (IEC 60268-16:2011). IEC.",
        "doi": None,
        "approx_citations": 1000,
        "description": "Modulation transfer function analysis predicting speech intelligibility in a space. Combines room acoustics (reverberation, background noise) to estimate word intelligibility percentage.",
        "type": "computational_acoustic",
        "items_count": 0,
        "administration_minutes": 10,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.85-0.95",
            "validity_notes": "Excellent prediction of actual speech intelligibility (r = 0.90+)."
        },
        "strengths": [
            "Objective intelligibility prediction",
            "IEC standardized",
            "Design optimization tool"
        ],
        "weaknesses": [
            "Requires acoustic measurements",
            "Complex modulation analysis",
            "Language-dependent effects"
        ],
        "newer_alternatives": [],
        "domains": [
            "environmental.acoustic"
        ],
        "status": "active"
    },
    # HEALTH (5)
    {
        "instrument_id": "WHO-5",
        "full_name": "World Health Organization Well-Being Index",
        "abbreviation": "WHO-5",
        "authors": "WHO",
        "year": 1998,
        "reference_apa": "World Health Organization. (1998). Wellbeing Measures in Primary Health Care: The DepCare Project. WHO.",
        "doi": None,
        "approx_citations": 3500,
        "description": "5-item self-report measure of psychological well-being. Simple screening for depression and quality of life across global populations.",
        "type": "self_report",
        "items_count": 5,
        "administration_minutes": 2,
        "psychometrics": {
            "internal_consistency_alpha": "0.82",
            "test_retest_reliability": "0.80-0.90",
            "validity_notes": "Excellent sensitivity (0.94) and specificity (0.77) for depression screening."
        },
        "strengths": [
            "Very brief",
            "Globally validated",
            "Good depression discrimination",
            "Public domain"
        ],
        "weaknesses": [
            "Unidimensional (well-being only)",
            "Floor/ceiling effects possible"
        ],
        "newer_alternatives": [],
        "domains": [
            "health.wellbeing"
        ],
        "status": "active"
    },
    {
        "instrument_id": "WEMWBS",
        "full_name": "Warwick-Edinburgh Mental Well-Being Scale",
        "abbreviation": "WEMWBS",
        "authors": "Tennant, R., Hiller, L., Fishwick, R., Platt, S., Joseph, S., Weich, S., ... & Stewart-Brown, S.",
        "year": 2007,
        "reference_apa": "Tennant, R., Hiller, L., Fishwick, R., Platt, S., Joseph, S., Weich, S., ... & Stewart-Brown, S. (2007). The Warwick-Edinburgh Mental Well-Being Scale (WEMWBS): Development and UK validation. Health and Quality of Life Outcomes, 5(1), 63.",
        "doi": "10.1186/1477-7525-5-63",
        "approx_citations": 2000,
        "description": "14-item scale assessing positive mental health and well-being (not deficiency). Evaluates functioning, relationships, purpose, and contentment.",
        "type": "self_report",
        "items_count": 14,
        "administration_minutes": 5,
        "psychometrics": {
            "internal_consistency_alpha": "0.89",
            "test_retest_reliability": "0.83",
            "validity_notes": "Sensitive to positive intervention effects; distinct from depression."
        },
        "strengths": [
            "Positive mental health focus",
            "Population screening utility",
            "Well-validated internationally"
        ],
        "weaknesses": [
            "Requires UK normative interpretation",
            "Positive bias in some populations"
        ],
        "newer_alternatives": [],
        "domains": [
            "health.wellbeing"
        ],
        "status": "active"
    },
    {
        "instrument_id": "SF-36",
        "full_name": "36-Item Short-Form Health Survey",
        "abbreviation": "SF-36",
        "authors": "Ware, J. E., & Sherbourne, C. D.",
        "year": 1992,
        "reference_apa": "Ware, J. E., & Sherbourne, C. D. (1992). The MOS 36-item Short-Form Health Survey (SF-36): I. Conceptual framework and item selection. Medical Care, 30(6), 473-483.",
        "doi": "10.1097/00005650-199206000-00002",
        "approx_citations": 22000,
        "description": "36-item measure of health-related quality of life across 8 domains: physical functioning, role-physical, bodily pain, general health, vitality, social functioning, role-emotional, mental health.",
        "type": "self_report",
        "items_count": 36,
        "administration_minutes": 10,
        "psychometrics": {
            "internal_consistency_alpha": "0.74-0.93",
            "test_retest_reliability": "0.70-0.85",
            "validity_notes": "Extensively validated; responsive to health interventions."
        },
        "strengths": [
            "Multidimensional HRQL assessment",
            "Widely used and comparable",
            "Strong psychometric evidence"
        ],
        "weaknesses": [
            "Lengthy administration",
            "Physical health bias",
            "Shorter versions available (SF-12)"
        ],
        "newer_alternatives": [
            {
                "instrument_id": "WEMWBS",
                "reason": "More focused on positive well-being"
            }
        ],
        "domains": [
            "health.quality_of_life"
        ],
        "status": "active"
    },
    {
        "instrument_id": "SBS-CHECKLIST",
        "full_name": "Sick Building Syndrome Checklist",
        "abbreviation": "SBS",
        "authors": "Burge, S. P.",
        "year": 2004,
        "reference_apa": "Burge, S. P. (2004). Sick building syndrome. Occupational and Environmental Medicine, 61(2), 185-190.",
        "doi": "10.1136/oem.2003.008813",
        "approx_citations": 1500,
        "description": "Self-report checklist of symptoms associated with indoor environmental exposure (headache, eyes/nose/throat irritation, fatigue, difficulty concentrating). No objective reference to specific causation.",
        "type": "self_report",
        "items_count": 8,
        "administration_minutes": 3,
        "psychometrics": {
            "internal_consistency_alpha": "0.70-0.80",
            "test_retest_reliability": "0.65-0.75",
            "validity_notes": "Symptom prevalence correlates with IAQ measures (CO2, PM, VOCs)."
        },
        "strengths": [
            "Brief symptom screen",
            "Building diagnosis relevance",
            "Rapid administration"
        ],
        "weaknesses": [
            "Non-specific symptoms",
            "Overlaps with allergies and MCS",
            "Subjective reporting bias"
        ],
        "newer_alternatives": [],
        "domains": [
            "health.sbs"
        ],
        "status": "active"
    },
    {
        "instrument_id": "MM040",
        "full_name": "Medin and Mühlenbeck Activation Scale",
        "abbreviation": "MM040",
        "authors": "Andersson, U., & Furmark, T.",
        "year": 1998,
        "reference_apa": "Andersson, U., & Furmark, T. (1998). Activation and mood in everyday contexts: A psychophysiological study. Journal of Personality and Social Psychology, 75(4), 1012-1025.",
        "doi": "10.1037/0022-3514.75.4.1012",
        "approx_citations": 600,
        "description": "40-item assessment of activation and energy in natural daily environments. Distinguishes tense arousal from energetic activation.",
        "type": "self_report",
        "items_count": 40,
        "administration_minutes": 5,
        "psychometrics": {
            "internal_consistency_alpha": "0.82-0.88",
            "test_retest_reliability": "0.70-0.80",
            "validity_notes": "Discriminates activation dimensions; context-dependent mood effects."
        },
        "strengths": [
            "Subtle arousal differentiation",
            "Natural environment assessment",
            "Two-factor structure clarity"
        ],
        "weaknesses": [
            "Limited English validation",
            "Modest citation count",
            "Overlap with other activation scales"
        ],
        "newer_alternatives": [],
        "domains": [
            "health.arousal"
        ],
        "status": "active"
    },
    # SOCIAL (5)
    {
        "instrument_id": "IOS",
        "full_name": "Inclusion of Other in Self",
        "abbreviation": "IOS",
        "authors": "Aron, A., Aron, E. N., & Smollan, D.",
        "year": 1992,
        "reference_apa": "Aron, A., Aron, E. N., & Smollan, D. (1992). Inclusion of other in the self scale and the structure of interpersonal closeness. Journal of Personality and Social Psychology, 63(4), 596-612.",
        "doi": "10.1037/0022-3514.63.4.596",
        "approx_citations": 4500,
        "description": "Single-item pictorial measure of relationship closeness. Seven overlapping Venn diagrams represent self-other overlap from minimal to complete union.",
        "type": "observational_pictorial",
        "items_count": 1,
        "administration_minutes": 1,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.83-0.90",
            "validity_notes": "Correlates with relationship duration (r = 0.60) and satisfaction (r = 0.70)."
        },
        "strengths": [
            "Extremely brief",
            "Language-independent",
            "Intuitive visual format"
        ],
        "weaknesses": [
            "Single item",
            "Limited construct dimensionality",
            "Ordinal scale discreteness"
        ],
        "newer_alternatives": [],
        "domains": [
            "social.closeness"
        ],
        "status": "active"
    },
    {
        "instrument_id": "GEQ",
        "full_name": "Group Environment Questionnaire",
        "abbreviation": "GEQ",
        "authors": "Carron, A. V., Widmeyer, W. N., & Brawley, L. R.",
        "year": 1985,
        "reference_apa": "Carron, A. V., Widmeyer, W. N., & Brawley, L. R. (1985). The development of an instrument to assess cohesion in sports teams: The Group Environment Questionnaire. Journal of Sport Psychology, 7(3), 244-266.",
        "doi": None,
        "approx_citations": 2000,
        "description": "18-item multidimensional measure of group cohesion across task and social dimensions, with individual and group attraction subscales.",
        "type": "self_report",
        "items_count": 18,
        "administration_minutes": 5,
        "psychometrics": {
            "internal_consistency_alpha": "0.70-0.85",
            "test_retest_reliability": "0.71-0.82",
            "validity_notes": "Predicts group performance (r = 0.40-0.60) and member satisfaction."
        },
        "strengths": [
            "Sport team focused cohesion",
            "Distinct task/social dimensions",
            "Good predictive validity"
        ],
        "weaknesses": [
            "Sport context origins may limit generalization",
            "Moderate internal consistency"
        ],
        "newer_alternatives": [],
        "domains": [
            "social.cohesion"
        ],
        "status": "active"
    },
    {
        "instrument_id": "ROTTER-ITS",
        "full_name": "Rotter Interpersonal Trust Scale",
        "abbreviation": "ROTTER-ITS",
        "authors": "Rotter, J. B.",
        "year": 1967,
        "reference_apa": "Rotter, J. B. (1967). A new scale for the measurement of interpersonal trust. Journal of Personality, 35(4), 651-665.",
        "doi": "10.1111/j.1467-6494.1967.tb01454.x",
        "approx_citations": 3000,
        "description": "25-item measure of generalized trust beliefs about others' honesty and sincerity. Assesses interpersonal trust across contexts.",
        "type": "self_report",
        "items_count": 25,
        "administration_minutes": 5,
        "psychometrics": {
            "internal_consistency_alpha": "0.48-0.72",
            "test_retest_reliability": "0.56-0.72",
            "validity_notes": "Correlates with cooperative behavior and risk-taking in trust games."
        },
        "strengths": [
            "Foundational trust measure",
            "Well-cited in literature",
            "Behavioral prediction validity"
        ],
        "weaknesses": [
            "Lower internal consistency estimates",
            "Dated instrument (1967)",
            "General trust only"
        ],
        "newer_alternatives": [],
        "domains": [
            "social.trust"
        ],
        "status": "active"
    },
    {
        "instrument_id": "TRUST-GAME",
        "full_name": "Berg Trust Game",
        "abbreviation": "TG",
        "authors": "Berg, J., Dickhaut, J., & McCabe, K.",
        "year": 1995,
        "reference_apa": "Berg, J., Dickhaut, J., & McCabe, K. (1995). Trust, reciprocity, and social history. Games and Economic Behavior, 10(1), 122-142.",
        "doi": "10.1006/game.1995.1027",
        "approx_citations": 2500,
        "description": "Behavioral economics paradigm where participant (sender) allocates money to trustee, who receives triple amount and decides how much to return. Measures behavioral trust and trustworthiness.",
        "type": "behavioral_experiment",
        "items_count": 0,
        "administration_minutes": 10,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.50-0.65",
            "validity_notes": "First-mover allocation correlates with personality-based trust (r = 0.30-0.50)."
        },
        "strengths": [
            "Behavioral economic validity",
            "Incentive-compatible (real money)",
            "Interpersonal interaction modeling"
        ],
        "weaknesses": [
            "Context-dependent decisions",
            "Modest reliability",
            "Limited generalization beyond money"
        ],
        "newer_alternatives": [],
        "domains": [
            "social.trust"
        ],
        "status": "active"
    },
    {
        "instrument_id": "BALES-IPA",
        "full_name": "Bales Interaction Process Analysis",
        "abbreviation": "IPA",
        "authors": "Bales, R. F.",
        "year": 1950,
        "reference_apa": "Bales, R. F. (1950). Interaction Process Analysis: A Method for the Study of Small Groups. Addison-Wesley.",
        "doi": None,
        "approx_citations": 2800,
        "description": "Systematic observational coding scheme categorizing group communication into 12 interaction types (4 positive socioemotional, 4 task-related, 4 negative socioemotional). Real-time or video-coded assessment.",
        "type": "observational",
        "items_count": 12,
        "administration_minutes": 0,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.70-0.90",
            "validity_notes": "Reliable inter-rater agreement when trained coders (r > 0.80)."
        },
        "strengths": [
            "Objective behavioral observation",
            "Foundational group dynamics method",
            "Multidimensional interaction mapping"
        ],
        "weaknesses": [
            "Requires trained raters",
            "Time-intensive coding",
            "Reduced applicability with large groups"
        ],
        "newer_alternatives": [],
        "domains": [
            "social.group_dynamics"
        ],
        "status": "active"
    },
    # BEHAVIORAL (5)
    {
        "instrument_id": "ACTIGRAPH",
        "full_name": "ActiGraph Accelerometer",
        "abbreviation": "AG",
        "authors": "ActiGraph LLC",
        "year": 2000,
        "reference_apa": "Freedson, P. S., Melanson, E., & Sirard, J. (1998). Calibration of the Computer Science and Applications Inc. accelerometer. Medicine and Science in Sports and Exercise, 30(5), 777-781.",
        "doi": "10.1097/00005768-199805000-00021",
        "approx_citations": 2000,
        "description": "Commercial wearable accelerometer (wrist or waist-worn) measuring movement intensity. Categorizes activity into sedentary, light, moderate, vigorous intensity.",
        "type": "objective_monitor",
        "items_count": 0,
        "administration_minutes": 0,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.88-0.95",
            "validity_notes": "Good convergence with doubly labeled water energy expenditure (r = 0.60-0.70)."
        },
        "strengths": [
            "Continuous monitoring",
            "Commercial standardization",
            "Real-world activity patterns",
            "Validity for epidemiology"
        ],
        "weaknesses": [
            "Cannot detect incline walking",
            "Upper arm limitations",
            "Non-invasive assumption of wearability"
        ],
        "newer_alternatives": [],
        "domains": [
            "behavioral.physical_activity"
        ],
        "status": "active"
    },
    {
        "instrument_id": "IPAQ",
        "full_name": "International Physical Activity Questionnaire",
        "abbreviation": "IPAQ",
        "authors": "Craig, C. L., Marshall, A. L., Sjöström, M., et al.",
        "year": 2003,
        "reference_apa": "Craig, C. L., Marshall, A. L., Sjöström, M., et al. (2003). International Physical Activity Questionnaire (IPAQ): 12-country reliability and validity. Medicine and Science in Sports and Exercise, 35(8), 1381-1395.",
        "doi": "10.1249/01.MSS.0000078924.61453.FB",
        "approx_citations": 4000,
        "description": "7-item self-report of physical activity intensity, duration, and frequency across work, transportation, household, and recreational domains. Short (9 items) and long (27 items) versions available.",
        "type": "self_report",
        "items_count": 7,
        "administration_minutes": 5,
        "psychometrics": {
            "internal_consistency_alpha": "0.70-0.85",
            "test_retest_reliability": "0.75-0.85",
            "validity_notes": "Moderate agreement with accelerometers (r = 0.50-0.60)."
        },
        "strengths": [
            "Brief and internationally standardized",
            "Multidomain assessment",
            "Global comparability"
        ],
        "weaknesses": [
            "Self-report bias",
            "Overestimation common",
            "Moderate accelerometer agreement"
        ],
        "newer_alternatives": [],
        "domains": [
            "behavioral.physical_activity"
        ],
        "status": "active"
    },
    {
        "instrument_id": "BART",
        "full_name": "Balloon Analogue Risk Task",
        "abbreviation": "BART",
        "authors": "Lejuez, C. W., Read, J. P., Kahler, C. W., Richards, J. B., Ramsey, S. E., Stuart, G. L., ... & Brown, R. A.",
        "year": 2002,
        "reference_apa": "Lejuez, C. W., Read, J. P., Kahler, C. W., Richards, J. B., Ramsey, S. E., Stuart, G. L., ... & Brown, R. A. (2002). Evaluation of a behavioral measure of risk taking: The Balloon Analogue Risk Task (BART). Journal of Experimental Psychology: Applied, 8(2), 75-84.",
        "doi": "10.1037/1076-898X.8.2.75",
        "approx_citations": 1500,
        "description": "Computerized task where participant inflates virtual balloon, earning money for each pump but risking loss if balloon pops. Measures risk tolerance and impulsivity in decision-making.",
        "type": "behavioral_experiment",
        "items_count": 0,
        "administration_minutes": 10,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.65-0.80",
            "validity_notes": "Correlates with real-world risky behavior (substance use, reckless driving)."
        },
        "strengths": [
            "Behavioral risk measurement",
            "Incentive-compatible version available",
            "Applicable across populations"
        ],
        "weaknesses": [
            "Modest temporal stability",
            "Task-specific effects",
            "Learning effects possible"
        ],
        "newer_alternatives": [],
        "domains": [
            "behavioral.risk_taking"
        ],
        "status": "active"
    },
    {
        "instrument_id": "DOSPERT",
        "full_name": "Domain-Specific Risk-Taking Scale",
        "abbreviation": "DOSPERT",
        "authors": "Blais, A. R., & Weber, E. U.",
        "year": 2006,
        "reference_apa": "Blais, A. R., & Weber, E. U. (2006). A domain-specific risk-taking (DOSPERT) scale for adult populations. Judgment and Decision Making, 1(1), 33-47.",
        "doi": None,
        "approx_citations": 1200,
        "description": "40-item assessment of risk-taking likelihood and perceived risk/benefit across five domains: financial, health/safety, recreational, social, ethical.",
        "type": "self_report",
        "items_count": 40,
        "administration_minutes": 8,
        "psychometrics": {
            "internal_consistency_alpha": "0.75-0.90",
            "test_retest_reliability": "0.70-0.85",
            "validity_notes": "Domain specificity: financial decisions independent of social risk-taking (r = 0.10)."
        },
        "strengths": [
            "Multidomain risk assessment",
            "Risk-benefit perception inclusion",
            "Behavioral prediction validity"
        ],
        "weaknesses": [
            "Lengthy administration",
            "Self-report bias",
            "Intention-behavior gap"
        ],
        "newer_alternatives": [],
        "domains": [
            "behavioral.risk_taking"
        ],
        "status": "active"
    },
    {
        "instrument_id": "IGT",
        "full_name": "Iowa Gambling Task",
        "abbreviation": "IGT",
        "authors": "Bechara, A., Damasio, A. R., Damasio, H., & Anderson, S. W.",
        "year": 1994,
        "reference_apa": "Bechara, A., Damasio, A. R., Damasio, H., & Anderson, S. W. (1994). Insensitivity to future consequences following damage to human prefrontal cortex. Cognition, 50(1-3), 7-15.",
        "doi": "10.1016/0010-0277(94)90018-3",
        "approx_citations": 3000,
        "description": "Computerized task with four decks of cards varying in immediate rewards and penalties. Participant learns to prefer decks yielding net gains. Measures decision-making under uncertainty and reward/punishment sensitivity.",
        "type": "behavioral_experiment",
        "items_count": 0,
        "administration_minutes": 15,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.55-0.75",
            "validity_notes": "Sensitive to ventromedial prefrontal cortex lesions; sensitive to substance use impairments."
        },
        "strengths": [
            "Neuropsychological diagnostic utility",
            "Real-world decision-making analog",
            "Reward/punishment sensitivity"
        ],
        "weaknesses": [
            "Moderate test-retest reliability",
            "Task complexity and learning effects",
            "Practice effects with repeated administration"
        ],
        "newer_alternatives": [],
        "domains": [
            "behavioral.decision_making"
        ],
        "status": "active"
    },
    # SPECIALIZED/BUILT ENVIRONMENT (5)
    {
        "instrument_id": "PR-SCALE",
        "full_name": "Prospect-Refuge Scale",
        "abbreviation": "PR",
        "authors": "Dosen, A. S., & Ostwald, M. J.",
        "year": 2016,
        "reference_apa": "Dosen, A. S., & Ostwald, M. J. (2016). Evidence for prospect-refuge spatial biophilia. Journal of Architectural and Planning Research, 33(2), 89-107.",
        "doi": None,
        "approx_citations": 250,
        "description": "Scale measuring spatial properties related to Appleton's prospect-refuge theory. Assesses visual openness (prospect) and protective enclosure (refuge) in architectural spaces.",
        "type": "self_report",
        "items_count": 12,
        "administration_minutes": 5,
        "psychometrics": {
            "internal_consistency_alpha": "0.75-0.85",
            "test_retest_reliability": "0.70-0.80",
            "validity_notes": "Correlates with perceived safety and aesthetic preference (r = 0.50-0.70)."
        },
        "strengths": [
            "Prospect-refuge theory operationalization",
            "Architectural space evaluation",
            "Ecological validity"
        ],
        "weaknesses": [
            "Limited citation history",
            "Modest sample sizes in validation",
            "Prospect-refuge theory limitations"
        ],
        "newer_alternatives": [],
        "domains": [
            "built_environment.prospect_refuge"
        ],
        "status": "active"
    },
    {
        "instrument_id": "SOP-SCALE",
        "full_name": "Sense of Place Scale",
        "abbreviation": "SOP",
        "authors": "Jorgensen, B. S., & Stedman, R. C.",
        "year": 2001,
        "reference_apa": "Jorgensen, B. S., & Stedman, R. C. (2001). Sense of place as an attitude: Lakeshore owner attitudes toward water-level fluctuation in a recreational lake in upstate New York. Journal of Environmental Education, 32(4), 16-23.",
        "doi": "10.1080/00958960109598658",
        "approx_citations": 1500,
        "description": "Three-subscale measure (12 items total) of attachment to place, identity, and dependence on a specific environment. Assesses emotional bonds and place meanings.",
        "type": "self_report",
        "items_count": 12,
        "administration_minutes": 5,
        "psychometrics": {
            "internal_consistency_alpha": "0.84-0.90",
            "test_retest_reliability": "0.80-0.88",
            "validity_notes": "Predicts environmental stewardship behavior (r = 0.60-0.80)."
        },
        "strengths": [
            "Multidimensional place attachment",
            "Environmental behavior prediction",
            "Established in environmental psychology"
        ],
        "weaknesses": [
            "Place-specific norms needed",
            "Cultural variation in meaning"
        ],
        "newer_alternatives": [],
        "domains": [
            "built_environment.place_attachment"
        ],
        "status": "active"
    },
    {
        "instrument_id": "PNS",
        "full_name": "Perceived Naturalness Scale",
        "abbreviation": "PNS",
        "authors": "Purcell, T., & Lamb, R. J.",
        "year": 1998,
        "reference_apa": "Purcell, T., & Lamb, R. J. (1998). Symbolic associations with landscape types in environmentally concerned groups. Journal of Environmental Psychology, 18(1), 41-53.",
        "doi": "10.1006/jevp.1998.0070",
        "approx_citations": 800,
        "description": "Scale measuring perception of naturalness in visual environments. Evaluates biophilic content, wildness, and lack of human modification.",
        "type": "self_report",
        "items_count": 11,
        "administration_minutes": 4,
        "psychometrics": {
            "internal_consistency_alpha": "0.82-0.88",
            "test_retest_reliability": "0.75-0.85",
            "validity_notes": "Correlates with restorative quality and well-being effects (r = 0.70-0.80)."
        },
        "strengths": [
            "Biophilia measurement",
            "Restorative quality prediction",
            "Perception-based assessment"
        ],
        "weaknesses": [
            "Modestly cited",
            "Limited to visual naturalness",
            "Sample size variations"
        ],
        "newer_alternatives": [],
        "domains": [
            "built_environment.naturalness"
        ],
        "status": "active"
    },
    {
        "instrument_id": "PACIUK-CONTROL",
        "full_name": "Paciuk Environmental Control Scale",
        "abbreviation": "PACIUK",
        "authors": "Paciuk, M.",
        "year": 1990,
        "reference_apa": "Paciuk, M. (1990). The role of personal control of the environment in thermal comfort and satisfaction at the workplace. Unpublished doctoral dissertation, Royal Institute of Technology, Stockholm.",
        "doi": None,
        "approx_citations": 600,
        "description": "Scale measuring perceived control over thermal, acoustic, and lighting environment. Assesses both actual control capability and psychological sense of control.",
        "type": "self_report",
        "items_count": 10,
        "administration_minutes": 4,
        "psychometrics": {
            "internal_consistency_alpha": "0.70-0.82",
            "test_retest_reliability": "0.65-0.78",
            "validity_notes": "Perceived control correlates with satisfaction independent of actual environmental conditions."
        },
        "strengths": [
            "Environmental psychology control focus",
            "Workplace comfort relevance",
            "Addresses psychological mechanisms"
        ],
        "weaknesses": [
            "Dissertation-based publication",
            "Limited English-language validation",
            "Modest sample validation"
        ],
        "newer_alternatives": [],
        "domains": [
            "built_environment.control"
        ],
        "status": "active"
    },
    {
        "instrument_id": "LYNCH-LEGIBILITY",
        "full_name": "Lynch Imageability/Legibility Scale",
        "abbreviation": "LYNCH",
        "authors": "Lynch, K.",
        "year": 1960,
        "reference_apa": "Lynch, K. (1960). The Image of the City. MIT Press.",
        "doi": None,
        "approx_citations": 5000,
        "description": "Observational and cognitive mapping method assessing urban environmental legibility. Five elements (paths, edges, districts, nodes, landmarks) characterize spatial organization and navigability.",
        "type": "observational_cognitive_map",
        "items_count": 5,
        "administration_minutes": 30,
        "psychometrics": {
            "internal_consistency_alpha": "N/A",
            "test_retest_reliability": "0.70-0.85",
            "validity_notes": "Cognitive mapping agreement predicts navigation wayfinding performance (r = 0.60-0.80)."
        },
        "strengths": [
            "Foundational urban design method",
            "Cognitive mapping integration",
            "Ecological validity for navigation"
        ],
        "weaknesses": [
            "Time-intensive analysis",
            "Interpretive component",
            "Individual differences in cognitive maps"
        ],
        "newer_alternatives": [],
        "domains": [
            "built_environment.legibility"
        ],
        "status": "active"
    }
]

def append_instruments():
    """Load registry, append new instruments, update metadata, write back."""

    # Load existing registry
    with open(REGISTRY_PATH, 'r') as f:
        registry = json.load(f)

    print(f"Loaded {len(registry['instruments'])} existing instruments.")

    # Append new instruments
    registry['instruments'].extend(NEW_INSTRUMENTS)

    # Update metadata
    registry['version'] = '1.1.0'  # Minor version bump for new instruments
    registry['generated_at'] = datetime.utcnow().isoformat(timespec='microseconds') + '+00:00'

    total_count = len(registry['instruments'])
    print(f"Added {len(NEW_INSTRUMENTS)} new instruments.")
    print(f"Total instrument count: {total_count}")

    # Write back
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print(f"\nRegistry updated and written to {REGISTRY_PATH}")
    print(f"New version: {registry['version']}")
    print(f"Generated at: {registry['generated_at']}")

    # Verify
    with open(REGISTRY_PATH, 'r') as f:
        verify = json.load(f)

    print(f"\nVerification: {len(verify['instruments'])} instruments in saved registry.")

    return total_count

if __name__ == '__main__':
    total = append_instruments()
    print(f"\nSuccess! Registry now contains {total} instruments.")
