"""
Knowledge Base — Home Page
==========================

Main entry point for the QA Browse System. Features:
- Full-text search across templates, molecules, sections, papers
- Domain browse grid with color-coded cards
- Theme browse (molecules) with popovers
- Featured topics (highest-confidence templates, worked examples)
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from topic_index import get_index, DOMAIN_CONFIG, BRIDGE_WARRANT_LABELS

st.set_page_config(
    page_title="CMR Knowledge Base",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──
st.markdown("""
<style>
    /* Warm cream base */
    .main { background-color: #FFF9F0; }
    .stApp { background-color: #FFF9F0; }
    
    /* Typography */
    h1 { color: #2C3E50; font-weight: 700; }
    h2 { color: #34495E; font-weight: 600; }
    h3 { color: #5B8FB9; font-weight: 600; }
    
    /* Domain cards */
    .domain-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid;
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
        min-height: 120px;
    }
    .domain-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }
    .domain-emoji { font-size: 2em; margin-bottom: 8px; }
    .domain-title { font-weight: 600; color: #2C3E50; font-size: 1.1em; }
    .domain-count { color: #7F8C8D; font-size: 0.9em; }
    
    /* Search results */
    .search-result {
        background: white;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
        border-left: 3px solid;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .search-type { 
        font-size: 0.7em; 
        text-transform: uppercase; 
        letter-spacing: 1px;
        padding: 2px 6px;
        border-radius: 3px;
        background: #EBF5FB;
        color: #2980B9;
    }
    
    /* Confidence badge */
    .conf-high { background: #D5F5E3; color: #196F3D; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }
    .conf-med { background: #FEF9E7; color: #7D6608; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }
    .conf-low { background: #FADBD8; color: #922B21; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }
    
    /* Molecule card */
    .mol-card {
        background: white;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        border: 1px solid #E8E8E8;
        transition: all 0.2s;
        height: 100%;
    }
    .mol-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.10);
        border-color: #5B8FB9;
    }
    
    /* Featured section */
    .featured-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.25);
    }
    .featured-card h4 { color: white !important; margin-bottom: 8px; }
    .featured-card p { color: rgba(255,255,255,0.85); }
    
    /* Stats bar */
    .stat-pill {
        background: #EBF5FB;
        border-radius: 20px;
        padding: 6px 14px;
        display: inline-block;
        margin: 4px;
        font-size: 0.85em;
        color: #2C3E50;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)


def confidence_badge(conf: float) -> str:
    """Return HTML for a confidence badge."""
    if conf is None:
        return ""
    if conf >= 0.5:
        cls = "conf-high"
    elif conf >= 0.35:
        cls = "conf-med"
    else:
        cls = "conf-low"
    return f'<span class="{cls}">⭐ {conf:.2f}</span>'


def render_header():
    """Render the page header with stats."""
    idx = get_index()
    stats = idx.get_stats()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 🧠 CMR Knowledge Base")
        st.markdown(
            "*From Correlation to Mechanism: Neural Explanations for "
            "Architecture-Behavior Relationships*"
        )
    with col2:
        st.markdown(f"""
        <div style="text-align: right; padding-top: 10px;">
            <span class="stat-pill">📋 {stats['templates']} Templates</span>
            <span class="stat-pill">🧬 {stats['molecules']} Molecules</span>
            <span class="stat-pill">📄 {stats['papers']} Papers</span>
            <span class="stat-pill">🔗 {stats['citation_edges']} Citations</span>
        </div>
        """, unsafe_allow_html=True)


def render_search():
    """Render the search interface."""
    idx = get_index()
    
    query = st.text_input(
        "🔍 Search topics, mechanisms, theories, papers...",
        placeholder="Try: biophilia, prediction error, circadian, thermal comfort, Ulrich 1984...",
        key="kb_search",
        label_visibility="collapsed",
    )
    
    if query and len(query) >= 2:
        results = idx.search(query, limit=15)
        
        if not results:
            st.info(f"No results for '{query}'. Try broader terms.")
            return
        
        st.markdown(f"**{len(results)} results** for *{query}*")
        
        type_icons = {
            "template": "📋", "molecule": "🧬",
            "section": "📖", "paper": "📄",
        }
        type_colors = {
            "template": "#3498DB", "molecule": "#27AE60",
            "section": "#8E44AD", "paper": "#E67E22",
        }
        
        for r in results:
            icon = type_icons.get(r.result_type, "•")
            color = type_colors.get(r.result_type, "#999")
            conf = confidence_badge(r.confidence) if r.confidence else ""
            
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    f'<div class="search-result" style="border-color: {color};">'
                    f'<span class="search-type">{icon} {r.result_type}</span> '
                    f'**{r.title}** {conf}<br>'
                    f'<span style="color: #666; font-size: 0.9em;">{r.snippet}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col2:
                if r.result_type == "template":
                    if st.button("View →", key=f"sr_{r.id}", use_container_width=True):
                        st.session_state["topic_id"] = r.id
                        st.switch_page("pages/10_topic.py")
                elif r.result_type == "molecule":
                    if st.button("View →", key=f"sr_{r.id}", use_container_width=True):
                        st.session_state["molecule_id"] = r.id
                        st.switch_page("pages/10_topic.py")


def render_domain_grid():
    """Render the domain browse grid."""
    idx = get_index()
    stats = idx.get_stats()
    domain_counts = stats.get("domains", {})
    
    st.markdown("## Browse by Domain")
    st.markdown("*Each domain groups templates by the sensory modality or architectural concern they address.*")
    
    # Arrange domains in a 4-column grid
    domains_to_show = [
        ("visual", "Prediction error, fractal scaling, complexity, views"),
        ("auditory", "Soundscapes, music emotion, reverberation, acoustics"),
        ("thermal", "Adaptive comfort, thermal PE, body budget"),
        ("spatial", "Wayfinding, isovists, prospect-refuge, enclosure"),
        ("circadian", "Daylight, melanopic irradiance, melatonin, sleep"),
        ("haptic", "Surfaces, materials, CT-afferent touch, texture"),
        ("stress", "Allostatic load, neuromodulators, HPA axis, DMN"),
        ("creative", "Incubation, divergent thinking, network dynamics"),
        ("social", "Proxemics, privacy, social affordance, density"),
        ("memory", "Episodic encoding, consolidation, schema"),
        ("multisensory", "Crossmodal, congruence, inverse effectiveness"),
        ("olfactory", "Olfactory PE, scent-space transitions"),
    ]
    
    cols = st.columns(4)
    for i, (domain, desc) in enumerate(domains_to_show):
        cfg = DOMAIN_CONFIG.get(domain, {"emoji": "•", "color": "#999", "label": domain.title()})
        count = domain_counts.get(domain, 0)
        
        with cols[i % 4]:
            st.markdown(f"""
            <div class="domain-card" style="border-color: {cfg['color']};">
                <div class="domain-emoji">{cfg['emoji']}</div>
                <div class="domain-title">{cfg['label']}</div>
                <div class="domain-count">{count} template{'s' if count != 1 else ''}</div>
                <div style="color: #95A5A6; font-size: 0.8em; margin-top: 4px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Explore {cfg['label']}", key=f"dom_{domain}", use_container_width=True):
                st.session_state["browse_domain"] = domain
                st.session_state["browse_mode"] = "domain"


def render_molecule_browse():
    """Render molecule/theme browse with descriptions."""
    idx = get_index()
    
    st.markdown("## Browse by Theme")
    st.markdown("*Molecules group related templates into coherent explanatory units.*")
    
    cols = st.columns(3)
    for i, (mid, mol) in enumerate(sorted(idx.molecules.items(), key=lambda x: x[1].name)):
        n_templates = len(mol.constituent_templates)
        qa = idx.get_qa_cache(mid)
        has_qa = qa is not None
        
        # Get L1 summary if available
        l1 = qa.get("l1_summary", "") if qa else ""
        if isinstance(l1, dict):
            l1 = l1.get("text", str(l1))
        l1_text = str(l1)[:150] if l1 else mol.short_description[:150]
        
        with cols[i % 3]:
            qa_badge = "✅ QA" if has_qa else ""
            st.markdown(f"""
            <div class="mol-card">
                <div style="font-size: 1.2em; font-weight: 600; color: #2C3E50; margin-bottom: 6px;">
                    🧬 {mol.name}
                </div>
                <div style="color: #666; font-size: 0.85em; margin-bottom: 8px;">
                    {l1_text}
                </div>
                <div style="font-size: 0.8em; color: #95A5A6;">
                    {n_templates} templates · {', '.join(mol.framework_ids[:3])} {qa_badge}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open {mol.name}", key=f"mol_{mid}", use_container_width=True):
                st.session_state["molecule_id"] = mid
                st.switch_page("pages/10_topic.py")


def render_featured():
    """Render featured topics — highest confidence and worked examples."""
    idx = get_index()
    
    st.markdown("## Featured Topics")
    
    # Tab layout
    tab1, tab2, tab3 = st.tabs(["🏆 Highest Confidence", "📝 Worked Examples", "🔬 Key Concepts"])
    
    with tab1:
        # Top templates by confidence
        all_templates = [t for tid, t in idx.templates.items() if tid == t.display_id and t.confidence]
        top = sorted(all_templates, key=lambda t: t.confidence or 0, reverse=True)[:8]
        
        cols = st.columns(2)
        for i, t in enumerate(top):
            domain = idx._classify_domain(t.template_id)
            cfg = DOMAIN_CONFIG.get(domain, {"emoji": "•", "color": "#999"})
            mech = str(t.mechanism_chain[0])[:80] if t.mechanism_chain else ""
            
            with cols[i % 2]:
                bw = BRIDGE_WARRANT_LABELS.get(t.bridge_warrant, ("", 0, ""))
                st.markdown(f"""
                <div style="background: white; border-radius: 8px; padding: 14px; margin: 6px 0;
                            border-left: 3px solid {cfg.get('color', '#999')}; 
                            box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600;">{cfg.get('emoji', '')} {t.name[:50]}</span>
                        {confidence_badge(t.confidence)}
                    </div>
                    <div style="color: #666; font-size: 0.85em; margin-top: 4px;">{mech}</div>
                    <div style="color: #95A5A6; font-size: 0.75em; margin-top: 4px;">
                        {t.display_id} · {t.bridge_warrant or '—'} {bw[0]} · {t.panel or ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View", key=f"feat_{t.display_id}", use_container_width=True):
                    st.session_state["topic_id"] = t.display_id
                    st.switch_page("pages/10_topic.py")
    
    with tab2:
        # Worked examples from MASTER_DOC §48
        worked = [
            ("48.6", "VF2", "Visual Rhythm", "0.32", 
             "Does the auditory groove response transfer to visual scanning of facades?"),
            ("48.7", "VIEW1", "Nature View Convergence", "0.55",
             "Five neural channels converge: why hospital windows with nature views reduce stress."),
            ("48.10", "MAT1", "Thermal Adaptive PE", "0.52",
             "How envelope systems maintaining adaptive neutral temperature suppress interoceptive prediction error."),
            ("48.11", "SC1", "Spatial Integration PE", "0.52",
             "Floor-plan connectivity determines cognitive-map fidelity and wayfinding stress."),
            ("48.12", "SOC2", "Privacy-Encounter Curve", "0.62",
             "Balancing amygdala-based privacy needs with hippocampal encounter prediction."),
            ("48.13", "L2", "Circadian Daylighting", "0.62",
             "Melanopic irradiance from windows entrains circadian rhythms and improves sleep."),
            ("48.14", "CREA3", "Incubation Architecture", "0.48",
             "Brief outdoor nature walks produce dose-response creative enhancement."),
        ]
        
        for sec_num, tid, name, composite, description in worked:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"""
                <div style="background: white; border-radius: 8px; padding: 14px; margin: 6px 0;
                            border-left: 3px solid #8E44AD; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
                    <span style="font-weight: 600;">📝 {name}</span>
                    <span class="conf-med">⭐ {composite}</span>
                    <span style="color: #95A5A6; font-size: 0.8em;"> · §{sec_num}</span>
                    <div style="color: #555; font-size: 0.9em; margin-top: 4px;">{description}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("Read →", key=f"ex_{sec_num}", use_container_width=True):
                    st.session_state["topic_id"] = tid
                    st.session_state["section_num"] = sec_num
                    st.switch_page("pages/10_topic.py")
    
    with tab3:
        concepts = [
            ("48", "The Credence Formula", "P(CNFA) = P(parent) × P(bridge) × P(CNFA-specific)"),
            ("49", "Quinean Webs & Bayesian Networks", "Foundherentist epistemology — web is primary, BN is derivative"),
            ("50", "Tiered Theoretical Architecture", "10 T1 frameworks, 14 T1.5 reductions, ~150 T2 templates"),
            ("51", "Bridge Warrants", "6-level hierarchy quantifying lab-to-architecture transfer"),
            ("52", "Confidence Discipline", "Coburn R² ceiling, red-flag scan, ceiling adjudication"),
            ("53", "Independence Assumption", "Why multiplicative structure understates composite credence"),
        ]
        
        for sec_num, title, desc in concepts:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"""
                <div style="background: white; border-radius: 8px; padding: 14px; margin: 6px 0;
                            border-left: 3px solid #16A085; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
                    <span style="font-weight: 600;">📖 §{sec_num}: {title}</span>
                    <div style="color: #555; font-size: 0.9em; margin-top: 4px;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("Read →", key=f"concept_{sec_num}", use_container_width=True):
                    st.session_state["section_num"] = sec_num
                    st.switch_page("pages/10_topic.py")


def render_domain_detail():
    """Render detailed view when a domain is selected."""
    idx = get_index()
    domain = st.session_state.get("browse_domain")
    if not domain:
        return
    
    cfg = DOMAIN_CONFIG.get(domain, {"emoji": "•", "color": "#999", "label": domain})
    templates = idx.get_domain_templates(domain)
    
    if st.button("← Back to Browse"):
        del st.session_state["browse_domain"]
        st.rerun()
    
    st.markdown(f"## {cfg['emoji']} {cfg['label']} Domain")
    st.markdown(f"**{len(templates)} templates** in this domain")
    
    # Sort by confidence
    templates.sort(key=lambda t: t.confidence or 0, reverse=True)
    
    for t in templates:
        mech = str(t.mechanism_chain[0])[:100] if t.mechanism_chain else ""
        bw = BRIDGE_WARRANT_LABELS.get(t.bridge_warrant, ("", 0, ""))
        
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(f"""
            **{t.display_id}: {t.name}**  
            <span style="color: #666; font-size: 0.9em;">{mech}</span>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"{confidence_badge(t.confidence)} {bw[0]}", unsafe_allow_html=True)
        with col3:
            if st.button("View", key=f"d_{t.display_id}"):
                st.session_state["topic_id"] = t.display_id
                st.switch_page("pages/10_topic.py")
        
        st.divider()


# ── Main ──

def main():
    render_header()
    st.divider()
    
    # If a domain is selected, show domain detail
    if st.session_state.get("browse_domain"):
        render_domain_detail()
        return
    
    # Search
    render_search()
    
    # If search is active, don't show browse
    if st.session_state.get("kb_search"):
        return
    
    st.divider()
    
    # Browse grids
    render_domain_grid()
    st.divider()
    render_molecule_browse()
    st.divider()
    render_featured()


if __name__ == "__page__":
    main()

main()
