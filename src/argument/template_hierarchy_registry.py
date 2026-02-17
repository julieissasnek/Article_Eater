"""
Template hierarchy registry adapter.

Builds a lightweight hierarchy registry and alias map from template JSON files.
This allows hierarchy QA queries to work even before a dedicated HierarchyRegistry
service is available.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def _normalize_alias(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text)
    return text


def _clean_level_label(text: str) -> str:
    text = re.sub(r"\(.*?\)", "", text)
    text = text.split("—", 1)[0]
    text = text.split("-", 1)[0]
    text = text.strip()
    text = text.replace("hue_warm_cool", "hue")
    text = text.replace("warm_cool", "hue")
    return _normalize_alias(text)


def _rank_effect_magnitude(value: str) -> int:
    v = value.lower()
    if "primary" in v or "strongest" in v:
        return 0
    if "secondary" in v:
        return 1
    if "tertiary" in v:
        return 2
    return 99


def _aliases_for_levels(levels: List[str]) -> List[str]:
    aliases: List[str] = []
    cleaned = [_clean_level_label(level) for level in levels]
    cleaned = [c for c in cleaned if c]
    if len(cleaned) >= 2:
        aliases.append(" > ".join(cleaned))
        # Adjacent pair aliases support direct comparative query text.
        for idx in range(len(cleaned) - 1):
            aliases.append(f"{cleaned[idx]} > {cleaned[idx + 1]}")
    return aliases


def _extract_hierarchies_from_template(template: Dict[str, Any]) -> List[Tuple[str, List[str]]]:
    rows: List[Tuple[str, List[str]]] = []

    # Generic pattern: any object named *hierarchy containing "hierarchy": [...]
    for key, value in template.items():
        if "hierarchy" not in key.lower():
            continue
        if isinstance(value, dict) and isinstance(value.get("hierarchy"), list):
            levels = [str(item) for item in value["hierarchy"] if str(item).strip()]
            if len(levels) >= 2:
                rows.append((key, levels))
        elif isinstance(value, list):
            levels = [str(item) for item in value if str(item).strip()]
            if len(levels) >= 2:
                rows.append((key, levels))

    # COL2-style pattern: arousal_dimensions with effect magnitude ordering.
    arousal_dims = template.get("arousal_dimensions")
    if isinstance(arousal_dims, dict):
        ranked: List[Tuple[int, str]] = []
        for dim_name, dim_data in arousal_dims.items():
            if not isinstance(dim_data, dict):
                continue
            magnitude = str(dim_data.get("effect_magnitude", ""))
            rank = _rank_effect_magnitude(magnitude)
            ranked.append((rank, dim_name))
        ranked.sort(key=lambda item: (item[0], item[1]))
        ordered = [name for rank, name in ranked if rank != 99]
        if len(ordered) >= 2:
            rows.append(("arousal_dimensions", ordered))

    return rows


def build_hierarchy_registry_from_dir(
    template_dir: Path,
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str]]:
    registry: Dict[str, Dict[str, Any]] = {}
    aliases: Dict[str, str] = {}

    if not template_dir.exists():
        return registry, aliases

    for template_file in sorted(template_dir.glob("*.json")):
        try:
            data = json.loads(template_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        template_key = data.get("display_id") or data.get("template_id") or template_file.stem
        template_key = str(template_key)
        hierarchies = _extract_hierarchies_from_template(data)

        for field_name, levels in hierarchies:
            hierarchy_id = _slugify(f"{template_key}_{field_name}")
            ordered_levels = [_clean_level_label(level) for level in levels]
            ordered_levels = [level for level in ordered_levels if level]
            if len(ordered_levels) < 2:
                continue

            registry[hierarchy_id] = {
                "source_template": template_key,
                "ordered_levels": ordered_levels,
                "source_field": field_name,
            }

            alias_values = [
                hierarchy_id,
                hierarchy_id.replace("_", " "),
                f"{template_key.lower()} {field_name.lower().replace('_', ' ')}",
                *(_aliases_for_levels(ordered_levels)),
            ]
            for alias in alias_values:
                key = _normalize_alias(alias)
                if key:
                    aliases[key] = hierarchy_id

    return registry, aliases


@lru_cache(maxsize=1)
def load_template_hierarchy_registry() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str]]:
    root = Path(__file__).resolve().parents[2]
    template_dir = root / "data" / "templates"
    return build_hierarchy_registry_from_dir(template_dir)
