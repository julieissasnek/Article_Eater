import streamlit as st
import json
import os
from pathlib import Path

# Fix path to allow importing from src
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.qa.router import MoleculeAwareRouter

# --- Config & Initialization ---
st.set_page_config(page_title="Article Eater: QA Engine", page_icon="🧠", layout="wide")

@st.cache_resource
def get_router():
    # Adjusted paths for running from project root
    return MoleculeAwareRouter(molecule_dir="data/molecules", cache_dir="data/qa_cache")

router = get_router()

# --- Custom Styling ---
st.markdown("""
<style>
    .level1-box { background-color: #f0f8ff; padding: 15px; border-radius: 5px; border-left: 5px solid #0052cc; margin-bottom: 20px;}
    .level2-box { background-color: #f5f5f5; padding: 15px; border-radius: 5px; border-left: 5px solid #00a3bf; margin-bottom: 20px;}
    .level3-box { background-color: #fffaf0; padding: 15px; border-radius: 5px; border-left: 5px solid #ff8b00; margin-bottom: 20px;}
    .provenance-card { background-color: #e6ffed; padding: 10px; border-radius: 5px; border: 1px solid #28a745; font-size: 0.9em;}
    .component-tag { background-color: #e1e4e8; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; margin-right: 5px;}
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.title("KB Navigation")

# Get list of pre-computed molecules
molecule_options = {"Select a topic...": None}
for mol_id, mol in router.molecule_registry.items():
    molecule_options[mol.name] = mol_id

selected_mol_name = st.sidebar.selectbox("Molecules (Tier 2 Constructs)", list(molecule_options.keys()))

st.sidebar.markdown("---")
st.sidebar.subheader("Live QA Search")
search_query = st.sidebar.text_input("Ask a custom question...")

# --- Main Area ---
st.title("Web of Belief: QA Engine")

def display_molecule(mol_id: str):
    mol = router.molecule_registry[mol_id]
    
    st.header(mol.name)
    st.markdown(f"**Domain:** {mol.domain} | **Empirical Support:** {mol.empirical_support}")
    
    # Check cache via router
    l1_res = router.route_query(mol.name, requested_depth=1)
    l2_res = router.route_query(mol.name, requested_depth=2)
    l3_res = router.route_query(mol.name, requested_depth=3)
    
    if "error" in l1_res:
         st.warning(f"Cache miss for {mol.name}. Try computing it first.")
         return

    status = l1_res.get("status")
    if status == "STALE":
        st.warning("⚠️ Warning: Underlying PDFs have changed. This cached answer may be out of date until recomputed.")

    # --- Progressive Disclosure UI ---
    
    # Level 1 (Always Visible)
    st.markdown("### Executive Summary")
    st.markdown(f"<div class='level1-box'>{l1_res.get('content', 'Level 1 summary missing.')}</div>", unsafe_allow_html=True)
    
    # Level 2 (Expander)
    with st.expander("Show Contextual Details (Level 2)"):
        st.markdown(f"<div class='level2-box'>{l2_res.get('content', 'Level 2 summary missing.')}</div>", unsafe_allow_html=True)
        
    # Level 3 (Mechanistic Expander)
    with st.expander("Deep Dive: Mechanisms & Components (Level 3)"):
        
        # Display interacting components conceptually
        comp_html = "<strong>Mechanistic Components:</strong> "
        for c in mol.components:
            comp_html += f"<span class='component-tag'>{c.name}</span>"
        st.markdown(comp_html, unsafe_allow_html=True)
        st.markdown("")
        
        st.markdown(f"<div class='level3-box'>{l3_res.get('content', 'Level 3 summary missing.')}</div>", unsafe_allow_html=True)
        
        # --- Mock Provenance Modal Data ---
        # In the future, this calls src.services.social_epistemology to build the Haack crossword
        st.markdown("#### Evidence Provenance (Foundherentist)")
        prov_html = """
        <div class='provenance-card'>
            <strong>Grounding Score:</strong> 0.85 (MULTI_HOP towards Physiological Anchors)<br/>
            <strong>Justification Status:</strong> <code>WELL_JUSTIFIED</code><br/>
            <strong>Crossword Integration:</strong> Supports 12 nodes, Supported by 5 nodes.<br/>
            <strong>Key Sources:</strong>
        """
        for ref in mol.key_references:
             prov_html += f"<li>{ref}</li>"
        prov_html += "</div>"
        
        st.markdown(prov_html, unsafe_allow_html=True)


if search_query:
    st.subheader(f"Results for: '{search_query}'")
    # Route via our backend
    result = router.route_query(search_query)
    
    if "error" in result:
        st.error(result["error"])
    elif result.get("query_type") == "molecule_lookup":
        st.success(f"Routed to molecule: {result['topic']}")
        
        # We know what molecule it is, just display the full UI
        for mol_id, mol in router.molecule_registry.items():
            if mol.name == result['topic']:
                 display_molecule(mol_id)
                 break
    else:
        st.info(f"Routed to: Live Synthesis Engine")
        st.write(result.get("content"))
        
elif molecule_options[selected_mol_name] is not None:
    display_molecule(molecule_options[selected_mol_name])
else:
    st.info("Select a theory from the sidebar, or ask a question in the search bar.")
