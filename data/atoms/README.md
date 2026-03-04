# T1 Atoms: Computational Primitives Registry

This directory contains the complete registry of T1 atoms for the ATLAS system, implementing the panel's Recommendation #1: "Separate canonical from hypothetical T1 atoms."

## Overview

T1 atoms are the ~30 computational primitives that underlie T1 frameworks. Each atom represents a distinct neural computation that can be characterized mathematically and grounded neurobiologically.

## Directory Structure

```
data/atoms/
├── README.md                              (this file)
├── [10 CANONICAL atoms]
│   ├── lateral_inhibition.json
│   ├── divisive_normalization.json
│   ├── gain_control.json
│   ├── hebbian_association.json
│   ├── temporal_integration.json
│   ├── adaptation.json
│   ├── oscillatory_coupling.json
│   ├── homeostatic_regulation.json
│   ├── error_signal_generation.json
│   └── spatial_mapping.json
├── [10 ESTABLISHED atoms]
│   ├── prediction_error_computation.json
│   ├── precision_weighting.json
│   ├── bayesian_updating.json
│   ├── reward_prediction.json
│   ├── working_memory_maintenance.json
│   ├── attentional_selection.json
│   ├── contextual_modulation.json
│   ├── interoceptive_inference.json
│   ├── arousal_modulation.json
│   └── memory_consolidation.json
└── [10 HYPOTHETICAL atoms]
    ├── empathic_resonance.json
    ├── affordance_computation.json
    ├── aesthetic_fluency.json
    ├── narrative_binding.json
    ├── place_cell_coding.json
    ├── allostatic_prediction.json
    ├── social_baseline.json
    ├── circadian_entrainment.json
    ├── multisensory_binding.json
    └── default_mode_suppression.json
```

## Maturity Categories

### CANONICAL (10 atoms)
Neurally grounded, mechanistically understood, cross-domain confirmed.

**Requirements**:
- `cross_domain_confirmed = True` (enforced)
- Direct neural evidence (recordings, lesions, imaging)
- Quantitative computational models
- Used across multiple sensory/cognitive domains

**Examples**: Lateral inhibition, divisive normalization, gain control, Hebbian association

### ESTABLISHED (10 atoms)
Good empirical evidence, but domain-limited or mechanism partially understood.

**Requirements**:
- Solid empirical support within domain(s)
- Mechanistic evidence (fMRI, single-unit, computational)
- May be domain-specific or mechanism debated
- Cross-domain status unknown or limited

**Examples**: Prediction error computation, Bayesian updating, reward prediction, working memory maintenance

### HYPOTHETICAL (10 atoms)
Theoretically motivated, limited direct evidence.

**Requirements**:
- Plausible theoretical motivation
- Candidate neural mechanisms identified
- Limited empirical/mechanistic evidence
- Research frontier: evidence accumulation ongoing

**Examples**: Empathic resonance, affordance computation, narrative binding, social baseline

## Atom JSON Schema

Each atom is defined as a JSON file with the following structure:

```json
{
  "atom_id": "lateral_inhibition",
  "name": "Lateral Inhibition",
  "description": "Suppression of neural responses by activity in neighboring neurons...",
  "maturity": "CANONICAL",
  "neural_substrate": ["retina", "V1", "auditory_cortex"],
  "computational_signature": "y_i = x_i - w * sum(x_j) for j in neighborhood",
  "t1_frameworks": ["predictive-processing", "multisensory-integration"],
  "key_references": [
    "Hartline, H. K., & Ratliff, F. (1957)...",
    "Carandini, M., & Heeger, D. J. (2012)..."
  ],
  "empirical_evidence": "Discovered in Limulus lateral eye...",
  "cross_domain_confirmed": true,
  "parameters": {
    "inhibition_radius": "varies by layer",
    "weight_profile": "Mexican hat / DoG"
  }
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `atom_id` | string | Yes | Unique identifier (lowercase_underscores) |
| `name` | string | Yes | Human-readable name |
| `description` | string | Yes | 2-3 sentence explanation |
| `maturity` | string | Yes | CANONICAL, ESTABLISHED, or HYPOTHETICAL |
| `neural_substrate` | array | Yes | Brain regions/circuits implementing atom |
| `computational_signature` | string | Yes | Mathematical characterization |
| `t1_frameworks` | array | Yes | T1 frameworks using this atom |
| `key_references` | array | Yes | APA-format citations |
| `empirical_evidence` | string | Yes | Summary of evidence base |
| `cross_domain_confirmed` | boolean | Yes | Cross-domain validated? |
| `parameters` | object | No | Atom-specific tunable parameters |

## Validation Rules

All atoms are validated against:

1. **Structural**
   - atom_id: non-empty, lowercase_underscores format
   - All required fields present
   - No null or undefined values

2. **Semantic**
   - name: non-empty, <100 characters
   - description: non-empty, 50-500 characters
   - maturity: one of three allowed values
   - neural_substrate: non-empty list
   - t1_frameworks: non-empty list
   - key_references: non-empty list with valid citations
   - empirical_evidence: non-empty, meaningful
   - computational_signature: detailed and specific

3. **Cross-Maturity**
   - CANONICAL atoms: `cross_domain_confirmed = True` (enforced)
   - ESTABLISHED/HYPOTHETICAL: cross_domain status consistent with description

4. **Consistency**
   - atom_id matches filename (atom_id.json)
   - No duplicate atom_ids
   - All frameworks linked are known T1 frameworks

## Registry Access

Use the Python registry to access atoms:

```python
from src.qa.molecules.t1_atom_registry import T1AtomRegistry

# Create registry
registry = T1AtomRegistry(atoms_dir="data/atoms")

# Get single atom
atom = registry.get("lateral_inhibition")

# Get by maturity
canonical_atoms = registry.find_canonical()      # 10 atoms
established_atoms = registry.find_established()  # 10 atoms
hypothetical_atoms = registry.find_hypothetical() # 10 atoms

# Get by framework
pp_atoms = registry.find_by_framework("predictive-processing")  # 11 atoms

# Get cross-domain atoms
cross_domain = registry.find_cross_domain()

# Analysis
print(registry.summary())
coverage = registry.get_framework_coverage()
validation = registry.validate_registry()
```

## Framework Coverage

The 30 atoms collectively link to 37 T1 frameworks:

**High-density** (5+ atoms):
- predictive-processing (11)
- attention (6)
- memory (5)
- homeostasis (5)
- learning (4)

**Moderate-density** (2-4 atoms):
- motor-control, multisensory-integration, arousal, etc.

**Sparse** (1 atom):
- Specialized frameworks like aesthetics, navigation, social-cognition

## Adding New Atoms

To add a new atom:

1. Create `atom_id.json` in this directory
2. Fill all required fields following the schema
3. Set appropriate `maturity` level
4. Ensure `cross_domain_confirmed` is consistent with maturity
5. Run validation: `registry.validate_registry()`
6. Update any referencing documentation

### Example: Adding a New Hypothetical Atom

```json
{
  "atom_id": "example_new_atom",
  "name": "Example New Atom",
  "description": "Brief 2-3 sentence description of the computation...",
  "maturity": "HYPOTHETICAL",
  "neural_substrate": ["candidate_region_1", "candidate_region_2"],
  "computational_signature": "model equation or description",
  "t1_frameworks": ["relevant-framework"],
  "key_references": ["Author (Year). Title. Journal."],
  "empirical_evidence": "Current state of evidence...",
  "cross_domain_confirmed": false,
  "parameters": {}
}
```

## Testing

All atoms are validated by 52 comprehensive tests:

```bash
python -m pytest tests/test_t1_atom_registry.py -v
```

Tests cover:
- Schema validation (10 tests)
- Registry loading (8 tests)
- Maturity stratification (7 tests)
- Framework indexing (6 tests)
- Cross-domain confirmation (3 tests)
- Content validation (5 tests)
- Registry-level validation (4 tests)
- Integration workflows (4 tests)
- Edge cases (3 tests)

**Current status**: 52/52 tests passing

## Quality Assurance

All atoms pass:
- ✓ Schema validation
- ✓ Content validation (no empty fields)
- ✓ Maturity validation (CANONICAL cross-domain, etc.)
- ✓ Reference validation (valid citations)
- ✓ Framework linkage (all atoms → frameworks)
- ✓ Computational signature review (non-trivial descriptions)

## References & Attribution

The atoms and their characterizations draw on:

- **Canonical Computations**: Carandini & Heeger (2012), foundational review
- **Neuroscience Standards**: Annual Reviews Neuroscience, Journal of Neuroscience
- **Computational Theory**: Knill & Pouget (2004), Rao & Ballard (1999), others
- **Cross-domain Analysis**: Carandini, Craver, and panel discussion

## Version History

- **V1.0** (2026-03-03): Initial release with 30 atoms (10 per category)
  - Implements Panel Recommendation #1
  - Ready for integration with QA engine and Article Eater
  - 100% test coverage (52 tests passing)

## Contact & Updates

For questions about specific atoms or to propose additions:
- Reference: `/docs/T1_ATOM_REGISTRY_IMPLEMENTATION.md`
- Schema: `src/qa/molecules/t1_atom_schema.py`
- Registry: `src/qa/molecules/t1_atom_registry.py`
- Tests: `tests/test_t1_atom_registry.py`
