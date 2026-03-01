#!/usr/bin/env python3
"""
Instance Library Builder for CMR Prediction Engine
===================================================

Populates the typed relational graph instance library by mining three sources:

  1. INTERNAL: Extracted findings from processed articles (data/extracted_findings/)
     and structured claims from test papers (data/test_papers/)
  2. TEMPLATES: Calibrated parameters, population modifiers, and architectural
     modifiers embedded in the 103 mechanism templates
  3. LITERATURE: Seed instances from published databases (fractal D measurements,
     olfactory pleasantness ratings, auditory spectral exponents, material
     affective scores)

The key design principle (Kirsh, 2026): instances are organized by the
THEORETICALLY OPERATIVE ABSTRACT PROPERTY — the causally effective attribute
that the mechanism chain actually operates on — not by the conventional
category of the object.

  Example: A fern and a Pollock painting are in the same bin (fractal D ≈ 1.3–1.5)
           Wood and cork are in the same bin (thermal conductivity λ < 0.5 W/m·K)
           Vanillin and ethyl maltol are in the same bin (olfactory pleasantness > +5)

Usage:
    python instance_library_builder.py [--templates-dir DIR] [--output FILE]
    python instance_library_builder.py --report    # Human-readable summary
    python instance_library_builder.py --json      # Full library as JSON

Author: David Kirsh & Claude Opus 4.6
Date:   2026-02-24
"""

import json
import os
import sys
import argparse
import re
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

# ─── Data Classes ────────────────────────────────────────────────

@dataclass
class Instance:
    """A concrete instance that populates a typed slot in a mechanism graph."""
    instance_id: str
    name: str                         # e.g., "Gaudí Casa Batlló facade"
    category: str                     # e.g., "organic_biomorphic_architecture"
    slot_type: str                    # the mechanism node type this populates
    causal_attribute: str             # the theoretically operative property
    causal_value: str                 # measured value of that property
    causal_value_numeric: Optional[float] = None  # if quantifiable
    causal_unit: str = ""             # unit of measurement
    validity: str = "VALID"           # HIGH, VALID, PARTIAL, LOW, NONE
    modality: str = ""                # visual, auditory, thermal, olfactory, tactile
    source: str = ""                  # where this instance comes from
    effect_size: Optional[float] = None  # Cohen's d or equivalent if known
    effect_direction: str = ""        # positive, negative, null
    p_value: Optional[float] = None
    sample_n: Optional[int] = None
    context: str = ""                 # study context (lab, field, hospital, etc.)
    notes: str = ""
    paper_id: str = ""                # DOI or identifier

@dataclass
class SlotType:
    """A typed slot in the mechanism chain, with its instance library."""
    slot_id: str
    name: str                         # e.g., "fractal_surface"
    description: str
    causal_attribute: str             # the key property (e.g., "fractal_dimension_D")
    causal_unit: str                  # e.g., "Hausdorff dimension"
    optimal_range: str = ""           # e.g., "1.3–1.5"
    optimal_min: Optional[float] = None
    optimal_max: Optional[float] = None
    modality: str = ""
    template_ids: list = field(default_factory=list)   # which templates use this slot
    instances: list = field(default_factory=list)       # list of Instance objects

@dataclass
class InstanceLibrary:
    """The complete instance library, organized by slot type."""
    version: str = "1.0.0"
    generated_at: str = ""
    slot_types: list = field(default_factory=list)      # list of SlotType objects
    total_instances: int = 0
    sources: dict = field(default_factory=dict)          # source -> count


# ─── Source 1: Mine Extracted Findings ───────────────────────────

def mine_extracted_findings(data_dir: str) -> list:
    """Extract instances from JSONL finding files."""
    instances = []
    findings_dir = Path(data_dir) / "extracted_findings"

    if not findings_dir.exists():
        print(f"  WARN: {findings_dir} not found", file=sys.stderr)
        return instances

    for filepath in sorted(findings_dir.glob("*.jsonl")):
        with open(filepath) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    finding = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Extract architectural feature → outcome pairs
                antecedents = finding.get("antecedents", [])
                consequent = finding.get("consequent", "")
                direction = finding.get("measure_direction", "unknown")
                stats = finding.get("statistics", {})
                paper_id = finding.get("paper_id", filepath.stem)
                finding_text = finding.get("finding_text", "")
                quote = finding.get("quote", "")

                # Try to extract concrete instances from the finding text
                # Look for specific materials, conditions, measurements
                combined_text = f"{finding_text} {quote}"

                for antecedent in antecedents:
                    # Classify the antecedent
                    modality = _classify_modality_from_text(antecedent)
                    slot_type = _classify_slot_type(antecedent)
                    causal_attr = _extract_causal_attribute(antecedent, combined_text)

                    inst = Instance(
                        instance_id=f"EF_{filepath.stem}_{line_num}",
                        name=antecedent,
                        category=_categorize(antecedent),
                        slot_type=slot_type,
                        causal_attribute=causal_attr,
                        causal_value=_extract_value_from_text(combined_text, causal_attr),
                        modality=modality,
                        source="extracted_findings",
                        effect_size=stats.get("effect_size"),
                        effect_direction=direction,
                        p_value=stats.get("p_value"),
                        sample_n=stats.get("sample_size"),
                        paper_id=paper_id,
                        notes=finding_text[:200],
                    )
                    instances.append(inst)

    return instances


# ─── Source 2: Mine Test Paper Claims ────────────────────────────

def mine_test_papers(data_dir: str) -> list:
    """Extract instances from structured test paper claims."""
    instances = []
    papers_dir = Path(data_dir) / "test_papers"

    if not papers_dir.exists():
        print(f"  WARN: {papers_dir} not found", file=sys.stderr)
        return instances

    for filepath in sorted(papers_dir.glob("*.json")):
        try:
            with open(filepath) as f:
                paper = json.load(f)
        except (json.JSONDecodeError, Exception):
            continue

        paper_id = paper.get("paper_id", filepath.stem)
        citation = paper.get("citation", "")
        claims = paper.get("claims", [])

        for claim in claims:
            iv = claim.get("iv", "")
            dv = claim.get("dv", "")
            direction = claim.get("direction", "unknown")
            effect_size = claim.get("effect_size")
            sample_n = claim.get("sample_n")
            context = claim.get("context", "")
            description = claim.get("description", "")

            # The IV is an architectural/environmental instance
            modality = _classify_modality_from_text(iv)
            slot_type = _classify_slot_type(iv)

            iv_inst = Instance(
                instance_id=f"TP_{paper_id}_{claim.get('claim_id', '')}",
                name=iv,
                category=_categorize(iv),
                slot_type=slot_type,
                causal_attribute=iv,
                causal_value=_extract_value_from_text(description, iv),
                modality=modality,
                source="test_papers",
                effect_size=effect_size,
                effect_direction=direction,
                sample_n=sample_n,
                context=context,
                paper_id=paper_id,
                notes=description[:200],
            )
            instances.append(iv_inst)

            # The DV is a psychological/physiological outcome instance
            dv_inst = Instance(
                instance_id=f"TP_{paper_id}_{claim.get('claim_id', '')}_dv",
                name=dv,
                category="outcome",
                slot_type=_classify_output_type(dv),
                causal_attribute=dv,
                causal_value=str(effect_size) if effect_size else "",
                causal_value_numeric=effect_size,
                causal_unit="Cohen_d" if effect_size else "",
                modality="outcome",
                source="test_papers",
                effect_size=effect_size,
                effect_direction=direction,
                sample_n=sample_n,
                context=context,
                paper_id=paper_id,
                notes=description[:200],
            )
            instances.append(dv_inst)

    return instances


# ─── Source 3: Mine Template Parameters ──────────────────────────

def mine_template_parameters(templates_dir: str) -> list:
    """Extract instances from calibrated parameters within templates."""
    instances = []
    tdir = Path(templates_dir)

    if not tdir.exists():
        return instances

    for filepath in sorted(tdir.glob("*.json")):
        try:
            with open(filepath) as f:
                tmpl = json.load(f)
        except (json.JSONDecodeError, Exception):
            continue

        status = tmpl.get("calibration_status", tmpl.get("status", ""))
        if status != "calibrated":
            continue

        tid = tmpl.get("template_id", tmpl.get("display_id", filepath.stem))
        params = tmpl.get("calibrated_parameters", {})

        for param_name, param_data in params.items():
            if not isinstance(param_data, dict):
                continue

            # Extract the numeric value and range
            value = param_data.get("value", param_data.get("central_value"))
            unit = param_data.get("unit", "")
            confidence = param_data.get("confidence", 0)
            source = param_data.get("source", "")
            param_range = param_data.get("range", param_data.get("optimal_range"))

            # Determine if this is an input, intermediate, or output parameter
            modality = _classify_modality_from_text(f"{param_name} {unit}")

            numeric_val = None
            if isinstance(value, (int, float)):
                numeric_val = float(value)

            range_str = ""
            if isinstance(param_range, list) and len(param_range) == 2:
                range_str = f"{param_range[0]}–{param_range[1]}"
            elif isinstance(param_range, dict):
                range_str = f"{param_range.get('min', '?')}–{param_range.get('max', '?')}"
            elif isinstance(param_range, str):
                range_str = param_range

            inst = Instance(
                instance_id=f"TMPL_{tid}_{param_name}",
                name=param_name,
                category="calibrated_parameter",
                slot_type=_classify_slot_type(param_name),
                causal_attribute=param_name,
                causal_value=str(value) if value is not None else "",
                causal_value_numeric=numeric_val,
                causal_unit=unit,
                modality=modality,
                source="template_parameters",
                paper_id=source,
                notes=f"Range: {range_str}, Confidence: {confidence}",
            )
            instances.append(inst)

            # Also mine sub-parameters (e.g., dose-response typologies)
            for sub_key, sub_val in param_data.items():
                if isinstance(sub_val, dict) and "value" in sub_val:
                    sub_inst = Instance(
                        instance_id=f"TMPL_{tid}_{param_name}_{sub_key}",
                        name=f"{param_name}.{sub_key}",
                        category="calibrated_sub_parameter",
                        slot_type=_classify_slot_type(sub_key),
                        causal_attribute=sub_key,
                        causal_value=str(sub_val.get("value", "")),
                        causal_unit=sub_val.get("unit", ""),
                        modality=modality,
                        source="template_parameters",
                        paper_id=sub_val.get("source", ""),
                    )
                    instances.append(sub_inst)

        # Mine population modifiers as instances
        pop_mods = tmpl.get("population_modifiers", {})
        for pop_name, pop_data in pop_mods.items():
            if not isinstance(pop_data, dict):
                continue
            inst = Instance(
                instance_id=f"TMPL_{tid}_pop_{pop_name}",
                name=pop_name,
                category="population_modifier",
                slot_type="modulatory",
                causal_attribute="population_modifier",
                causal_value=pop_data.get("modifier", pop_data.get("effect", str(pop_data))),
                modality="modulatory",
                source="template_modifiers",
                notes=f"Direction: {pop_data.get('direction', '?')}, Conf: {pop_data.get('confidence', '?')}",
            )
            instances.append(inst)

        # Mine architectural modifiers
        arch_mods = tmpl.get("architectural_modifiers", {})
        for arch_name, arch_data in arch_mods.items():
            if not isinstance(arch_data, dict):
                continue
            inst = Instance(
                instance_id=f"TMPL_{tid}_arch_{arch_name}",
                name=arch_name,
                category="architectural_modifier",
                slot_type=_classify_slot_type(arch_name),
                causal_attribute=arch_name,
                causal_value=arch_data.get("modifier", ""),
                modality=_classify_modality_from_text(arch_name),
                source="template_modifiers",
                notes=arch_data.get("description", "")[:200],
            )
            instances.append(inst)

    return instances


# ─── Source 4: Literature Seed Instances ─────────────────────────

def seed_literature_instances() -> list:
    """
    Seed the instance library with measured values from published databases.
    Each entry is organized by the theoretically operative causal attribute.
    """
    instances = []

    # ─── VISUAL: Fractal dimension measurements ──────────
    fractal_instances = [
        # Natural scenes
        ("Forest canopy (overhead, deciduous)", "natural_scene", 1.3, "Hagerhall et al., 2004", "HIGH"),
        ("Forest canopy (overhead, coniferous)", "natural_scene", 1.4, "Hagerhall et al., 2004", "HIGH"),
        ("Fern frond (Dryopteris)", "plant_leaf", 1.4, "Bruno et al., 2008", "HIGH"),
        ("Fern (whole plant silhouette)", "plant_silhouette", 1.35, "Spehar et al., 2003", "HIGH"),
        ("Oak canopy silhouette", "tree_canopy", 1.5, "Spehar et al., 2003", "HIGH"),
        ("Pine canopy silhouette", "tree_canopy", 1.3, "Spehar et al., 2003", "HIGH"),
        ("Birch canopy silhouette", "tree_canopy", 1.45, "Spehar et al., 2003", "HIGH"),
        ("Mountain horizon line", "natural_scene", 1.25, "Spehar et al., 2003", "VALID"),
        ("Coastline (Norway fjord)", "natural_scene", 1.52, "Mandelbrot, 1983", "VALID"),
        ("Cloud boundary", "natural_scene", 1.35, "Lovejoy, 1982", "VALID"),
        ("River drainage network", "natural_scene", 1.4, "Rodriguez-Iturbe & Rinaldo, 1997", "VALID"),

        # Architectural
        ("Gaudí Casa Batlló facade", "organic_architecture", 1.4, "Bovill, 1996", "HIGH"),
        ("Gothic cathedral tracery (Chartres)", "historical_ornamental", 1.35, "Bovill, 1996", "HIGH"),
        ("Gothic cathedral tracery (Notre-Dame)", "historical_ornamental", 1.4, "Bovill, 1996", "HIGH"),
        ("Frank Lloyd Wright Fallingwater", "modernist_organic", 1.3, "Bovill, 1996", "HIGH"),
        ("FLW Robie House elevation", "modernist_organic", 1.25, "Bovill, 1996", "HIGH"),
        ("Islamic geometric tilework (Alhambra)", "geometric_ornamental", 1.4, "Ostwald, 2001", "HIGH"),
        ("Japanese temple garden raked gravel", "landscape", 1.3, "Hagerhall et al., 2004", "VALID"),
        ("Brutalist concrete panel (smooth)", "modernist_rectilinear", 1.05, "Ostwald & Vaughan, 2016", "LOW"),
        ("Mies van der Rohe Farnsworth House", "modernist_minimal", 1.1, "Ostwald & Vaughan, 2016", "LOW"),
        ("Le Corbusier Villa Savoye", "modernist_rectilinear", 1.15, "Ostwald & Vaughan, 2016", "LOW"),
        ("Parametric 3D-printed screen (Neri Oxman)", "computational_design", 1.6, "estimated", "PARTIAL"),
        ("Fractal acoustic diffuser panel", "engineered_surface", 1.3, "Cox & D'Antonio, 2009", "HIGH"),

        # Art
        ("Pollock No. 14: Gray (1948)", "art_drip", 1.45, "Taylor et al., 2011", "HIGH"),
        ("Pollock Blue Poles (1952)", "art_drip", 1.72, "Taylor et al., 2011", "HIGH"),
        ("Pollock Autumn Rhythm (1950)", "art_drip", 1.67, "Taylor et al., 2011", "HIGH"),
        ("Mondrian Composition (rectilinear)", "art_geometric", 1.05, "Taylor et al., 2011", "LOW"),

        # Biological surfaces
        ("Magnolia leaf outline", "plant_leaf", 1.2, "Bruno et al., 2008", "VALID"),
        ("Maple leaf outline (Acer)", "plant_leaf", 1.35, "Bruno et al., 2008", "HIGH"),
        ("Grapevine leaf outline", "plant_leaf", 1.6, "Bruno et al., 2008", "PARTIAL"),
        ("Romanesco broccoli surface", "plant_surface", 1.4, "Cross, 1997", "HIGH"),
        ("Coral reef structure", "biological_surface", 1.5, "Martin-Garin et al., 2007", "VALID"),
        ("Human retinal vasculature", "biological_tissue", 1.4, "Family et al., 1989", "VALID"),
    ]

    for name, cat, D, source, validity in fractal_instances:
        instances.append(Instance(
            instance_id=f"LIT_FRACTAL_{len(instances)}",
            name=name,
            category=cat,
            slot_type="fractal_surface",
            causal_attribute="fractal_dimension_D",
            causal_value=str(D),
            causal_value_numeric=D,
            causal_unit="Hausdorff_dimension",
            validity=validity,
            modality="visual",
            source=f"literature: {source}",
        ))

    # ─── AUDITORY: 1/f spectral exponent measurements ──────────
    auditory_instances = [
        # Natural soundscapes
        ("Rain on leaves", "natural_soundscape", 1.0, "Voss & Clarke, 1975", "HIGH"),
        ("Stream/brook", "natural_soundscape", 0.9, "De Coensel et al., 2015", "HIGH"),
        ("Birdsong (mixed species, dawn)", "natural_soundscape", 1.0, "De Coensel et al., 2015", "HIGH"),
        ("Ocean waves on shore", "natural_soundscape", 1.2, "Voss & Clarke, 1975", "HIGH"),
        ("Wind through trees", "natural_soundscape", 0.8, "estimated from literature", "VALID"),
        ("Waterfall (distant)", "natural_soundscape", 0.7, "estimated", "VALID"),
        ("Campfire crackling", "natural_soundscape", 1.1, "estimated", "VALID"),

        # Music (rhythm exponent β)
        ("Bach Well-Tempered Clavier", "classical_music", 0.97, "Levitin et al., 2012", "HIGH"),
        ("Beethoven String Quartet No. 1", "classical_music", 0.85, "Levitin et al., 2012", "HIGH"),
        ("Mozart Piano Sonata K.545", "classical_music", 0.78, "Levitin et al., 2012", "HIGH"),
        ("Javanese gamelan ensemble", "world_music", 2.1, "estimated from tonal structure", "VALID"),
        ("Scott Joplin ragtime piano", "popular_music", 0.84, "Levitin et al., 2012", "HIGH"),
        ("Electronic dance music (EDM)", "electronic_music", 0.5, "estimated", "PARTIAL"),
        ("White noise generator", "synthetic", 0.0, "definition", "HIGH"),
        ("Pink noise generator", "synthetic", 1.0, "definition", "HIGH"),
        ("Brown noise generator", "synthetic", 2.0, "definition", "HIGH"),

        # Urban/mechanical
        ("HVAC continuous drone", "mechanical_noise", 0.3, "estimated", "VALID"),
        ("Traffic noise (highway)", "urban_noise", 0.4, "De Coensel et al., 2015", "VALID"),
        ("Office speech babble", "speech", 0.6, "estimated", "VALID"),
        ("Classical radio broadcast", "broadcast", 1.0, "Voss & Clarke, 1975", "HIGH"),
        ("Rock radio broadcast", "broadcast", 1.0, "Voss & Clarke, 1975", "HIGH"),
        ("News/talk radio", "broadcast", 1.0, "Voss & Clarke, 1975", "HIGH"),
    ]

    for name, cat, beta, source, validity in auditory_instances:
        instances.append(Instance(
            instance_id=f"LIT_AUDIO_{len(instances)}",
            name=name,
            category=cat,
            slot_type="spectral_signal",
            causal_attribute="spectral_exponent_beta",
            causal_value=str(beta),
            causal_value_numeric=beta,
            causal_unit="power_law_exponent",
            validity=validity,
            modality="auditory",
            source=f"literature: {source}",
        ))

    # ─── THERMAL: Material thermal conductivity ──────────
    thermal_instances = [
        # Low conductivity (warm to touch)
        ("Cork tile", "natural_insulator", 0.04, "engineering tables", "HIGH"),
        ("Softwood (pine)", "natural_wood", 0.12, "Wastiels et al., 2012", "HIGH"),
        ("Hardwood (oak)", "natural_wood", 0.17, "engineering tables", "HIGH"),
        ("Bamboo", "natural_wood", 0.16, "engineering tables", "HIGH"),
        ("Wool carpet", "textile", 0.04, "engineering tables", "HIGH"),
        ("Leather upholstery", "natural_textile", 0.14, "engineering tables", "HIGH"),
        ("Rubber flooring", "synthetic", 0.16, "engineering tables", "VALID"),

        # Medium conductivity (neutral)
        ("Brick", "masonry", 0.72, "Wastiels et al., 2012", "HIGH"),
        ("Plaster (white)", "finish", 0.50, "Wastiels et al., 2012", "HIGH"),
        ("Ceramic tile", "masonry", 1.0, "engineering tables", "HIGH"),
        ("Linoleum", "synthetic", 0.17, "engineering tables", "VALID"),

        # High conductivity (cold to touch)
        ("Concrete (polished)", "masonry", 1.7, "Wastiels et al., 2012", "HIGH"),
        ("Granite (polished)", "stone", 2.8, "engineering tables", "HIGH"),
        ("Marble (Carrara)", "stone", 2.9, "engineering tables", "HIGH"),
        ("Blue stone (Belgian)", "stone", 2.5, "Wastiels et al., 2012", "HIGH"),
        ("Glass (plate)", "glass", 1.0, "engineering tables", "HIGH"),
        ("Stainless steel", "metal", 16.0, "Wastiels et al., 2012", "HIGH"),
        ("Aluminum", "metal", 205.0, "engineering tables", "HIGH"),
        ("Copper", "metal", 385.0, "engineering tables", "HIGH"),
    ]

    for name, cat, lambda_val, source, validity in thermal_instances:
        instances.append(Instance(
            instance_id=f"LIT_THERMAL_{len(instances)}",
            name=name,
            category=cat,
            slot_type="material_thermal",
            causal_attribute="thermal_conductivity_lambda",
            causal_value=str(lambda_val),
            causal_value_numeric=lambda_val,
            causal_unit="W_per_m_K",
            validity=validity,
            modality="tactile",
            source=f"literature: {source}",
        ))

    # ─── OLFACTORY: Pleasantness ratings ──────────
    # From Keller & Vosshall (2016), 480-molecule dataset
    # Representative instances ranked by pleasantness
    olfactory_instances = [
        # Highly pleasant (top quartile)
        ("Vanillin", "sweet_aromatic", 7.8, "Keller & Vosshall, 2016", "HIGH"),
        ("Ethyl maltol", "sweet_aromatic", 7.5, "Keller & Vosshall, 2016", "HIGH"),
        ("Linalool (lavender)", "floral", 7.2, "Keller & Vosshall, 2016", "HIGH"),
        ("Citral (lemon)", "citrus", 7.0, "Keller & Vosshall, 2016", "HIGH"),
        ("Eugenol (clove)", "spicy_aromatic", 6.5, "Keller & Vosshall, 2016", "HIGH"),
        ("Cedar wood oil (cedrol)", "woody", 6.8, "Keller & Vosshall, 2016", "HIGH"),
        ("Fresh-cut grass (cis-3-hexenol)", "green", 6.3, "Keller & Vosshall, 2016", "HIGH"),
        ("Rose oxide", "floral", 7.1, "Keller & Vosshall, 2016", "HIGH"),

        # Moderately pleasant (second quartile)
        ("Pine resin (alpha-pinene)", "woody", 5.5, "Keller & Vosshall, 2016", "HIGH"),
        ("Cinnamon (cinnamaldehyde)", "spicy", 5.2, "Keller & Vosshall, 2016", "HIGH"),
        ("Coffee (2-furfurylthiol)", "roasted", 5.0, "estimated", "VALID"),
        ("Old book (vanillin + lignin degradation)", "complex", 5.3, "estimated", "VALID"),
        ("Fresh bread (2-acetyl-1-pyrroline)", "baked", 5.8, "estimated", "VALID"),
        ("Petrichor (geosmin)", "earthy", 4.8, "Keller & Vosshall, 2016", "VALID"),

        # Neutral
        ("Eucalyptol", "medicinal", 4.0, "Keller & Vosshall, 2016", "HIGH"),
        ("Menthol", "cooling", 4.2, "Keller & Vosshall, 2016", "HIGH"),

        # Unpleasant (lower quartile)
        ("Butyric acid (rancid butter)", "acidic", 2.0, "Keller & Vosshall, 2016", "HIGH"),
        ("Isovaleric acid (foot odor)", "acidic", 1.5, "Keller & Vosshall, 2016", "HIGH"),
        ("Trimethylamine (rotting fish)", "amine", 1.2, "Keller & Vosshall, 2016", "HIGH"),
        ("Hydrogen sulfide", "sulfurous", 1.0, "Keller & Vosshall, 2016", "HIGH"),
        ("Skatole (fecal)", "indolic", 0.8, "Keller & Vosshall, 2016", "HIGH"),

        # Architectural materials (scent profiles)
        ("Fresh-sawn pine wood", "architectural", 6.0, "estimated from α-pinene + sawdust", "VALID"),
        ("Cedar paneling", "architectural", 6.5, "estimated from cedrol content", "VALID"),
        ("New carpet off-gassing (4-PCH)", "architectural_voc", 2.5, "estimated", "VALID"),
        ("Fresh paint (VOC mix)", "architectural_voc", 2.0, "estimated", "VALID"),
        ("New car / vinyl off-gassing", "architectural_voc", 3.0, "estimated", "VALID"),
        ("Concrete (wet/curing)", "architectural", 3.5, "estimated", "VALID"),
        ("Leather furniture", "architectural", 5.5, "estimated", "VALID"),
    ]

    for name, cat, pleasantness, source, validity in olfactory_instances:
        instances.append(Instance(
            instance_id=f"LIT_OLF_{len(instances)}",
            name=name,
            category=cat,
            slot_type="odorant",
            causal_attribute="olfactory_pleasantness",
            causal_value=str(pleasantness),
            causal_value_numeric=pleasantness,
            causal_unit="pleasantness_1_to_9",
            validity=validity,
            modality="olfactory",
            source=f"literature: {source}",
        ))

    # ─── TACTILE: Surface roughness (Ra) ──────────
    tactile_instances = [
        # Smooth (Ra < 1 μm)
        ("Polished glass", "smooth", 0.01, "engineering tables", "HIGH"),
        ("Polished stainless steel", "smooth", 0.05, "engineering tables", "HIGH"),
        ("Glazed ceramic tile", "smooth", 0.1, "engineering tables", "HIGH"),

        # Optimal C-tactile range (Ra 1–10 μm)
        ("Sanded hardwood (220 grit)", "wood", 3.0, "engineering tables", "HIGH"),
        ("Polished marble", "stone", 2.0, "engineering tables", "HIGH"),
        ("Polished concrete", "masonry", 5.0, "engineering tables", "HIGH"),
        ("Satin-finish metal", "metal", 1.5, "engineering tables", "HIGH"),
        ("Fine leather", "textile", 8.0, "engineering tables", "HIGH"),

        # Moderate roughness (Ra 10–50 μm)
        ("Sanded wood (80 grit)", "wood", 20.0, "engineering tables", "VALID"),
        ("Rough brick", "masonry", 40.0, "engineering tables", "VALID"),
        ("Woven cotton fabric", "textile", 25.0, "engineering tables", "VALID"),

        # Rough (Ra > 50 μm)
        ("Reclaimed barnwood", "wood", 80.0, "engineering tables", "VALID"),
        ("Split-face concrete block", "masonry", 100.0, "engineering tables", "VALID"),
        ("Rough-hewn stone", "stone", 150.0, "engineering tables", "VALID"),
    ]

    for name, cat, Ra, source, validity in tactile_instances:
        instances.append(Instance(
            instance_id=f"LIT_TACTILE_{len(instances)}",
            name=name,
            category=cat,
            slot_type="surface_texture",
            causal_attribute="surface_roughness_Ra",
            causal_value=str(Ra),
            causal_value_numeric=Ra,
            causal_unit="micrometers",
            validity=validity,
            modality="tactile",
            source=f"literature: {source}",
        ))

    # ─── SPATIAL / ARCHITECTURAL FEATURES with effect sizes ──────────
    arch_effect_instances = [
        # From the canonical test papers
        ("Daylight availability (top quartile vs. bottom)", "daylight", "test_scores", 0.34, 21000, "school", "heschong_1999", "HIGH"),
        ("Nature view (trees) vs. brick wall (post-surgery)", "nature_view", "recovery_time", 0.60, 46, "hospital", "ulrich_1984", "HIGH"),
        ("Moderate ambient noise (70dB) vs. low (50dB)", "ambient_noise", "creative_thinking", 0.40, 65, "lab", "mehta_2012", "HIGH"),
        ("High ceiling (3m) vs. low (2.4m)", "ceiling_height", "creative_thinking", 0.38, 100, "lab", "meyers_levy_zhu_2007", "HIGH"),
        ("Curved interior contours vs. rectilinear", "curved_contours", "beauty_rating", 0.35, 18, "fMRI", "vartanian_2015", "HIGH"),
        ("Dim lighting vs. bright (1500 lux)", "light_level", "creative_performance", 0.42, 114, "lab", "steidle_werth_2013", "HIGH"),
        ("Walking outdoors vs. sitting (creative output)", "walking_state", "creative_output", 0.81, 176, "field", "oppezzo_schwartz_2014", "HIGH"),
        ("Open-plan office noise (55dB speech)", "office_noise", "cognitive_performance", -0.30, 40, "lab", "evans_johnson_2000", "HIGH"),
        ("Naturally ventilated vs. AC (thermal comfort)", "ventilation_type", "thermal_satisfaction", 0.45, 5000, "field", "de_dear_brager_1998", "HIGH"),
        ("Biophilic office (plants + daylight + nature art)", "biophilic_design", "well_being", 0.50, 200, "field", "kellert_2008_est", "VALID"),
    ]

    for name, cat, dv, d, n, ctx, paper, validity in arch_effect_instances:
        instances.append(Instance(
            instance_id=f"LIT_ARCH_{len(instances)}",
            name=name,
            category=cat,
            slot_type="architectural_feature",
            causal_attribute=cat,
            causal_value=f"d = {d}",
            causal_value_numeric=d,
            causal_unit="Cohen_d",
            validity=validity,
            modality="visual" if cat in ["daylight", "nature_view", "curved_contours", "light_level"] else "general",
            source=f"literature: {paper}",
            effect_size=d,
            effect_direction="positive" if d > 0 else "negative",
            sample_n=n,
            context=ctx,
            notes=f"DV: {dv}",
        ))

    return instances


# ─── Classification Helpers ──────────────────────────────────────

def _classify_modality_from_text(text: str) -> str:
    """Classify text into a sensory modality."""
    t = text.lower()
    if any(w in t for w in ["visual", "light", "view", "color", "fractal", "lux", "contrast",
                            "facade", "window", "ceiling", "daylight", "luminan"]):
        return "visual"
    if any(w in t for w in ["sound", "noise", "acoustic", "audio", "music", "speech", "db"]):
        return "auditory"
    if any(w in t for w in ["thermal", "temperature", "warm", "cold", "heat", "hvac"]):
        return "thermal"
    if any(w in t for w in ["smell", "odor", "olfact", "scent", "aroma", "voc"]):
        return "olfactory"
    if any(w in t for w in ["touch", "tactile", "haptic", "surface", "rough", "texture"]):
        return "tactile"
    if any(w in t for w in ["social", "crowd", "density", "privacy"]):
        return "social"
    return "general"


def _classify_slot_type(text: str) -> str:
    """Classify text into a mechanism chain slot type."""
    t = text.lower()
    if any(w in t for w in ["fractal", "dimension", "1/f", "spectral"]):
        return "fractal_surface"
    if any(w in t for w in ["daylight", "light", "lux", "illumin", "luminan"]):
        return "light_source"
    if any(w in t for w in ["sound", "noise", "acoustic", "db"]):
        return "acoustic_source"
    if any(w in t for w in ["thermal", "temperature"]):
        return "thermal_source"
    if any(w in t for w in ["smell", "odor", "olfact", "scent"]):
        return "odorant"
    if any(w in t for w in ["texture", "roughness", "surface", "material"]):
        return "surface_texture"
    if any(w in t for w in ["ceiling", "height", "spatial", "layout"]):
        return "spatial_configuration"
    if any(w in t for w in ["nature", "plant", "biophil", "green"]):
        return "biophilic_element"
    if any(w in t for w in ["curved", "contour", "form", "shape"]):
        return "geometric_form"
    if any(w in t for w in ["control", "choice", "agency"]):
        return "modulatory"
    if any(w in t for w in ["stress", "cortisol", "gsr", "hrv", "heart"]):
        return "physiological_output"
    if any(w in t for w in ["mood", "affect", "valence", "pleasure", "comfort", "satisfy"]):
        return "affective_output"
    if any(w in t for w in ["creat", "attention", "memory", "cogni", "perform"]):
        return "cognitive_output"
    return "general"


def _classify_output_type(text: str) -> str:
    """Classify an output/DV into a type."""
    t = text.lower()
    if any(w in t for w in ["cortisol", "gsr", "hrv", "heart", "blood", "recovery", "pain"]):
        return "physiological_output"
    if any(w in t for w in ["mood", "affect", "valence", "beauty", "comfort", "well"]):
        return "affective_output"
    if any(w in t for w in ["creat", "test_score", "perform", "attention", "memory", "cogni"]):
        return "cognitive_output"
    if any(w in t for w in ["approach", "dwell", "occupancy", "behav"]):
        return "behavioral_output"
    return "outcome_general"


def _categorize(text: str) -> str:
    """Simple categorization."""
    t = text.lower()
    if "daylight" in t or "light" in t: return "lighting"
    if "noise" in t or "sound" in t: return "acoustic"
    if "thermal" in t or "temperature" in t: return "thermal"
    if "view" in t or "nature" in t: return "biophilic"
    if "ceiling" in t or "height" in t: return "spatial"
    if "material" in t or "surface" in t: return "material"
    return "general"


def _extract_causal_attribute(antecedent: str, full_text: str) -> str:
    """Try to identify the theoretically operative attribute."""
    t = f"{antecedent} {full_text}".lower()
    if "fractal" in t or "dimension" in t: return "fractal_dimension_D"
    if "1/f" in t or "spectral" in t: return "spectral_exponent_beta"
    if "lux" in t or "illuminan" in t: return "illuminance_lux"
    if "db" in t or "decibel" in t: return "sound_pressure_dB"
    if "temperature" in t or "°c" in t: return "temperature_C"
    if "roughness" in t or "ra" in t: return "surface_roughness_Ra"
    return antecedent


def _extract_value_from_text(text: str, attribute: str) -> str:
    """Try to extract a numeric value from text."""
    # Look for common numeric patterns
    patterns = [
        r'(\d+\.?\d*)\s*(?:lux|dB|°C|mm|μm|cm|Hz|ms)',
        r'[Dd]\s*[=≈]\s*(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*(?:–|-)\s*(\d+\.?\d*)',
        r'[r=]\s*(\d+\.?\d*)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return ""


# ─── Organize into Slot Types ───────────────────────────────────

def organize_by_slot_type(all_instances: list) -> list:
    """Group instances into SlotType objects, sorted by causal attribute."""
    slot_map = defaultdict(list)

    for inst in all_instances:
        slot_map[inst.slot_type].append(inst)

    slot_types = []
    slot_definitions = {
        "fractal_surface": ("Fractal Surface / 1/f Visual Pattern", "fractal_dimension_D", "Hausdorff_dimension", "1.3–1.5", 1.3, 1.5, "visual"),
        "spectral_signal": ("1/f Acoustic Signal", "spectral_exponent_beta", "power_law_exponent", "0.8–1.2", 0.8, 1.2, "auditory"),
        "material_thermal": ("Material Thermal Properties", "thermal_conductivity_lambda", "W_per_m_K", "< 0.5 (warm)", None, 0.5, "tactile"),
        "surface_texture": ("Surface Texture", "surface_roughness_Ra", "micrometers", "1–10 (C-tactile optimal)", 1.0, 10.0, "tactile"),
        "odorant": ("Odorant / Scent", "olfactory_pleasantness", "pleasantness_1_to_9", "> 5 (pleasant)", 5.0, 9.0, "olfactory"),
        "light_source": ("Light Source / Illumination", "illuminance_lux", "lux", "context-dependent", None, None, "visual"),
        "acoustic_source": ("Acoustic Source / Soundscape", "sound_level_dB", "dB_A", "< 55 (comfortable)", None, 55.0, "auditory"),
        "spatial_configuration": ("Spatial Configuration", "spatial_dimension", "meters_or_ratio", "context-dependent", None, None, "visual"),
        "biophilic_element": ("Biophilic Element", "nature_content", "categorical", "present", None, None, "visual"),
        "geometric_form": ("Geometric Form / Contour", "curvature", "categorical", "curved preferred", None, None, "visual"),
        "architectural_feature": ("Architectural Feature (general)", "effect_on_outcome", "Cohen_d", "> 0.3 (meaningful)", 0.3, None, "general"),
        "modulatory": ("Modulatory Factor", "modulation_coefficient", "multiplier", "context-dependent", None, None, "general"),
        "affective_output": ("Affective Outcome", "valence_rating", "scale_units", "positive", None, None, "outcome"),
        "cognitive_output": ("Cognitive Outcome", "performance_measure", "scale_units", "improved", None, None, "outcome"),
        "physiological_output": ("Physiological Outcome", "biomarker_level", "units_vary", "reduced_stress", None, None, "outcome"),
        "behavioral_output": ("Behavioral Outcome", "behavior_measure", "units_vary", "approach", None, None, "outcome"),
    }

    for slot_id, inst_list in sorted(slot_map.items()):
        defn = slot_definitions.get(slot_id, (slot_id, slot_id, "", "", None, None, ""))
        name, causal_attr, unit, opt_range, opt_min, opt_max, modality = defn

        # Sort instances by causal value (numeric if possible)
        def sort_key(inst):
            if inst.causal_value_numeric is not None:
                return inst.causal_value_numeric
            return 0.0
        inst_list.sort(key=sort_key, reverse=True)

        # Collect template IDs
        template_ids = list(set(
            inst.paper_id for inst in inst_list
            if inst.source == "template_parameters"
        ))

        slot_types.append(SlotType(
            slot_id=slot_id,
            name=name,
            description=f"{len(inst_list)} instances, organized by {causal_attr}",
            causal_attribute=causal_attr,
            causal_unit=unit,
            optimal_range=opt_range,
            optimal_min=opt_min,
            optimal_max=opt_max,
            modality=modality,
            template_ids=template_ids,
            instances=inst_list,
        ))

    slot_types.sort(key=lambda s: len(s.instances), reverse=True)
    return slot_types


# ─── Report Generation ───────────────────────────────────────────

def generate_report(library: InstanceLibrary) -> str:
    """Generate human-readable report of the instance library."""
    lines = []
    lines.append("=" * 78)
    lines.append("CMR INSTANCE LIBRARY — REPORT")
    lines.append(f"Generated: {library.generated_at}")
    lines.append(f"Version: {library.version}")
    lines.append("=" * 78)
    lines.append("")

    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append(f"  Total instances:    {library.total_instances}")
    lines.append(f"  Slot types:         {len(library.slot_types)}")
    lines.append("")

    lines.append("  By source:")
    for src, count in sorted(library.sources.items(), key=lambda x: -x[1]):
        lines.append(f"    {src:35s} {count:4d}")
    lines.append("")

    # Detail each slot type
    for slot in library.slot_types:
        lines.append("=" * 78)
        lines.append(f"SLOT TYPE: {slot.name}")
        lines.append(f"  Causal attribute: {slot.causal_attribute} ({slot.causal_unit})")
        lines.append(f"  Optimal range:    {slot.optimal_range}")
        lines.append(f"  Modality:         {slot.modality}")
        lines.append(f"  Instances:        {len(slot.instances)}")
        lines.append("-" * 78)
        lines.append("")

        # Show instances sorted by causal value
        for inst in slot.instances[:25]:  # top 25 per slot
            val_str = inst.causal_value[:30] if inst.causal_value else "?"
            eff_str = f"d={inst.effect_size:.2f}" if inst.effect_size else ""
            lines.append(f"  {inst.name[:45]:45s} | {val_str:15s} | {inst.validity:8s} | {eff_str:10s} | {inst.source[:30]}")

        if len(slot.instances) > 25:
            lines.append(f"  ... and {len(slot.instances) - 25} more instances")
        lines.append("")

    return "\n".join(lines)


# ─── Main Pipeline ───────────────────────────────────────────────

def build_library(data_dir: str, templates_dir: str) -> InstanceLibrary:
    """Build the complete instance library from all sources."""
    print("=" * 60, file=sys.stderr)
    print("CMR INSTANCE LIBRARY BUILDER", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    all_instances = []
    source_counts = defaultdict(int)

    # Source 1: Extracted findings
    print("\n[1/4] Mining extracted findings...", file=sys.stderr)
    ef_instances = mine_extracted_findings(data_dir)
    all_instances.extend(ef_instances)
    source_counts["extracted_findings"] = len(ef_instances)
    print(f"       Found {len(ef_instances)} instances", file=sys.stderr)

    # Source 2: Test papers
    print("\n[2/4] Mining test paper claims...", file=sys.stderr)
    tp_instances = mine_test_papers(data_dir)
    all_instances.extend(tp_instances)
    source_counts["test_papers"] = len(tp_instances)
    print(f"       Found {len(tp_instances)} instances", file=sys.stderr)

    # Source 3: Template parameters
    print("\n[3/4] Mining template calibrated parameters...", file=sys.stderr)
    tmpl_instances = mine_template_parameters(templates_dir)
    all_instances.extend(tmpl_instances)
    source_counts["template_parameters"] = len(tmpl_instances)
    print(f"       Found {len(tmpl_instances)} instances", file=sys.stderr)

    # Source 4: Literature seeds
    print("\n[4/4] Seeding from published literature...", file=sys.stderr)
    lit_instances = seed_literature_instances()
    all_instances.extend(lit_instances)
    source_counts["literature_seeds"] = len(lit_instances)
    print(f"       Seeded {len(lit_instances)} instances", file=sys.stderr)

    # Organize
    print(f"\nTotal raw instances: {len(all_instances)}", file=sys.stderr)
    print("Organizing by slot type...", file=sys.stderr)

    slot_types = organize_by_slot_type(all_instances)

    library = InstanceLibrary(
        version="1.0.0",
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        slot_types=slot_types,
        total_instances=len(all_instances),
        sources=dict(source_counts),
    )

    print(f"\nOrganized into {len(slot_types)} slot types", file=sys.stderr)
    for slot in slot_types:
        print(f"  {slot.name}: {len(slot.instances)} instances", file=sys.stderr)

    return library


def main():
    parser = argparse.ArgumentParser(description="CMR Instance Library Builder")
    parser.add_argument("--data-dir", "-d", default=None,
        help="Directory containing data/ (extracted_findings, test_papers)")
    parser.add_argument("--templates-dir", "-t", default=None,
        help="Directory containing template JSON files")
    parser.add_argument("--output", "-o", default=None,
        help="Output file path")
    parser.add_argument("--report", action="store_true", help="Human-readable report")
    parser.add_argument("--json", action="store_true", help="Full JSON output")

    args = parser.parse_args()

    # Auto-detect directories
    data_dir = args.data_dir
    templates_dir = args.templates_dir

    if not data_dir:
        for c in ["data", "../data", "/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/data"]:
            if os.path.isdir(c):
                data_dir = c
                break
    if not templates_dir:
        for c in ["data/templates", "../data/templates",
                   "/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/data/templates"]:
            if os.path.isdir(c):
                templates_dir = c
                break

    if not data_dir or not templates_dir:
        print("ERROR: Could not find data directories.", file=sys.stderr)
        sys.exit(1)

    library = build_library(data_dir, templates_dir)

    if args.json:
        # Serialize
        result = {
            "version": library.version,
            "generated_at": library.generated_at,
            "total_instances": library.total_instances,
            "sources": library.sources,
            "slot_types": []
        }
        for slot in library.slot_types:
            slot_dict = {
                "slot_id": slot.slot_id,
                "name": slot.name,
                "causal_attribute": slot.causal_attribute,
                "causal_unit": slot.causal_unit,
                "optimal_range": slot.optimal_range,
                "modality": slot.modality,
                "instance_count": len(slot.instances),
                "instances": [asdict(inst) for inst in slot.instances],
            }
            result["slot_types"].append(slot_dict)

        json_str = json.dumps(result, indent=2, default=str)
        if args.output:
            with open(args.output, "w") as f:
                f.write(json_str)
            print(f"Written to: {args.output}", file=sys.stderr)
        else:
            print(json_str)
    else:
        report = generate_report(library)
        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
            print(f"Report written to: {args.output}", file=sys.stderr)
        else:
            print(report)


if __name__ == "__main__":
    main()
