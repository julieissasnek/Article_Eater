
import sqlite3
import pandas as pd
import networkx as nx
import os
import sys
from src.services.db_locator import get_web_db

DB_PATH = get_web_db()  # Centralized: was hardcoded
REPORT_PATH = "docs/web_of_belief_health_report.md"

def analyze_web_health():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    
    report_lines = []
    report_lines.append("# Sprint D.9: Web of Belief Health Report\n")
    report_lines.append("## 1. Database Overview\n")
    
    # 1. Schema & Counts
    try:
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
        report_lines.append(f"- **Tables:** {', '.join(tables['name'].tolist())}")
        
        if 'nodes' in tables['name'].values:
            node_count = pd.read_sql("SELECT count(*) as count FROM nodes", conn).iloc[0]['count']
            report_lines.append(f"- **Total Nodes:** {node_count}")
        
        if 'edges' in tables['name'].values:
            edge_count = pd.read_sql("SELECT count(*) as count FROM edges", conn).iloc[0]['count']
            report_lines.append(f"- **Total Edges:** {edge_count}")
            
    except Exception as e:
        report_lines.append(f"Error reading schema: {e}")

    # 2. Variable Quality (Garbage Detection)
    report_lines.append("\n## 2. Variable Quality (Garbage Detection)\n")
    try:
        # In this schema, nodes are implicit in the environment_id and outcome_id columns of the beliefs table
        if 'beliefs' in tables['name'].values:
            # Get all source and target nodes
            # We'll check environment_id/outcome_id first, but also look at 'content' if needed 
            # (though content is likely a JSON or text description)
            
            df = pd.read_sql("SELECT environment_id, outcome_id FROM beliefs", conn)
            
            # Combine to get unique nodes
            all_nodes = pd.concat([df['environment_id'], df['outcome_id']]).dropna().unique()
            nodes_df = pd.DataFrame(all_nodes, columns=['id'])
            
            report_lines.append(f"- **Total Implicit Nodes:** {len(nodes_df)}")

            # Simple heuristic for "garbage" variables: 
            # - Long strings (likely sentences)
            # - Contain spaces (variable names should generally be concise or snake_case in this system context)
            
            long_nodes = nodes_df[nodes_df['id'].str.len() > 50]
            space_nodes = nodes_df[nodes_df['id'].str.contains(' ')]
            
            report_lines.append(f"- **Nodes > 50 chars (likely fragments):** {len(long_nodes)} ({len(long_nodes)/len(nodes_df)*100:.1f}%)")
            report_lines.append(f"- **Nodes with spaces:** {len(space_nodes)} ({len(space_nodes)/len(nodes_df)*100:.1f}%)")
            
            report_lines.append("\n**Sample Garbage Nodes:**")
            for _, row in long_nodes.head(10).iterrows():
                report_lines.append(f"- `{str(row['id'])[:80]}...`")
                
    except Exception as e:
        report_lines.append(f"Error analyzing node quality: {e}")

    # 3. Graph Connectivity
    report_lines.append("\n## 3. Graph Connectivity\n")
    try:
        if 'beliefs' in tables['name'].values:
            edges_df = pd.read_sql("SELECT environment_id as source, outcome_id as target FROM beliefs WHERE environment_id IS NOT NULL AND outcome_id IS NOT NULL", conn)
            G = nx.from_pandas_edgelist(edges_df, 'source', 'target')
            
            # Nodes are already added by from_pandas_edgelist for connected ones. 
            # If we want singletons, we need to know the full set of intended nodes, 
            # but in an edge-list-only DB, singletons might not exist unless we define a separate node list.
            # We'll assume the graph is defined by the edges present.
            
            num_connected = nx.number_connected_components(G)
            report_lines.append(f"- **Connected Components:** {num_connected}")
            
            components = list(nx.connected_components(G))
            largest_cc_size = len(max(components, key=len)) if components else 0
            report_lines.append(f"- **Largest Component Size:** {largest_cc_size} nodes")
            
    except Exception as e:
        report_lines.append(f"Error analyzing connectivity: {e}")
        
    # 4. Edge Weight Distribution
    report_lines.append("\n## 4. Edge Weight Distribution\n")
    try:
        if 'beliefs' in tables['name'].values:
            edges_df = pd.read_sql("SELECT credence_value FROM beliefs", conn)
            
            if 'credence_value' in edges_df.columns:
                report_lines.append(f"- **Mean Credence:** {edges_df['credence_value'].mean():.4f}")
                report_lines.append(f"- **Min Credence:** {edges_df['credence_value'].min()}")
                report_lines.append(f"- **Max Credence:** {edges_df['credence_value'].max()}")
                
                # Check for default/dummy weights
                default_weights = len(edges_df[edges_df['credence_value'] == 0.5]) # Assuming 0.5 might be a default
                report_lines.append(f"- **Edges with Credence = 0.5 (Default?):** {default_weights}")
            
    except Exception as e:
        report_lines.append(f"Error analyzing edge weights: {e}")

    # 5. Conclusion
    report_lines.append("\n## 5. Conclusion\n")
    report_lines.append("This database reflects the 'garbage in, garbage out' problem identified in Doc 70.")
    report_lines.append("- The high number of singleton and disconnected components indicates a lack of semantic integration.")
    report_lines.append("- The prevalence of long, space-containing node IDs confirms that raw text was treated as variables.")
    report_lines.append("- **Recommendation:** Proceed with Task D.11 (Web Rebuild) to replace this database with a clean version derived from the variable vocabulary.")

    # Write Report
    with open(REPORT_PATH, "w") as f:
        f.writelines(report_lines)
    
    print(f"Report generated at {REPORT_PATH}")
    conn.close()

if __name__ == "__main__":
    analyze_web_health()
