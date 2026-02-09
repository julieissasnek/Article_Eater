"""
Article Eater V23 — Export Page
Sprint 3.0.4 — 2026-02-08

Export evidence summaries, BibTeX, and verification checklists.
Implements purpose-driven bundles per Munzner's recommendation.
"""

import streamlit as st
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import PAGE_TITLE, COLORS, USER_TYPES
from styles import apply_shared_styles

st.set_page_config(
    page_title=f"{PAGE_TITLE} — Export",
    page_icon="📤",
    layout="wide"
)


def init_session_state():
    """Initialize session state for export page."""
    if "export_topic" not in st.session_state:
        st.session_state.export_topic = ""
    if "export_purpose" not in st.session_state:
        st.session_state.export_purpose = "literature_review"
    if "export_format" not in st.session_state:
        st.session_state.export_format = "markdown"
    if "generated_export" not in st.session_state:
        st.session_state.generated_export = None


# Export purpose descriptions
EXPORT_PURPOSES = {
    "practitioner_briefing": {
        "name": "Practitioner Briefing",
        "icon": "🏗️",
        "description": "Quick design guidance with practical recommendations",
        "outputs": ["Evidence summary (Markdown)", "Verification checklist"],
        "best_for": "Architects, designers, practitioners"
    },
    "literature_review": {
        "name": "Literature Review",
        "icon": "📚",
        "description": "Academic synthesis with full citations",
        "outputs": ["Evidence summary", "BibTeX references", "Belief data (JSON)", "Verification checklist"],
        "best_for": "Researchers, academics, students"
    },
    "systematic_review": {
        "name": "Systematic Review",
        "icon": "📋",
        "description": "PRISMA-compatible comprehensive export",
        "outputs": ["Evidence summary (JSON)", "BibTeX references", "Beliefs (JSONL)", "Sources (JSONL)", "Verification checklist"],
        "best_for": "Systematic reviewers, meta-analysts"
    },
    "data_pipeline": {
        "name": "Data Pipeline",
        "icon": "⚙️",
        "description": "Machine-readable formats for integration",
        "outputs": ["Beliefs (JSONL)", "Sources (JSONL)", "Manifest (JSON)"],
        "best_for": "Data scientists, developers"
    },
    "presentation": {
        "name": "Presentation",
        "icon": "📊",
        "description": "Visual summaries for slides and reports",
        "outputs": ["Evidence summary (Markdown)", "Key findings", "Visual export (coming soon)"],
        "best_for": "Presentations, stakeholder communication"
    }
}


def render_purpose_selection():
    """Render export purpose selection cards."""
    st.markdown("### Select Export Purpose")
    st.caption("Choose the format that best fits your needs")

    cols = st.columns(len(EXPORT_PURPOSES))

    for idx, (purpose_id, purpose) in enumerate(EXPORT_PURPOSES.items()):
        with cols[idx]:
            is_selected = st.session_state.export_purpose == purpose_id

            st.markdown(f"#### {purpose['icon']} {purpose['name']}")
            st.caption(purpose['description'])

            if st.button(
                "Selected ✓" if is_selected else "Select",
                key=f"purpose_{purpose_id}",
                type="primary" if is_selected else "secondary",
                use_container_width=True
            ):
                st.session_state.export_purpose = purpose_id
                st.rerun()


def render_topic_input():
    """Render topic/query input for export."""
    st.markdown("### What to Export")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.session_state.export_topic = st.text_input(
            "Topic or Query",
            value=st.session_state.export_topic,
            placeholder="e.g., 'plants and stress reduction' or 'biophilic design in hospitals'"
        )

    with col2:
        st.markdown("")  # Spacing
        st.markdown("")
        if st.button("🔍 Preview", use_container_width=True):
            st.session_state.preview_requested = True


def render_export_options():
    """Render additional export options."""
    purpose = EXPORT_PURPOSES[st.session_state.export_purpose]

    st.markdown("### Export Options")

    col1, col2, col3 = st.columns(3)

    with col1:
        include_scope = st.checkbox("Include scope conditions", value=True)
        include_caveats = st.checkbox("Include caveats", value=True)

    with col2:
        include_sources = st.checkbox("Include source papers", value=True)
        include_checklist = st.checkbox("Include verification checklist", value=True)

    with col3:
        max_beliefs = st.slider("Maximum beliefs", 10, 100, 50)
        min_credence = st.slider("Minimum credence", 0.0, 1.0, 0.3, 0.05)

    return {
        "include_scope": include_scope,
        "include_caveats": include_caveats,
        "include_sources": include_sources,
        "include_checklist": include_checklist,
        "max_beliefs": max_beliefs,
        "min_credence": min_credence
    }


def generate_sample_export(topic: str, purpose: str, options: Dict) -> Dict[str, str]:
    """Generate sample export content (demo data)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Evidence summary (Markdown)
    summary_md = f"""# Evidence Summary: {topic}
*Generated: {timestamp}*

## Key Finding
Plants are associated with stress reduction in indoor environments (credence: 0.72 ± 0.12)

**Confidence**: Moderate

## Methods and Stimuli

**Research Methods**: RCT, Quasi-experimental, Observational, Self-report, Physiological
**Stimuli/Interventions**: Indoor plants, Window views, Natural light

## Scope Conditions

- **Population**: Office workers, primarily Western countries
- **Setting**: Indoor office environments, some hospital studies
- **Methodology**: Self-report surveys (majority), cortisol measurements (subset)
- **Limitations**: Limited long-term studies, cultural variations understudied

## Supporting Evidence

1. [ACCEPTED] Natural environments restore directed attention capacity (0.85)
   - Sources: Kaplan & Kaplan 1989, Berman et al. 2008
2. [ACCEPTED] Plants in offices reduce self-reported stress by 15-25% (0.72)
   - Sources: Lohr et al. 1996, Bringslimark et al. 2007
3. [CONTESTED] Window views to nature improve patient recovery (0.65)
   - Sources: Ulrich 1984 (contested sample size)

## Contradicting Evidence

- Artificial plants may provide similar benefits in some contexts (weak evidence)
- Effect sizes vary significantly across studies

## Practical Implications

- Minimum 1 plant per 10m² workspace recommended
- Visible greenery more effective than hidden plants
- Real plants preferred over artificial for stress outcomes
- Window views to nature complement indoor plants

## What Could Defeat This

- Findings may not replicate in non-Western populations
- Long-term effects unstudied
- 3 findings are contested and may be revised

---
*Based on 24 source studies*
*Export purpose: {EXPORT_PURPOSES[purpose]['name']}*
"""

    # BibTeX
    bibtex = """@article{kaplan1989,
  author = {Kaplan, Rachel and Kaplan, Stephen},
  title = {{The Experience of Nature: A Psychological Perspective}},
  year = {1989},
  publisher = {Cambridge University Press},
}

@article{ulrich1984,
  author = {Ulrich, Roger S.},
  title = {{View Through a Window May Influence Recovery from Surgery}},
  journal = {Science},
  year = {1984},
  volume = {224},
  pages = {420--421},
  doi = {10.1126/science.6143402},
}

@article{lohr1996,
  author = {Lohr, Virginia I. and Pearson-Mims, Caroline H. and Goodwin, Georgia K.},
  title = {{Interior Plants May Improve Worker Productivity and Reduce Stress in a Windowless Environment}},
  journal = {Journal of Environmental Horticulture},
  year = {1996},
  volume = {14},
  pages = {97--100},
}

@article{bringslimark2007,
  author = {Bringslimark, Tina and Hartig, Terry and Patil, Grete G.},
  title = {{Psychological Benefits of Indoor Plants in Workplaces}},
  journal = {HortScience},
  year = {2007},
  volume = {42},
  pages = {581--587},
}
"""

    # Verification checklist
    checklist_md = f"""# Verification Checklist: {topic}
*Generated: {timestamp}*

**Status**: 4/5 items verified

## Verification Items

- [✓] **Scope conditions reviewed** (Scope)
  - 3/3 beliefs have scope conditions

- [✓] **Contradicting evidence acknowledged** (Evidence)
  - 0 rejected, 1 contested

- [☐] **Confidence levels appropriate** (Confidence)
  - 1 belief may have inflated confidence

- [✓] **Citations complete** (Citations)
  - 3/3 beliefs have citations

- [✓] **Source papers included** (Sources)
  - 4 source papers

## Warnings

⚠️ 1 belief may have inflated confidence relative to evidence
⚠️ 1 finding is contested between communities
"""

    # JSONL (for data pipeline)
    beliefs_jsonl = """{"id": "B001", "content": "Natural environments restore directed attention capacity", "credence": 0.85, "status": "ACCEPTED", "level": "THEORETICAL", "theory": "ART"}
{"id": "B002", "content": "Plants in offices reduce self-reported stress by 15-25%", "credence": 0.72, "status": "ACCEPTED", "level": "EMPIRICAL", "theory": "Biophilia"}
{"id": "B003", "content": "Window views to nature improve patient recovery", "credence": 0.65, "status": "CONTESTED", "level": "EMPIRICAL", "theory": "SRT"}"""

    # Manifest
    manifest = {
        "topic": topic,
        "generated_at": timestamp,
        "purpose": purpose,
        "belief_count": 3,
        "source_count": 4,
        "format_version": "1.0",
        "generator": "Article Eater V23.0.0"
    }

    # Article Metadata Table (complete table format)
    article_table_md = f"""# Article Metadata Table
*Generated: {timestamp}*

## Study Characteristics

| Citation | Year | Type | N | Population | Setting | Intervention |
|----------|------|------|---|------------|---------|--------------|
| Ulrich (1984) | 1984 | RCT | 46 | Post-surgery patients | Hospital | Window view to trees vs brick wall |
| Kaplan & Kaplan (1989) | 1989 | Observational | 200+ | General population | Various | Natural environments |
| Lohr et al. (1996) | 1996 | RCT | 96 | Office workers | Windowless lab | Indoor plants vs no plants |
| Bringslimark et al. (2007) | 2007 | Meta-analysis | k=21 | Office workers | Indoor offices | Plants and greenery |

## Methods and Design

| Citation | Randomization | Blinding | Control | Duration | Follow-up |
|----------|---------------|----------|---------|----------|-----------|
| Ulrich (1984) | True | Single-blind | Brick wall view | Recovery period | Until discharge |
| Kaplan & Kaplan (1989) | None | Open | Comparison groups | Cross-sectional | None |
| Lohr et al. (1996) | True | Single-blind | No plants | 1 hour task | Immediate |
| Bringslimark et al. (2007) | N/A | N/A | Various | Varied | Varied |

## Outcomes and Results

| Citation | Primary Outcome | Effect Size | 95% CI | p-value | Quality |
|----------|-----------------|-------------|--------|---------|---------|
| Ulrich (1984) | Hospital stay (days) | -0.74 (d) | [-1.20, -0.28] | 0.020 | Some concerns |
| Kaplan & Kaplan (1989) | Attention restoration | N/A | N/A | N/A | Low |
| Lohr et al. (1996) | Self-reported stress | 0.52 (d) | [0.11, 0.93] | 0.014 | Low |
| Bringslimark et al. (2007) | Stress reduction | 0.45 (d) | [0.28, 0.62] | <.001 | Some concerns |

## Key Findings

### Ulrich (1984)
- Patients with tree views had shorter hospital stays (7.96 vs 8.70 days)
- Required fewer strong analgesics
- Had fewer negative evaluative comments in nurses' notes

### Kaplan & Kaplan (1989)
- Natural environments provide "soft fascination" that allows attention to rest
- Directed attention can be fatigued and restored through nature exposure
- Framework established for Attention Restoration Theory (ART)

### Lohr et al. (1996)
- Participants in plant-present condition reported lower stress
- Blood pressure was lower in plant condition
- Productivity was 12% higher with plants

### Bringslimark et al. (2007)
- Meta-analysis of 21 studies confirms benefits of indoor plants
- Effects consistent across different plant types and densities
- Larger effects for stress outcomes than productivity

---
*4 articles included*
"""

    return {
        "summary.md": summary_md,
        "article_table.md": article_table_md,
        "references.bib": bibtex,
        "checklist.md": checklist_md,
        "beliefs.jsonl": beliefs_jsonl,
        "manifest.json": json.dumps(manifest, indent=2)
    }


def render_export_preview(exports: Dict[str, str]):
    """Render preview of export content."""
    st.markdown("### Export Preview")

    # Create tabs for each export file
    tab_names = list(exports.keys())
    tabs = st.tabs(tab_names)

    for idx, (filename, content) in enumerate(exports.items()):
        with tabs[idx]:
            if filename.endswith(".md"):
                st.markdown(content)
            elif filename.endswith(".json"):
                st.code(content, language="json")
            elif filename.endswith(".bib"):
                st.code(content, language="bibtex")
            elif filename.endswith(".jsonl"):
                st.code(content, language="json")
            else:
                st.text(content)


def render_download_buttons(exports: Dict[str, str]):
    """Render download buttons for each export file."""
    st.markdown("### Download Files")

    # Group files by type
    md_files = {k: v for k, v in exports.items() if k.endswith('.md')}
    other_files = {k: v for k, v in exports.items() if not k.endswith('.md')}

    # Markdown files with format options
    if md_files:
        st.markdown("#### Documents")
        for filename, content in md_files.items():
            col1, col2, col3 = st.columns(3)
            base_name = filename.rsplit('.', 1)[0]

            with col1:
                st.download_button(
                    f"{base_name}.md",
                    data=content,
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True
                )

            with col2:
                # DOCX option (note: requires python-docx)
                st.download_button(
                    f"{base_name}.docx",
                    data=content,  # Would be converted with export_to_docx
                    file_name=f"{base_name}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    disabled=True,
                    help="Requires python-docx library"
                )

            with col3:
                # PDF option (note: requires reportlab)
                st.download_button(
                    f"{base_name}.pdf",
                    data=content,  # Would be converted with export_to_pdf
                    file_name=f"{base_name}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    disabled=True,
                    help="Requires reportlab library"
                )

    # Other files
    if other_files:
        st.markdown("#### Data Files")
        cols = st.columns(min(len(other_files), 4))

        for idx, (filename, content) in enumerate(other_files.items()):
            with cols[idx % 4]:
                if filename.endswith(".json") or filename.endswith(".jsonl"):
                    mime = "application/json"
                elif filename.endswith(".bib"):
                    mime = "application/x-bibtex"
                elif filename.endswith(".csv"):
                    mime = "text/csv"
                else:
                    mime = "text/plain"

                st.download_button(
                    filename,
                    data=content,
                    file_name=filename,
                    mime=mime,
                    use_container_width=True
                )

    # Bundle download
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Download All as ZIP", use_container_width=True, type="primary"):
            st.info("ZIP bundle generation coming soon!")
    with col2:
        st.caption("Install python-docx and reportlab for DOCX/PDF export")


def main():
    """Main export page."""
    apply_shared_styles()
    init_session_state()

    st.title("Export Evidence")
    st.caption("Generate publication-ready exports with verification checklists")

    # Purpose selection
    render_purpose_selection()

    st.markdown("---")

    # Show selected purpose details
    purpose = EXPORT_PURPOSES[st.session_state.export_purpose]
    st.info(f"**{purpose['icon']} {purpose['name']}**: {purpose['description']}\n\n**Best for**: {purpose['best_for']}\n\n**Outputs**: {', '.join(purpose['outputs'])}")

    st.markdown("---")

    # Topic input
    render_topic_input()

    # Export options
    options = render_export_options()

    st.markdown("---")

    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate Export", type="primary", use_container_width=True):
            if st.session_state.export_topic:
                with st.spinner("Generating export..."):
                    exports = generate_sample_export(
                        st.session_state.export_topic,
                        st.session_state.export_purpose,
                        options
                    )
                    st.session_state.generated_export = exports
            else:
                st.warning("Please enter a topic or query")

    # Preview and download
    if st.session_state.generated_export:
        st.markdown("---")
        render_export_preview(st.session_state.generated_export)
        st.markdown("---")
        render_download_buttons(st.session_state.generated_export)


if __name__ == "__main__":
    main()
