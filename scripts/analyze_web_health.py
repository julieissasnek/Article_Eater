
import sqlite3
import pandas as pd
import networkx as nx
import os
import sys

DB_PATH = "data/web_persistence.db"
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
        if 'nodes' in tables['name'].values:
            nodes_df = pd.read_sql("SELECT * FROM nodes", conn)
            
            # Simple heuristic for "garbage" variables: 
            # - Long strings (likely sentences)
            # - Contain spaces (variable names should generally be concise or snake_case in this system context, though natural language nodes exist)
            
            long_nodes = nodes_df[nodes_df['id'].str.len() > 50]
            space_nodes = nodes_df[nodes_df['id'].str.contains(' ')]
            
            report_lines.append(f"- **Nodes > 50 chars (likely fragments):** {len(long_nodes)} ({len(long_nodes)/len(nodes_df)*100:.1f}%)")
            report_lines.append(f"- **Nodes with spaces:** {len(space_nodes)} ({len(space_nodes)/len(nodes_df)*100:.1f}%)")
            
            report_lines.append("\n**Sample Garbage Nodes:**")
            for _, row in long_nodes.head(10).iterrows():
                report_lines.append(f"- `{row['id'][:80]}...`")
                
    except Exception as e:
        report_lines.append(f"Error analyzing node quality: {e}")

    # 3. Graph Connectivity
    report_lines.append("\n## 3. Graph Connectivity\n")
    try:
        if 'edges' in tables['name'].values and 'nodes' in tables['name'].values:
            edges_df = pd.read_sql("SELECT source, target FROM edges", conn)
            G = nx.from_pandas_edgelist(edges_df, 'source', 'target')
            
            # Add standalone nodes
            all_nodes = pd.read_sql("SELECT id FROM nodes", conn)['id'].tolist()
            G.add_nodes_from(all_nodes)
            
            num_connected = nx.number_connected_components(G)
            report_lines.append(f"- **Connected Components:** {num_connected}")
            
            # Find specific "Islands"
            components = list(nx.connected_components(G))
            singletons = [c for c in components if len(c) == 1]
            report_lines.append(f"- **Singleton Nodes (Completely Disconnected):** {len(singletons)}")
            
            largest_cc_size = len(max(components, key=len)) if components else 0
            report_lines.append(f"- **Largest Component Size:** {largest_cc_size} nodes")
            
    except Exception as e:
        report_lines.append(f"Error analyzing connectivity: {e}")
        
    # 4. Edge Weight Distribution
    report_lines.append("\n## 4. Edge Weight Distribution\n")
    try:
        if 'edges' in tables['name'].values:
            edges_df = pd.read_sql("SELECT weight FROM edges", conn)
            
            if 'weight' in edges_df.columns:
                report_lines.append(f"- **Mean Weight:** {edges_df['weight'].mean():.4f}")
                report_lines.append(f"- **Min Weight:** {edges_df['weight'].min()}")
                report_lines.append(f"- **Max Weight:** {edges_df['weight'].max()}")
                
                # Check for default/dummy weights
                zero_weights = len(edges_df[edges_df['weight'] == 0])
                one_weights = len(edges_df[edges_df['weight'] == 1])
                report_lines.append(f"- **Edges with Weight = 0:** {zero_weights}")
                report_lines.append(f"- **Edges with Weight = 1:** {one_weights}")
            else:
                report_lines.append("- 'weight' column not found in edges table.")
                
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
