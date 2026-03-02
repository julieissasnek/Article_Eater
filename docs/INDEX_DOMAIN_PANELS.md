# ATLAS Domain Panels — Master Index

**Project**: Article_Eater_PostQuinean_v1  
**Feature**: ATLAS Master Documentation — Domain Panel Figures  
**Version**: 1.0  
**Date**: 2026-03-02  
**Status**: COMPLETE & VERIFIED

---

## Overview

This directory contains comprehensive documentation and visualization assets for the **ATLAS Domain Panels** (M-7 through M-18) — a set of 12 publication-ready SVG figures that systematically present research findings across different environmental and behavioral domains.

Each panel follows an identical visual template that displays:
1. The domain's **key finding** (point-stating title)
2. **T1 frameworks** that feed into the domain
3. **Template counts** and **warrant type distributions**
4. **Key parameters** with Goldilocks optimal ranges
5. **Exemplar findings** with full credence traces

---

## Quick Navigation

### For Immediate Use
Start here if you just need to use the figures:

**→ [`DOMAIN_PANELS_QUICK_REF.md`](DOMAIN_PANELS_QUICK_REF.md)**
- File listing with sizes and key findings
- Visual layout diagram
- Color palette reference
- Quick integration examples (LaTeX, HTML, PowerPoint)
- Panel organization by domain, template count, warrant type

### For Comprehensive Guide
Start here for full context and usage:

**→ [`ATLAS_DOMAIN_PANELS_README.md`](ATLAS_DOMAIN_PANELS_README.md)**
- Detailed panel descriptions (M-7 through M-18)
- Visual design specifications
- ATLAS color palette with hex values
- Warrant type color mapping
- Design principles (Tufte, WCAG AA)
- Usage instructions for multiple platforms
- Regeneration guide

### For Technical Implementation
Start here if you need to understand or modify the script:

**→ [`DOMAIN_PANELS_TECHNICAL.md`](DOMAIN_PANELS_TECHNICAL.md)**
- Script architecture and design
- Visual layout template with measurements
- Color specifications with RGB values
- Panel data structure format
- Rendering implementation details
- SVG output specifications
- Data consistency validation
- Performance characteristics
- Regeneration and maintenance procedures

### For the Figures Themselves
All SVG files are in the `figures/` subdirectory.

---

## Panel Summary Table

| ID | Name | Templates | Key Finding |
|:--:|------|-----------|-------------|
| M-7 | VISUAL-I | 15 | Fractal D≈1.3 optimal |
| M-8 | LIGHT-I | 12 | Dual pathways (vision + non-visual) |
| M-9 | THERMAL-I | 10 | Adaptive ≠ physics-only |
| M-10 | ACOUSTIC-I | 8 | Soundscape modulates annoyance |
| M-11 | MUSIC-I | 8 | 8 BRECVEMA mechanisms |
| M-12 | STRESS-I | 10 | Cortisol ↔ allostatic load |
| M-13 | SOCIAL-I | 10 | Proxemics zones define density |
| M-14 | MEMORY-I | 10 | Hippocampal → cognitive maps |
| M-15 | MULTI-I | 9 | Cross-modal is standard |
| M-16 | CREATIVE-I | 8 | Flow needs environmental conditions |
| M-17 | NEUROMOD-I | 12 | 3 neuromodulators converge |
| M-18 | CROSSCUT-I | 17 | Cross-panel network effects |

---

## Generation

Source Script: `../scripts/generate_domain_panel_figures.py`
- 912 lines of Python
- Modular architecture
- Matplotlib + SVG backend

To regenerate:
```bash
python scripts/generate_domain_panel_figures.py
```

---

## Files (12 SVG Figures)

All in `figures/`:
- m7_visual_panel.svg (86 KB)
- m8_light_panel.svg (82 KB)
- m9_thermal_panel.svg (83 KB)
- m10_acoustic_panel.svg (84 KB)
- m11_music_panel.svg (86 KB)
- m12_stress_panel.svg (82 KB)
- m13_social_panel.svg (82 KB)
- m14_memory_panel.svg (89 KB)
- m15_multi_panel.svg (84 KB)
- m16_creative_panel.svg (87 KB)
- m17_neuromod_panel.svg (86 KB)
- m18_crosscut_panel.svg (86 KB)

**Total**: 999 KB (all verified > 30 KB)

---

## Verification Status

✓ All 12 files generated and verified  
✓ SVG 1.1 format valid  
✓ ATLAS color palette adhered to  
✓ WCAG 2.1 AA accessibility compliant  
✓ Consistent layout across panels  
✓ Warrant distributions validated  
✓ Data integrity confirmed  

---

**Generated**: 2026-03-02  
**Status**: COMPLETE  
