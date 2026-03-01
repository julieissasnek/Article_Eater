"""
Fix AG's broken molecule_ids by mapping them to canonical rasa attractor names.

AG's linking process produced invalid molecule_id formats like:
  - M_ATTRACTOR_TRANSITION
  - M_CULTURAL_VALUATION
  - M_CCT_PREFERENCE
  - M_BEAUTY_COMPRESSION
  - M_RASA

These need to be mapped to the 9 canonical rasa attractors:
  1. shringara (Love/Beauty)
  2. hasya (Joy/Humor)
  3. karuna (Compassion)
  4. veera (Heroism)
  5. bibhatsa (Disgust)
  6. bhayanaka (Terror/Awe)
  7. raudra (Wrath/Power)
  8. shanta (Peace/Serenity)
  9. adbhuta (Wonder)
"""

import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Semantic mapping from broken IDs to canonical rasa attractors
MOLECULE_ID_MAPPING = {
    # Attractor transition → wonder (novelty/change)
    "M_ATTRACTOR_TRANSITION": "adbhuta",
    
    # Cultural valuation → love/beauty (aesthetic appreciation in culture)
    "M_CULTURAL_VALUATION": "shringara",
    
    # CCT preference (Correlated Color Temperature) → aesthetic preference (beauty)
    "M_CCT_PREFERENCE": "shringara",
    
    # Beauty compression → love/beauty (compression of aesthetic information)
    "M_BEAUTY_COMPRESSION": "shringara",
    
    # Generic M_RASA → wonder (neutral attractor, maps to interest/novelty)
    "M_RASA": "adbhuta",
}

# Canonical rasa attractors (from rasa_attractors.json)
CANONICAL_RASA = {
    "shringara": "Love/Beauty",
    "hasya": "Joy/Humor",
    "karuna": "Compassion",
    "veera": "Heroism",
    "bibhatsa": "Disgust",
    "bhayanaka": "Terror/Awe",
    "raudra": "Wrath/Power",
    "shanta": "Peace/Serenity",
    "adbhuta": "Wonder",
}


def fix_molecule_ids_in_file(filepath):
    """Fix molecule_ids in a single extraction file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return {"file": filepath, "status": "error", "error": str(e), "changes": 0}
    
    changes = 0
    old_ids_set = set()
    
    if 'molecule_ids' in data and data['molecule_ids']:
        new_molecule_ids = []
        for mol_id in data['molecule_ids']:
            if isinstance(mol_id, str):
                if mol_id in MOLECULE_ID_MAPPING:
                    old_ids_set.add(mol_id)
                    new_molecule_ids.append(MOLECULE_ID_MAPPING[mol_id])
                    changes += 1
                else:
                    new_molecule_ids.append(mol_id)
            elif isinstance(mol_id, dict):
                if 'id' in mol_id and mol_id['id'] in MOLECULE_ID_MAPPING:
                    old_ids_set.add(mol_id['id'])
                    mol_id['id'] = MOLECULE_ID_MAPPING[mol_id['id']]
                    new_molecule_ids.append(mol_id)
                    changes += 1
                else:
                    new_molecule_ids.append(mol_id)
            else:
                new_molecule_ids.append(mol_id)
        
        if changes > 0:
            data['molecule_ids'] = new_molecule_ids
            try:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                return {
                    "file": filepath,
                    "status": "fixed",
                    "changes": changes,
                    "old_ids": list(old_ids_set)
                }
            except Exception as e:
                return {
                    "file": filepath,
                    "status": "write_error",
                    "error": str(e),
                    "changes": 0
                }
    
    return {"file": filepath, "status": "no_changes", "changes": 0}


def main():
    """Main entry point: fix all extraction files."""
    extraction_dir = Path("data/extractions")
    
    if not extraction_dir.exists():
        print(f"Error: {extraction_dir} does not exist")
        return
    
    print("=" * 80)
    print("FIXING AG'S BROKEN MOLECULE_IDS")
    print("=" * 80)
    print()
    
    # Print mapping
    print("Semantic Mapping (Broken → Canonical):")
    print("-" * 80)
    for broken, canonical in sorted(MOLECULE_ID_MAPPING.items()):
        print(f"  {broken:30} → {canonical:20} ({CANONICAL_RASA[canonical]})")
    print()
    
    # Process all files
    results = []
    for filepath in sorted(extraction_dir.glob("*.json")):
        result = fix_molecule_ids_in_file(str(filepath))
        if result["changes"] > 0:
            results.append(result)
    
    # Report statistics
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()
    
    fixed_files = [r for r in results if r["status"] == "fixed"]
    errors = [r for r in results if r["status"] in ["error", "write_error"]]
    
    print(f"Total extraction files: {len(list(extraction_dir.glob('*.json')))}")
    print(f"Files with changes: {len(fixed_files)}")
    print(f"Total ID replacements: {sum(r['changes'] for r in fixed_files)}")
    print(f"Errors: {len(errors)}")
    print()
    
    # Detailed changes by old ID
    changes_by_old_id = defaultdict(int)
    for result in fixed_files:
        for old_id in result.get("old_ids", []):
            changes_by_old_id[old_id] += result["changes"] // len(result.get("old_ids", [1]))
    
    print("Changes by Old ID Type:")
    print("-" * 80)
    for old_id in sorted(MOLECULE_ID_MAPPING.keys()):
        count = sum(1 for r in fixed_files for oid in r.get("old_ids", []) if oid == old_id) * 1
        canonical = MOLECULE_ID_MAPPING[old_id]
        print(f"  {old_id:30} → {canonical:20}")
        # Count actual replacements by looking at the data
        count = sum(
            data['molecule_ids'].count(old_id) if isinstance(data['molecule_ids'], list) else 0
            for filepath in extraction_dir.glob("*.json")
            for data in [json.load(open(filepath, 'r'))]
            if 'molecule_ids' in data
        )
    print()
    
    # Files that were fixed
    if fixed_files:
        print("Files fixed (first 10):")
        print("-" * 80)
        for result in fixed_files[:10]:
            print(f"  {Path(result['file']).name:50} ({result['changes']} replacements)")
        if len(fixed_files) > 10:
            print(f"  ... and {len(fixed_files) - 10} more files")
    
    print()
    print("=" * 80)
    print(f"Job completed at {datetime.now().isoformat()}")
    print("=" * 80)
    
    return {
        "total_files": len(list(extraction_dir.glob('*.json'))),
        "files_fixed": len(fixed_files),
        "total_replacements": sum(r['changes'] for r in fixed_files),
        "errors": len(errors),
        "mapping": MOLECULE_ID_MAPPING,
    }


if __name__ == "__main__":
    main()
