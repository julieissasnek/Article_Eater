#!/usr/bin/env python3
"""
Self-Interrogation Script for Interpretation Space Phase 1 Pilot

This script processes 50 pilot beliefs and interrogates the ATLAS QA system's
mechanistic knowledge for each belief. The goal is to assess what the system
actually knows about mechanisms vs. what it claims to know.

Process:
1. Load pilot beliefs (50 beliefs with credence, entrenchment, templates)
2. For each belief:
   - Assemble available context (extraction data, templates, theories)
   - Generate mechanism question (MECHANISM_QUESTION field)
   - Construct honest system_answer from available data
   - Track sources and confidence
3. Output evaluation dataset: interrogation_results_raw.json
4. Output summary statistics: interrogation_data_summary.md

Date: 2026-03-01
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, List, Any
from collections import defaultdict
import re


class InterrogationBuilder:
    """Builds the self-interrogation dataset for interpretation space pilot."""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.data_dir = self.repo_root / "data"
        self.extraction_dir = self.data_dir / "extractions"
        self.template_dir = self.data_dir / "templates"
        self.theory_dir = self.data_dir / "theories"
        self.interp_dir = self.data_dir / "interpretation_space"

        self.results = []
        self.stats = {
            "total_beliefs": 0,
            "by_zone": defaultdict(int),
            "mechanism_data_rich": 0,  # has extraction mechanism
            "mechanism_data_sparse": 0,  # only templates
            "mechanism_data_none": 0,  # no mechanism info
            "template_coverage": [],
            "template_used_count": defaultdict(int),
        }

    def load_pilot_beliefs(self) -> List[Dict[str, Any]]:
        """Load the 50 pilot beliefs from pilot_beliefs_50.json"""
        beliefs_file = self.interp_dir / "pilot_beliefs_50.json"
        with open(beliefs_file, "r") as f:
            return json.load(f)

    def load_extraction(self, doi: str) -> Optional[Dict[str, Any]]:
        """Load extraction JSON for a given DOI.

        Convert DOI to filename: replace '/' with '_', keep dots.
        E.g., "10.1006/jevp.2000.0198" -> "10.1006_jevp.2000.0198.json"
        """
        # Extract DOI conversion: 10.1006/jevp.2000.0198 -> 10.1006_jevp.2000.0198
        normalized_doi = doi.replace("/", "_")
        extraction_file = self.extraction_dir / f"{normalized_doi}.json"

        if extraction_file.exists():
            with open(extraction_file, "r") as f:
                return json.load(f)
        return None

    def extract_finding_from_extraction(
        self, extraction: Dict[str, Any], finding_number: int
    ) -> Optional[Dict[str, Any]]:
        """Extract finding N from extraction (1-indexed).

        belief_id format: {doi}__f{N} where N is 1-indexed
        Convert to 0-indexed for the findings array.
        """
        if "findings" not in extraction or not extraction["findings"]:
            return None

        # finding_number is 1-indexed (from belief_id)
        idx = finding_number - 1
        if 0 <= idx < len(extraction["findings"]):
            return extraction["findings"][idx]
        return None

    def parse_belief_id(self, belief_id: str) -> tuple:
        """Parse belief_id format: {doi}__f{N}

        Returns: (doi, finding_number)
        """
        # Format: "10.1006/jevp.2000.0198__f8"
        match = re.match(r"(.+?)__f(\d+)$", belief_id)
        if match:
            return match.group(1), int(match.group(2))
        return None, None

    def load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Load a template by its display_id (e.g., 'T36', 'MS2')."""
        # Try direct file first (display_id.json)
        template_file = self.template_dir / f"{template_id}.json"
        if template_file.exists():
            with open(template_file, "r") as f:
                return json.load(f)
        return None

    def load_theory(self, theory_name: str) -> Optional[Dict[str, Any]]:
        """Load a theory file."""
        theory_file = self.theory_dir / f"{theory_name}.json"
        if theory_file.exists():
            with open(theory_file, "r") as f:
                return json.load(f)
        return None

    def extract_mechanism_chain(self, template: Dict[str, Any]) -> Optional[str]:
        """Extract mechanism description from template.

        Look for: causal_links (with activity descriptions), mechanism,
        structural_pattern, short_description, etc.
        """
        parts = []

        # Template name often has the mechanism
        if "name" in template:
            parts.append(f"Template mechanism: {template['name']}")

        # Causal links describe the chain
        if "causal_links" in template and template["causal_links"]:
            chain_parts = []
            for link in template["causal_links"]:
                from_entity = link.get("from_entity", "?")
                activity = link.get("activity", "→")
                to_entity = link.get("to_entity", "?")
                evidence = link.get("evidence_base", "")

                chain_str = f"{from_entity} {activity} {to_entity}"
                if evidence:
                    chain_str += f" [{evidence}]"
                chain_parts.append(chain_str)

            if chain_parts:
                parts.append("Causal chain: " + " → ".join(chain_parts))

        # Short description
        if "short_description" in template:
            parts.append(f"Description: {template['short_description']}")

        # Structural pattern
        if "structural_pattern" in template:
            parts.append(f"Pattern: {template['structural_pattern']}")

        return " | ".join(parts) if parts else None

    def construct_system_answer(
        self, belief: Dict[str, Any], extraction: Optional[Dict[str, Any]],
        finding: Optional[Dict[str, Any]], templates: List[Dict[str, Any]]
    ) -> tuple:
        """Construct an honest system_answer from available data.

        Returns: (system_answer_text, list_of_sources)
        """
        sources = []
        answer_parts = []

        # Start with what we know honestly
        if finding and finding.get("mechanism"):
            # Direct mechanistic information from the extraction
            answer_parts.append(f"Empirical mechanism (from paper): {finding['mechanism']}")
            sources.append(f"extraction finding mechanism")

        if finding and finding.get("theory_links"):
            # Theory links from finding
            theories = ", ".join(finding["theory_links"])
            answer_parts.append(f"Linked theories: {theories}")
            sources.append(f"extraction theory_links")

        # Template-level mechanisms (not empirically verified for this specific finding)
        template_mechanisms = []
        for template in templates:
            mechanism = self.extract_mechanism_chain(template)
            if mechanism:
                template_mechanisms.append(mechanism)
                display_id = template.get("display_id", template.get("template_id", "?"))
                sources.append(f"template {display_id} mechanism")

        if template_mechanisms:
            if answer_parts:
                answer_parts.append(
                    "Theoretical mechanisms (from matched templates, "
                    "not empirically verified for this specific finding):"
                )
            else:
                answer_parts.append(
                    "Only theoretical mechanisms available (from matched templates):"
                )

            for mech in template_mechanisms[:3]:  # Limit to top 3 templates
                answer_parts.append(f"  • {mech}")

        # Honest admission if we have no mechanism data
        if not answer_parts:
            answer_parts.append(
                "No mechanistic information available. The system has no data "
                "about how this causal relationship works."
            )
            sources.append("none (no mechanism data)")

        system_answer = "\n".join(answer_parts)
        return system_answer, sources

    def generate_mechanism_question(
        self, belief_content: str, finding: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate the mechanism question for a belief.

        If belief is in "X → Y" format, parse and generate targeted question.
        Otherwise use belief content directly.
        """
        # Try to parse "X → Y" format
        arrow_patterns = ["→", "->", "=>"]
        antecedent = None
        consequent = None

        for arrow in arrow_patterns:
            if arrow in belief_content:
                parts = belief_content.split(arrow)
                if len(parts) == 2:
                    antecedent = parts[0].strip()
                    consequent = parts[1].strip()
                    break

        # If we have antecedent/consequent from belief content
        if antecedent and consequent:
            return f"How does {antecedent} cause or lead to {consequent}? What is the causal mechanism?"

        # If we have finding object with structured fields
        if finding:
            antecedent = finding.get("antecedent", "")
            consequent = finding.get("consequent", "")
            if antecedent and consequent:
                return f"How does {antecedent} cause or lead to {consequent}? What is the causal mechanism?"

        # Fallback: generic mechanism question about the belief
        return f"What is the causal mechanism underlying this belief: {belief_content}?"

    def process_belief(
        self, belief: Dict[str, Any], belief_idx: int
    ) -> Dict[str, Any]:
        """Process a single belief through the interrogation pipeline."""

        belief_id = belief["belief_id"]
        content = belief["content"]
        credence = belief.get("credence_value")
        entrenchment = belief.get("entrenchment")
        zone = belief.get("stratification_zone", "unknown")

        # Parse belief_id to get DOI and finding number
        doi, finding_number = self.parse_belief_id(belief_id)

        # Load extraction if DOI is present
        extraction = None
        finding = None
        finding_fields = {}

        if doi:
            extraction = self.load_extraction(doi)
            if extraction and finding_number:
                finding = self.extract_finding_from_extraction(extraction, finding_number)

                if finding:
                    # Extract key fields from finding
                    finding_fields = {
                        "antecedent": finding.get("antecedent"),
                        "consequent": finding.get("consequent"),
                        "direction": finding.get("direction"),
                        "claim_type": finding.get("claim_type"),
                        "p_value": finding.get("p_value"),
                        "effect_size": finding.get("effect_size"),
                        "sample_size": finding.get("sample_size"),
                        "mechanism": finding.get("mechanism"),
                        "theory_links": finding.get("theory_links"),
                        "source": finding.get("source"),
                        "quote": finding.get("quote", "")[:100] if finding.get("quote") else None,
                    }

        # Load linked templates
        top_templates = []
        linked_templates = []
        linked_theories = []
        other_findings_from_paper = []

        if "epistemic_v2" in belief and "template_relevance_v1" in belief["epistemic_v2"]:
            template_list = belief["epistemic_v2"]["template_relevance_v1"].get(
                "top_templates", []
            )
            for template_ref in template_list:
                display_id = template_ref.get("display_id")
                template = self.load_template(display_id)
                if template:
                    top_templates.append(template)
                    linked_templates.append(
                        {
                            "display_id": display_id,
                            "template_id": template.get("template_id"),
                            "score": template_ref.get("score"),
                            "name": template.get("name"),
                        }
                    )

        # Extract other findings from same paper
        if extraction and extraction.get("findings"):
            for idx, other_finding in enumerate(extraction["findings"], 1):
                if idx != finding_number:  # Skip current finding
                    other_findings_from_paper.append(
                        {
                            "id": idx,
                            "antecedent": other_finding.get("antecedent"),
                            "consequent": other_finding.get("consequent"),
                            "direction": other_finding.get("direction"),
                            "mechanism": other_finding.get("mechanism"),
                        }
                    )

        # Generate mechanism question
        mechanism_question = self.generate_mechanism_question(content, finding)

        # Construct system answer
        system_answer, sources = self.construct_system_answer(
            belief, extraction, finding, top_templates
        )

        # Build available_data structure
        available_data = {
            "has_extraction": extraction is not None,
            "finding_fields": finding_fields if finding else {},
            "linked_templates": linked_templates,
            "linked_theories": linked_theories,
            "other_findings_from_paper": other_findings_from_paper[:5],  # Top 5
        }

        # Categorize mechanism data quality
        if finding and finding.get("mechanism"):
            data_quality = "rich"
            self.stats["mechanism_data_rich"] += 1
        elif top_templates:
            data_quality = "sparse"
            self.stats["mechanism_data_sparse"] += 1
        else:
            data_quality = "none"
            self.stats["mechanism_data_none"] += 1

        # Track template usage
        for template in linked_templates:
            self.stats["template_used_count"][template["display_id"]] += 1

        return {
            "belief_idx": belief_idx,
            "belief_id": belief_id,
            "content": content,
            "credence": credence,
            "entrenchment": entrenchment,
            "stratification_zone": zone,
            "mechanism_question": mechanism_question,
            "available_data": available_data,
            "system_answer": system_answer,
            "answer_sources": sources,
            "data_quality": data_quality,
        }

    def run(self) -> tuple:
        """Run the full interrogation pipeline.

        Returns: (results, stats)
        """
        print("Loading pilot beliefs...")
        beliefs = self.load_pilot_beliefs()

        print(f"Processing {len(beliefs)} beliefs...")
        for idx, belief in enumerate(beliefs):
            print(f"  [{idx+1}/{len(beliefs)}] {belief['belief_id']}", end="")
            try:
                result = self.process_belief(belief, idx)
                self.results.append(result)
                self.stats["total_beliefs"] += 1
                self.stats["by_zone"][result["stratification_zone"]] += 1
                print(" ✓")
            except Exception as e:
                print(f" ✗ {str(e)}")
                continue

        return self.results, self.stats

    def write_results(self, results: List[Dict[str, Any]]) -> None:
        """Write interrogation_results_raw.json"""
        output_file = self.interp_dir / "interrogation_results_raw.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Written: {output_file}")

    def write_summary(self, results: List[Dict[str, Any]], stats: Dict[str, Any]) -> None:
        """Write interrogation_data_summary.md"""
        summary_lines = [
            "# Interpretation Space Phase 1: Interrogation Summary",
            "",
            f"**Generated**: 2026-03-01",
            f"**Total Beliefs Processed**: {stats['total_beliefs']}",
            "",
            "## Mechanism Data Coverage",
            "",
            f"- **Rich mechanism data** (empirical finding-level mechanism): "
            f"{stats['mechanism_data_rich']} beliefs "
            f"({100*stats['mechanism_data_rich']/max(1, stats['total_beliefs']):.1f}%)",
            f"- **Sparse mechanism data** (only theoretical templates): "
            f"{stats['mechanism_data_sparse']} beliefs "
            f"({100*stats['mechanism_data_sparse']/max(1, stats['total_beliefs']):.1f}%)",
            f"- **No mechanism data**: "
            f"{stats['mechanism_data_none']} beliefs "
            f"({100*stats['mechanism_data_none']/max(1, stats['total_beliefs']):.1f}%)",
            "",
            "## Distribution by Stratification Zone",
            "",
        ]

        for zone in sorted(stats["by_zone"].keys()):
            count = stats["by_zone"][zone]
            pct = 100 * count / max(1, stats["total_beliefs"])
            summary_lines.append(f"- **Zone {zone}**: {count} beliefs ({pct:.1f}%)")

        summary_lines.extend([
            "",
            "## Data Quality by Zone",
            "",
        ])

        # Calculate by-zone statistics
        zone_stats = defaultdict(lambda: {"rich": 0, "sparse": 0, "none": 0})
        for result in results:
            zone = result["stratification_zone"]
            quality = result["data_quality"]
            zone_stats[zone][quality] += 1

        for zone in sorted(zone_stats.keys()):
            zone_data = zone_stats[zone]
            total = sum(zone_data.values())
            summary_lines.append(f"### Zone {zone} (n={total})")
            summary_lines.append(
                f"- Rich: {zone_data['rich']} ({100*zone_data['rich']/max(1,total):.0f}%)"
            )
            summary_lines.append(
                f"- Sparse: {zone_data['sparse']} ({100*zone_data['sparse']/max(1,total):.0f}%)"
            )
            summary_lines.append(
                f"- None: {zone_data['none']} ({100*zone_data['none']/max(1,total):.0f}%)"
            )
            summary_lines.append("")

        summary_lines.extend([
            "## Top Template Usage",
            "",
            "Templates contributing to mechanistic answers (top 15):",
            "",
        ])

        # Sort templates by usage count
        sorted_templates = sorted(
            stats["template_used_count"].items(), key=lambda x: x[1], reverse=True
        )

        for display_id, count in sorted_templates[:15]:
            summary_lines.append(f"- **{display_id}**: used in {count} beliefs")

        summary_lines.extend([
            "",
            "## Key Observations",
            "",
            "### System Knowledge Assessment",
            "",
            f"The ATLAS system's mechanistic knowledge is distributed across three tiers:",
            "",
            f"1. **Empirical findings** ({stats['mechanism_data_rich']} beliefs): "
            f"The extraction layer captured finding-level mechanisms from papers.",
            "",
            f"2. **Theoretical templates** ({stats['mechanism_data_sparse']} beliefs): "
            f"Template relevance matched beliefs to theoretical frameworks, but these are "
            f"not empirically validated for specific findings.",
            "",
            f"3. **No information** ({stats['mechanism_data_none']} beliefs): "
            f"Some beliefs lack both empirical mechanisms and template matches.",
            "",
            "### Implications for Self-Interrogation",
            "",
            "This distribution shows that the system's mechanistic comprehensiveness depends on:",
            f"- **Extraction quality**: How well the LLM captured mechanisms from papers",
            f"- **Template coverage**: How well theoretical templates bridge findings to mechanisms",
            f"- **Honest epistemology**: Admitting when no mechanism data exists (vs. hallucination)",
            "",
            "### Recommendations",
            "",
            "1. For beliefs with no mechanism data: investigate why extraction failed",
            "   (missing mechanism statement in paper? poor finding identification?)",
            "",
            "2. For sparse-data beliefs: clarify which template mechanisms are empirically "
            "   validated vs. purely theoretical",
            "",
            "3. For rich-data beliefs: perform deeper interrogation on mechanism quality "
            "   (are mechanisms specific? testable? grounded in theory?)",
            "",
        ])

        summary_text = "\n".join(summary_lines)
        output_file = self.interp_dir / "interrogation_data_summary.md"
        with open(output_file, "w") as f:
            f.write(summary_text)
        print(f"Written: {output_file}")


def main():
    repo_root = "/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1"

    builder = InterrogationBuilder(repo_root)

    print("=" * 70)
    print("INTERPRETATION SPACE PHASE 1: SELF-INTERROGATION SCRIPT")
    print("=" * 70)
    print()

    results, stats = builder.run()

    print()
    print("=" * 70)
    print("WRITING RESULTS")
    print("=" * 70)
    print()

    builder.write_results(results)
    builder.write_summary(results, stats)

    print()
    print("=" * 70)
    print("COMPLETION SUMMARY")
    print("=" * 70)
    print()
    print(f"Processed: {stats['total_beliefs']} beliefs")
    print(f"  - Zone 1: {stats['by_zone']['1']} beliefs")
    print(f"  - Zone 2: {stats['by_zone']['2']} beliefs")
    print(f"  - Zone 3: {stats['by_zone']['3']} beliefs")
    print()
    print(f"Mechanism data distribution:")
    print(f"  - Rich: {stats['mechanism_data_rich']} ({100*stats['mechanism_data_rich']/max(1, stats['total_beliefs']):.1f}%)")
    print(f"  - Sparse: {stats['mechanism_data_sparse']} ({100*stats['mechanism_data_sparse']/max(1, stats['total_beliefs']):.1f}%)")
    print(f"  - None: {stats['mechanism_data_none']} ({100*stats['mechanism_data_none']/max(1, stats['total_beliefs']):.1f}%)")
    print()


if __name__ == "__main__":
    main()
