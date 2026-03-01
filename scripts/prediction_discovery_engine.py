#!/usr/bin/env python3
"""
Prediction Discovery Engine for CMR Templates
==============================================

Operationalizes the typed relational graph instantiation framework
described in Kirsh & Claude (2026), "Prediction Generation via Typed
Relational Graph Instantiation."

The engine:
  1. Parses all calibrated templates into normalized graph representations
  2. Builds a type ontology from mechanism chain nodes across templates
  3. Discovers shared nodes between template pairs (composition candidates)
  4. Generates predictions by instantiation and composition
  5. Scores informativeness
  6. Classifies interaction types
  7. Produces a ranked prediction report

Usage:
    python prediction_discovery_engine.py [--templates-dir DIR] [--output FILE]
    python prediction_discovery_engine.py --report   # Full report to stdout
    python prediction_discovery_engine.py --json      # Machine-readable JSON output

Author: David Kirsh & Claude Opus 4.6
Date:   2026-02-24
"""

import json
import os
import sys
import argparse
import re
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ─── Data Classes ────────────────────────────────────────────────

@dataclass
class MechanismNode:
    """A typed node in a mechanism chain graph."""
    node_id: str            # e.g., "T1:step1:from"
    template_id: str        # parent template
    step: int               # step number in chain
    position: str           # "from", "to", or "intermediate"
    label: str              # the text label
    type_tags: list = field(default_factory=list)  # inferred type categories
    modality: str = ""      # visual, auditory, thermal, olfactory, tactile, social, general
    substrate: str = ""     # neural substrate if specified
    parameters: dict = field(default_factory=dict)  # calibrated parameter values

@dataclass
class MechanismEdge:
    """A typed causal edge in a mechanism chain graph."""
    edge_id: str
    template_id: str
    step: int
    from_node: str          # node_id of source
    to_node: str            # node_id of target
    warrant: str            # MECHANISM, EMPIRICAL_ASSOCIATION, FUNCTIONAL, CAPACITY
    confidence: float
    description: str = ""
    has_competing_accounts: bool = False
    competing_account_names: list = field(default_factory=list)

@dataclass
class TemplateGraph:
    """A template represented as a typed relational graph."""
    template_id: str
    display_id: str
    name: str
    nodes: list = field(default_factory=list)       # list of MechanismNode
    edges: list = field(default_factory=list)        # list of MechanismEdge
    overall_confidence: float = 0.0
    bridge_warrant: str = ""
    modality: str = ""                               # primary sensory modality
    cross_interactions: list = field(default_factory=list)  # raw interaction data
    calibrated_params: dict = field(default_factory=dict)
    population_modifiers: dict = field(default_factory=dict)
    competing_accounts: list = field(default_factory=list)  # template-level

@dataclass
class SharedNode:
    """A node shared between two templates — a composition point."""
    node_a: MechanismNode
    node_b: MechanismNode
    template_a: str
    template_b: str
    similarity_score: float     # 0-1, how closely the types match
    shared_type_tags: list = field(default_factory=list)
    composition_type: str = ""  # "output-input", "shared-output", "shared-substrate"

@dataclass
class Prediction:
    """A generated prediction with informativeness score."""
    prediction_id: str
    description: str
    templates: list                  # template_ids involved
    prediction_type: str             # single_slot, multi_slot, composition, abductive
    interaction_type: str = "none"   # enhancement, catalysis, synergy, addition, diminishment, negation, distortion, ruination
    modalities: list = field(default_factory=list)
    informativeness: float = 0.0
    prior_improbability: float = 0.0
    mechanistic_specificity: float = 0.0
    discriminating_power: float = 0.0
    transfer_distance: float = 0.0
    transfer_confidence: float = 0.0
    testable_hypothesis: str = ""
    discriminating_experiment: str = ""
    detractor_vulnerability: str = ""


# ─── Type Ontology ───────────────────────────────────────────────

# Modality keywords for classification
MODALITY_KEYWORDS = {
    "visual": ["visual", "V1", "V2", "retina", "luminance", "chromatic", "fractal",
               "spatial frequency", "contrast", "glare", "flicker", "color", "light",
               "daylight", "facade", "pattern", "magnocellular", "parvocellular",
               "view", "window", "scene", "image", "saccade", "eye", "optic",
               "photoreception", "ipRGC", "melanopsin"],
    "auditory": ["auditory", "A1", "acoustic", "sound", "noise", "music", "speech",
                 "frequency", "temporal", "spectral", "soundscape", "reverberation",
                 "birdsong", "cochlea", "auditory cortex", "1/f temporal"],
    "thermal": ["thermal", "temperature", "thermoregulat", "TRPM", "TRPV",
                "warm", "cold", "heat", "insular", "allesthesia", "HVAC",
                "ventilat", "metabolic"],
    "olfactory": ["olfact", "smell", "scent", "odor", "aroma", "piriform",
                  "olfactory bulb", "nasal", "volatile", "VOC", "fragrance"],
    "tactile": ["tactile", "haptic", "touch", "S1", "somatosensory", "C-tactile",
                "roughness", "texture", "surface", "Meissner", "Pacinian",
                "mechanoreceptor", "afferent"],
    "social": ["social", "crowd", "density", "personal space", "proxemic",
               "conversational", "group", "privacy", "visibility"],
    "interoceptive": ["interoceptive", "body budget", "allostatic", "insular",
                      "homeostatic", "HPA", "cortisol", "stress", "arousal"],
}

# Type category keywords for node classification
TYPE_CATEGORIES = {
    "sensory_input": ["stimulus", "input", "surface", "material", "light",
                      "sound", "temperature", "scent", "texture"],
    "neural_encoding": ["V1", "A1", "S1", "cortex", "activation", "receptive field",
                        "sparse coding", "efficient coding", "representation",
                        "ipRGC", "melanopsin", "afferent", "thalamic"],
    "prediction_error": ["prediction error", "PE", "surprise", "mismatch",
                         "deviation", "expectation", "bayesian", "update"],
    "metabolic_cost": ["metabolic", "glucose", "BOLD", "energy", "synaptic",
                       "ATP", "oxygen", "cortical load"],
    "affective_output": ["aesthetic", "pleasure", "valence", "comfort",
                         "preference", "satisfaction", "delight", "stress",
                         "relaxation", "well-being", "mood", "affect"],
    "behavioral_output": ["approach", "avoidance", "dwell time", "occupancy",
                          "performance", "attention", "restoration", "sleep"],
    "physiological_output": ["GSR", "cortisol", "HRV", "EEG", "ERP",
                             "melatonin", "blood pressure", "heart rate", "BOLD"],
    "modulatory": ["control", "agency", "choice", "familiarity", "expertise",
                   "sensitivity", "individual differences", "SPS"],
    "dose_response": ["dose", "duration", "intensity", "threshold", "optimum",
                      "inverted-U", "logarithmic", "monotonic", "saturation"],
}


def classify_modality(text: str) -> str:
    """Classify a text string into a sensory modality."""
    text_lower = text.lower()
    scores = {}
    for modality, keywords in MODALITY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        if score > 0:
            scores[modality] = score
    if not scores:
        return "general"
    return max(scores, key=scores.get)


def classify_type(text: str) -> list:
    """Classify a text string into type categories."""
    text_lower = text.lower()
    tags = []
    for category, keywords in TYPE_CATEGORIES.items():
        if any(kw.lower() in text_lower for kw in keywords):
            tags.append(category)
    return tags if tags else ["unclassified"]


# ─── Template Parser ─────────────────────────────────────────────

def parse_template(filepath: str) -> Optional[TemplateGraph]:
    """Parse a template JSON file into a TemplateGraph."""
    with open(filepath) as f:
        data = json.load(f)

    # Filter: only calibrated templates
    status = data.get("calibration_status", data.get("status", ""))
    if status != "calibrated":
        return None

    tid = data.get("template_id", data.get("display_id", Path(filepath).stem))
    did = data.get("display_id", tid)
    name = data.get("name", "")

    chain = data.get("mechanism_chain", [])
    if not chain:
        return None

    graph = TemplateGraph(
        template_id=tid,
        display_id=did,
        name=name,
        overall_confidence=data.get("confidence", 0.0),
        bridge_warrant=data.get("bridge_warrant", ""),
        calibrated_params=data.get("calibrated_parameters", {}),
        population_modifiers=data.get("population_modifiers", {}),
    )

    # Parse cross-template interactions (handle both dict and list forms)
    raw_interactions = data.get("cross_template_interactions", {})
    if isinstance(raw_interactions, dict):
        for key, desc in raw_interactions.items():
            graph.cross_interactions.append({
                "template_id": key,
                "description": str(desc),
                "interaction_type": "unspecified"
            })
    elif isinstance(raw_interactions, list):
        for item in raw_interactions:
            if isinstance(item, dict):
                graph.cross_interactions.append(item)

    # Also grab interaction_templates and interactions fields
    for field_name in ["interaction_templates", "interactions"]:
        extra = data.get(field_name, [])
        if isinstance(extra, list):
            for item in extra:
                if isinstance(item, dict):
                    graph.cross_interactions.append(item)

    # Parse mechanism chain into nodes and edges
    all_node_texts = []
    for step_data in chain:
        step_num = step_data.get("step", 0)
        warrant = step_data.get("warrant", step_data.get("warrant_type", "UNKNOWN"))
        conf = step_data.get("confidence",
                step_data.get("warrant_confidence", graph.overall_confidence))

        # Extract from/to text
        from_text = step_data.get("from", step_data.get("label", f"step_{step_num}"))
        to_text = step_data.get("to", "")
        description = step_data.get("description", step_data.get("process", ""))
        substrate = step_data.get("substrate", "")

        # Build combined text for type/modality classification
        combined = f"{from_text} {to_text} {description} {substrate}"
        all_node_texts.append(combined)

        # Create FROM node
        from_id = f"{tid}:s{step_num}:from"
        from_node = MechanismNode(
            node_id=from_id,
            template_id=tid,
            step=step_num,
            position="from",
            label=from_text,
            type_tags=classify_type(f"{from_text} {description}"),
            modality=classify_modality(f"{from_text} {substrate}"),
            substrate=substrate,
        )
        graph.nodes.append(from_node)

        # Create TO node (if present)
        if to_text:
            to_id = f"{tid}:s{step_num}:to"
            to_node = MechanismNode(
                node_id=to_id,
                template_id=tid,
                step=step_num,
                position="to",
                label=to_text,
                type_tags=classify_type(f"{to_text} {description}"),
                modality=classify_modality(f"{to_text} {substrate}"),
                substrate=substrate,
            )
            graph.nodes.append(to_node)
        else:
            to_id = from_id  # self-loop placeholder

        # Extract competing accounts
        justification = step_data.get("justification", {})
        competing = justification.get("competing_accounts", [])
        comp_names = []
        if competing and isinstance(competing, list):
            for ca in competing:
                if isinstance(ca, dict):
                    comp_names.append(ca.get("account", ca.get("claim", "unknown")))
                    graph.competing_accounts.append(ca)

        # Create edge
        edge = MechanismEdge(
            edge_id=f"{tid}:e{step_num}",
            template_id=tid,
            step=step_num,
            from_node=from_id,
            to_node=to_id,
            warrant=warrant,
            confidence=conf if isinstance(conf, (int, float)) else 0.0,
            description=description,
            has_competing_accounts=len(comp_names) > 0,
            competing_account_names=comp_names,
        )
        graph.edges.append(edge)

    # Determine primary modality from all node texts
    combined_text = " ".join(all_node_texts)
    graph.modality = classify_modality(combined_text)

    return graph


def load_all_templates(templates_dir: str) -> list:
    """Load and parse all calibrated templates from directory."""
    graphs = []
    template_dir = Path(templates_dir)
    if not template_dir.exists():
        print(f"ERROR: Templates directory not found: {templates_dir}", file=sys.stderr)
        return graphs

    for filepath in sorted(template_dir.glob("*.json")):
        try:
            graph = parse_template(str(filepath))
            if graph:
                graphs.append(graph)
        except Exception as e:
            print(f"  WARN: Could not parse {filepath.name}: {e}", file=sys.stderr)
    return graphs


# ─── Node Similarity & Composition Discovery ────────────────────

def compute_node_similarity(node_a: MechanismNode, node_b: MechanismNode) -> float:
    """
    Compute similarity between two mechanism nodes based on:
    - Type tag overlap (Jaccard similarity)
    - Modality match (binary)
    - Keyword overlap in labels (Jaccard on words)
    """
    if node_a.template_id == node_b.template_id:
        return 0.0  # Same template — not a composition

    # Type tag Jaccard
    tags_a = set(node_a.type_tags)
    tags_b = set(node_b.type_tags)
    if tags_a and tags_b:
        type_sim = len(tags_a & tags_b) / len(tags_a | tags_b)
    else:
        type_sim = 0.0

    # Modality match
    modality_sim = 1.0 if node_a.modality == node_b.modality else 0.3

    # Label word overlap
    words_a = set(re.findall(r'\w+', node_a.label.lower()))
    words_b = set(re.findall(r'\w+', node_b.label.lower()))
    if words_a and words_b:
        word_sim = len(words_a & words_b) / len(words_a | words_b)
    else:
        word_sim = 0.0

    # Weighted combination
    return 0.4 * type_sim + 0.3 * modality_sim + 0.3 * word_sim


def discover_shared_nodes(graphs: list, min_similarity: float = 0.45) -> list:
    """Find pairs of nodes across templates that share types (composition candidates)."""
    shared = []
    seen_pairs = set()

    for i, g_a in enumerate(graphs):
        for j, g_b in enumerate(graphs):
            if j <= i:
                continue
            pair_key = (g_a.template_id, g_b.template_id)
            if pair_key in seen_pairs:
                continue

            best_sim = 0.0
            best_pair = None

            for n_a in g_a.nodes:
                for n_b in g_b.nodes:
                    sim = compute_node_similarity(n_a, n_b)
                    if sim > best_sim:
                        best_sim = sim
                        best_pair = (n_a, n_b)

            if best_sim >= min_similarity and best_pair:
                n_a, n_b = best_pair
                shared_tags = list(set(n_a.type_tags) & set(n_b.type_tags))

                # Determine composition type
                if "affective_output" in shared_tags or "behavioral_output" in shared_tags:
                    comp_type = "shared-output"
                elif "sensory_input" in shared_tags:
                    comp_type = "output-input"
                elif n_a.substrate and n_b.substrate and n_a.substrate == n_b.substrate:
                    comp_type = "shared-substrate"
                else:
                    comp_type = "shared-type"

                shared.append(SharedNode(
                    node_a=n_a,
                    node_b=n_b,
                    template_a=g_a.template_id,
                    template_b=g_b.template_id,
                    similarity_score=best_sim,
                    shared_type_tags=shared_tags,
                    composition_type=comp_type,
                ))
                seen_pairs.add(pair_key)

    # Sort by similarity descending
    shared.sort(key=lambda s: s.similarity_score, reverse=True)
    return shared


# ─── Interaction Classification ──────────────────────────────────

def classify_interaction(
    graph_a: TemplateGraph,
    graph_b: TemplateGraph,
    shared_node: SharedNode
) -> str:
    """
    Classify the interaction type between two templates based on:
    - Their explicit cross_template_interactions
    - The nature of the shared node
    - Modality relationship
    """
    # Check explicit interactions first
    for interaction in graph_a.cross_interactions:
        target = interaction.get("template_id", interaction.get("id", ""))
        itype = interaction.get("interaction_type", interaction.get("nature", ""))
        desc = interaction.get("description", "").lower()

        if (graph_b.template_id in target or graph_b.display_id in target or
            target in graph_b.template_id or target in graph_b.display_id):
            # Map explicit types to our taxonomy
            if any(w in desc for w in ["amplif", "catalyz", "catalys", "potentiat"]):
                return "catalysis"
            if any(w in desc for w in ["synerg", "super-additive", "convergent", "convergence"]):
                return "synergy"
            if any(w in desc for w in ["moderat", "modulates", "modulat"]):
                return "enhancement"
            if any(w in desc for w in ["compet", "diminish", "reduce", "attenuate"]):
                return "diminishment"
            if any(w in desc for w in ["block", "negat", "eliminat", "prevent"]):
                return "negation"
            if any(w in desc for w in ["distort", "shift", "narrow", "widen"]):
                return "distortion"
            if any(w in desc for w in ["complement", "independent", "additive"]):
                return "addition"
            if any(w in desc for w in ["feeds_into", "receives_from"]):
                return "enhancement"

    # Infer from structural properties
    if graph_a.modality == graph_b.modality:
        # Same modality: likely enhancement or competition
        if shared_node.composition_type == "shared-output":
            return "enhancement"
        elif shared_node.composition_type == "shared-substrate":
            return "diminishment"  # competing for same neural resource
    else:
        # Different modalities: likely addition or synergy
        if shared_node.composition_type == "shared-output":
            return "addition"  # independent pathways, same outcome

    return "enhancement"  # default conservative estimate


# ─── Informativeness Scoring ─────────────────────────────────────

def compute_transfer_distance(graph_a: TemplateGraph, graph_b: TemplateGraph) -> float:
    """
    Compute the transfer distance between two templates.
    0.0 = home domain (same template), 1.0 = maximum distance.
    """
    # Same modality = low distance
    if graph_a.modality == graph_b.modality:
        return 0.2
    # Related modalities
    related_pairs = {
        ("visual", "auditory"), ("visual", "tactile"),
        ("auditory", "tactile"), ("thermal", "tactile"),
        ("olfactory", "thermal"),
    }
    pair = tuple(sorted([graph_a.modality, graph_b.modality]))
    if pair in related_pairs:
        return 0.5
    # Distant modalities
    return 0.8


def score_informativeness(prediction: Prediction) -> float:
    """
    Compute the informativeness score as the product of three factors:
    I = prior_improbability * mechanistic_specificity * discriminating_power
    Each factor is on [0, 1]. The overall score is on [0, 1].
    """
    # Clamp factors
    pi = max(0.0, min(1.0, prediction.prior_improbability))
    ms = max(0.0, min(1.0, prediction.mechanistic_specificity))
    dp = max(0.0, min(1.0, prediction.discriminating_power))

    # Geometric mean (treats all factors as equally important)
    if pi * ms * dp == 0:
        return (pi + ms + dp) / 3.0  # fallback to arithmetic mean
    return (pi * ms * dp) ** (1.0 / 3.0)


# ─── Prediction Generators ──────────────────────────────────────

def generate_single_template_predictions(graph: TemplateGraph) -> list:
    """Generate predictions from a single template by analyzing its structure."""
    predictions = []
    tid = graph.template_id
    did = graph.display_id

    # --- Prediction 1: Home-domain confirmation ---
    if graph.edges:
        first_edge = graph.edges[0]
        last_edge = graph.edges[-1]

        input_label = graph.nodes[0].label if graph.nodes else "input"
        output_nodes = [n for n in graph.nodes if "affective_output" in n.type_tags
                       or "behavioral_output" in n.type_tags
                       or "physiological_output" in n.type_tags]
        output_label = output_nodes[-1].label if output_nodes else "output"

        predictions.append(Prediction(
            prediction_id=f"{did}_HOME",
            description=f"Home-domain confirmation: {input_label} produces {output_label} via the {graph.bridge_warrant} pathway specified in {did}",
            templates=[tid],
            prediction_type="single_slot",
            modalities=[graph.modality],
            prior_improbability=0.1,  # expected, not surprising
            mechanistic_specificity=0.7,  # well-specified mechanism
            discriminating_power=0.2,   # doesn't distinguish from competing accounts
            transfer_distance=0.0,
            transfer_confidence=graph.overall_confidence,
            testable_hypothesis=f"Replicate the canonical finding of {did} with pre-registered protocol",
        ))

    # --- Prediction 2: Competing-accounts discrimination ---
    if graph.competing_accounts:
        for ca in graph.competing_accounts[:2]:  # top 2 competing accounts
            account_name = ca.get("account", ca.get("claim", "alternative"))
            implication = ca.get("implication_for_template", "modifies prediction")

            predictions.append(Prediction(
                prediction_id=f"{did}_DISCRIM_{len(predictions)}",
                description=f"Discriminating test: {did} mechanism vs. {account_name}",
                templates=[tid],
                prediction_type="single_slot",
                modalities=[graph.modality],
                prior_improbability=0.6,
                mechanistic_specificity=0.8,
                discriminating_power=0.9,  # explicitly discriminating
                transfer_distance=0.0,
                transfer_confidence=graph.overall_confidence,
                testable_hypothesis=f"Design experiment where {did} and {account_name} make divergent predictions",
                discriminating_experiment=f"If {did} is correct: {implication}",
            ))

    # --- Prediction 3: Dose-response boundary ---
    if graph.calibrated_params:
        # Look for parameters with ranges
        for param_name, param_data in graph.calibrated_params.items():
            if not isinstance(param_data, dict):
                continue
            if "range" in param_data or "optimal_range" in param_data:
                range_val = param_data.get("range", param_data.get("optimal_range", ""))
                predictions.append(Prediction(
                    prediction_id=f"{did}_DOSE_{len(predictions)}",
                    description=f"Dose-response boundary: {param_name} beyond optimal range ({range_val}) should produce diminished or inverted effect",
                    templates=[tid],
                    prediction_type="single_slot",
                    interaction_type="distortion",
                    modalities=[graph.modality],
                    prior_improbability=0.5,
                    mechanistic_specificity=0.7,
                    discriminating_power=0.5,
                    transfer_distance=0.1,
                    transfer_confidence=graph.overall_confidence * 0.8,
                    testable_hypothesis=f"Systematically vary {param_name} above and below optimal range to map dose-response curve shape",
                ))
                break  # one dose-response prediction per template

    # --- Prediction 4: Population modifier test ---
    if graph.population_modifiers:
        for pop_name, pop_data in list(graph.population_modifiers.items())[:1]:
            modifier_desc = ""
            if isinstance(pop_data, dict):
                modifier_desc = pop_data.get("modifier", pop_data.get("effect", str(pop_data)))
            predictions.append(Prediction(
                prediction_id=f"{did}_POP_{len(predictions)}",
                description=f"Population modifier: {pop_name} shifts {did} effect ({modifier_desc})",
                templates=[tid],
                prediction_type="single_slot",
                interaction_type="distortion",
                modalities=[graph.modality],
                prior_improbability=0.4,
                mechanistic_specificity=0.6,
                discriminating_power=0.4,
                transfer_distance=0.1,
                transfer_confidence=graph.overall_confidence * 0.7,
                testable_hypothesis=f"Compare {did} effect in {pop_name} population vs. baseline population",
            ))

    # Score all predictions
    for p in predictions:
        p.informativeness = score_informativeness(p)

    return predictions


def generate_composition_predictions(
    graph_a: TemplateGraph,
    graph_b: TemplateGraph,
    shared: SharedNode
) -> list:
    """Generate predictions from composing two templates at a shared node."""
    predictions = []

    interaction_type = classify_interaction(graph_a, graph_b, shared)
    transfer_dist = compute_transfer_distance(graph_a, graph_b)

    # Combined confidence: product of individual confidences, scaled by similarity
    combined_conf = (graph_a.overall_confidence * graph_b.overall_confidence *
                     shared.similarity_score)

    modalities = list(set([graph_a.modality, graph_b.modality]))

    # Prior improbability scales with transfer distance and interaction complexity
    base_improbability = 0.3 + 0.5 * transfer_dist

    # --- Composition Prediction ---
    desc_parts = []
    desc_parts.append(f"Compose {graph_a.display_id} ({graph_a.name})")
    desc_parts.append(f"with {graph_b.display_id} ({graph_b.name})")
    desc_parts.append(f"via shared node type [{', '.join(shared.shared_type_tags)}]")
    desc_parts.append(f"({shared.composition_type})")

    interaction_descriptions = {
        "enhancement": f"Effect of {graph_a.display_id} raises baseline for {graph_b.display_id}; combined effect is sub-additive but larger than either alone",
        "catalysis": f"{graph_a.display_id} has small direct effect but dramatically amplifies {graph_b.display_id}",
        "synergy": f"Combined effect of {graph_a.display_id} + {graph_b.display_id} exceeds sum of individual effects",
        "addition": f"{graph_a.display_id} and {graph_b.display_id} operate on independent pathways; effects simply sum",
        "diminishment": f"{graph_a.display_id} partially reduces {graph_b.display_id} effect through shared resource competition",
        "negation": f"{graph_a.display_id} blocks {graph_b.display_id} at the shared node, eliminating its effect",
        "distortion": f"{graph_a.display_id} alters the dose-response shape of {graph_b.display_id}",
        "ruination": f"Co-activation of {graph_a.display_id} and {graph_b.display_id} produces mutual degradation",
    }

    hypothesis = interaction_descriptions.get(interaction_type,
        f"Unknown interaction between {graph_a.display_id} and {graph_b.display_id}")

    # Specificity bonus for cross-modal compositions
    specificity_bonus = 0.2 if graph_a.modality != graph_b.modality else 0.0

    predictions.append(Prediction(
        prediction_id=f"COMP_{graph_a.display_id}x{graph_b.display_id}",
        description=" ".join(desc_parts),
        templates=[graph_a.template_id, graph_b.template_id],
        prediction_type="composition",
        interaction_type=interaction_type,
        modalities=modalities,
        prior_improbability=min(1.0, base_improbability),
        mechanistic_specificity=min(1.0, 0.5 + specificity_bonus + 0.2 * shared.similarity_score),
        discriminating_power=0.4 + 0.3 * transfer_dist,  # more surprising = more discriminating
        transfer_distance=transfer_dist,
        transfer_confidence=combined_conf,
        testable_hypothesis=hypothesis,
        discriminating_experiment=f"Present both stimuli simultaneously vs. individually; measure whether combined effect matches {interaction_type} prediction",
    ))

    # Score
    for p in predictions:
        p.informativeness = score_informativeness(p)

    return predictions


def generate_cross_modal_interference_predictions(graphs: list) -> list:
    """
    Generate predictions about cross-modal interference:
    what happens when beneficial stimuli from one modality encounter
    detractors from another.
    """
    predictions = []

    # Canonical detractors by modality
    detractors = {
        "visual": [
            ("visual_clutter", "Visual clutter (spatial entropy > 4 bits/deg²)", "attentional_capture"),
            ("visual_randomness", "Random visual noise (β < 1.0)", "mechanism_interference"),
            ("glare", "Glare (luminance ratio > 1:40)", "mechanism_interference"),
        ],
        "auditory": [
            ("speech_noise", "Intelligible speech at 55dB", "attentional_capture"),
            ("mechanical_drone", "Low-frequency mechanical drone at 45dB", "chronic_stress"),
            ("impulsive_noise", "Intermittent door slams at 85dB", "startle_reset"),
        ],
        "olfactory": [
            ("voc_offgassing", "Synthetic material VOC off-gassing", "contextual_contamination"),
            ("olfactory_incongruence", "Scent-material mismatch", "mechanism_interference"),
        ],
        "thermal": [
            ("thermal_neutrality", "Strict HVAC thermal neutrality (±0.5°C)", "mechanism_elimination"),
            ("thermal_extreme", "Temperature outside comfort band (>28°C or <18°C)", "nociceptive_override"),
        ],
        "tactile": [
            ("vibration", "Structural vibration from HVAC/traffic", "signal_masking"),
            ("surface_extreme", "Surface temperature extreme (<15°C or >40°C)", "nociceptive_override"),
        ],
    }

    for graph in graphs:
        # For each template, find detractors from OTHER modalities
        for det_modality, det_list in detractors.items():
            if det_modality == graph.modality:
                continue  # skip same-modality (those are intra-modal)

            for det_id, det_desc, det_route in det_list:
                # Determine interaction type based on degradation route
                if det_route == "attentional_capture":
                    interaction = "diminishment"
                    improbability = 0.4
                elif det_route == "mechanism_interference":
                    interaction = "negation"
                    improbability = 0.5
                elif det_route == "contextual_contamination":
                    interaction = "ruination"
                    improbability = 0.3
                elif det_route == "mechanism_elimination":
                    interaction = "negation"
                    improbability = 0.6
                elif det_route == "chronic_stress":
                    interaction = "diminishment"
                    improbability = 0.3
                elif det_route == "nociceptive_override":
                    interaction = "negation"
                    improbability = 0.2
                elif det_route == "signal_masking":
                    interaction = "diminishment"
                    improbability = 0.4
                elif det_route == "startle_reset":
                    interaction = "ruination"
                    improbability = 0.3
                else:
                    interaction = "diminishment"
                    improbability = 0.3

                predictions.append(Prediction(
                    prediction_id=f"XMOD_{graph.display_id}_{det_id}",
                    description=f"Cross-modal interference: {det_desc} ({det_modality}) acting on {graph.display_id} ({graph.modality})",
                    templates=[graph.template_id],
                    prediction_type="cross_modal_interference",
                    interaction_type=interaction,
                    modalities=[graph.modality, det_modality],
                    prior_improbability=improbability,
                    mechanistic_specificity=0.5,
                    discriminating_power=0.5,
                    transfer_distance=compute_transfer_distance(graph, graph),  # within-template
                    transfer_confidence=graph.overall_confidence * 0.6,
                    testable_hypothesis=f"Test {graph.display_id} benefit with and without {det_desc} present",
                    detractor_vulnerability=f"Route: {det_route}; predicted interaction: {interaction}",
                ))

    # Score all
    for p in predictions:
        p.informativeness = score_informativeness(p)

    return predictions


# ─── Report Generation ───────────────────────────────────────────

def informativeness_label(score: float) -> str:
    if score >= 0.7: return "VERY HIGH"
    if score >= 0.55: return "HIGH"
    if score >= 0.4: return "MODERATE"
    if score >= 0.25: return "LOW"
    return "VERY LOW"


def generate_report(
    graphs: list,
    shared_nodes: list,
    all_predictions: list,
    output_file: str = None
) -> str:
    """Generate human-readable report of discovered predictions."""
    lines = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines.append("=" * 78)
    lines.append("CMR PREDICTION DISCOVERY ENGINE — REPORT")
    lines.append(f"Generated: {timestamp}")
    lines.append("=" * 78)
    lines.append("")

    # Summary statistics
    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append(f"  Templates analyzed:         {len(graphs)}")
    lines.append(f"  Composition candidates:     {len(shared_nodes)}")
    lines.append(f"  Total predictions generated: {len(all_predictions)}")
    lines.append("")

    # Count by type
    type_counts = defaultdict(int)
    interaction_counts = defaultdict(int)
    modality_counts = defaultdict(int)
    info_counts = defaultdict(int)

    for p in all_predictions:
        type_counts[p.prediction_type] += 1
        interaction_counts[p.interaction_type] += 1
        for m in p.modalities:
            modality_counts[m] += 1
        info_counts[informativeness_label(p.informativeness)] += 1

    lines.append("  By prediction type:")
    for t, c in sorted(type_counts.items()):
        lines.append(f"    {t:35s} {c:4d}")
    lines.append("")
    lines.append("  By interaction type:")
    for t, c in sorted(interaction_counts.items()):
        lines.append(f"    {t:35s} {c:4d}")
    lines.append("")
    lines.append("  By modality involved:")
    for m, c in sorted(modality_counts.items(), key=lambda x: -x[1]):
        lines.append(f"    {m:35s} {c:4d}")
    lines.append("")
    lines.append("  By informativeness rating:")
    for label in ["VERY HIGH", "HIGH", "MODERATE", "LOW", "VERY LOW"]:
        lines.append(f"    {label:35s} {info_counts.get(label, 0):4d}")
    lines.append("")

    # ─── Top predictions by informativeness ───
    sorted_preds = sorted(all_predictions, key=lambda p: p.informativeness, reverse=True)

    lines.append("=" * 78)
    lines.append("TOP 30 MOST INFORMATIVE PREDICTIONS")
    lines.append("=" * 78)
    lines.append("")

    for i, p in enumerate(sorted_preds[:30], 1):
        lines.append(f"  [{i:2d}] {p.prediction_id}")
        lines.append(f"       Type:           {p.prediction_type}")
        lines.append(f"       Interaction:     {p.interaction_type}")
        lines.append(f"       Modalities:      {', '.join(p.modalities)}")
        lines.append(f"       Informativeness: {p.informativeness:.3f} ({informativeness_label(p.informativeness)})")
        lines.append(f"       Prior improb.:   {p.prior_improbability:.2f}")
        lines.append(f"       Specificity:     {p.mechanistic_specificity:.2f}")
        lines.append(f"       Discrim. power:  {p.discriminating_power:.2f}")
        lines.append(f"       Transfer conf.:  {p.transfer_confidence:.3f}")
        lines.append(f"       Description:     {p.description[:120]}")
        if p.testable_hypothesis:
            lines.append(f"       Hypothesis:      {p.testable_hypothesis[:120]}")
        if p.discriminating_experiment:
            lines.append(f"       Experiment:      {p.discriminating_experiment[:120]}")
        lines.append("")

    # ─── Composition map ───
    lines.append("=" * 78)
    lines.append("TEMPLATE COMPOSITION MAP (top 20 pairs by node similarity)")
    lines.append("=" * 78)
    lines.append("")

    for sn in shared_nodes[:20]:
        lines.append(f"  {sn.template_a} <-> {sn.template_b}")
        lines.append(f"    Similarity:  {sn.similarity_score:.3f}")
        lines.append(f"    Shared tags: {', '.join(sn.shared_type_tags)}")
        lines.append(f"    Comp. type:  {sn.composition_type}")
        lines.append(f"    Node A:      {sn.node_a.label[:80]}")
        lines.append(f"    Node B:      {sn.node_b.label[:80]}")
        lines.append("")

    # ─── Interaction type distribution per modality pair ───
    lines.append("=" * 78)
    lines.append("INTERACTION TYPES BY MODALITY PAIR")
    lines.append("=" * 78)
    lines.append("")

    pair_interactions = defaultdict(lambda: defaultdict(int))
    for p in all_predictions:
        if len(p.modalities) >= 2:
            pair = tuple(sorted(p.modalities[:2]))
            pair_interactions[pair][p.interaction_type] += 1

    for pair, itypes in sorted(pair_interactions.items()):
        lines.append(f"  {pair[0]} × {pair[1]}:")
        for itype, count in sorted(itypes.items(), key=lambda x: -x[1]):
            lines.append(f"    {itype:25s} {count:3d}")
        lines.append("")

    # ─── Detractor vulnerability ranking ───
    lines.append("=" * 78)
    lines.append("MOST DETRACTOR-VULNERABLE TEMPLATES")
    lines.append("=" * 78)
    lines.append("")

    vulnerability = defaultdict(int)
    for p in all_predictions:
        if p.prediction_type == "cross_modal_interference":
            for tid in p.templates:
                vulnerability[tid] += 1

    for tid, count in sorted(vulnerability.items(), key=lambda x: -x[1])[:15]:
        # Find graph
        g = next((g for g in graphs if g.template_id == tid), None)
        dname = g.display_id if g else tid
        lines.append(f"  {dname:40s} {count:3d} detractor exposures ({g.modality if g else '?'})")
    lines.append("")

    report = "\n".join(lines)

    if output_file:
        with open(output_file, "w") as f:
            f.write(report)
        print(f"Report written to: {output_file}", file=sys.stderr)

    return report


# ─── Main Pipeline ───────────────────────────────────────────────

def run_pipeline(templates_dir: str, output_file: str = None,
                 json_output: bool = False) -> dict:
    """
    Run the full prediction discovery pipeline.

    Steps:
      1. Load and parse all calibrated templates
      2. Discover shared nodes (composition candidates)
      3. Generate single-template predictions
      4. Generate composition predictions
      5. Generate cross-modal interference predictions
      6. Score and rank all predictions
      7. Produce report
    """
    print("=" * 60, file=sys.stderr)
    print("CMR PREDICTION DISCOVERY ENGINE", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # Step 1: Load templates
    print(f"\n[1/7] Loading templates from {templates_dir}...", file=sys.stderr)
    graphs = load_all_templates(templates_dir)
    print(f"       Loaded {len(graphs)} calibrated templates", file=sys.stderr)

    if not graphs:
        print("ERROR: No calibrated templates found!", file=sys.stderr)
        return {}

    # Print modality distribution
    mod_dist = defaultdict(int)
    for g in graphs:
        mod_dist[g.modality] += 1
    for mod, count in sorted(mod_dist.items(), key=lambda x: -x[1]):
        print(f"       {mod}: {count}", file=sys.stderr)

    # Step 2: Discover shared nodes
    print(f"\n[2/7] Discovering shared nodes...", file=sys.stderr)
    shared_nodes = discover_shared_nodes(graphs, min_similarity=0.40)
    print(f"       Found {len(shared_nodes)} composition candidates", file=sys.stderr)

    # Step 3: Single-template predictions
    print(f"\n[3/7] Generating single-template predictions...", file=sys.stderr)
    single_preds = []
    for g in graphs:
        preds = generate_single_template_predictions(g)
        single_preds.extend(preds)
    print(f"       Generated {len(single_preds)} single-template predictions", file=sys.stderr)

    # Step 4: Composition predictions
    print(f"\n[4/7] Generating composition predictions...", file=sys.stderr)
    comp_preds = []
    graph_map = {g.template_id: g for g in graphs}
    for sn in shared_nodes:
        if sn.template_a in graph_map and sn.template_b in graph_map:
            preds = generate_composition_predictions(
                graph_map[sn.template_a],
                graph_map[sn.template_b],
                sn
            )
            comp_preds.extend(preds)
    print(f"       Generated {len(comp_preds)} composition predictions", file=sys.stderr)

    # Step 5: Cross-modal interference
    print(f"\n[5/7] Generating cross-modal interference predictions...", file=sys.stderr)
    xmod_preds = generate_cross_modal_interference_predictions(graphs)
    print(f"       Generated {len(xmod_preds)} cross-modal interference predictions", file=sys.stderr)

    # Step 6: Combine and rank
    print(f"\n[6/7] Scoring and ranking all predictions...", file=sys.stderr)
    all_predictions = single_preds + comp_preds + xmod_preds
    all_predictions.sort(key=lambda p: p.informativeness, reverse=True)
    print(f"       Total: {len(all_predictions)} predictions", file=sys.stderr)

    # Step 7: Report
    print(f"\n[7/7] Generating report...", file=sys.stderr)

    if json_output:
        result = {
            "timestamp": datetime.now().isoformat(),
            "templates_analyzed": len(graphs),
            "composition_candidates": len(shared_nodes),
            "total_predictions": len(all_predictions),
            "predictions": [asdict(p) for p in all_predictions[:100]],  # top 100
            "shared_nodes": [
                {
                    "template_a": sn.template_a,
                    "template_b": sn.template_b,
                    "similarity": sn.similarity_score,
                    "shared_tags": sn.shared_type_tags,
                    "composition_type": sn.composition_type,
                }
                for sn in shared_nodes[:50]
            ],
        }
        json_str = json.dumps(result, indent=2)
        if output_file:
            with open(output_file, "w") as f:
                f.write(json_str)
        else:
            print(json_str)
        return result

    report = generate_report(graphs, shared_nodes, all_predictions, output_file)
    if not output_file:
        print(report)

    return {
        "templates": len(graphs),
        "shared_nodes": len(shared_nodes),
        "predictions": len(all_predictions),
        "report": report,
    }


# ─── CLI ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="CMR Prediction Discovery Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python prediction_discovery_engine.py --report
  python prediction_discovery_engine.py --json --output predictions.json
  python prediction_discovery_engine.py --output report.txt
        """
    )
    parser.add_argument("--templates-dir", "-t",
        default=None,
        help="Directory containing template JSON files")
    parser.add_argument("--output", "-o",
        default=None,
        help="Output file path (default: stdout)")
    parser.add_argument("--report", action="store_true",
        help="Generate human-readable report (default)")
    parser.add_argument("--json", action="store_true",
        help="Generate machine-readable JSON output")

    args = parser.parse_args()

    # Auto-detect templates directory
    if args.templates_dir:
        templates_dir = args.templates_dir
    else:
        # Try common locations
        candidates = [
            "data/templates",
            "../data/templates",
            "/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/data/templates",
        ]
        templates_dir = None
        for c in candidates:
            if os.path.isdir(c):
                templates_dir = c
                break
        if not templates_dir:
            print("ERROR: Could not find templates directory. Use --templates-dir.", file=sys.stderr)
            sys.exit(1)

    run_pipeline(templates_dir, args.output, args.json)


if __name__ == "__main__":
    main()
