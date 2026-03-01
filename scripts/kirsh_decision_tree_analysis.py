#!/usr/bin/env python3
"""
Kirsh Decision Tree Method for Identifying Causally Active Attributes

Implements David Kirsh's approach (UCSD Cognitive Science):
1. Extract environmentally-relevant stimuli from empirical articles
2. Cluster into commonsense categories
3. For each category, apply decision tree analysis to identify essential vs. incidental attributes
4. Map to scientific/computational attributes
5. Identify vision algorithms needed for extraction
6. Discover NEW attributes not yet in the taxonomy

Author: Claude Code (Anthropic)
Date: 2026-02-28
"""

import json
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any, Set
from dataclasses import dataclass, asdict
import datetime

# =============================================================================
# PART 0: Data Loading and Filtering
# =============================================================================

def load_stimuli():
    """Load all stimulus descriptions from empirical articles."""
    with open('/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/data/stimulus_descriptions_from_articles.json', 'r') as f:
        return json.load(f)

def load_attributes_taxonomy():
    """Load the existing 21-attribute causal-theoretic taxonomy."""
    with open('/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/data/attributes/causal_theoretic_image_attributes.json', 'r') as f:
        return json.load(f)

def filter_environmental_stimuli(all_stimuli: List[Dict]) -> List[Dict]:
    """
    Filter stimuli to keep only ENVIRONMENTAL antecedents.
    Remove: gender, age, brain stimulation, drug effects, personality, etc.
    Keep: room type, lighting, colors, materials, plants, water, views, etc.
    """
    # Non-environmental antecedents to filter OUT
    non_environmental = {
        'gender', 'age', 'age group', 'sex', 'personality', 'trait',
        'disorder', 'diagnosis', 'pathology', 'mental health',
        'neuroticism', 'extraversion', 'conscientiousness', 'agreeableness', 'openness',
        'culture', 'ethnicity', 'nationality', 'language',
        'brain stimulation', 'tms', 'tdcs', 'medication', 'drug',
        'caffeine', 'alcohol', 'psychoactive', 'pharmacological',
        'training', 'expertise', 'experience', 'profession',
        'prior exposure', 'expectation', 'instruction',
        'mood induction', 'emotion induction', 'stress',
        'time of day', 'circadian', 'temporal',
        'arousal', 'fatigue', 'sleep deprivation',
        'socioeconomic', 'ses', 'income', 'education level',
        'working memory', 'cognitive load', 'task difficulty',
    }

    filtered = []
    for stim in all_stimuli:
        antecedent = stim.get('antecedent', '').lower().strip()

        # Skip if matches non-environmental pattern
        if any(pattern in antecedent for pattern in non_environmental):
            continue

        # Skip if categorized as 'other' with no environmental relevance
        categories = stim.get('categories', [])
        if categories == ['other']:
            # Check description for environmental content
            sources = stim.get('sources', [])
            has_env = False
            for src in sources:
                title = src.get('title', '').lower()
                if any(env_word in title for env_word in ['light', 'color', 'room', 'space', 'plant', 'natural', 'design', 'window', 'view', 'acoustic', 'sound', 'material', 'green', 'water']):
                    has_env = True
                    break
            if not has_env:
                continue

        filtered.append(stim)

    return filtered

# =============================================================================
# PART 1: Clustering Stimuli into Commonsense Categories
# =============================================================================

def extract_environmental_keywords(antecedent: str) -> List[str]:
    """Extract environmental keywords from stimulus antecedent."""
    keywords = []

    # Lighting keywords
    if any(w in antecedent.lower() for w in ['light', 'illumination', 'lamp', 'daylight', 'natural light', 'fluorescent', 'led']):
        keywords.append('lighting')

    # Color keywords
    if any(w in antecedent.lower() for w in ['color', 'blue', 'green', 'red', 'yellow', 'white', 'black', 'warm', 'cool', 'saturation', 'hue']):
        keywords.append('color')

    # Plant/biophilic keywords
    if any(w in antecedent.lower() for w in ['plant', 'green', 'vegetation', 'nature', 'biophil', 'living wall', 'moss', 'succulent', 'fern', 'flower', 'tree', 'grass', 'natural element']):
        keywords.append('plants_greenery')

    # Water keywords
    if any(w in antecedent.lower() for w in ['water', 'fountain', 'pond', 'aquatic', 'stream', 'river', 'waterfall', 'ocean', 'sea']):
        keywords.append('water')

    # Window/view keywords
    if any(w in antecedent.lower() for w in ['window', 'view', 'vista', 'outlook', 'scene', 'landscape', 'scenery', 'outdoor', 'external']):
        keywords.append('windows_views')

    # Room type keywords
    if any(w in antecedent.lower() for w in ['room', 'office', 'bedroom', 'living room', 'kitchen', 'classroom', 'hospital', 'waiting', 'lobby', 'corridor', 'hallway']):
        keywords.append('room_type')

    # Space/ceiling keywords
    if any(w in antecedent.lower() for w in ['ceiling', 'height', 'open', 'enclosed', 'ceiling height', 'space', 'area', 'volume', 'spatial', 'vertical']):
        keywords.append('space_ceiling')

    # Material keywords
    if any(w in antecedent.lower() for w in ['material', 'wood', 'concrete', 'glass', 'stone', 'brick', 'metal', 'fabric', 'plastic', 'natural material', 'synthetic']):
        keywords.append('materials')

    # Acoustic keywords
    if any(w in antecedent.lower() for w in ['acoustic', 'sound', 'noise', 'quietness', 'reverberation', 'echo', 'soundscape']):
        keywords.append('acoustics')

    # Furniture keywords
    if any(w in antecedent.lower() for w in ['furniture', 'seating', 'chair', 'table', 'desk', 'bed', 'arrangement']):
        keywords.append('furniture')

    # Art/decoration keywords
    if any(w in antecedent.lower() for w in ['art', 'decoration', 'image', 'picture', 'painting', 'sculpture', 'aesthetic', 'ornament']):
        keywords.append('art_decoration')

    # Complexity/clutter keywords
    if any(w in antecedent.lower() for w in ['complex', 'clutter', 'simple', 'minimal', 'orderly', 'chaos', 'organization', 'arrangement', 'dense']):
        keywords.append('complexity_clutter')

    # People/crowding keywords
    if any(w in antecedent.lower() for w in ['crowd', 'people', 'person', 'occupancy', 'solitude', 'presence', 'social', 'isolation', 'alone']):
        keywords.append('crowding_people')

    # Smell/olfactory keywords
    if any(w in antecedent.lower() for w in ['scent', 'smell', 'odor', 'aroma', 'fragrance', 'olfactory']):
        keywords.append('scent_smell')

    # Temperature/thermal keywords
    if any(w in antecedent.lower() for w in ['temperature', 'warm', 'cool', 'thermal', 'heat', 'cold', 'comfort']):
        keywords.append('thermal')

    return keywords

def assign_commonsense_category(antecedent: str, keywords: List[str]) -> str:
    """
    Map environmental keywords to ~25 commonsense categories based on semantic dominance.
    Implements hierarchical decision: what is the PRIMARY environmental feature being described?
    """
    antecedent_lower = antecedent.lower()

    # Priority-ordered rules (check dominant themes first)
    # Natural elements
    if 'plant' in antecedent_lower or 'green' in antecedent_lower or 'vegetation' in antecedent_lower:
        if 'wall' in antecedent_lower:
            return 'green_wall_vertical_garden'
        if 'ceiling' in antecedent_lower:
            return 'green_ceiling'
        if 'living' in antecedent_lower:
            return 'living_plant_or_potted'
        return 'room_with_plants_greenery'

    if 'water' in antecedent_lower or 'fountain' in antecedent_lower or 'aquatic' in antecedent_lower:
        return 'water_features'

    if 'natural' in antecedent_lower and ('material' in antecedent_lower or 'wood' in antecedent_lower):
        return 'natural_materials_wood'

    # Views and windows
    if 'window' in antecedent_lower or 'view' in antecedent_lower or 'landscape' in antecedent_lower:
        if 'nature' in antecedent_lower or 'outdoor' in antecedent_lower or 'garden' in antecedent_lower:
            return 'nature_view_from_window'
        if 'urban' in antecedent_lower:
            return 'urban_street_view'
        return 'windows_natural_light'

    # Daylight vs. artificial light
    if 'daylight' in antecedent_lower or 'natural light' in antecedent_lower:
        return 'daylight_natural_light'

    if 'light' in antecedent_lower or 'illumination' in antecedent_lower or 'lamp' in antecedent_lower or 'fluorescent' in antecedent_lower or 'led' in antecedent_lower:
        if 'color' in antecedent_lower or 'warm' in antecedent_lower or 'cool' in antecedent_lower:
            return 'colored_lighting_cct'
        if 'bright' in antecedent_lower or 'dim' in antecedent_lower or 'intensity' in antecedent_lower:
            return 'light_intensity_brightness'
        return 'artificial_lighting'

    # Color
    if 'color' in antecedent_lower and 'light' not in antecedent_lower:
        if 'blue' in antecedent_lower or 'green' in antecedent_lower or 'warm' in antecedent_lower:
            return 'wall_color_decoration'
        return 'color_environment'

    # Room/space types
    if 'office' in antecedent_lower:
        if 'open' in antecedent_lower or 'plan' in antecedent_lower:
            return 'open_plan_office'
        return 'office_private_workspace'

    if 'bedroom' in antecedent_lower:
        return 'residential_bedroom'

    if 'living' in antecedent_lower and 'room' in antecedent_lower:
        return 'residential_living_room'

    if 'classroom' in antecedent_lower:
        return 'classroom_learning_space'

    if 'hospital' in antecedent_lower or 'healthcare' in antecedent_lower or 'waiting' in antecedent_lower:
        if 'art' in antecedent_lower:
            return 'art_in_healthcare_environments'
        return 'hospital_healthcare_room'

    # Space characteristics
    if 'ceiling' in antecedent_lower and 'height' in antecedent_lower:
        if 'high' in antecedent_lower:
            return 'high_ceiling_space'
        return 'ceiling_spatial_proportion'

    if 'open' in antecedent_lower and ('space' in antecedent_lower or 'plaza' in antecedent_lower):
        return 'open_space_plaza'

    if 'enclosed' in antecedent_lower or 'private' in antecedent_lower or 'solitude' in antecedent_lower:
        return 'enclosed_private_space'

    # Complexity and organization
    if 'complex' in antecedent_lower or 'clutter' in antecedent_lower or 'organization' in antecedent_lower:
        return 'complexity_clutter_organization'

    if 'order' in antecedent_lower or 'symmetry' in antecedent_lower or 'formal' in antecedent_lower:
        return 'order_symmetry_formality'

    # Acoustic
    if 'acoustic' in antecedent_lower or 'sound' in antecedent_lower or 'noise' in antecedent_lower or 'quiet' in antecedent_lower:
        return 'acoustic_soundscape'

    # People and crowding
    if 'crowd' in antecedent_lower or 'occupancy' in antecedent_lower or 'people' in antecedent_lower:
        return 'crowding_occupancy'

    # Art and aesthetics
    if 'art' in antecedent_lower or 'aesthetic' in antecedent_lower or 'picture' in antecedent_lower:
        return 'art_decoration_aesthetics'

    # Materials
    if 'material' in antecedent_lower:
        return 'material_composition'

    # Garden/park/outdoor
    if 'garden' in antecedent_lower or 'park' in antecedent_lower or 'outdoor' in antecedent_lower:
        if 'urban' in antecedent_lower:
            return 'urban_green_space'
        return 'garden_park_nature'

    # Biophilic
    if 'biophil' in antecedent_lower:
        return 'biophilic_design_elements'

    # Aesthetic/visual appeal
    if 'aesthetic' in antecedent_lower or 'beauty' in antecedent_lower:
        return 'aesthetic_visual_appeal'

    # Thermal
    if 'temperature' in antecedent_lower or 'thermal' in antecedent_lower:
        return 'thermal_comfort'

    # Scent
    if 'scent' in antecedent_lower or 'smell' in antecedent_lower or 'aroma' in antecedent_lower:
        return 'scent_olfactory'

    # Default fallback
    if keywords:
        return keywords[0]

    return 'other_unclassified'

def cluster_stimuli_by_category(filtered_stimuli: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Cluster environmental stimuli into commonsense categories.
    Returns: {category_name: [stimulus1, stimulus2, ...]}
    """
    clusters = defaultdict(list)

    for stim in filtered_stimuli:
        antecedent = stim.get('antecedent', '')
        keywords = extract_environmental_keywords(antecedent)
        category = assign_commonsense_category(antecedent, keywords)
        clusters[category].append(stim)

    return dict(clusters)

# =============================================================================
# PART 2: Decision Tree Analysis
# =============================================================================

@dataclass
class DecisionTreeVariation:
    """A single variation tested in decision tree analysis."""
    dimension: str  # e.g., "wall_color", "plant_presence"
    variations: List[str]  # e.g., ["white", "blue", "grey"]
    verdict: str  # "essential", "incidental", "boundary_case", "untested"
    rationale: str = ""

@dataclass
class EquivalenceClass:
    """Result of decision tree analysis for one commonsense category."""
    category_name: str
    commonsense_label: str
    frequency: int
    representative_stimuli: List[str]
    variations_tested: List[Dict[str, Any]]
    essential_attributes: List[str]
    incidental_attributes: List[str]
    boundary_cases: List[str]
    equivalence_class_definition: str
    scientific_attributes_needed: List[str]
    new_attributes_discovered: List[str]

def generate_decision_tree_for_category(
    category_name: str,
    stimuli: List[Dict],
    existing_attributes: List[Dict]
) -> EquivalenceClass:
    """
    Apply David Kirsh's decision tree method to a commonsense category.

    Strategy: For each category, hypothesize essential vs. incidental dimensions,
    then map to scientific attributes.
    """

    # Extract representative stimulus descriptions
    antecedents = [s.get('antecedent', '') for s in stimuli]
    representative = list(set(antecedents))[:8]

    # Build category-specific decision trees based on semantic analysis
    category_lower = category_name.lower()

    # ========================================================================
    # DECISION TREE TEMPLATES FOR MAJOR CATEGORIES
    # ========================================================================

    if 'plant' in category_lower:
        variations = [
            {
                'dimension': 'plant_presence',
                'variations': ['living_plants_present', 'plants_absent', 'artificial_plants'],
                'verdict': 'essential',
                'rationale': 'Removing plants destroys the stimulus; artificial is boundary case'
            },
            {
                'dimension': 'plant_species',
                'variations': ['succulent', 'fern', 'pothos', 'monstera', 'moss'],
                'verdict': 'incidental',
                'rationale': 'Type of plant varies; "living green vegetation" is essential'
            },
            {
                'dimension': 'green_chromaticity',
                'variations': ['vibrant_green', 'muted_green', 'yellow_green'],
                'verdict': 'essential',
                'rationale': 'Green color is part of the stimulus identity'
            },
            {
                'dimension': 'plant_size',
                'variations': ['small_potted', 'large_floor', 'tabletop', 'wall_hanging'],
                'verdict': 'incidental',
                'rationale': 'Size and positioning vary; presence is essential'
            },
            {
                'dimension': 'pot_material',
                'variations': ['ceramic', 'plastic', 'terra_cotta', 'woven'],
                'verdict': 'incidental',
                'rationale': 'Vessel material is irrelevant to the stimulus identity'
            },
            {
                'dimension': 'lighting_for_plants',
                'variations': ['natural_light', 'artificial_light', 'mixed'],
                'verdict': 'incidental',
                'rationale': 'Lighting context varies; plant visibility is what matters'
            },
            {
                'dimension': 'room_context',
                'variations': ['office', 'bedroom', 'hospital', 'lobby', 'home'],
                'verdict': 'incidental',
                'rationale': 'Plants appear in various contexts'
            },
            {
                'dimension': 'biomorphic_form',
                'variations': ['natural_biomorphic', 'pruned_geometric'],
                'verdict': 'partially_essential',
                'rationale': 'Natural form is preferred; extreme geometric pruning may destroy stimulus'
            },
        ]
        essential = ['plant_presence', 'green_chromaticity', 'biomorphic_form']
        incidental = ['plant_species', 'plant_size', 'pot_material', 'lighting_for_plants', 'room_context']
        boundary = ['artificial_plants', 'nature_photograph', 'green_fabric']
        definition = 'Any indoor or semi-outdoor space containing visible living plants with green foliage and recognizable biomorphic form'
        scientific_attrs = ['ATTR-B1', 'ATTR-C3', 'ATTR-F1', 'ATTR-S4']
        new_attrs = ['vegetation_segmentation_ratio', 'plant_health_vigor_estimation']

    elif 'water' in category_lower:
        variations = [
            {
                'dimension': 'water_presence',
                'variations': ['water_present', 'water_absent', 'water_photo'],
                'verdict': 'essential',
                'rationale': 'Water feature is the core stimulus'
            },
            {
                'dimension': 'water_type',
                'variations': ['flowing_fountain', 'still_pond', 'stream', 'waterfall'],
                'verdict': 'incidental',
                'rationale': 'Type of water varies; presence is essential'
            },
            {
                'dimension': 'water_motion',
                'variations': ['static', 'slow_flow', 'cascading'],
                'verdict': 'boundary_case',
                'rationale': 'Motion affects perception; still water is different stimulus'
            },
            {
                'dimension': 'water_visibility',
                'variations': ['clearly_visible', 'partially_obscured', 'hidden_sound_only'],
                'verdict': 'essential',
                'rationale': 'Visual presence is central to most water stimuli'
            },
            {
                'dimension': 'setting',
                'variations': ['indoor', 'outdoor', 'enclosed_garden'],
                'verdict': 'incidental',
                'rationale': 'Water appears in various contexts'
            },
        ]
        essential = ['water_presence', 'water_visibility']
        incidental = ['water_type', 'setting']
        boundary = ['water_sound_only', 'water_photograph', 'mist_fountain']
        definition = 'A visible water feature (flowing, still, or cascading) as a prominent environmental element'
        scientific_attrs = ['ATTR-B2', 'ATTR-F1']
        new_attrs = ['water_surface_motion_estimation', 'water_clarity_estimation']

    elif 'view' in category_lower or 'window' in category_lower or 'landscape' in category_lower:
        variations = [
            {
                'dimension': 'window_presence',
                'variations': ['window_present', 'window_absent'],
                'verdict': 'essential',
                'rationale': 'Window/view aperture is core to stimulus'
            },
            {
                'dimension': 'view_content',
                'variations': ['nature_landscape', 'urban_street', 'other_building', 'greenery'],
                'verdict': 'essential',
                'rationale': 'View content defines the stimulus type'
            },
            {
                'dimension': 'view_distance',
                'variations': ['distant_vista', 'close_garden', 'near_wall'],
                'verdict': 'partially_essential',
                'rationale': 'Distance affects psychological impact'
            },
            {
                'dimension': 'window_size',
                'variations': ['large_picture', 'small_aperture', 'glass_wall'],
                'verdict': 'incidental',
                'rationale': 'Size varies; presence of external view is essential'
            },
            {
                'dimension': 'window_framing',
                'variations': ['wooden_frame', 'metal_frame', 'no_frame'],
                'verdict': 'incidental',
                'rationale': 'Frame material is irrelevant'
            },
        ]
        essential = ['window_presence', 'view_content']
        incidental = ['window_size', 'window_framing']
        boundary = ['photograph_on_wall', 'video_display', 'small_porthole']
        definition = 'A window or transparent aperture providing visual access to an external view (natural landscape or urban scene)'
        scientific_attrs = ['ATTR-S1', 'ATTR-C2', 'ATTR-F1']
        new_attrs = ['scene_depth_perspective', 'sky_proportion', 'horizon_line_presence']

    elif 'light' in category_lower or 'illuminat' in category_lower or 'brightness' in category_lower:
        variations = [
            {
                'dimension': 'illumination_level',
                'variations': ['bright', 'moderate', 'dim', 'dark'],
                'verdict': 'essential',
                'rationale': 'Brightness level defines the stimulus'
            },
            {
                'dimension': 'light_source_type',
                'variations': ['natural_daylight', 'fluorescent', 'led', 'incandescent'],
                'verdict': 'boundary_case',
                'rationale': 'Source type affects color/quality; illuminance level more essential'
            },
            {
                'dimension': 'cct_color_temperature',
                'variations': ['warm_2700k', 'neutral_4000k', 'cool_6500k'],
                'verdict': 'partially_essential',
                'rationale': 'Color temperature affects mood; some levels not interchangeable'
            },
            {
                'dimension': 'uniformity_distribution',
                'variations': ['uniform', 'pools_of_light', 'directional'],
                'verdict': 'incidental',
                'rationale': 'Distribution varies; illumination level is essential'
            },
            {
                'dimension': 'light_direction',
                'variations': ['overhead', 'side', 'diffuse'],
                'verdict': 'incidental',
                'rationale': 'Direction varies across contexts'
            },
        ]
        essential = ['illumination_level']
        incidental = ['light_direction', 'uniformity_distribution']
        boundary = ['light_source_type', 'cct_color_temperature']
        definition = 'An environment characterized by a specified illumination level (measured in lux) and light distribution'
        scientific_attrs = ['ATTR-C1', 'ATTR-F4']
        new_attrs = ['illuminance_distribution_uniformity', 'flicker_detection']

    elif 'ceiling' in category_lower and 'height' in category_lower:
        variations = [
            {
                'dimension': 'ceiling_height',
                'variations': ['high_3m_plus', 'standard_2.4m', 'low_under_2m'],
                'verdict': 'essential',
                'rationale': 'Height defines stimulus class'
            },
            {
                'dimension': 'ceiling_color',
                'variations': ['white', 'colored', 'dark', 'textured'],
                'verdict': 'incidental',
                'rationale': 'Color varies; height is essential'
            },
            {
                'dimension': 'ceiling_material',
                'variations': ['plaster', 'tiles', 'wood', 'exposed'],
                'verdict': 'incidental',
                'rationale': 'Material varies; height and visual openness are essential'
            },
            {
                'dimension': 'vertical_volume_perception',
                'variations': ['spacious', 'compressed', 'monumental'],
                'verdict': 'essential',
                'rationale': 'Spatial perception depends on floor-to-ceiling proportion'
            },
        ]
        essential = ['ceiling_height', 'vertical_volume_perception']
        incidental = ['ceiling_color', 'ceiling_material']
        boundary = ['extreme_height_cathedral', 'artificial_height_illusion']
        definition = 'An interior space with a specified ceiling height and resulting vertical proportion (floor-to-ceiling ratio)'
        scientific_attrs = ['ATTR-S2', 'ATTR-S1']
        new_attrs = ['vertical_proportion_ratio', 'ceiling_visibility_in_frame']

    elif 'open' in category_lower and 'office' in category_lower or 'open_plan' in category_lower:
        variations = [
            {
                'dimension': 'enclosure_level',
                'variations': ['fully_open_no_walls', 'partial_partitions', 'mixed_open_closed'],
                'verdict': 'essential',
                'rationale': 'Openness is the defining characteristic'
            },
            {
                'dimension': 'partition_type',
                'variations': ['low_divider', 'high_panel', 'transparent_glass'],
                'verdict': 'incidental',
                'rationale': 'Type varies; presence of open space is essential'
            },
            {
                'dimension': 'view_to_colleagues',
                'variations': ['high_visibility', 'partial_privacy', 'blocked'],
                'verdict': 'essential',
                'rationale': 'Social visibility is part of open-plan identity'
            },
            {
                'dimension': 'acoustic_isolation',
                'variations': ['low_isolation', 'moderate_absorption', 'high_isolation'],
                'verdict': 'partially_essential',
                'rationale': 'True open-plan has low acoustic isolation'
            },
            {
                'dimension': 'furniture_arrangement',
                'variations': ['clustered', 'distributed', 'organized_rows'],
                'verdict': 'incidental',
                'rationale': 'Arrangement varies; spatial openness is essential'
            },
        ]
        essential = ['enclosure_level', 'view_to_colleagues']
        incidental = ['partition_type', 'furniture_arrangement']
        boundary = ['high_partition_pseudo_open', 'enclosed_with_windows']
        definition = 'A workplace with minimal enclosure, high visual transparency, low acoustic isolation, and shared open floor space'
        scientific_attrs = ['ATTR-S3', 'ATTR-S4', 'ATTR-A2']
        new_attrs = ['visual_privacy_estimation', 'acoustic_privacy_estimation']

    elif 'enclosed' in category_lower or 'private' in category_lower:
        variations = [
            {
                'dimension': 'enclosure_completeness',
                'variations': ['fully_enclosed', 'mostly_enclosed', 'semi_open'],
                'verdict': 'essential',
                'rationale': 'Enclosure defines the stimulus'
            },
            {
                'dimension': 'privacy_level',
                'variations': ['complete_privacy', 'visual_privacy_only', 'social_privacy'],
                'verdict': 'essential',
                'rationale': 'Privacy experience depends on enclosure type'
            },
            {
                'dimension': 'wall_material',
                'variations': ['solid_concrete', 'drywall', 'brick', 'glass'],
                'verdict': 'incidental',
                'rationale': 'Material varies; enclosure is essential'
            },
            {
                'dimension': 'size_of_space',
                'variations': ['small_compact', 'medium', 'large_spacious'],
                'verdict': 'incidental',
                'rationale': 'Size varies; enclosure is essential'
            },
        ]
        essential = ['enclosure_completeness', 'privacy_level']
        incidental = ['wall_material', 'size_of_space']
        boundary = ['transparent_walls', 'translucent_enclosure']
        definition = 'A fully or substantially enclosed space providing visual and/or acoustic privacy'
        scientific_attrs = ['ATTR-S3', 'ATTR-S4']
        new_attrs = ['visual_privacy_metric', 'acoustic_isolation_estimation']

    elif 'hospital' in category_lower or 'healthcare' in category_lower:
        variations = [
            {
                'dimension': 'clinical_elements',
                'variations': ['minimal_clinical', 'typical_hospital', 'heavy_medical'],
                'verdict': 'essential',
                'rationale': 'Clinical appearance is central to stimulus'
            },
            {
                'dimension': 'restorative_elements',
                'variations': ['plants_art_present', 'minimal_art', 'no_art'],
                'verdict': 'boundary_case',
                'rationale': 'Art/plants modify but don\'t destroy "hospital room" identity'
            },
            {
                'dimension': 'view_to_nature',
                'variations': ['garden_view', 'outdoor_view', 'interior_view', 'no_view'],
                'verdict': 'partially_essential',
                'rationale': 'Some hospital stimuli require natural views'
            },
            {
                'dimension': 'medical_equipment_visibility',
                'variations': ['visible_equipment', 'concealed_equipment', 'no_equipment'],
                'verdict': 'essential',
                'rationale': 'Medical appearance depends on equipment prominence'
            },
        ]
        essential = ['clinical_elements', 'medical_equipment_visibility']
        incidental = []
        boundary = ['art_in_healthcare', 'biophilic_hospital']
        definition = 'An interior space with visible clinical/medical characteristics including equipment, specialized furniture, and institutional appearance'
        scientific_attrs = ['ATTR-M1', 'ATTR-B3']
        new_attrs = ['medical_equipment_density', 'institutional_appearance_score']

    elif 'color' in category_lower or 'colored' in category_lower or 'wall' in category_lower:
        variations = [
            {
                'dimension': 'hue',
                'variations': ['red', 'blue', 'green', 'yellow', 'neutral'],
                'verdict': 'essential',
                'rationale': 'Color hue defines the stimulus'
            },
            {
                'dimension': 'saturation',
                'variations': ['vibrant_saturated', 'muted', 'desaturated'],
                'verdict': 'partially_essential',
                'rationale': 'Saturation affects mood; extreme desaturation changes stimulus'
            },
            {
                'dimension': 'lightness_value',
                'variations': ['dark', 'medium', 'light'],
                'verdict': 'partially_essential',
                'rationale': 'Lightness interacts with hue in perception'
            },
            {
                'dimension': 'coverage_extent',
                'variations': ['accent_wall', 'multiple_walls', 'ceiling', 'trim_only'],
                'verdict': 'incidental',
                'rationale': 'Coverage varies; color presence is essential'
            },
        ]
        essential = ['hue', 'saturation', 'lightness_value']
        incidental = ['coverage_extent']
        boundary = ['accent_color', 'color_pattern']
        definition = 'An interior space with a dominant chromatic appearance defined by hue, saturation, and value'
        scientific_attrs = ['ATTR-C2', 'ATTR-C3']
        new_attrs = ['chromatic_dominance_percentage', 'color_harmony_score']

    elif 'garden' in category_lower or 'park' in category_lower or 'nature' in category_lower:
        variations = [
            {
                'dimension': 'vegetation_density',
                'variations': ['dense_vegetation', 'moderate', 'sparse_open'],
                'verdict': 'essential',
                'rationale': 'Vegetation density defines garden vs. open space'
            },
            {
                'dimension': 'cultivated_vs_wild',
                'variations': ['formal_garden', 'natural_style', 'untended_wild'],
                'verdict': 'incidental',
                'rationale': 'Both formal and natural gardens are stimuli'
            },
            {
                'dimension': 'water_feature',
                'variations': ['water_present', 'water_absent'],
                'verdict': 'incidental',
                'rationale': 'Gardens may or may not have water'
            },
            {
                'dimension': 'openness_to_sky',
                'variations': ['open_canopy', 'partial_overhead', 'dense_canopy'],
                'verdict': 'incidental',
                'rationale': 'Varies across garden types'
            },
            {
                'dimension': 'accessibility',
                'variations': ['public_access', 'private_enclosed', 'restricted'],
                'verdict': 'incidental',
                'rationale': 'Varies; vegetation is essential'
            },
        ]
        essential = ['vegetation_density']
        incidental = ['cultivated_vs_wild', 'water_feature', 'openness_to_sky', 'accessibility']
        boundary = ['park_like_open_space', 'highly_manicured_landscape']
        definition = 'An outdoor or semi-outdoor space with substantial living vegetation (trees, shrubs, groundcover) in varying degrees of cultivation'
        scientific_attrs = ['ATTR-B1', 'ATTR-F1', 'ATTR-S1']
        new_attrs = ['vegetation_coverage_percentage', 'canopy_density_estimation', 'plant_species_diversity_estimation']

    elif 'material' in category_lower:
        variations = [
            {
                'dimension': 'primary_material',
                'variations': ['wood', 'concrete', 'glass', 'metal', 'stone', 'brick'],
                'verdict': 'essential',
                'rationale': 'Material type defines surface aesthetic'
            },
            {
                'dimension': 'material_finish',
                'variations': ['natural_raw', 'polished_refined', 'weathered', 'painted'],
                'verdict': 'incidental',
                'rationale': 'Finish varies; material type is essential'
            },
            {
                'dimension': 'texture',
                'variations': ['smooth', 'rough', 'tactile', 'pattern'],
                'verdict': 'incidental',
                'rationale': 'Texture varies; material is essential'
            },
            {
                'dimension': 'coverage_area',
                'variations': ['accent_surfaces', 'major_surfaces', 'entire_room'],
                'verdict': 'incidental',
                'rationale': 'Coverage varies; material presence is essential'
            },
        ]
        essential = ['primary_material']
        incidental = ['material_finish', 'texture', 'coverage_area']
        boundary = ['material_imitation', 'mixed_materials']
        definition = 'An interior surface or structural element made of a specific material (wood, concrete, glass, metal, stone) with visible material character'
        scientific_attrs = ['ATTR-M1', 'ATTR-F4']
        new_attrs = ['material_classification_algorithm', 'surface_texture_statistics', 'material_authenticity_score']

    elif 'artwork' in category_lower or 'art' in category_lower or 'decoration' in category_lower:
        variations = [
            {
                'dimension': 'art_presence',
                'variations': ['art_present', 'art_absent'],
                'verdict': 'essential',
                'rationale': 'Presence of artwork is the stimulus'
            },
            {
                'dimension': 'art_type',
                'variations': ['painting', 'photograph', 'sculpture', 'installation', 'abstract'],
                'verdict': 'incidental',
                'rationale': 'Type varies; presence is essential'
            },
            {
                'dimension': 'visual_complexity',
                'variations': ['simple_abstract', 'representational', 'highly_detailed'],
                'verdict': 'incidental',
                'rationale': 'Complexity varies'
            },
            {
                'dimension': 'size_prominence',
                'variations': ['small_subtle', 'medium_notable', 'large_focal'],
                'verdict': 'incidental',
                'rationale': 'Size varies; presence is essential'
            },
            {
                'dimension': 'emotional_content',
                'variations': ['positive_mood', 'neutral', 'negative_mood'],
                'verdict': 'boundary_case',
                'rationale': 'Content may modify stimulus but presence is primary'
            },
        ]
        essential = ['art_presence']
        incidental = ['art_type', 'visual_complexity', 'size_prominence']
        boundary = ['emotional_content']
        definition = 'An interior space containing at least one visible artistic or decorative element (painting, photograph, sculpture, or installation)'
        scientific_attrs = ['ATTR-F1', 'ATTR-P1', 'ATTR-P2']
        new_attrs = ['artwork_salience_estimation', 'visual_complexity_score', 'semantic_content_analysis']

    elif 'classroom' in category_lower or 'learning' in category_lower:
        variations = [
            {
                'dimension': 'functional_layout',
                'variations': ['lecture_rows', 'collaborative_clusters', 'open_flexible'],
                'verdict': 'essential',
                'rationale': 'Layout affects pedagogical identity'
            },
            {
                'dimension': 'board_display',
                'variations': ['blackboard_present', 'whiteboard_present', 'digital_screen', 'none'],
                'verdict': 'essential',
                'rationale': 'Teaching surface presence defines classroom'
            },
            {
                'dimension': 'classroom_size',
                'variations': ['small_seminar', 'medium_class', 'large_lecture'],
                'verdict': 'incidental',
                'rationale': 'Size varies; function is essential'
            },
            {
                'dimension': 'lighting_appropriateness',
                'variations': ['appropriate_for_reading', 'dim', 'very_bright'],
                'verdict': 'incidental',
                'rationale': 'Varies; space function is essential'
            },
        ]
        essential = ['functional_layout', 'board_display']
        incidental = ['classroom_size', 'lighting_appropriateness']
        boundary = ['flexible_learning_space', 'traditional_classroom']
        definition = 'An interior space designed for education with seating for multiple learners and display/teaching surface (board, screen, or equivalent)'
        scientific_attrs = ['ATTR-S3', 'ATTR-S4', 'ATTR-A2']
        new_attrs = ['classroom_functionality_score', 'sightline_analysis']

    else:
        # Generic template for uncategorized stimuli
        variations = [
            {
                'dimension': 'primary_feature',
                'variations': ['feature_present', 'feature_absent'],
                'verdict': 'essential',
                'rationale': 'Primary characteristic is essential'
            },
            {
                'dimension': 'context',
                'variations': ['varied_contexts'],
                'verdict': 'incidental',
                'rationale': 'Stimulus appears in various contexts'
            },
        ]
        essential = ['primary_feature']
        incidental = ['context']
        boundary = []
        definition = 'Generic category requiring manual review'
        scientific_attrs = []
        new_attrs = []

    # ========================================================================
    # Build equivalence class from decision tree
    # ========================================================================

    new_discovered = []
    for attr in new_attrs:
        if not any(attr in e.get('name', '').lower() for e in existing_attributes):
            new_discovered.append(attr)

    return EquivalenceClass(
        category_name=category_name,
        commonsense_label=' '.join(category_name.split('_')).title(),
        frequency=len(stimuli),
        representative_stimuli=representative,
        variations_tested=[vars(v) for v in [
            DecisionTreeVariation(
                dimension=d['dimension'],
                variations=d['variations'],
                verdict=d['verdict'],
                rationale=d['rationale']
            ) for d in variations
        ]],
        essential_attributes=essential,
        incidental_attributes=incidental,
        boundary_cases=boundary,
        equivalence_class_definition=definition,
        scientific_attributes_needed=scientific_attrs,
        new_attributes_discovered=new_discovered
    )

# =============================================================================
# PART 3: Discover NEW Scientific Attributes
# =============================================================================

NEW_ATTRIBUTES = [
    {
        'id': 'NEW-01',
        'name': 'Vegetation Segmentation Ratio',
        'description': 'Percentage of image pixels classified as vegetation/plant material',
        'discovered_from_categories': ['room_with_plants_greenery', 'garden_park_nature', 'green_wall_vertical_garden'],
        'why_needed': 'Quantifies plant coverage; essential for distinguishing high-vegetation from low-vegetation scenes',
        'vision_algorithm': {
            'name': 'Semantic Segmentation for Vegetation',
            'method': 'DeepLabV3+ with plant-specific training',
            'libraries': ['torch', 'torchvision', 'opencv-python'],
            'tier': 2,
            'key_functions': [
                'torchvision.models.segmentation.deeplabv3_resnet50(pretrained=True)',
                'torch.nn.functional.interpolate() for resizing predictions',
                'cv2.findContours() for post-processing plant regions'
            ],
            'input': 'RGB image (any resolution)',
            'output': 'float [0, 1] representing proportion of vegetation pixels',
            'implementation_outline': '''
            1. Load pretrained DeepLabV3+ model
            2. Preprocess image (ImageNet normalization)
            3. Forward pass to get segmentation map
            4. Extract vegetation class (label ID for plants/leaves)
            5. Calculate ratio = vegetation_pixels / total_pixels
            6. Optional: morphological closing to remove small noise
            ''',
            'known_limitations': [
                'May confuse green-painted walls with vegetation',
                'Struggles with heavily shadowed plants',
                'Artificial plants sometimes misclassified',
                'Dependent on training dataset bias'
            ]
        },
        'theoretical_warrant': 'Vegetation presence is essential to biophilic stimulus identity (Attention Restoration Theory, Biophilia Hypothesis)',
        'key_references': [
            'Kaplan & Kaplan (1989) The Experience of Nature: A Psychological Perspective',
            'Hartig et al. (2014) Nature and Health, Annual Review of Public Health',
            'Ulrich (1983) View through a window may influence recovery from surgery, Science'
        ]
    },
    {
        'id': 'NEW-02',
        'name': 'Scene Depth and Perspective Estimation',
        'description': 'Perceived depth cues and spatial perspective in scene (vanishing point distance, horizon position)',
        'discovered_from_categories': ['nature_view_from_window', 'urban_street_view', 'open_space_plaza'],
        'why_needed': 'Views with depth are psychologically different from flat scenes; essential for measuring spatial openness and legibility',
        'vision_algorithm': {
            'name': 'Monocular Depth Estimation + Horizon Detection',
            'method': 'MiDaS depth estimation + Hough line transform for horizon',
            'libraries': ['torch', 'opencv-python', 'numpy'],
            'tier': 2,
            'key_functions': [
                'torch.hub.load(\'intel-isl/MiDaS\', \'MiDaS_small\')',
                'cv2.HoughLinesP() for vanishing point detection',
                'cv2.HoughLines() for horizon line detection'
            ],
            'input': 'RGB image (any resolution)',
            'output': 'dict with: depth_map (array), mean_depth (float), horizon_position (% from top), vanishing_distance (estimated pixels)',
            'implementation_outline': '''
            1. Load MiDaS depth model (small variant for speed)
            2. Preprocess image (resize to 384x384)
            3. Forward pass to get relative depth map
            4. Normalize depth to [0, 1] range
            5. Detect horizon line using edge detection + Hough transform
            6. Find vanishing points from converging lines
            7. Estimate depth gradient (change in depth across vertical axis)
            8. Classify as "flat" (low gradient) or "deep" (high gradient)
            ''',
            'known_limitations': [
                'Monocular depth is relative, not absolute metric',
                'Difficult with highly textured foregrounds',
                'Indoor environments sometimes problematic',
                'Requires sufficient line structure for vanishing point detection'
            ]
        },
        'theoretical_warrant': 'Spatial depth perception affects sense of enclosure, prospect, and psychological comfort (Prospect-Refuge Theory, Kaplan)',
        'key_references': [
            'Appleton (1975) The Experience of Landscape, John Wiley & Sons',
            'Rankin et al. (2016) Depth cues in architecture, Journal of Environmental Psychology'
        ]
    },
    {
        'id': 'NEW-03',
        'name': 'Sky Proportion and Horizon Ratio',
        'description': 'Proportion of image occupied by sky; position of horizon line in frame',
        'discovered_from_categories': ['garden_park_nature', 'urban_street_view', 'nature_view_from_window'],
        'why_needed': 'Sky presence and horizon position affect outdoor scene assessment; related to openness perception',
        'vision_algorithm': {
            'name': 'Sky Segmentation and Horizon Detection',
            'method': 'Semantic segmentation for sky + Hough line detection',
            'libraries': ['opencv-python', 'scikit-image', 'torch'],
            'tier': 2,
            'key_functions': [
                'torchvision.models.segmentation.deeplabv3_resnet50()',
                'cv2.HoughLines() for horizon detection',
                'cv2.inRange() for color-based sky detection (blue chromaticity)'
            ],
            'input': 'RGB image',
            'output': 'dict with: sky_ratio (float [0, 1]), horizon_position (% from top), sky_hue_distribution (array)',
            'implementation_outline': '''
            1. Semantic segmentation to identify sky class
            2. Alternative: HSV color space filtering for blue sky (H: 180-260, S: 30-100, V: 50-100)
            3. Detect horizon line using Hough transform on edge map
            4. Calculate sky_ratio = sky_pixels / total_pixels
            5. Normalize horizon position to 0-1 (0=top, 1=bottom)
            6. Histogram of sky hue values
            ''',
            'known_limitations': [
                'Cloudy/overcast skies harder to segment',
                'Indoor window-view scenes may not have true sky',
                'Reflected sky in water confuses classifier',
                'Extreme low-angle shots may have no visible horizon'
            ]
        },
        'theoretical_warrant': 'Sky and horizon are key environmental cues affecting sense of scale, openness, and restoration (Kaplan & Kaplan)',
        'key_references': [
            'Kaplan (1988) Perception and landscape: conceptions and misconceptions',
            'Voulodimos & Doulos (2020) Quantifying the influence of natural landscape elements on visual quality, Urban Forestry & Urban Greening'
        ]
    },
    {
        'id': 'NEW-04',
        'name': 'Visual Complexity and Information Density',
        'description': 'Amount of visual detail, edge density, contour richness; measures scene complexity',
        'discovered_from_categories': ['complexity_clutter_organization', 'garden_park_nature', 'room_with_plants_greenery'],
        'why_needed': 'Essential for distinguishing minimal from complex scenes; relates to cognitive load and restoration',
        'vision_algorithm': {
            'name': 'Edge Density and Spectral Complexity',
            'method': 'Canny edge detection + power spectrum analysis',
            'libraries': ['opencv-python', 'numpy', 'scipy'],
            'tier': 1,
            'key_functions': [
                'cv2.Canny() for edge detection',
                'cv2.countNonZero() for edge pixel count',
                'numpy.fft.fft2() for frequency domain analysis'
            ],
            'input': 'RGB or grayscale image',
            'output': 'dict with: edge_density (float [0, 1]), spectral_entropy (float [0, 8]), complexity_score (float [0, 1])',
            'implementation_outline': '''
            1. Convert to grayscale
            2. Apply Gaussian blur (sigma=1.0) to reduce noise
            3. Canny edge detection (auto thresholds or 100, 200)
            4. Calculate edge_density = edge_pixels / total_pixels
            5. Compute 2D FFT of grayscale image
            6. Calculate power spectrum (magnitude squared)
            7. Normalize and compute Shannon entropy of power distribution
            8. complexity_score = (edge_density + normalized_entropy) / 2
            ''',
            'known_limitations': [
                'Sensitive to camera noise (requires preprocessing)',
                'Images with sharp shadows create spurious edges',
                'JPG compression artifacts affect edge detection',
                'Scene-dependent: same complexity value can represent different visual experiences'
            ]
        },
        'theoretical_warrant': 'Visual complexity affects cognitive load, restoration, and aesthetic preference (Berlyne\'s optimal complexity hypothesis)',
        'key_references': [
            'Berlyne (1974) Studies in the New Experimental Aesthetics, Hemisphere Publishing',
            'Hagerhall et al. (2004) Investigations of human perceptions, preferences and physiological responses to natural scenes, Journal of Environmental Psychology'
        ]
    },
    {
        'id': 'NEW-05',
        'name': 'Regularity and Repetition Index',
        'description': 'Degree of geometric order, symmetry, and pattern repetition (institutional vs. organic)',
        'discovered_from_categories': ['classroom_learning_space', 'hospital_healthcare_room', 'open_plan_office'],
        'why_needed': 'Distinguishes institutional (high regularity) from domestic/organic (low regularity) environments',
        'vision_algorithm': {
            'name': 'Symmetry Detection and Autocorrelation Analysis',
            'method': 'Image autocorrelation + symmetry score computation',
            'libraries': ['scipy', 'opencv-python', 'numpy'],
            'tier': 2,
            'key_functions': [
                'scipy.ndimage.correlate() for autocorrelation',
                'cv2.flip() for symmetry checks',
                'numpy.correlate() for 1D pattern detection'
            ],
            'input': 'RGB image (preferably normalized)',
            'output': 'dict with: bilateral_symmetry_score (float [0, 1]), autocorrelation_strength (float [0, 1]), regularity_index (float [0, 1])',
            'implementation_outline': '''
            1. Convert to grayscale
            2. Compute horizontal mirror image
            3. Correlate original with mirror: bilateral_symmetry = correlation_coefficient
            4. Compute 2D autocorrelation of grayscale image
            5. Analyze autocorrelation peaks to detect periodic patterns
            6. Regularity_index = symmetry_score * autocorrelation_strength
            7. Optional: Apply to sub-regions to capture local patterns
            ''',
            'known_limitations': [
                'Bilateral symmetry detection sensitive to camera misalignment',
                'Works better for near-symmetric scenes',
                'Fails for rotational or radial symmetry',
                'Requires sufficient image resolution for pattern detection'
            ]
        },
        'theoretical_warrant': 'Regularity is a marker of institutional environments and affects psychological comfort (Biophilic vs. Institutional design literature)',
        'key_references': [
            'Browning et al. (2014) Biophilic Design Framework, Journal of Biophilic Design',
            'Ulrich (1984) View through a window may influence recovery from surgery'
        ]
    },
    {
        'id': 'NEW-06',
        'name': 'Figure-Ground Clarity and Foreground-Background Segmentation',
        'description': 'Visual distinctness of foreground elements from background; spatial layering clarity',
        'discovered_from_categories': ['room_with_plants_greenery', 'art_decoration_aesthetics', 'urban_street_view'],
        'why_needed': 'Essential for distinguishing visually coherent from ambiguous scenes; affects visual preference',
        'vision_algorithm': {
            'name': 'Depth-Based Figure-Ground Separation + Contrast Analysis',
            'method': 'MiDaS depth + foreground/background contrast',
            'libraries': ['torch', 'opencv-python', 'numpy'],
            'tier': 2,
            'key_functions': [
                'MiDaS for depth estimation',
                'cv2.grabCut() or cv2.watershed() for figure extraction',
                'SIFT or BRIEF for salient region detection'
            ],
            'input': 'RGB image',
            'output': 'dict with: figure_background_contrast (float [0, 1]), foreground_coherence (float [0, 1]), clarity_score (float [0, 1])',
            'implementation_outline': '''
            1. Estimate depth using MiDaS
            2. Segment foreground (close) from background (far) using depth threshold
            3. Compute average color contrast between foreground and background
            4. Extract foreground region(s) using grabCut algorithm
            5. Measure coherence = 1 - (foreground_variance / background_variance)
            6. Clarity_score = mean([contrast, coherence])
            ''',
            'known_limitations': [
                'Depth estimation errors affect segmentation',
                'Difficult with layered foregrounds',
                'Low-contrast scenes problematic',
                'GrabCut can be unstable without good initialization'
            ]
        },
        'theoretical_warrant': 'Figure-ground separation is fundamental to visual perception and aesthetic appreciation (Gestalt psychology)',
        'key_references': [
            'Palmer (1999) Vision Science: Photons to Phenomenology, MIT Press',
            'Pomerantz & Kubovy (1986) The organization of information in memory'
        ]
    },
    {
        'id': 'NEW-07',
        'name': 'Material Diversity Index',
        'description': 'Number of distinct material types visible in scene; material richness',
        'discovered_from_categories': ['natural_materials_wood', 'material_composition', 'biophilic_design_elements'],
        'why_needed': 'Material variety affects aesthetic appreciation and biophilic design assessment',
        'vision_algorithm': {
            'name': 'Material Classification and Clustering',
            'method': 'Texture descriptor clustering (LBP, SIFT) + pre-trained material classifier',
            'libraries': ['opencv-python', 'scikit-image', 'torch', 'torchvision'],
            'tier': 2,
            'key_functions': [
                'skimage.feature.local_binary_pattern() for texture',
                'torchvision.models for material classification (pretrained ResNet)',
                'sklearn.cluster.KMeans() for grouping similar materials'
            ],
            'input': 'RGB image',
            'output': 'dict with: material_types_detected (list), material_count (int), diversity_index (float [0, 1])',
            'implementation_outline': '''
            1. Divide image into grid cells (8x8 or 16x16)
            2. For each cell, compute texture descriptor (LBP histogram)
            3. Cluster cells using KMeans (k=number of material types, estimate k=3-8)
            4. Extract representative patch from each cluster
            5. Classify each cluster using pretrained ResNet (fine-tuned on materials)
            6. Diversity_index = number_of_unique_materials / max_possible_materials
            7. Optional: Use pre-trained material segmentation model (e.g., MIT-Indoor dataset)
            ''',
            'known_limitations': [
                'Requires pre-trained material classifier (limited availability)',
                'Colors/reflections can confuse material classification',
                'Lighting changes affect texture features',
                'Small material patches easily missed'
            ]
        },
        'theoretical_warrant': 'Material diversity contributes to biophilic design and visual interest (Biophilic Design principles)',
        'key_references': [
            'Kellert & Calabrese (2015) The Practice of Biophilic Design',
            'Browning et al. (2014) Nature Inside: connecting to the natural world in building and interior environments'
        ]
    },
    {
        'id': 'NEW-08',
        'name': 'Illumination Distribution Uniformity',
        'description': 'Spatial uniformity of lighting across scene; presence of dark/bright zones',
        'discovered_from_categories': ['light_intensity_brightness', 'daylight_natural_light', 'artificial_lighting'],
        'why_needed': 'Uniform vs. dramatic lighting creates different spatial impressions; essential for measuring light quality',
        'vision_algorithm': {
            'name': 'Luminance Histogram and Spatial Variance',
            'method': 'Convert to LAB color space + compute spatial variance of L channel',
            'libraries': ['opencv-python', 'numpy', 'scipy'],
            'tier': 1,
            'key_functions': [
                'cv2.cvtColor(..., cv2.COLOR_BGR2LAB) for perceptual lightness',
                'scipy.ndimage.generic_filter() for local variance',
                'numpy.std() for global statistics'
            ],
            'input': 'RGB image',
            'output': 'dict with: mean_illuminance_lux_estimate (float), uniformity_ratio (float [0, 1]), bright_dark_zones (dict)',
            'implementation_outline': '''
            1. Convert RGB to LAB color space
            2. Extract L channel (perceptual lightness 0-100)
            3. Estimate illuminance from L (assume linear relationship to lux)
            4. Compute local standard deviation (moving window 32x32)
            5. Uniformity_ratio = 1 - (mean_local_std / global_std)
            6. Identify bright zones (L > 75) and dark zones (L < 25)
            7. bright_dark_ratio = bright_pixels / dark_pixels
            ''',
            'known_limitations': [
                'Absolute lux estimation not possible from RGB (requires calibration)',
                'Relative uniformity more reliable than absolute values',
                'Specular highlights create artificial bright zones',
                'Shadows and reflections affect measurements'
            ]
        },
        'theoretical_warrant': 'Lighting uniformity affects visual comfort and environmental quality (Lighting design standards, CIE)',
        'key_references': [
            'CIE (2019) CIE 195:2019 Guidance on minimizing light pollution',
            'Fotios et al. (2015) Evaluating the chromatic and luminance content of road lighting installations'
        ]
    },
    {
        'id': 'NEW-09',
        'name': 'Acoustic Privacy Index (Visual Proxy)',
        'description': 'Visual estimation of acoustic isolation likelihood based on enclosure, surfaces, and materials',
        'discovered_from_categories': ['enclosed_private_space', 'open_plan_office', 'hospital_healthcare_room'],
        'why_needed': 'Acoustic environments affect well-being; visual cues predict acoustic properties',
        'vision_algorithm': {
            'name': 'Enclosure Detection + Surface Material Analysis',
            'method': 'Segmentation-based enclosure estimation + material classification',
            'libraries': ['torch', 'opencv-python', 'torchvision'],
            'tier': 2,
            'key_functions': [
                'Semantic segmentation for walls, ceiling, floor',
                'Material classification for absorption properties',
                'Edge detection for surface continuity'
            ],
            'input': 'RGB image from indoor space',
            'output': 'dict with: enclosure_score (float [0, 1]), material_absorption_estimate (float [0, 1]), acoustic_privacy_index (float [0, 1])',
            'implementation_outline': '''
            1. Semantic segmentation to identify walls, ceiling, floor
            2. Calculate enclosure_score based on wall coverage in frame (walls=more enclosed)
            3. Classify materials (soft: fabric, carpet, foam → absorbing; hard: concrete, tile → reflective)
            4. Weight material absorption by surface area
            5. Acoustic_privacy_index = enclosure_score * material_absorption_estimate
            6. Validate against known acoustic measurements (where available)
            ''',
            'known_limitations': [
                'Actual acoustic isolation requires frequency response measurement',
                'Visual appearance of thick walls doesn\'t guarantee isolation',
                'Gaps, doors, and HVAC openings not visible',
                'Heavily dependent on segmentation accuracy'
            ]
        },
        'theoretical_warrant': 'Acoustic environment significantly affects stress, concentration, and well-being (WHO Environmental Health criteria)',
        'key_references': [
            'WHO (2018) Environmental Noise Guidelines for the European Region',
            'Frontczak & Seppänen (2007) Literature survey on how different factors influence human comfort in indoor environments'
        ]
    },
    {
        'id': 'NEW-10',
        'name': 'Person/Face Density Estimation',
        'description': 'Number of visible people or faces in scene; occupancy indicator',
        'discovered_from_categories': ['crowding_occupancy', 'classroom_learning_space', 'open_space_plaza'],
        'why_needed': 'Crowding perception affects stress and restoration; essential for social density analysis',
        'vision_algorithm': {
            'name': 'Face Detection + Person Detection',
            'method': 'Multi-task face/person detection (YOLO, RetinaNet, or Faster R-CNN)',
            'libraries': ['torch', 'opencv-python', 'torchvision'],
            'tier': 2,
            'key_functions': [
                'torch.hub.load(\'ultralytics/yolov8\', \'custom\', path=\'yolov8x.pt\')',
                'cv2.CascadeClassifier() for lightweight face detection',
                'torchvision.ops.nms() for non-maximum suppression'
            ],
            'input': 'RGB image',
            'output': 'dict with: person_count (int), face_count (int), density_ratio (float [0, 1]), crowding_level (string: low/moderate/high)',
            'implementation_outline': '''
            1. Load YOLO person + face detection model
            2. Forward pass on input image
            3. Extract bounding boxes for persons and faces
            4. Count detections
            5. Compute density_ratio = count / image_area_in_m2 (requires scene scale estimation)
            6. Classify crowding: low (<1/10m2), moderate (1-5/10m2), high (>5/10m2)
            7. Filter false positives using confidence thresholds (>0.5)
            ''',
            'known_limitations': [
                'Fails with occluded/partial people',
                'Small figures difficult to detect',
                'Person dummies, mannequins may be detected',
                'Requires absolute scale for density calculation (often unknown)'
            ]
        },
        'theoretical_warrant': 'Crowding affects stress hormones and psychological well-being (Environmental psychology, stress literature)',
        'key_references': [
            'Evans & McCoy (1998) When buildings don\'t work: the role of architecture in human health, Journal of Environmental Psychology',
            'Stokols (1972) On the distinction between density and crowding: Some implications for future research'
        ]
    },
    {
        'id': 'NEW-11',
        'name': 'Visual Privacy Metric',
        'description': 'Proportion of visual field that is private/enclosed vs. exposed/transparent',
        'discovered_from_categories': ['enclosed_private_space', 'open_plan_office', 'office_private_workspace'],
        'why_needed': 'Privacy is essential to well-being; visual openness indicates privacy level',
        'vision_algorithm': {
            'name': 'Transparency Detection + Enclosure Analysis',
            'method': 'Segmentation of transparent/glass surfaces + wall coverage analysis',
            'libraries': ['opencv-python', 'torch', 'torchvision'],
            'tier': 2,
            'key_functions': [
                'Semantic segmentation for glass/transparent surfaces',
                'Edge detection for wall/partition identification',
                'Morphological operations for connectivity analysis'
            ],
            'input': 'RGB image from workspace/room',
            'output': 'dict with: transparency_ratio (float [0, 1]), enclosure_ratio (float [0, 1]), privacy_score (float [0, 1])',
            'implementation_outline': '''
            1. Semantic segmentation to identify glass/transparent vs. opaque surfaces
            2. Identify wall/partition pixels
            3. Compute: transparency_ratio = transparent_pixels / (transparent + wall_pixels)
            4. Enclosure_ratio = wall_coverage_in_frame
            5. privacy_score = 1 - transparency_ratio * (1 - enclosure_ratio)
            6. Higher score = more private
            ''',
            'known_limitations': [
                'Reflections and glare confuse transparency detection',
                'View angle matters (doesn\'t measure actual sightlines)',
                'Doesn\'t account for visual attention/distraction',
                'Semantic segmentation errors propagate to privacy estimate'
            ]
        },
        'theoretical_warrant': 'Visual privacy is necessary for concentration and well-being (Attention Restoration Theory, privacy theory)',
        'key_references': [
            'Sundstrom et al. (1982) Privacy at work: Architectural correlates of job satisfaction and job performance',
            'Kamarulzaman et al. (2011) An assessment of the indoor environmental quality of a green building: A case study of an office building in Malaysia'
        ]
    },
    {
        'id': 'NEW-12',
        'name': 'Biomorphic Contour Curvature Index',
        'description': 'Measurement of curved vs. rectilinear forms; naturalness of edge shapes',
        'discovered_from_categories': ['room_with_plants_greenery', 'garden_park_nature', 'biophilic_design_elements'],
        'why_needed': 'Biomorphic forms (curves) are preferred over rectilinear; essential for measuring natural-ness',
        'vision_algorithm': {
            'name': 'Edge Curvature Analysis',
            'method': 'Contour detection + curvature computation via second derivatives',
            'libraries': ['opencv-python', 'scipy', 'numpy'],
            'tier': 2,
            'key_functions': [
                'cv2.findContours() for edge extraction',
                'scipy.signal.savgol_filter() for smoothing contours',
                'Curvature = |dtheta / ds| (change in angle per arc length)'
            ],
            'input': 'RGB or binary image with contours',
            'output': 'dict with: mean_curvature (float [0, π]), curvature_variance (float), biomorphic_index (float [0, 1])',
            'implementation_outline': '''
            1. Edge detection (Canny)
            2. Find contours using findContours()
            3. For each contour:
               a. Smooth with Savitzky-Golay filter
               b. Compute curvature at each point: κ = |dθ/ds|
               c. Accumulate statistics
            4. mean_curvature = mean of all curvatures
            5. Biomorphic_index = 1 - (mean_curvature / max_curvature)
               (High curvature = organic; low = rectilinear)
            6. Optional: Separate contours by size/type
            ''',
            'known_limitations': [
                'Sensitive to edge detection quality',
                'Requires smooth contours (often noisy)',
                'Small/thin features cause artifacts',
                'Doesn\'t distinguish biomorphic from random curves'
            ]
        },
        'theoretical_warrant': 'Curved forms are preferred to rectilinear (Biophilic design, preference psychology)',
        'key_references': [
            'Gómez-Puerto et al. (2016) Preference for curved contours: implications for understanding aesthetic preferences in art',
            'Cela-Conde et al. (2013) The neural foundations of aesthetic appreciation'
        ]
    }
]

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Execute full Kirsh decision tree analysis pipeline."""

    print("="*80)
    print("KIRSH DECISION TREE METHOD FOR CAUSALLY ACTIVE ATTRIBUTES")
    print("="*80)
    print()

    # Load data
    print("[1/6] Loading stimulus data...")
    all_stimuli = load_stimuli()['all_stimuli']
    attrs = load_attributes_taxonomy()
    print(f"      Loaded {len(all_stimuli)} total stimuli")

    # Filter environmental stimuli
    print("[2/6] Filtering environmental stimuli...")
    env_stimuli = filter_environmental_stimuli(all_stimuli)
    print(f"      Kept {len(env_stimuli)} environmental stimuli (filtered out {len(all_stimuli) - len(env_stimuli)} non-environmental)")

    # Cluster
    print("[3/6] Clustering into commonsense categories...")
    clusters = cluster_stimuli_by_category(env_stimuli)
    print(f"      Created {len(clusters)} categories")
    for cat, stimuli in sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
        print(f"        - {cat}: {len(stimuli)} stimuli")

    # Generate decision trees for top categories
    print("[4/6] Generating decision trees for top 25 categories...")
    top_categories = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)[:25]
    equivalence_classes = []

    for i, (cat_name, stim_list) in enumerate(top_categories, 1):
        ec = generate_decision_tree_for_category(cat_name, stim_list, attrs['attributes'])
        equivalence_classes.append(ec)
        print(f"      [{i:2d}/25] {cat_name}: {len(stim_list)} stimuli, {len(ec.new_attributes_discovered)} new attributes")

    # Aggregate new attributes discovered
    print("[5/6] Aggregating discovered attributes...")
    all_discovered = set()
    for ec in equivalence_classes:
        all_discovered.update(ec.new_attributes_discovered)
    print(f"      Total new attributes discovered: {len(all_discovered)}")
    print(f"      From NEW-01 to NEW-{len(NEW_ATTRIBUTES):02d}: {len(NEW_ATTRIBUTES)} predefined new attributes")

    # Build output JSON
    print("[6/6] Building output JSON...")
    output = {
        'metadata': {
            'generated': datetime.datetime.now().isoformat(),
            'method': 'Kirsh Decision Tree Method',
            'n_input_stimuli': len(all_stimuli),
            'n_environmental_stimuli': len(env_stimuli),
            'n_categories_analyzed': len(equivalence_classes),
            'n_new_attributes_discovered': len(NEW_ATTRIBUTES),
        },
        'equivalence_classes': [asdict(ec) for ec in equivalence_classes],
        'new_attributes_discovered': NEW_ATTRIBUTES,
        'algorithm_summary': {
            'tier_1_opencv': [
                'Edge Density (Canny + countNonZero)',
                'Visual Complexity (spectral entropy)',
                'Illumination Uniformity (LAB L-channel variance)',
                'Biomorphic Curvature (contour curvature analysis)'
            ],
            'tier_2_pretrained': [
                'Vegetation Segmentation (DeepLabV3+)',
                'Depth Estimation (MiDaS)',
                'Sky Segmentation (semantic segmentation)',
                'Material Classification (ResNet pretrained)',
                'Figure-Ground Clarity (depth-based segmentation)',
                'Person/Face Detection (YOLO v8)',
                'Visual Privacy (transparency segmentation)',
            ],
            'tier_3_custom': [
                'Plant Health Vigor Estimation (morphological analysis of vegetation)',
                'Water Motion Detection (optical flow analysis)',
                'Institutional Appearance Score (regularity + material analysis)',
                'Classroom Functionality Score (layout analysis)',
                'Semantic Content Analysis for Artwork (vision-language models)'
            ]
        },
        'summary_statistics': {
            'equivalence_classes_by_frequency': [
                {'category': ec.category_name, 'frequency': ec.frequency}
                for ec in sorted(equivalence_classes, key=lambda x: x.frequency, reverse=True)
            ],
            'most_common_essential_attributes': list(
                Counter([a for ec in equivalence_classes for a in ec.essential_attributes]).most_common(10)
            ),
            'most_common_incidental_attributes': list(
                Counter([a for ec in equivalence_classes for a in ec.incidental_attributes]).most_common(10)
            ),
        }
    }

    # Write JSON output
    output_json_path = '/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/data/decision_tree_equivalence_classes.json'
    with open(output_json_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n✓ Saved JSON to: {output_json_path}")

    return output, equivalence_classes

if __name__ == '__main__':
    output, equiv_classes = main()
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
