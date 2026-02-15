"""
Auto-generated EvidenceType adapter.
Canonical contract section: enums.EvidenceType
"""

from __future__ import annotations

from typing import Dict, Optional

VALUE_TO_CANONICAL: Dict[str, str] = {
  "computational_model": "computational_model",
  "correlational": "correlational",
  "direct": "observational",
  "empirical": "observational",
  "experimental": "experimental",
  "indirect": "observational",
  "meta": "meta_analysis",
  "meta_analysis": "meta_analysis",
  "neuroscientific": "neuroscientific",
  "replication_failure": "replication_failure",
  "replication_success": "replication_success",
  "review": "theoretical",
  "theoretical": "theoretical"
}
SOURCE_CANONICAL_TO_LOCAL: Dict[str, Dict[str, str]] = {
  "article_finder_detected": {
    "computational_model": "",
    "correlational": "",
    "experimental": "",
    "meta_analysis": "",
    "neuroimaging": "",
    "neuroscientific": "",
    "observational": "",
    "replication_failure": "",
    "replication_success": "",
    "theoretical": ""
  },
  "bn_enhanced_edge": {
    "computational_model": "theoretical",
    "correlational": "empirical",
    "experimental": "empirical",
    "meta_analysis": "meta_analysis",
    "neuroimaging": "theoretical",
    "neuroscientific": "theoretical",
    "observational": "empirical",
    "replication_failure": "replication_failure",
    "replication_success": "replication_success",
    "theoretical": "theoretical"
  },
  "bn_literature_linker": {
    "computational_model": "theoretical",
    "correlational": "indirect",
    "experimental": "direct",
    "meta_analysis": "meta",
    "neuroimaging": "indirect",
    "neuroscientific": "indirect",
    "observational": "direct",
    "replication_failure": "direct",
    "replication_success": "direct",
    "theoretical": "theoretical"
  },
  "bn_mechanism_spec": {
    "computational_model": "computational_model",
    "correlational": "correlational",
    "experimental": "experimental",
    "meta_analysis": "theoretical",
    "neuroimaging": "neuroscientific",
    "neuroscientific": "neuroscientific",
    "observational": "correlational",
    "replication_failure": "experimental",
    "replication_success": "experimental",
    "theoretical": "theoretical"
  },
  "bn_sql_evidence_type": {
    "computational_model": "theoretical",
    "correlational": "empirical",
    "experimental": "empirical",
    "meta_analysis": "meta_analysis",
    "neuroimaging": "theoretical",
    "neuroscientific": "theoretical",
    "observational": "empirical",
    "replication_failure": "replication_failure",
    "replication_success": "replication_success",
    "theoretical": "theoretical"
  },
  "bn_sql_mechanism_evidence_type": {
    "computational_model": "computational_model",
    "correlational": "correlational",
    "experimental": "experimental",
    "meta_analysis": "theoretical",
    "neuroimaging": "neuroscientific",
    "neuroscientific": "neuroscientific",
    "observational": "correlational",
    "replication_failure": "experimental",
    "replication_success": "experimental",
    "theoretical": "theoretical"
  },
  "tagging_csv": {
    "computational_model": "",
    "correlational": "",
    "experimental": "",
    "meta_analysis": "",
    "neuroimaging": "",
    "neuroscientific": "",
    "observational": "",
    "replication_failure": "",
    "replication_success": "",
    "theoretical": ""
  }
}
UNMAPPED_BY_SOURCE = {
  "article_finder_detected": [],
  "bn_enhanced_edge": [],
  "bn_literature_linker": [],
  "bn_mechanism_spec": [],
  "bn_sql_evidence_type": [],
  "bn_sql_mechanism_evidence_type": [],
  "tagging_csv": [
    "computed",
    "image_2d",
    "image_3d",
    "metadata",
    "sensor"
  ]
}


def source_evidence_to_canonical(source: str, value: str) -> Optional[str]:
    key = value.strip().lower()
    return VALUE_TO_CANONICAL.get(key)


def canonical_to_source_evidence(source: str, canonical_value: str) -> Optional[str]:
    source_key = source.strip().lower()
    canonical_key = canonical_value.strip().lower()
    table = SOURCE_CANONICAL_TO_LOCAL.get(source_key, {})
    result = table.get(canonical_key)
    if result == "":
        return None
    return result


def test_migration_lossless() -> None:
    # Lossless check on BN mechanism surface.
    sample = {
      "theoretical": "theoretical",
      "correlational": "correlational",
      "experimental": "experimental",
      "neuroscientific": "neuroscientific",
      "computational_model": "computational_model"
    }
    for source_value, canonical in sample.items():
        mapped = source_evidence_to_canonical("bn_mechanism_spec", source_value)
        assert mapped == canonical
        back = canonical_to_source_evidence("bn_mechanism_spec", mapped)
        assert back == source_value


if __name__ == "__main__":
    test_migration_lossless()
    print("EvidenceType adapter self-test passed.")
