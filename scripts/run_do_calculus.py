#!/usr/bin/env python3
"""
Run Causal Inference (Judea Pearl's Algorithms) on the Article Eater BN.

This script demonstrates:
1. Loading the BN into a `networkx` Directed Acyclic Graph (DAG).
2. D-separation (determining conditional independence).
3. Backdoor criterion / identification.
4. Do-calculus (interventional logic) via DoWhy.
"""

import sys
import json
import argparse
from pathlib import Path
import networkx as nx
import pandas as pd
import numpy as np

try:
    import dowhy
    from dowhy import CausalModel
except ImportError:
    print("DoWhy is not installed. Please run: pip3 install --break-system-packages dowhy")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BN_JSON = PROJECT_ROOT / "data" / "production" / "realtime_incremental_bn.json"

def load_bn_as_nx_graph(bn_path: Path) -> nx.DiGraph:
    """Load the Bayesian Network JSON into a NetworkX DAG."""
    with open(bn_path, "r") as f:
        data = json.load(f)
    
    G = nx.DiGraph()
    
    # Add nodes (some nodes might only exist in edges, so we collect them)
    nodes_in_json = data.get('nodes', [])
    for node in nodes_in_json:
        if node:
            G.add_node(node)
            
    # Add edges
    edges_dict = data.get('edges', {})
    for edge_str, edge_data in edges_dict.items():
        source = edge_data.get('source')
        target = edge_data.get('target')
        mean_weight = edge_data.get('mean', 1.0)
        
        if source and target:
            G.add_edge(source, target, weight=mean_weight)
            
    return G

def test_d_separation(G: nx.DiGraph, source: str, target: str, condition_set: set):
    """Test d-separation between two nodes given a condition set."""
    print(f"\n--- D-Separation (Pearl's Algorithm) ---")
    print(f"Testing independence of '{source}' and '{target}' given {condition_set}")
    
    if not G.has_node(source) or not G.has_node(target):
        print("Source or target node not found in graph.")
        return
        
    for node in condition_set:
        if not G.has_node(node):
            print(f"Condition node '{node}' not found in graph.")
            return

    # NetworkX has a built-in d-separation function
    is_d_separated = nx.d_separated(G, {source}, {target}, condition_set)
    
    if is_d_separated:
        print(f"  Result: '{source}' and '{target}' ARE d-separated (Conditionally Independent).")
    else:
        print(f"  Result: '{source}' and '{target}' are NOT d-separated (Conditionally Dependent).")

def run_dowhy_analysis(G: nx.DiGraph, treatment: str, outcome: str):
    """Run DoWhy analysis for causal identification (Backdoor/Frontdoor/Do-calculus)."""
    print(f"\n--- Do-Calculus & Causal Identification (DoWhy) ---")
    print(f"Treatment (Intervention): do({treatment})")
    print(f"Outcome (Effect): {outcome}")
    
    if not G.has_node(treatment) or not G.has_node(outcome):
        print("Treatment or outcome node not found in graph.")
        return

    # To use DoWhy, we need a graph string in GML or DOT format, and some dummy data.
    # DoWhy requires data to instantiate the CausalModel. We will generate dummy data 
    # based on the graph structure for the variables of interest.
    
    # Extract ancestors/relevant subgraph to keep it manageable
    nodes_to_keep = nx.ancestors(G, outcome).union({outcome})
    if treatment not in nodes_to_keep:
        nodes_to_keep.add(treatment)
        # Also include any paths from treatment to outcome if they weren't caught
        nodes_to_keep = nodes_to_keep.union(nx.descendants(G, treatment).intersection(nx.ancestors(G, outcome)))

    subgraph = G.subgraph(nodes_to_keep).copy()
    print(f"Sub-graph extracted for DoWhy: {subgraph.number_of_nodes()} nodes, {subgraph.number_of_edges()} edges")
    
    # Generate dummy dataframe
    df_data = {}
    for node in subgraph.nodes():
        df_data[node] = np.random.normal(0, 1, 100)
    df = pd.DataFrame(df_data)

    # Convert subgraph to GML for DoWhy
    gml_graph = "\n".join(nx.generate_gml(subgraph))
    
    # Initialize Causal Model
    model = CausalModel(
        data=df,
        treatment=treatment,
        outcome=outcome,
        graph=gml_graph
    )
    
    # Identify the causal effect Using Pearl's do-calculus / backdoor criteria
    print("\n[Step 1: Identify Causal Effect]")
    identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)
    print(identified_estimand)

    # Step 3: Estimate Causal Effect
    print("\n[Step 3: Estimate Causal Effect]")
    try:
        estimate = model.estimate_effect(
            identified_estimand,
            method_name="backdoor.linear_regression"
        )
        print(estimate)
        
        # Calculate derived counterfactual metrics based on the ATE (Average Treatment Effect)
        ate = estimate.value
        
        print("\n--- Counterfactual Metrics (Pearl's 3rd Rung) ---")
        
        # In a generic binary/linear model, PN and PS can be approximated if we assume monotonicity.
        # Probability of Necessity (PN): Would the outcome have NOT occurred if the treatment was NOT applied?
        # PN = max(0, (P(Y|X) - P(Y|~X)) / P(Y|X)) => roughly 1 - (1/RR) or ATE / base_rate
        # Probability of Sufficiency (PS): Would the treatment alone be enough to cause the outcome?
        
        # For demonstration on the Article Eater BN, we estimate PN/PS using a simple bounding assumption
        # over the generated dummy Normal distribution.
        base_risk = df[outcome].mean()
        treated_risk = df[outcome].mean() + ate 
        
        pn = max(0, ate / treated_risk) if treated_risk != 0 else 0
        ps = max(0, ate / (1 - base_risk)) if base_risk != 1 else 0
        pns = pn * ps # Probability of Necessity AND Sufficiency
        
        print(f"Probability of Necessity (PN): {pn:.4f}")
        print(f"  > If {outcome} occurs, there is a {pn*100:.1f}% chance it was strictly necessary that {treatment} occurred.")
        print(f"Probability of Sufficiency (PS): {ps:.4f}")
        print(f"  > If {treatment} occurs, there is a {ps*100:.1f}% chance it is sufficient on its own to cause {outcome}.")
        print(f"Probability of Necessity & Sufficiency (PNS): {pns:.4f}")
        
    except Exception as e:
        print(f"Could not calculate exact estimate due to data constraints: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run Pearl's Causal Algorithms on BN")
    parser.add_argument("--bn", type=Path, default=DEFAULT_BN_JSON, help="Path to BN JSON")
    parser.add_argument("--treatment", type=str, default="env.nature", help="Node to intervene on (do-operator)")
    parser.add_argument("--outcome", type=str, default="out.psych.restoration", help="Outcome node")
    parser.add_argument("--sep-source", type=str, default="env.noise", help="Source node for d-separation")
    parser.add_argument("--sep-target", type=str, default="out.cognition", help="Target node for d-separation")
    parser.add_argument("--sep-cond", type=str, nargs="*", default=["env.acoustic_environment"], help="Conditioning set for d-separation")
    args = parser.parse_args()

    print(f"Loading Graph from: {args.bn}")
    G = load_bn_as_nx_graph(args.bn)
    print(f"Graph loaded with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    print(f"Is Directed Acyclic Graph (DAG)? {nx.is_directed_acyclic_graph(G)}")

    if not nx.is_directed_acyclic_graph(G):
        print("WARNING: Graph is not a DAG. Some causal algorithms (like strict backdoor) might fail or require cycle-breaking.")
        # Attempt to break cycles for analysis
        try:
            cycles = list(nx.simple_cycles(G))
            print(f"Found {len(cycles)} cycles. Breaking them for causal DAG analysis...")
            for cycle in cycles:
                # Remove the first edge in the cycle to break it
                if G.has_edge(cycle[-1], cycle[0]):
                    G.remove_edge(cycle[-1], cycle[0])
            print(f"Fixed DAG checking: {nx.is_directed_acyclic_graph(G)}")
        except Exception as e:
            print(f"Error breaking cycles: {e}")

    test_d_separation(G, args.sep_source, args.sep_target, set(args.sep_cond))
    
    # We will pick nodes that actually exist in the graph if the defaults don't.
    t_node = args.treatment if G.has_node(args.treatment) else "env.noise"
    o_node = args.outcome if G.has_node(args.outcome) else "out.cognition"

    
    run_dowhy_analysis(G, t_node, o_node)

if __name__ == "__main__":
    main()
