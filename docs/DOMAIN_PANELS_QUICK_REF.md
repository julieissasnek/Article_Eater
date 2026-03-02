# ATLAS Domain Panels — Quick Reference Card

**Generated**: 2026-03-02  
**Panels**: M-7 through M-18 (12 total)  
**Format**: SVG 1.1 (vector)  
**Total Size**: 999 KB

---

## File Listing (12 SVG Figures)

| Panel | Filename | Size | Templates | Key Finding |
|-------|----------|------|-----------|-------------|
| M-7 | m7_visual_panel.svg | 86 KB | 15 | Fractal dimension at D≈1.3 |
| M-8 | m8_light_panel.svg | 82 KB | 12 | Two pathways: vision + regulation |
| M-9 | m9_thermal_panel.svg | 83 KB | 10 | Adaptive comfort ≠ physics |
| M-10 | m10_acoustic_panel.svg | 84 KB | 8 | Soundscape modulates annoyance |
| M-11 | m11_music_panel.svg | 86 KB | 8 | Eight BRECVEMA mechanisms |
| M-12 | m12_stress_panel.svg | 82 KB | 10 | Cortisol dynamics reveal allostasis |
| M-13 | m13_social_panel.svg | 82 KB | 10 | Proxemics zones optimal density |
| M-14 | m14_memory_panel.svg | 89 KB | 10 | Hippocampal → cognitive maps |
| M-15 | m15_multi_panel.svg | 84 KB | 9 | Cross-modal is the rule |
| M-16 | m16_creative_panel.svg | 87 KB | 8 | Flow requires conditions |
| M-17 | m17_neuromod_panel.svg | 86 KB | 12 | 3 neuromodulators converge |
| M-18 | m18_crosscut_panel.svg | 86 KB | 17 | Cross-panel network interactions |

---

## Visual Layout (All Panels)

```
┌─────────────────────────────────┐
│  M-N: NAME (§XX)                │
│  " Key Finding (Point-Stating) "│
├─────────┬───────────┬───────────┤
│ T1 FW   │ TEMPLATES │ PARAMETERS│
│ [3 boxes│ & WARRANTS│ [3 bars]  │
│  w/     │ [Stacked  │           │
│  arrows]│  bar]     │           │
├─────────────────────────────────┤
│ EXEMPLAR: Finding → d/ω/δ → C   │
├─────────────────────────────────┤
│         M-N | ATLAS Master      │
└─────────────────────────────────┘
```

---

## Color Palette (7 colors)

| Name | Hex | Use |
|------|-----|-----|
| Deep Navy | #1B2A4A | Titles |
| Slate Blue | #2E5090 | Borders |
| Warm Gold | #D4A843 | Highlights |
| Sage Green | #5B8C5A | Evidence |
| Terracotta | #C17B4A | Warnings |
| Cool Gray | #8B9DAF | Secondary |
| Cream | #F5F0E8 | Canvas |

---

## Warrant Types (4 colors)

| Type | Color | Abbrev |
|------|-------|--------|
| EMPIRICAL_ASSOCIATION | Sage Green | EA |
| MECHANISM | Warm Gold | M |
| THEORY_DERIVED | Slate Blue | TD |
| ANALOGICAL | Terracotta | AN |

---

## Quick Commands

### Generate All Figures
```bash
cd /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1
python scripts/generate_domain_panel_figures.py
```

### View a Specific Panel
```bash
# SVG files can be opened in:
# - Web browsers (Chrome, Firefox, Safari)
# - Vector editors (Inkscape, Adobe Illustrator)
# - Image viewers (Preview on macOS)
open docs/figures/m7_visual_panel.svg
```

### Check File Sizes
```bash
ls -lh docs/figures/m*.svg | grep -E "m[0-9]"
```

---

## Integration Examples

### LaTeX
```latex
\includegraphics[width=\textwidth]{docs/figures/m7_visual_panel.svg}
```

### HTML
```html
<img src="docs/figures/m7_visual_panel.svg" alt="M-7: VISUAL-I">
```

### Markdown
```markdown
![M-7: VISUAL-I](docs/figures/m7_visual_panel.svg)
```

### PowerPoint
Drag SVG directly into slide

---

## Key Design Features

1. **Consistent Layout** → All panels identical structure
2. **Tufte-Optimized** → Max data-ink, min decoration
3. **WCAG AA** → Accessible color contrast (4.5:1)
4. **Vectorized** → Infinitely scalable
5. **Warranted** → Credence traces shown

---

## Panel Organization

### By Domain
- **Visual**: M-7
- **Light**: M-8
- **Thermal**: M-9
- **Acoustic**: M-10
- **Music**: M-11
- **Stress**: M-12
- **Social**: M-13
- **Memory**: M-14
- **Multi-sensory**: M-15
- **Creative**: M-16
- **Neuromodulation**: M-17
- **Cross-cutting**: M-18

### By Template Count
| Range | Panels |
|-------|--------|
| 8 | M-10, M-11, M-16 |
| 9 | M-15 |
| 10 | M-9, M-12, M-13, M-14 |
| 12 | M-8, M-17 |
| 15 | M-7 |
| 17 | M-18 |

### By Warrant Distribution
| Dominant Type | Panels |
|---------------|--------|
| EMPIRICAL_ASSOCIATION | M-7, M-9, M-10, M-12, M-13 |
| MECHANISM | M-8, M-11, M-14, M-15 |
| THEORY_DERIVED | M-16, M-17, M-18 |

---

## Exemplar Pattern

All exemplars follow same format:
```
Finding Name → d: 0.XX → ω: 0.XX → δ: 0.XX → credence: 0.XX
```

Where:
- **d** = initial evidence strength
- **ω** = warrant weight/reliability
- **δ** = coherence/dependence adjustment
- **credence** = final warranted confidence

---

## Data Integrity Checks

✓ All 12 files exist  
✓ All > 30 KB (content present)  
✓ Valid SVG 1.1 XML  
✓ Colors ATLAS-compliant  
✓ Warrant distributions sum to template count  
✓ Parameter ranges normalized  
✓ Framework assignments deterministic  

---

## File Locations

```
Article_Eater_PostQuinean_v1/
├── scripts/
│   └── generate_domain_panel_figures.py  (912 lines)
├── docs/
│   ├── figures/
│   │   ├── m7_visual_panel.svg
│   │   ├── m8_light_panel.svg
│   │   ├── ... (12 total)
│   │   └── m18_crosscut_panel.svg
│   ├── ATLAS_DOMAIN_PANELS_README.md    (comprehensive guide)
│   ├── DOMAIN_PANELS_TECHNICAL.md       (implementation details)
│   └── DOMAIN_PANELS_QUICK_REF.md       (this file)
```

---

## Support

For questions or modifications:

1. **Data changes**: Edit `PANELS` dict in script, re-run
2. **Color changes**: Edit `COLORS` dict in script, re-run
3. **Layout changes**: Modify drawing functions, re-run
4. **Format changes**: Adjust `fig.savefig()` parameters

---

**Last Updated**: 2026-03-02
