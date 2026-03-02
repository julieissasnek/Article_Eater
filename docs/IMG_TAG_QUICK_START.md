# IMG-TAG Quick Start Guide

This guide helps you get started with image tagging for environmental psychology research.

---

## 5-Minute Setup

### 1. Initialize the Service

```python
from src.services.image_tag_service import ImageTagService

service = ImageTagService()
print(service.get_vocabulary_summary())
```

### 2. Tag Your First Image

```python
tags = {
    "spatial-properties": {
        "spatial-volume": {"value": 60},
        "spatial-enclosure-degree": {"value": "semi-enclosed (partial barriers, >180° view)"},
    },
    "vegetation": {
        "vegetation-presence": {"value": "abundant (major vegetation component, 25-50%)"},
        "vegetation-density": {"value": 40},
    },
    "lighting": {
        "lighting-source-type": {"value": "natural-daylight-diffuse"},
    },
}

record = service.tag_image(
    image_id="my-image-001",
    tags=tags,
    tagged_by="me",
    source_paper_id="10.1234/example"
)

print(f"Naturalness: {record['domain_scores']['naturalness']['score']}")
print(f"Relevant templates: {[t['template_id'] for t in record['relevant_templates']]}")
```

---

## Understanding the 7 Domains

### Quick Reference Table

| Domain | What to Tag | Examples |
|--------|------------|----------|
| **Spatial Properties** | Room volume, enclosure, view distance | Open plaza (90), office (40), forest trail (50) |
| **Lighting** | Source (sun/lamp), brightness, color | Daylight vs. electric, warm (2700K) vs. cool (6500K) |
| **Materials** | Wood, stone, glass, plants, synthetic | Natural ratio: 30% stone, 50% plants, 20% concrete |
| **Vegetation** | Plants present? Type, density, health | Trees (40%), shrubs (20%), grass (40%) |
| **Color** | Dominant hues, saturation, warmth | Greens 60%, browns 30%, grays 10%; high saturation |
| **Complexity** | Visual detail level, organization | Busy forest (80) vs. open field (20) |
| **View/Space** | Depth, layering, focal point | 3 depth layers, strong focal point (monument) |
| **Environment** | Setting type, human scale, activity | Park (natural 80%), office (human-scale 70%), busy (80%) |

---

## Attribute Details by Domain

### SPATIAL PROPERTIES (5 attributes)

**spatial-volume** (continuous, 0–100)
- 0 = tiny closet, 50 = medium office, 100 = vast plaza
- Measurement: Visual estimation of spaciousness

**spatial-enclosure-degree** (ordinal)
- fully-open → semi-enclosed → partially-enclosed → highly-enclosed → completely-enclosed
- Best for: Prospect-Refuge Theory predictions

**spatial-openness-prospect** (continuous, 0–100 meters)
- How far can you see? 10m = urban street, 100m = large plaza, 1000m = mountain vista
- Related to perceived safety and exploration potential

**spatial-mystery** (ordinal)
- none → low → moderate → high
- "I wonder what's around that corner?"
- Drives exploration and engagement

**spatial-legibility** (ordinal)
- low → moderate → high
- Can I find my way around? Are there landmarks?

---

### LIGHTING (5 attributes)

**lighting-source-type** (categorical)
- natural-daylight-direct: Sun streaming through window
- natural-daylight-diffuse: Overcast, indirect natural light
- natural-daylight-mixed: Combination
- artificial-electric: Lamps, fluorescent, LED
- twilight: Dawn/dusk
- artificial-warm: ~2700K incandescent
- artificial-cool: ~6500K daylight-balanced LED

**lighting-illuminance** (continuous, lux)
- 1 lux = moonlight
- 100 lux = office task lighting
- 10,000 lux = sunny day outside
- Measured with light meter or visually estimated

**lighting-color-temperature** (continuous, Kelvin)
- 2700K = warm, cozy (incandescent)
- 4000K = neutral (office standard)
- 6500K = cool, alert (daylight simulation)

**lighting-uniformity** (ordinal)
- poor: Glare areas, harsh shadows
- moderate: Some variation
- good: Even distribution across space

**lighting-shadow-character** (categorical)
- no-shadows: Fully diffuse lighting (overcast)
- soft-shadows: Gentle directional light
- defined-shadows: Clear boundaries
- harsh-shadows: Extreme contrast, potential glare

---

### MATERIALS & TEXTURE (4 attributes)

**materials-dominant-types** (categorical, non-exclusive)
- wood, stone-brick-concrete, glass-metal
- natural-living-vegetation, earth-sand-gravel
- synthetic-plastic-fiberglass, mixed-urban-composite

**materials-naturalness-ratio** (continuous, %)
- 0% = all concrete/plastic/glass
- 50% = mixed natural and synthetic
- 100% = all wood, stone, plants, earth

**materials-surface-finish** (ordinal)
- pristine-polished: New, well-maintained
- clean-matte: Functional, in good repair
- worn-textured: Visible age, weathered look
- deteriorated: Damaged, in disrepair

**materials-texture-visual-complexity** (continuous, 0–100)
- 0 = smooth blank wall
- 50 = wood grain or regular pattern
- 100 = complex natural texture (bark, cracked stone)

---

### VEGETATION (5 attributes)

**vegetation-presence** (categorical)
- absent: No visible plants
- minimal: <5% of scene
- moderate: 5–25% of scene
- abundant: 25–50% of scene
- dominant: >50% of scene (forest, jungle)

**vegetation-types** (categorical, non-exclusive)
- herbaceous-flowers-groundcover
- shrubs-low-woody
- trees-deciduous, trees-coniferous
- tree-canopy-closed, tree-canopy-dappled
- water-vegetation-aquatic
- potted-houseplants
- green-walls-living-architecture

**vegetation-density** (continuous, %)
- 0% = no foliage
- 33% = sparse trees, open to sky
- 67% = moderate dappled shade
- 100% = dense closed canopy

**vegetation-healthfulness** (ordinal)
- poor: Wilted, dead, diseased
- fair: Some stress signs
- good: Healthy, green, vigorous
- excellent: Lush, thriving

**vegetation-spatial-arrangement** (categorical)
- scattered-individual: Isolated trees
- clustered-groups: Groves
- linear-edges: Trees lining a path
- dense-forest-thicket: Impenetrable vegetation
- layered-canopy-understory: Multi-story forest
- formal-ornamental: Landscaped gardens
- informal-naturalistic: Wild appearance

---

### COLOR (5 attributes)

**color-dominant-hues** (categorical, non-exclusive)
- greens-natural, blues-sky-water
- browns-earth-wood
- grays-neutral-concrete
- warm-oranges-reds
- cool-purples-violets
- whites-highlights, blacks-shadows

**color-saturation** (continuous, 0–100)
- 0 = grayscale, muted
- 50 = normal saturation
- 100 = vivid, highly saturated colors

**color-contrast** (continuous, 0–100)
- 0 = monochromatic (all same color)
- 50 = moderate variety
- 100 = high chromatic diversity

**color-warm-cool-ratio** (continuous, %)
- 0% = all cool (blues, purples)
- 50% = balanced
- 100% = all warm (reds, oranges, yellows)

**color-naturalness** (ordinal)
- highly-artificial: Neon, synthetic colors
- partially-artificial: Mixed palette
- natural: Earth tones, greens, sky blues
- highly-natural: Rich nature colors

---

### COMPLEXITY & INFORMATION (4 attributes)

**complexity-visual** (continuous, 0–100)
- 0 = blank wall, minimal detail
- 50 = moderate detail, some variation
- 100 = rich detail, many textures and elements

**complexity-clutter-orderliness** (ordinal)
- cluttered-chaotic: Overwhelming mess
- moderately-busy: Some organization
- organized: Clear structure, visual hierarchy
- sparse-minimal: Intentional simplicity

**complexity-information-density** (continuous, 0–100)
- How much distinct visual information per unit area?
- 0 = sparse/redundant
- 50 = moderate density
- 100 = high density of details

**complexity-pattern-coherence** (ordinal)
- random-incoherent: No discernible pattern
- weakly-patterned: Some repeated elements
- moderately-patterned: Clear patterns
- highly-coherent: Strong visual unity

---

### VIEW & PERCEPTUAL SPACE (5 attributes)

**view-depth-cues** (ordinal)
- minimal: Flat appearance
- moderate: Some depth cues
- rich: Multiple cues (perspective, occlusion, size)
- very-rich: Strong 3D immersion

**view-layering** (ordinal)
- single-layer: Flat composition
- two-layers: Foreground + background
- three-layers: Foreground + middle-ground + background
- multiple-layers: 4+ distinct depth planes

**view-focal-point** (ordinal)
- absent: Equal visual weight, no center
- weak: Subtle focal area
- moderate: Clear focal point
- strong: Dominant element, draws attention

**view-vertical-horizontal-balance** (ordinal)
- sky-dominant: Tall composition, focus on upper portion
- balanced: Even split
- ground-dominant: Wide/low composition, focus on lower portion

**view-visual-flow** (ordinal)
- static: No clear visual pathways
- weak-flow: Some directional elements
- moderate-flow: Clear visual pathways
- strong-flow: Compelling rhythm, guided eye movement

---

### ENVIRONMENTAL CONTEXT (5 attributes)

**environment-built-natural-ratio** (continuous, %)
- 0% = wilderness, all natural
- 50% = mixed urban and natural
- 100% = dense urban, all built

**environment-setting-type** (categorical)
- natural-wilderness, natural-managed-park
- urban-street, urban-plaza-square
- office-workspace, residential-interior/exterior
- healthcare-institutional
- industrial-commercial
- transportation-hub
- educational-academic
- recreational-leisure
- agricultural-rural
- mixed-hybrid

**environment-scale-human** (ordinal)
- inhuman-scale: Elements far too large or small
- below-human: Elements smaller than comfortable
- human-compatible: Elements proportioned to body
- above-human: Elements larger but proportioned
- mixed-scales: Multiple scales present

**environment-accessibility** (ordinal)
- restricted: Barriers, obstacles
- moderate: Some navigation required
- open: Clear paths, easy access
- highly-accessible: Barrier-free, intuitive

**environment-activity-evidence** (ordinal)
- none: Empty, unused, abandoned
- minimal: Some signs of occupation
- moderate: Regular use evident
- high: Active, vibrant with human presence

---

## Validation Checklist

Before submitting tags, check:

- [ ] At least one attribute tagged in each applicable domain
- [ ] All categorical values match the vocabulary (with full descriptive text if provided)
- [ ] All continuous values within specified ranges
- [ ] Ordinal values use the provided level names exactly
- [ ] Consistency: If vegetation-presence = "absent", then vegetation-density should be ≤ 5%
- [ ] Consistency: High spatial-volume (>80) should not have completely-enclosed enclosure
- [ ] Confidence levels recorded (low, moderate, high)
- [ ] Any measurement methods documented (instrumented, visual-estimation, computational)

---

## Running Tests

```bash
# Test the service locally
python -m pytest tests/test_image_tag_service.py -v

# Expected: 42 tests, all passing
```

---

## Common Patterns

### Urban Park Image

```python
tags = {
    "spatial-properties": {
        "spatial-volume": {"value": 85},
        "spatial-enclosure-degree": {"value": "fully-open (no barriers, 360° view)"},
        "spatial-openness-prospect": {"value": 90},
    },
    "vegetation": {
        "vegetation-presence": {"value": "abundant (major vegetation component, 25-50%)"},
        "vegetation-types": {"value": ["trees-deciduous", "shrubs-low-woody", "herbaceous-flowers-groundcover"]},
        "vegetation-density": {"value": 35},
        "vegetation-healthfulness": {"value": "good (healthy, green, vigorous)"},
    },
    "environment-context": {
        "environment-built-natural-ratio": {"value": 30},
        "environment-setting-type": {"value": "natural-managed-park"},
    },
}
```

### Office Interior

```python
tags = {
    "spatial-properties": {
        "spatial-volume": {"value": 45},
        "spatial-enclosure-degree": {"value": "completely-enclosed (interior room)"},
    },
    "lighting": {
        "lighting-source-type": {"value": "artificial-electric"},
        "lighting-illuminance": {"value": 400},
        "lighting-uniformity": {"value": "good (relatively even distribution)"},
    },
    "materials-texture": {
        "materials-dominant-types": {"value": ["glass-metal", "synthetic-plastic-fiberglass"]},
        "materials-naturalness-ratio": {"value": 15},
    },
    "environment-context": {
        "environment-built-natural-ratio": {"value": 100},
        "environment-setting-type": {"value": "office-workspace"},
        "environment-scale-human": {"value": "human-compatible (elements proportioned to human body)"},
    },
}
```

### Natural Wilderness

```python
tags = {
    "vegetation": {
        "vegetation-presence": {"value": "dominant (primary visual element, >50%)"},
        "vegetation-types": {"value": ["trees-coniferous", "herbaceous-flowers-groundcover", "shrubs-low-woody"]},
        "vegetation-density": {"value": 85},
        "vegetation-healthfulness": {"value": "excellent (lush, vibrant, thriving)"},
    },
    "materials-texture": {
        "materials-naturalness-ratio": {"value": 95},
    },
    "environment-context": {
        "environment-built-natural-ratio": {"value": 5},
        "environment-setting-type": {"value": "natural-wilderness"},
    },
    "color": {
        "color-dominant-hues": {"value": ["greens-natural", "browns-earth-wood"]},
        "color-naturalness": {"value": "highly-natural (rich natural palette, full saturation of nature colors)"},
    },
}
```

---

## Troubleshooting

**Error: Could not locate image_tagging_vocabulary.json**
- Ensure you're running from the project root directory
- Check that `data/attributes/` contains the vocabulary file

**Error: Invalid attribute value**
- Check that ordinal values match exactly (e.g., "high (clear structure, easy to navigate)" not just "high")
- Verify continuous values are within the stated range
- Ensure categorical values use exact strings from the vocabulary

**Scores seem wrong**
- Check that you have tagged enough attributes (completeness matters)
- Verify measurement types (continuous values should be numeric, not strings)
- Review the consistency rules—contradictions may affect scoring

**Inter-rater disagreement**
- Calculate ICC(3,1) for each attribute across raters
- If ICC < 0.60, have raters discuss and re-rate together
- Use median of values for final record

---

## Next Steps

1. **Read Full Documentation**: See `IMG_TAG_IMPLEMENTATION_SUMMARY.md`
2. **Tag Your Images**: Use the service to create records
3. **Validate Results**: Run tests locally to verify behavior
4. **Link to Templates**: Use `get_relevant_templates()` to see which T2 templates benefit from your tags
5. **Batch Process**: Scale up to many images using `batch_validate_tags()`

---

## Questions?

Refer to:
- **Attribute details**: Full vocabulary in `image_tagging_vocabulary.json`
- **Schema details**: `image_tagging_schema.json`
- **Service methods**: Docstrings in `src/services/image_tag_service.py`
- **Test examples**: `tests/test_image_tag_service.py`
