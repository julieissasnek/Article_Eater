"""
Topic Page — Wikipedia-style Article View
==========================================

Renders a single template, molecule, or MASTER_DOC section as a
comprehensive article with:
- Sidebar infobox (confidence, bridge warrant, domain, panel)
- Progressive disclosure (overview → mechanism → evidence)
- Hot references (click DOI → paper summary + extraction data)
- Argumentation (critiques, evidence hierarchy, debates)
- Mechanism chain as visual diagram
- Related topics grid
"""

import json
import streamlit as st
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from topic_index import (
    get_index,
    DOMAIN_CONFIG,
    BRIDGE_WARRANT_LABELS,
    TemplateData,
    MoleculeData,
)

st.set_page_config(
    page_title="CMR Topic",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ──
st.markdown("""
<style>
    .main { background-color: #FFF9F0; }
    .stApp { background-color: #FFF9F0; }
    
    /* Infobox */
    .infobox {
        background: #F8F9FA;
        border: 1px solid #DEE2E6;
        border-radius: 10px;
        padding: 16px;
        font-size: 0.9em;
    }
    .infobox-title {
        text-align: center;
        font-weight: 700;
        color: #2C3E50;
        font-size: 1.1em;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 2px solid #5B8FB9;
    }
    .infobox-row {
        display: flex;
        justify-content: space-between;
        padding: 4px 0;
        border-bottom: 1px solid #EEE;
    }
    .infobox-label { color: #7F8C8D; font-weight: 500; }
    .infobox-value { color: #2C3E50; font-weight: 600; text-align: right; }
    
    /* Confidence badge */
    .conf-high { background: #D5F5E3; color: #196F3D; padding: 3px 10px; border-radius: 4px; font-weight: 600; }
    .conf-med { background: #FEF9E7; color: #7D6608; padding: 3px 10px; border-radius: 4px; font-weight: 600; }
    .conf-low { background: #FADBD8; color: #922B21; padding: 3px 10px; border-radius: 4px; font-weight: 600; }
    
    /* Hot reference */
    .ref-card {
        background: white;
        border: 1px solid #E8E8E8;
        border-radius: 8px;
        padding: 12px;
        margin: 6px 0;
        transition: all 0.2s;
    }
    .ref-card:hover { border-color: #5B8FB9; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
    .ref-doi { color: #2980B9; font-size: 0.8em; }
    .ref-cites { color: #95A5A6; font-size: 0.8em; }
    
    /* Argument card */
    .arg-card {
        background: #FDF2E9;
        border-left: 3px solid #E67E22;
        border-radius: 6px;
        padding: 12px;
        margin: 6px 0;
        font-size: 0.9em;
    }
    
    /* Breadcrumb */
    .breadcrumb {
        color: #95A5A6;
        font-size: 0.85em;
        margin-bottom: 8px;
    }
    .breadcrumb a { color: #5B8FB9; text-decoration: none; }
    
    /* Section expander styling */
    .stExpander { border: 1px solid #E8E8E8 !important; border-radius: 8px !important; }
    
    /* Related topic card */
    .related-card {
        background: white;
        border: 1px solid #E8E8E8;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        transition: all 0.2s;
    }
    .related-card:hover { border-color: #5B8FB9; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)


def confidence_badge(conf: float) -> str:
    if conf is None:
        return ""
    cls = "conf-high" if conf >= 0.5 else ("conf-med" if conf >= 0.35 else "conf-low")
    return f'<span class="{cls}">⭐ {conf:.2f}</span>'


def render_breadcrumb(parts: list):
    """Render breadcrumb navigation."""
    crumbs = ' → '.join(parts)
    st.markdown(f'<div class="breadcrumb">🏠 Knowledge Base → {crumbs}</div>', unsafe_allow_html=True)


def render_infobox(t: TemplateData, domain: str = None):
    """Render the Wikipedia-style sidebar infobox."""
    cfg = DOMAIN_CONFIG.get(domain, {}) if domain else {}
    bw = BRIDGE_WARRANT_LABELS.get(t.bridge_warrant, ("", 0, ""))
    
    rows = [
        ("Template ID", t.display_id),
        ("Full ID", t.template_id[:35] + "..." if len(t.template_id) > 35 else t.template_id),
        ("Panel", t.panel),
        ("Status", t.status.title() if t.status else "—"),
        ("Maturity", t.maturity.title() if t.maturity else "—"),
        ("Domain", f"{cfg.get('emoji', '')} {cfg.get('label', domain or '—')}"),
        ("Confidence", f'{confidence_badge(t.confidence)}'),
        ("Bridge Warrant", f"{bw[0]} {t.bridge_warrant or '—'}"),
        ("Bridge Prior", f"{t.bridge_prior:.2f}" if t.bridge_prior else "—"),
    ]
    
    if t.t1_frameworks:
        rows.append(("T1 Frameworks", ", ".join(t.t1_frameworks[:4])))
    
    if t.t1_5_parent_theories:
        theories = t.t1_5_parent_theories
        if isinstance(theories, list):
            rows.append(("T1.5 Theories", ", ".join(str(th) for th in theories[:3])))
        elif isinstance(theories, str):
            rows.append(("T1.5 Theories", theories))
    
    html = '<div class="infobox">'
    html += f'<div class="infobox-title">{t.display_id}: {t.name[:40]}</div>'
    for label, value in rows:
        html += f'<div class="infobox-row"><span class="infobox-label">{label}</span>'
        html += f'<span class="infobox-value">{value}</span></div>'
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)


def render_mechanism_chain(t: TemplateData):
    """Render the mechanism chain as a visual flow."""
    if not t.mechanism_chain:
        return
    
    st.markdown("### ⛓️ Mechanism Chain")
    
    # Build mermaid diagram
    chain = t.mechanism_chain
    if len(chain) >= 2:
        mermaid = "graph LR\n"
        for i in range(len(chain) - 1):
            step_a = str(chain[i])[:50].replace('"', "'")
            step_b = str(chain[i + 1])[:50].replace('"', "'")
            mermaid += f'    S{i}["{step_a}"] --> S{i+1}["{step_b}"]\n'
        
        # Style
        mermaid += "    classDef default fill:#EBF5FB,stroke:#2980B9,color:#2C3E50\n"
        mermaid += f"    classDef endpoint fill:#D5F5E3,stroke:#27AE60,color:#196F3D\n"
        mermaid += f"    class S0 endpoint\n    class S{len(chain)-1} endpoint\n"
        
        try:
            st.markdown(f"```mermaid\n{mermaid}\n```")
        except Exception:
            pass
    
    # Also show as text list
    with st.expander("View as text chain", expanded=False):
        for i, step in enumerate(chain):
            arrow = "→ " if i > 0 else "▶ "
            st.markdown(f"**{arrow}** {step}")


def render_parameters(t: TemplateData):
    """Render calibrated parameters and population modifiers."""
    has_params = bool(t.calibrated_parameters)
    has_mods = bool(t.population_modifiers)
    
    if not has_params and not has_mods:
        return
    
    with st.expander("📏 Calibrated Parameters & Population Modifiers", expanded=False):
        if has_params:
            st.markdown("#### Parameters")
            param_data = []
            for k, v in t.calibrated_parameters.items():
                if isinstance(v, dict):
                    val = v.get("value", v.get("estimate", str(v)))
                    unit = v.get("unit", "")
                    note = v.get("note", v.get("theoretical_default", ""))
                    param_data.append({"Parameter": k, "Value": str(val), "Unit": unit, "Note": str(note)[:80]})
                else:
                    param_data.append({"Parameter": k, "Value": str(v), "Unit": "", "Note": ""})
            
            if param_data:
                st.dataframe(param_data, use_container_width=True, hide_index=True)
        
        if has_mods:
            st.markdown("#### Population Modifiers")
            mod_data = []
            for k, v in t.population_modifiers.items():
                if isinstance(v, dict):
                    val = v.get("value", v.get("modifier", str(v)))
                    note = v.get("note", "")
                    mod_data.append({"Modifier": k, "Value": str(val), "Note": str(note)[:80]})
                else:
                    mod_data.append({"Modifier": k, "Value": str(v), "Note": ""})
            
            if mod_data:
                st.dataframe(mod_data, use_container_width=True, hide_index=True)


def render_hot_reference(doi_or_ref, idx):
    """Render a single hot reference with expandable paper summary."""
    index = get_index()
    
    # Extract DOI from various formats
    doi = None
    citation_text = ""
    if isinstance(doi_or_ref, str):
        doi = doi_or_ref
        citation_text = doi
    elif isinstance(doi_or_ref, dict):
        doi = doi_or_ref.get("doi", "")
        citation_text = doi_or_ref.get("citation", doi_or_ref.get("title", doi or ""))
    
    if not doi:
        st.markdown(f"• {citation_text}")
        return
    
    # Look up paper in our index
    paper = index.get_paper(doi)
    
    if paper:
        title = paper.get("title", "")[:80]
        year = paper.get("year", "?")
        authors = ", ".join(paper.get("authors", [])[:3])
        journal = paper.get("journal", "")
        cites = paper.get("citation_count") or 0
        
        st.markdown(f"""
        <div class="ref-card">
            <div style="font-weight: 600; color: #2C3E50;">{title}</div>
            <div style="color: #555; font-size: 0.85em;">{authors} ({year}) · {journal}</div>
            <div>
                <span class="ref-doi">🔗 {doi}</span>
                <span class="ref-cites">📊 {cites:,} citations</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Expandable detail from extraction data
        with st.expander(f"📄 View extraction data for {doi[:30]}...", expanded=False):
            # Try to load the full extraction file
            ext_path = Path(PROJECT_ROOT) / "data" / "extractions" / f"{doi.replace('/', '_')}.json"
            if ext_path.exists():
                try:
                    ext_data = json.loads(ext_path.read_text())
                    
                    # Paper metadata
                    pm = ext_data.get("paper_metadata", {})
                    if pm.get("abstract"):
                        st.markdown("**Abstract:**")
                        st.markdown(f"> {pm['abstract'][:500]}")
                    
                    # Extracted claims/findings
                    claims = ext_data.get("claims", ext_data.get("findings", []))
                    if claims and isinstance(claims, list):
                        st.markdown(f"**Key Findings ({len(claims)} extracted):**")
                        for c in claims[:5]:
                            if isinstance(c, dict):
                                text = c.get("text", c.get("claim", str(c)))
                                st.markdown(f"• {str(text)[:200]}")
                            else:
                                st.markdown(f"• {str(c)[:200]}")
                    
                    # Tables/evidence rows
                    tables = ext_data.get("tables", ext_data.get("evidence_rows", []))
                    if tables:
                        st.markdown(f"**Evidence Data ({len(tables)} entries):**")
                        if isinstance(tables, list) and len(tables) > 0:
                            if isinstance(tables[0], dict):
                                st.dataframe(tables[:10], use_container_width=True, hide_index=True)
                    
                    # Template links
                    links = ext_data.get("template_links", ext_data.get("mechanism_claims", []))
                    if links:
                        st.markdown(f"**Template Links ({len(links)}):**")
                        for l in links[:5]:
                            if isinstance(l, dict):
                                st.markdown(f"• {l.get('template_id', '')} — {l.get('mechanism', str(l))[:100]}")
                    
                except Exception:
                    st.info("Extraction data not parseable.")
            else:
                st.info(f"No extraction file found for {doi}")
                st.markdown(f"[View on CrossRef](https://doi.org/{doi})")
    else:
        # No paper in our index — still show the reference
        st.markdown(f"""
        <div class="ref-card">
            <div style="color: #2C3E50;">{citation_text}</div>
            <div><span class="ref-doi">🔗 <a href="https://doi.org/{doi}" target="_blank">{doi}</a></span></div>
        </div>
        """, unsafe_allow_html=True)


def render_argumentation(t: TemplateData):
    """Render argumentation content — critiques, debates, evidence hierarchy."""
    st.markdown("### 🔍 Arguments & Critiques")
    
    # Try to load critique data
    try:
        from src.argument.critique_aggregator import CritiqueAggregator
        aggregator = CritiqueAggregator()
        collection = aggregator.collect_critiques(
            target_id=t.template_id,
            target_type="template",
        )
        if collection and collection.total_critique_count > 0:
            st.markdown(f"**{collection.total_critique_count} critiques found** "
                       f"(severity: {collection.weighted_critique_severity:.2f})")
            
            critique_types = [
                ("Method", collection.method_critiques),
                ("Stimulus", collection.stimulus_critiques),
                ("Population", collection.population_critiques),
                ("Assumption", collection.assumption_critiques),
                ("Interpretation", collection.interpretation_critiques),
                ("Statistical", collection.statistical_critiques),
            ]
            
            for ctype, critiques in critique_types:
                if critiques:
                    with st.expander(f"⚠️ {ctype} Critiques ({len(critiques)})", expanded=False):
                        for c in critiques:
                            d = c.to_dict() if hasattr(c, 'to_dict') else {}
                            st.markdown(f"""
                            <div class="arg-card">
                                <strong>{d.get('critique_type', ctype)}</strong>: {d.get('description', str(c))[:200]}
                                <div style="color: #95A5A6; font-size: 0.8em;">
                                    Severity: {d.get('severity', '?')} · 
                                    Status: {d.get('resolution_status', 'unresolved')}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info(
                "No critiques catalogued for this template yet. "
                "This typically means the template has not been through "
                "formal panel review or the critique database is empty."
            )
    except Exception:
        # Argumentation system not available — show what we know from template data
        st.markdown("""
        <div class="arg-card">
            <strong>Bridge Warrant Analysis</strong><br>
            The bridge warrant determines how confidently laboratory findings 
            transfer to architectural conditions. This template's warrant constrains 
            the maximum confidence score.
        </div>
        """, unsafe_allow_html=True)
        
        # Show bridge warrant commentary
        bw = t.bridge_warrant
        if bw and bw in BRIDGE_WARRANT_LABELS:
            emoji, prior, desc = BRIDGE_WARRANT_LABELS[bw]
            st.markdown(f"**{emoji} {bw}** (prior: {prior}) — {desc}")
            
            if bw == "ANALOGICAL":
                st.warning(
                    "⚠️ **ANALOGICAL** warrant is the weakest bridge type. "
                    "This claim rests on structural analogy alone — it should be "
                    "treated as a hypothesis for investigation, not a design recommendation."
                )
            elif bw == "CONSTITUTIVE":
                st.success(
                    "✅ **CONSTITUTIVE** warrant — the architectural feature "
                    "literally IS the mechanism. The lab-to-architecture transfer "
                    "gap is minimal."
                )
        
        # Check confidence vs bridge ceiling
        if t.confidence and t.bridge_prior:
            if t.confidence > t.bridge_prior + 0.1:
                st.error(
                    f"🚩 **Ceiling violation detected**: Confidence ({t.confidence:.2f}) "
                    f"exceeds bridge ceiling ({t.bridge_prior:.2f}). "
                    f"This warrants review per §52 red-flag protocol."
                )


def render_design_implications(t: TemplateData):
    """Render building types and architectural modifiers."""
    has_bt = bool(t.building_types)
    has_am = bool(t.architectural_modifiers)
    
    if not has_bt and not has_am:
        return
    
    with st.expander("🏗️ Design Implications", expanded=False):
        if has_bt:
            st.markdown("**Applicable Building Types:**")
            for bt in t.building_types:
                if isinstance(bt, dict):
                    st.markdown(f"• **{bt.get('type', bt.get('name', str(bt)))}** — {bt.get('note', '')}")
                else:
                    st.markdown(f"• {bt}")
        
        if has_am:
            st.markdown("**Architectural Modifiers:**")
            for k, v in t.architectural_modifiers.items():
                if isinstance(v, dict):
                    st.markdown(f"• **{k}**: {v.get('value', v)} — {v.get('note', '')}")
                else:
                    st.markdown(f"• **{k}**: {v}")


def render_related_topics(t: TemplateData):
    """Render related topics grid."""
    index = get_index()
    related = index.get_related_templates(t.template_id)
    
    if not related:
        return
    
    st.markdown("### 🔗 Related Topics")
    
    cols = st.columns(min(4, len(related)))
    for i, r in enumerate(related[:8]):
        with cols[i % len(cols)]:
            st.markdown(f"""
            <div class="related-card">
                <div style="font-weight: 600; font-size: 0.9em;">{r.display_id}</div>
                <div style="font-size: 0.8em; color: #555;">{r.name[:40]}</div>
                <div>{confidence_badge(r.confidence)}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View", key=f"rel_{r.display_id}_{i}"):
                st.session_state["topic_id"] = r.display_id
                st.rerun()


def render_master_doc_section(section_num: str):
    """Render a MASTER_DOC section as an article."""
    index = get_index()
    sec = index.get_master_doc_section(section_num)
    
    if not sec:
        st.error(f"Section §{section_num} not found in MASTER_DOC.")
        return
    
    render_breadcrumb([sec.part or "Concepts", f"§{sec.section_num}"])
    
    st.markdown(f"# §{sec.section_num}: {sec.title}")
    
    if sec.executive_summary:
        st.info(sec.executive_summary[:500])
    
    # Render the full content with some cleanup
    content = sec.content
    # Remove the heading line itself (we already rendered it)
    lines = content.split("\n")
    if lines and lines[0].startswith("#"):
        content = "\n".join(lines[1:])
    
    # Render in expandable sections if too long
    if len(content) > 3000:
        preview = content[:2000]
        remainder = content[2000:]
        st.markdown(preview)
        with st.expander("Continue reading...", expanded=False):
            st.markdown(remainder)
    else:
        st.markdown(content)


def render_molecule_page(molecule_id: str):
    """Render a molecule page — groups constituent templates."""
    index = get_index()
    mol = index.get_molecule(molecule_id)
    
    if not mol:
        st.error(f"Molecule '{molecule_id}' not found.")
        return
    
    render_breadcrumb(["Molecules", mol.name])
    
    col_main, col_side = st.columns([3, 1])
    
    with col_main:
        st.markdown(f"# 🧬 {mol.name}")
        st.markdown(mol.short_description)
        
        # QA Cache content (L1/L2/L3)
        qa = index.get_qa_cache(molecule_id)
        if qa:
            l1 = qa.get("l1_summary", "")
            l2 = qa.get("l2_summary", "")
            l3 = qa.get("l3_summary", "")
            
            if l1:
                st.markdown("### Overview")
                if isinstance(l1, dict):
                    l1 = l1.get("text", str(l1))
                st.markdown(str(l1))
            
            if l2:
                with st.expander("📖 Detailed Mechanism", expanded=False):
                    if isinstance(l2, dict):
                        l2 = l2.get("text", str(l2))
                    st.markdown(str(l2))
            
            if l3:
                with st.expander("🔬 Evidence & Statistics", expanded=False):
                    if isinstance(l3, dict):
                        l3 = l3.get("text", str(l3))
                    st.markdown(str(l3))
        else:
            st.info(f"No QA cache available for {mol.name}. "
                    f"Progressive disclosure summaries (L1/L2/L3) have not been generated yet.")
        
        # Constituent templates
        templates = index.get_molecule_templates(molecule_id)
        if templates:
            st.markdown(f"### 📋 Constituent Templates ({len(templates)})")
            for t in sorted(templates, key=lambda t: t.confidence or 0, reverse=True):
                mech = str(t.mechanism_chain[0])[:100] if t.mechanism_chain else ""
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(
                        f"**{t.display_id}: {t.name}** {confidence_badge(t.confidence)}",
                        unsafe_allow_html=True,
                    )
                    st.caption(mech)
                with col2:
                    if st.button("Open", key=f"mt_{t.display_id}"):
                        st.session_state["topic_id"] = t.display_id
                        st.session_state.pop("molecule_id", None)
                        st.rerun()
                st.divider()
    
    with col_side:
        # Molecule infobox
        n_templates = len(mol.constituent_templates)
        frameworks = ", ".join(mol.framework_ids[:4]) if mol.framework_ids else "—"
        
        st.markdown(f"""
        <div class="infobox">
            <div class="infobox-title">🧬 {mol.name}</div>
            <div class="infobox-row">
                <span class="infobox-label">Templates</span>
                <span class="infobox-value">{n_templates}</span>
            </div>
            <div class="infobox-row">
                <span class="infobox-label">Frameworks</span>
                <span class="infobox-value">{frameworks}</span>
            </div>
            <div class="infobox-row">
                <span class="infobox-label">Type</span>
                <span class="infobox-value">{mol.molecule_type or '—'}</span>
            </div>
            <div class="infobox-row">
                <span class="infobox-label">Domain</span>
                <span class="infobox-value">{mol.domain or '—'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_template_page(template_id: str):
    """Render a Wikipedia-style template topic page."""
    index = get_index()
    t = index.get_template(template_id)
    
    if not t:
        st.error(f"Template '{template_id}' not found.")
        return
    
    domain = index._classify_domain(t.template_id)
    cfg = DOMAIN_CONFIG.get(domain, {}) if domain else {}
    
    render_breadcrumb([
        cfg.get("label", domain or "Unclassified"),
        t.panel or "",
        t.display_id,
    ])
    
    col_main, col_side = st.columns([3, 1])
    
    with col_main:
        # Title
        st.markdown(f"# {cfg.get('emoji', '📋')} {t.name}")
        
        # Overview — first mechanism chain step as summary
        if t.mechanism_chain:
            first_step = str(t.mechanism_chain[0])
            st.markdown(f"> {first_step}")
        
        # Check for MASTER_DOC worked example
        sec_num = st.session_state.get("section_num")
        if sec_num:
            sec = index.get_master_doc_section(sec_num)
            if sec:
                with st.expander("📝 Worked Example (from §" + sec_num + ")", expanded=True):
                    # Adapt content for web — shorter, more scannable
                    content = sec.content
                    # Remove the heading
                    lines = content.split("\n")
                    if lines and lines[0].startswith("#"):
                        content = "\n".join(lines[1:])
                    st.markdown(content[:3000])
                    if len(content) > 3000:
                        with st.expander("Continue reading...", expanded=False):
                            st.markdown(content[3000:])
        
        # Mechanism chain diagram
        render_mechanism_chain(t)
        
        # Parameters
        render_parameters(t)
        
        # Argumentation & critiques
        render_argumentation(t)
        
        # Design implications
        render_design_implications(t)
        
        # References — HOT
        if t.key_references:
            st.markdown("### 📚 Key References")
            st.markdown("*Click to expand — shows paper summary, extraction data, and technical details.*")
            for i, ref in enumerate(t.key_references):
                render_hot_reference(ref, i)
        
        # Panel docs
        if t.panel_docs:
            with st.expander("📄 Panel Documentation", expanded=False):
                for doc in t.panel_docs:
                    st.markdown(f"• {doc}")
        
        # Related topics
        render_related_topics(t)
    
    with col_side:
        render_infobox(t, domain)
        
        # Quick links
        st.markdown("---")
        st.markdown("**Quick Links:**")
        if st.button("🏠 Back to Browse", use_container_width=True):
            st.session_state.pop("topic_id", None)
            st.session_state.pop("section_num", None)
            st.switch_page("pages/9_knowledge_base.py")


# ── Main ──

def main():
    # Navigation back button
    if st.button("← Knowledge Base"):
        st.session_state.pop("topic_id", None)
        st.session_state.pop("molecule_id", None)
        st.session_state.pop("section_num", None)
        st.switch_page("pages/9_knowledge_base.py")
    
    # Route to appropriate view
    topic_id = st.session_state.get("topic_id")
    molecule_id = st.session_state.get("molecule_id")
    section_num = st.session_state.get("section_num")
    
    # Also check query params
    if not topic_id and not molecule_id and not section_num:
        params = st.query_params
        topic_id = params.get("topic")
        molecule_id = params.get("molecule")
        section_num = params.get("section")
    
    if topic_id:
        render_template_page(topic_id)
    elif molecule_id:
        render_molecule_page(molecule_id)
    elif section_num:
        render_master_doc_section(section_num)
    else:
        st.info("Select a topic from the Knowledge Base home page.")
        if st.button("Go to Knowledge Base →"):
            st.switch_page("pages/9_knowledge_base.py")


if __name__ == "__page__":
    main()

main()
