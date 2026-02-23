# Gap Panel JSON Extraction Log

This document serves as a persistent ledger of which neuroscience consensus panel reports have been successfully parsed, with their JSON templates extracted and written into `data/templates/`. 

**CRITICAL SAFEGUARD**: Before running `scripts/extract_panel_json.py` on any new panel output, check this log. Do not re-extract a panel that has already been extracted unless you are explicitly updating its templates from a revised panel document. The extraction script has been updated to match existing templates by *both* `template_id` and `display_id` to prevent duplication, but maintaining this log ensures workflow provenance.

## Extracted Panels

### 1. STRESS-I
* **Source Document**: `docs/STRESS_I_Panel_Output_Feb21.md`
* **Extraction Date**: 2026-02-21
* **Templates Extracted**: 
  - `T6` (Cortisol-Hippocampal Cascade)
  - `T7` (Allostatic Anticipation)
  - `T14` (Navigation-Stress Vicious Cycle)

### 2. LIGHT-I
* **Source Document**: `docs/LIGHT_I_Panel_Output_Feb21.md`
* **Extraction Date**: 2026-02-21
* **Templates Extracted**: 
  - `L3_daylight_multichannel_convergence`
  - `L2_circadian_architectural_regulation`
  - `T55` (NM_CIRCADIAN_ENTRAINMENT_001)
  - `L4_cct_temporal_ecological`
  - `L5_dynamic_light_temporal_pe`
  - `T30` (CHRONO_LIGHT_ENTRAINMENT_001)
  - `T70` (CIRCADIAN_ARCH_REGULATION_001)
  - `CB2` (CB_SLEEP_ARCHITECTURE_002)

### 3. SPATIAL-I
* **Source Document**: `docs/SPATIAL_I_Panel_Output_Feb21.md`
* **Extraction Date**: 2026-02-21
* **Templates Extracted**: 
  - `SPATIAL_INTEGRATION_PE_001` (SC1)
  - `SC2_isovist_visual_prediction` (SC2)
  - `ARCH_PROMENADE_TEMPORAL_PE_001` (SC3)
  - `SC4_spatial_social_encounter` (SC4)
  - *Note*: An issue where evolving `template_id` fields (`SPATIAL_INTEGRATION_NAV_PE_001` -> `SPATIAL_INTEGRATION_PE_001`) caused duplicate files alongside legacy `SC1` strings has been resolved. The extractor now maps via `display_id` as well.

---
*Note: Ensure you update this log whenever new `.md` panel output files are fed into `scripts/extract_panel_json.py`.*
