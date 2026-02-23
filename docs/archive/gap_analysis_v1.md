
# Gap Analysis Report (v1.0)
**Date**: 2026-02-17
**Task**: CC-4 (Gap Analysis)

## 1. Executive Summary
The Theory Tier (Tier 2 Integration) is partially complete. While Attention Restoration Theory (ART) and Biophilia are well-represented with Reductions RC1-RC7, **Stress Recovery Theory (SRT) is entirely missing** from the reduction layer. Additionally, structural inconsistencies were found in `RC4` (Prospect-Refuge).

## 2. Reduction Coverage Analysis

| Theory Domain | Construct | Reduction Claim ID | Status | Notes |
|---|---|---|---|---|
| **ART** | Soft Fascination | `RC1` | **COMPLETE** | Uses T2, T27, T31 |
| **ART** | Being Away | `RC2` | **COMPLETE** | Uses T23, T29 |
| **ART** | Extent | `RC3` | **COMPLETE** | Uses T3, T14 |
| **ART** | Compatibility | `RC7` | **COMPLETE** | Uses T1, T8, T45 |
| **Biophilia** | Prospect-Refuge | `RC4` | **PARTIAL** | Structure exists but has data integrity issues (see below). |
| **Biophilia** | Convergence | `RC5` | **COMPLETE** | Uses T53, T58, T71, T76 |
| **Biophilia** | Social Engagement | `RC6` | **COMPLETE** | Uses T48, T49, T65, T66 |
| **SRT** | Stress Recovery | - | **MISSING** | No reduction for basic stress recovery curve (Ulrich). |
| **SRT** | Parasympathetic Activation | - | **MISSING** | No reduction linking nature -> vagal tone. |
| **SRT** | Affective Response | - | **MISSING** | No reduction for rapid affective precedence (Zajonc/Ulrich). |

## 3. Structural Integrity Findings

### Critical Error in RC4 (Prospect-Refuge)
- **Issue**: The `template_nodes` array lists `ISOVIST_VISUAL_PREDICTION_001`, `ENCLOSURE_SAFETY_030`, `SPATIAL_INTEGRATION_NAV_PE_001`.
- **Reality**: The `reduction_edges` reference `NM_VAGAL_REGULATION_001` (T65), which is **missing** from `template_nodes`.
- **Impact**: Graph traversal algorithms will fail or misreport connectivity for Prospect-Refuge.

### Orphaned Templates
The following templates are implemented but likely not linked to any Reduction Claim (based on SRT absence):
- **T5 (NM_THREAT_HPA_001)**: Core stress mechanism.
- **T9 (DP_IMPLICIT_EVALUATION_001)**: Rapid affect.
- **T65 (NM_VAGAL_REGULATION_001)**: Although used in RC6 (Social) and RC4 (Prospect), it lacks its primary theoretical home (SRT).

## 4. Recommendations

### Priority 1: Implement SRT Reductions
Create `RC8` (Stress Recovery) and `RC9` (Rapid Affect) to complete the "Big Three" theoretical frameworks.
- **RC8 Components**: T29 (Allostasis), T65 (Vagal), T5 (HPA Axis).
- **RC9 Components**: T9 (Implicit Eval), T22 (Rapid Gist).

### Priority 2: Fix RC4 Integrity
Update `RC4.json` to include `NM_VAGAL_REGULATION_001` in the `template_nodes` list.

### Priority 3: Systematic Audit
Run a script to ensure every `to_node` and `from_node` in `reduction_edges` is explicitly listed in `template_nodes`.
