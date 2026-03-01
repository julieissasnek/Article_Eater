#!/usr/bin/env python3
"""
Extract commonsense stimulus descriptions from article extraction JSON files.
Categories environmental conditions used as stimuli in studies of built environments.
"""

import json
import os
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import re

# Define categorization keywords (case-insensitive substring matching)
CATEGORY_KEYWORDS = {
    "plants_greenery": [
        "plant", "green", "vegetation", "biophil", "natural element", "foliage",
        "nature element", "living wall", "green wall", "potted plant", "flora", "botanical"
    ],
    "lighting": [
        "light", "illumination", "bright", "daylight", "natural light", "artificial light",
        "lighting condition", "window", "sunlight", "daylighting", "luminance", "illuminant"
    ],
    "views": [
        "view", "window view", "vista", "outlook", "scenery", "landscape view", "nature view",
        "scenic", "visual connection", "prospect"
    ],
    "spatial_configuration": [
        "open plan", "enclosed", "spatial", "layout", "configuration", "circulation",
        "distance", "proxim", "space arrangement", "room size", "spatial density",
        "crowding", "density", "floor plan"
    ],
    "color_material": [
        "color", "material", "texture", "surface", "finish", "paint", "ceiling", "wall",
        "floor material", "brick", "wood", "metal", "concrete", "tile"
    ],
    "sound_acoustic": [
        "sound", "acoustic", "noise", "silent", "quiet", "auditory", "reverberation",
        "echo", "noise level", "sound level", "decibel", "loudness"
    ],
    "thermal": [
        "thermal", "temperature", "heat", "cooling", "warm", "cold", "ventilation",
        "air flow", "humidity", "climate control", "temperature control", "HVAC"
    ],
    "nature": [
        "outdoor", "natural environment", "nature", "landscape", "water feature", "water",
        "sky", "garden", "park", "forest", "mountain", "stream", "pond", "natural area",
        "natural setting", "environmental", "ecological"
    ],
    "furniture_interior": [
        "furniture", "desk", "table", "chair", "sofa", "seating", "interior", "furnishing",
        "spatial arrangement", "equipment", "fixture", "decor", "decoration"
    ],
    "building_type": [
        "hospital", "office", "school", "home", "residential", "commercial", "retail",
        "workplace", "classroom", "patient", "public space", "institutional",
        "building type", "workplace environment", "educational"
    ],
    "outdoor_environment": [
        "outdoor", "outside", "exterior", "patio", "terrace", "plaza", "street",
        "public space", "urban", "garden", "landscape", "open air"
    ],
    "art_decoration": [
        "art", "decor", "aesthetic", "design", "visual", "artwork", "picture",
        "display", "ornament", "artistic", "decorative"
    ]
}

def categorize_antecedent(antecedent_text):
    """
    Categorize an antecedent by matching keywords.
    Returns a list of category names (a stimulus can be in multiple categories).
    """
    if not antecedent_text:
        return []

    text_lower = antecedent_text.lower()
    categories = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                categories.append(category)
                break  # Only add once per category

    return categories if categories else ["other"]

def extract_stimuli():
    """
    Extract all antecedent stimulus descriptions from extraction files.
    """
    extraction_dir = Path("/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/data/extractions")

    # Data structures
    stimuli_by_category = defaultdict(list)
    all_stimuli = {}  # antecedent -> metadata
    category_counter = Counter()

    # Track processing
    files_processed = 0
    files_with_errors = 0
    findings_processed = 0

    # Get all JSON files (skip .DS_Store and non-JSON files)
    json_files = sorted([f for f in extraction_dir.iterdir()
                        if f.is_file() and f.suffix == '.json' and f.name != '.DS_Store'])

    print(f"Processing {len(json_files)} extraction files...")
    print()

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8', errors='replace') as f:
                data = json.load(f)

            files_processed += 1

            # Extract metadata
            doi = data.get('doi', 'N/A')
            title = data.get('title', 'N/A')

            # Process findings
            findings = data.get('findings', [])
            for finding in findings:
                findings_processed += 1
                antecedent = finding.get('antecedent', '').strip()
                claim_type = finding.get('claim_type', 'unknown')

                if not antecedent:
                    continue

                # Skip overly generic antecedents
                if len(antecedent) < 5:
                    continue

                # Categorize the antecedent
                categories = categorize_antecedent(antecedent)

                # Store stimulus with metadata
                stimulus_key = antecedent

                if stimulus_key not in all_stimuli:
                    all_stimuli[stimulus_key] = {
                        'antecedent': antecedent,
                        'sources': []
                    }

                # Add source if not already there
                source_info = {
                    'doi': doi,
                    'title': title,
                    'claim_type': claim_type
                }

                if source_info not in all_stimuli[stimulus_key]['sources']:
                    all_stimuli[stimulus_key]['sources'].append(source_info)

                # Add to each category
                for category in categories:
                    category_counter[category] += 1
                    # Only store once per category per stimulus
                    if not any(s['antecedent'] == antecedent for s in stimuli_by_category[category]):
                        stimuli_by_category[category].append({
                            'antecedent': antecedent,
                            'doi': doi,
                            'title': title,
                            'claim_type': claim_type,
                            'categories': categories
                        })

        except json.JSONDecodeError:
            files_with_errors += 1
        except Exception as e:
            files_with_errors += 1

    return stimuli_by_category, all_stimuli, files_processed, files_with_errors, findings_processed, category_counter

def main():
    """Main execution."""
    print("=" * 80)
    print("COMMONSENSE STIMULUS EXTRACTION FROM ARTICLE FINDINGS")
    print("=" * 80)
    print()

    # Extract stimuli
    stimuli_by_category, all_stimuli, files_processed, files_with_errors, findings_processed, category_counter = extract_stimuli()

    # Prepare output structure
    output = {
        "metadata": {
            "generated": datetime.now().strftime("%Y-%m-%d"),
            "source": f"{files_processed} extraction files",
            "total_findings_processed": findings_processed,
            "total_unique_stimuli": len(all_stimuli),
            "total_unique_categories": len(stimuli_by_category),
            "files_processed_successfully": files_processed,
            "files_with_errors": files_with_errors
        },
        "categories": {}
    }

    # Build category descriptions and organize stimuli
    category_descriptions = {
        "plants_greenery": "Indoor plants, green walls, biophilic design, natural vegetation",
        "lighting": "Natural and artificial lighting conditions, daylighting, illumination",
        "views": "Window views, visual connections to nature and landscapes",
        "spatial_configuration": "Room layout, open vs. enclosed spaces, spatial density, floor plans",
        "color_material": "Colors, materials, textures, surface finishes",
        "sound_acoustic": "Acoustic conditions, noise levels, sound environments",
        "thermal": "Temperature, ventilation, humidity, thermal comfort",
        "nature": "Outdoor environments, natural landscapes, environmental conditions",
        "furniture_interior": "Furniture, interior design, spatial furnishings",
        "building_type": "Types of buildings (hospitals, offices, schools, homes)",
        "outdoor_environment": "Outdoor spaces, gardens, patios, public areas",
        "art_decoration": "Artistic elements, decorations, visual aesthetics",
        "other": "Other environmental stimulus descriptions"
    }

    for category in sorted(stimuli_by_category.keys()):
        output["categories"][category] = {
            "description": category_descriptions.get(category, ""),
            "count": len(stimuli_by_category[category]),
            "stimuli": stimuli_by_category[category]
        }

    # Flatten all stimuli for the all_stimuli section
    flat_stimuli = []
    for antecedent, metadata in all_stimuli.items():
        stimulus_entry = {
            "antecedent": antecedent,
            "source_count": len(metadata['sources']),
            "sources": metadata['sources'],
            "categories": categorize_antecedent(antecedent)
        }
        flat_stimuli.append(stimulus_entry)

    output["all_stimuli"] = sorted(flat_stimuli, key=lambda x: x['source_count'], reverse=True)

    # Save output file
    output_path = Path("/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/data/stimulus_descriptions_from_articles.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✓ Output saved to {output_path}")
    print()

    # Print summary report
    print("=" * 80)
    print("SUMMARY REPORT")
    print("=" * 80)
    print()
    print(f"Files processed:              {files_processed}")
    print(f"Files with errors:            {files_with_errors}")
    print(f"Total findings processed:     {findings_processed}")
    print(f"Total unique stimuli:         {len(all_stimuli)}")
    print(f"Total unique categories:      {len(stimuli_by_category)}")
    print()

    print("STIMULI COUNT BY CATEGORY")
    print("-" * 80)
    sorted_categories = sorted(category_counter.items(), key=lambda x: x[1], reverse=True)
    for category, count in sorted_categories:
        pct = (count / sum(category_counter.values())) * 100 if sum(category_counter.values()) > 0 else 0
        print(f"  {category:25s}  {count:6d}  ({pct:5.1f}%)")

    print()
    print("TOP 20 MOST COMMON STIMULUS TYPES (by frequency)")
    print("-" * 80)

    # Count stimulus frequency across all sources
    stimulus_freq = Counter()
    for antecedent, metadata in all_stimuli.items():
        stimulus_freq[antecedent] = len(metadata['sources'])

    for i, (stimulus, count) in enumerate(stimulus_freq.most_common(20), 1):
        categories = categorize_antecedent(stimulus)
        cat_str = ", ".join(categories[:2])  # Show first 2 categories
        print(f"{i:2d}. [{count:3d}x] {stimulus[:70]:<70s}")
        print(f"    Categories: {cat_str}")

    print()
    print("EXAMPLES FROM EACH CATEGORY")
    print("-" * 80)

    for category in sorted(stimuli_by_category.keys()):
        stimuli_list = stimuli_by_category[category]
        print(f"\n{category.upper().replace('_', ' ')}")
        print(f"  Total in category: {len(stimuli_list)}")

        # Show up to 3 examples
        for i, stimulus in enumerate(stimuli_list[:3], 1):
            antecedent = stimulus['antecedent']
            if len(antecedent) > 75:
                antecedent = antecedent[:75] + "..."
            print(f"  {i}. {antecedent}")
            print(f"     DOI: {stimulus['doi']}")

    print()
    print("=" * 80)
    print(f"Extraction complete. Output: {output_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
