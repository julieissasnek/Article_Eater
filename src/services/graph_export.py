"""
Graph Export Service — Sprint 3.0.3-F
2026-02-09

Export belief networks in various graph formats for external analysis tools.

Supported formats:
- GraphML: For Gephi, Cytoscape, yEd
- GEXF: Gephi's native format with dynamics support
- JSON: For D3.js, vis.js, custom web visualizations
- DOT: For Graphviz

Expert Panel Guidance:
- Munzner: Purpose-driven export format selection
- Shneiderman: Support overview-first exploration in external tools
"""

import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats."""
    GRAPHML = "graphml"
    GEXF = "gexf"
    JSON = "json"
    DOT = "dot"
    HTML = "html"


@dataclass
class ExportOptions:
    """Options for graph export."""
    include_metadata: bool = True
    include_positions: bool = False
    include_communities: bool = True
    include_metrics: bool = True
    min_credence: float = 0.0
    max_nodes: int = 500
    node_attributes: List[str] = field(default_factory=lambda: [
        "credence", "status", "level", "theory", "entrenchment"
    ])
    edge_attributes: List[str] = field(default_factory=lambda: [
        "weight", "polarity", "reason"
    ])


class GraphExporter:
    """
    Export belief networks to various graph formats.

    Supports GraphML, GEXF, JSON, and DOT formats for use with
    external tools like Gephi, Cytoscape, and Graphviz.
    """

    def __init__(self):
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}

    def load_from_web(
        self,
        options: Optional[ExportOptions] = None
    ) -> int:
        """
        Load graph data from WebOfBelief.

        Returns:
            Number of nodes loaded
        """
        opts = options or ExportOptions()

        try:
            from src.services.web_of_belief import get_web
            web = get_web()

            self.nodes = []
            self.edges = []

            # Build node list
            belief_ids = set()
            for belief_id, belief in list(web.beliefs.items())[:opts.max_nodes]:
                credence = belief.credence
                if hasattr(credence, 'point'):
                    credence = credence.point

                if credence < opts.min_credence:
                    continue

                status = belief.status.value if hasattr(belief.status, 'value') else str(belief.status)
                level = belief.level.value if hasattr(belief.level, 'value') else str(belief.level)

                node = {
                    "id": belief_id,
                    "label": belief.content[:50] + "..." if len(belief.content) > 50 else belief.content,
                    "content": belief.content,
                    "credence": credence,
                    "status": status.upper(),
                    "level": level.upper(),
                    "theory": belief.theory_ids[0] if belief.theory_ids else "",
                    "entrenchment": web.get_entrenchment(belief_id)
                }

                self.nodes.append(node)
                belief_ids.add(belief_id)

            # Build edge list
            for i, constraint in enumerate(web.constraints):
                if constraint.source_id in belief_ids and constraint.target_id in belief_ids:
                    polarity = constraint.polarity.value if hasattr(constraint.polarity, 'value') else str(constraint.polarity)

                    edge = {
                        "id": f"e{i}",
                        "source": constraint.source_id,
                        "target": constraint.target_id,
                        "weight": constraint.weight,
                        "polarity": polarity.upper(),
                        "reason": constraint.reason or ""
                    }

                    self.edges.append(edge)

            # Metadata
            self.metadata = {
                "name": "Article Eater Belief Network",
                "description": "Epistemic web of beliefs from scientific literature",
                "creator": "Article Eater V23.0.0",
                "created": datetime.now().isoformat(),
                "node_count": len(self.nodes),
                "edge_count": len(self.edges)
            }

            return len(self.nodes)

        except Exception as e:
            logger.error(f"Failed to load from WebOfBelief: {e}")
            return 0

    def load_from_data(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Load graph data from provided lists."""
        self.nodes = nodes
        self.edges = edges
        self.metadata = metadata or {
            "name": "Belief Network",
            "created": datetime.now().isoformat(),
            "node_count": len(nodes),
            "edge_count": len(edges)
        }

    # =========================================================================
    # GraphML Export
    # =========================================================================

    def to_graphml(self, options: Optional[ExportOptions] = None) -> str:
        """
        Export to GraphML format.

        GraphML is an XML-based format supported by:
        - Gephi
        - Cytoscape
        - yEd
        - NetworkX
        - igraph
        """
        opts = options or ExportOptions()

        # Create root element
        graphml = ET.Element("graphml")
        graphml.set("xmlns", "http://graphml.graphdrawing.org/xmlns")
        graphml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        graphml.set("xsi:schemaLocation",
            "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd")

        # Define node attribute keys
        node_keys = {
            "label": ("label", "string"),
            "content": ("content", "string"),
            "credence": ("credence", "double"),
            "status": ("status", "string"),
            "level": ("level", "string"),
            "theory": ("theory", "string"),
            "entrenchment": ("entrenchment", "double"),
        }

        for attr, (name, dtype) in node_keys.items():
            if attr in opts.node_attributes or attr in ["label", "content"]:
                key = ET.SubElement(graphml, "key")
                key.set("id", f"n_{attr}")
                key.set("for", "node")
                key.set("attr.name", name)
                key.set("attr.type", dtype)

        # Define edge attribute keys
        edge_keys = {
            "weight": ("weight", "double"),
            "polarity": ("polarity", "string"),
            "reason": ("reason", "string"),
        }

        for attr, (name, dtype) in edge_keys.items():
            if attr in opts.edge_attributes:
                key = ET.SubElement(graphml, "key")
                key.set("id", f"e_{attr}")
                key.set("for", "edge")
                key.set("attr.name", name)
                key.set("attr.type", dtype)

        # Create graph element
        graph = ET.SubElement(graphml, "graph")
        graph.set("id", "G")
        graph.set("edgedefault", "directed")

        # Add nodes
        for node in self.nodes:
            node_elem = ET.SubElement(graph, "node")
            node_elem.set("id", node["id"])

            for attr in ["label", "content"] + opts.node_attributes:
                if attr in node:
                    data = ET.SubElement(node_elem, "data")
                    data.set("key", f"n_{attr}")
                    data.text = str(node[attr])

        # Add edges
        for edge in self.edges:
            edge_elem = ET.SubElement(graph, "edge")
            edge_elem.set("id", edge["id"])
            edge_elem.set("source", edge["source"])
            edge_elem.set("target", edge["target"])

            for attr in opts.edge_attributes:
                if attr in edge:
                    data = ET.SubElement(edge_elem, "data")
                    data.set("key", f"e_{attr}")
                    data.text = str(edge[attr])

        # Pretty print
        xml_str = ET.tostring(graphml, encoding="unicode")
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ")

    # =========================================================================
    # GEXF Export
    # =========================================================================

    def to_gexf(self, options: Optional[ExportOptions] = None) -> str:
        """
        Export to GEXF format.

        GEXF is Gephi's native format with support for:
        - Dynamic graphs (time-varying)
        - Hierarchical structure
        - Rich visualization attributes
        """
        opts = options or ExportOptions()

        # Create root element
        gexf = ET.Element("gexf")
        gexf.set("xmlns", "http://www.gexf.net/1.3")
        gexf.set("xmlns:viz", "http://www.gexf.net/1.3/viz")
        gexf.set("version", "1.3")

        # Metadata
        meta = ET.SubElement(gexf, "meta")
        meta.set("lastmodifieddate", datetime.now().strftime("%Y-%m-%d"))

        creator = ET.SubElement(meta, "creator")
        creator.text = self.metadata.get("creator", "Article Eater")

        description = ET.SubElement(meta, "description")
        description.text = self.metadata.get("description", "Belief network")

        # Graph
        graph = ET.SubElement(gexf, "graph")
        graph.set("mode", "static")
        graph.set("defaultedgetype", "directed")

        # Node attributes
        node_attrs = ET.SubElement(graph, "attributes")
        node_attrs.set("class", "node")

        attr_types = {
            "content": "string",
            "credence": "float",
            "status": "string",
            "level": "string",
            "theory": "string",
            "entrenchment": "float"
        }

        for i, (attr, atype) in enumerate(attr_types.items()):
            if attr in opts.node_attributes or attr == "content":
                attr_elem = ET.SubElement(node_attrs, "attribute")
                attr_elem.set("id", str(i))
                attr_elem.set("title", attr)
                attr_elem.set("type", atype)

        # Edge attributes
        edge_attrs = ET.SubElement(graph, "attributes")
        edge_attrs.set("class", "edge")

        edge_attr_types = {
            "polarity": "string",
            "reason": "string"
        }

        for i, (attr, atype) in enumerate(edge_attr_types.items()):
            if attr in opts.edge_attributes:
                attr_elem = ET.SubElement(edge_attrs, "attribute")
                attr_elem.set("id", str(100 + i))
                attr_elem.set("title", attr)
                attr_elem.set("type", atype)

        # Nodes
        nodes_elem = ET.SubElement(graph, "nodes")

        # Color mapping for status
        status_colors = {
            "ACCEPTED": (46, 125, 50),      # Green
            "ESTABLISHED": (46, 125, 50),
            "CONTESTED": (245, 124, 0),     # Orange
            "STUB": (158, 158, 158),         # Gray
            "TENTATIVE": (100, 181, 246),   # Light blue
            "REJECTED": (198, 40, 40),      # Red
        }

        for node in self.nodes:
            node_elem = ET.SubElement(nodes_elem, "node")
            node_elem.set("id", node["id"])
            node_elem.set("label", node.get("label", node["id"]))

            # Attributes
            attvalues = ET.SubElement(node_elem, "attvalues")
            for i, attr in enumerate(attr_types.keys()):
                if attr in node and (attr in opts.node_attributes or attr == "content"):
                    attvalue = ET.SubElement(attvalues, "attvalue")
                    attvalue.set("for", str(i))
                    attvalue.set("value", str(node[attr]))

            # Visual attributes
            status = node.get("status", "STUB")
            color = status_colors.get(status, (158, 158, 158))

            viz_color = ET.SubElement(node_elem, "viz:color")
            viz_color.set("r", str(color[0]))
            viz_color.set("g", str(color[1]))
            viz_color.set("b", str(color[2]))

            # Size based on credence
            credence = node.get("credence", 0.5)
            viz_size = ET.SubElement(node_elem, "viz:size")
            viz_size.set("value", str(10 + credence * 20))

        # Edges
        edges_elem = ET.SubElement(graph, "edges")

        for edge in self.edges:
            edge_elem = ET.SubElement(edges_elem, "edge")
            edge_elem.set("id", edge["id"])
            edge_elem.set("source", edge["source"])
            edge_elem.set("target", edge["target"])
            edge_elem.set("weight", str(edge.get("weight", 1.0)))

            # Attributes
            attvalues = ET.SubElement(edge_elem, "attvalues")
            for i, attr in enumerate(edge_attr_types.keys()):
                if attr in edge and attr in opts.edge_attributes:
                    attvalue = ET.SubElement(attvalues, "attvalue")
                    attvalue.set("for", str(100 + i))
                    attvalue.set("value", str(edge[attr]))

            # Color based on polarity
            polarity = edge.get("polarity", "NEUTRAL")
            if polarity == "POSITIVE":
                edge_color = (76, 175, 80)  # Green
            elif polarity == "NEGATIVE":
                edge_color = (244, 67, 54)  # Red
            else:
                edge_color = (158, 158, 158)  # Gray

            viz_color = ET.SubElement(edge_elem, "viz:color")
            viz_color.set("r", str(edge_color[0]))
            viz_color.set("g", str(edge_color[1]))
            viz_color.set("b", str(edge_color[2]))

        # Pretty print
        xml_str = ET.tostring(gexf, encoding="unicode")
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ")

    # =========================================================================
    # JSON Export
    # =========================================================================

    def to_json(self, options: Optional[ExportOptions] = None) -> str:
        """
        Export to JSON format.

        Compatible with D3.js, vis.js, and custom web visualizations.
        """
        opts = options or ExportOptions()

        output = {
            "metadata": self.metadata if opts.include_metadata else {},
            "nodes": [],
            "edges": []
        }

        for node in self.nodes:
            node_data = {"id": node["id"]}
            for attr in ["label", "content"] + opts.node_attributes:
                if attr in node:
                    node_data[attr] = node[attr]
            output["nodes"].append(node_data)

        for edge in self.edges:
            edge_data = {
                "id": edge["id"],
                "source": edge["source"],
                "target": edge["target"]
            }
            for attr in opts.edge_attributes:
                if attr in edge:
                    edge_data[attr] = edge[attr]
            output["edges"].append(edge_data)

        if opts.include_metrics:
            output["metrics"] = self._compute_metrics()

        return json.dumps(output, indent=2)

    # =========================================================================
    # DOT Export
    # =========================================================================

    def to_dot(self, options: Optional[ExportOptions] = None) -> str:
        """
        Export to DOT format for Graphviz.

        Can be rendered with:
        - dot, neato, fdp, sfdp, circo, twopi
        """
        opts = options or ExportOptions()

        lines = [
            "digraph BeliefNetwork {",
            "  // Graph attributes",
            "  graph [rankdir=TB, overlap=false, splines=true];",
            "  node [shape=ellipse, style=filled];",
            "  edge [arrowsize=0.8];",
            ""
        ]

        # Status colors
        status_colors = {
            "ACCEPTED": "#2E7D32",
            "ESTABLISHED": "#2E7D32",
            "CONTESTED": "#F57C00",
            "STUB": "#9E9E9E",
            "TENTATIVE": "#64B5F6",
            "REJECTED": "#C62828",
        }

        # Nodes
        lines.append("  // Nodes")
        for node in self.nodes:
            node_id = node["id"].replace("-", "_").replace(".", "_")
            label = node.get("label", node["id"]).replace('"', '\\"')
            status = node.get("status", "STUB")
            color = status_colors.get(status, "#9E9E9E")
            credence = node.get("credence", 0.5)

            # Font color based on background
            fontcolor = "white" if status in ["ACCEPTED", "ESTABLISHED", "REJECTED"] else "black"

            lines.append(
                f'  {node_id} [label="{label}", fillcolor="{color}", '
                f'fontcolor="{fontcolor}", width={0.5 + credence}];'
            )

        lines.append("")

        # Edges
        lines.append("  // Edges")
        for edge in self.edges:
            source = edge["source"].replace("-", "_").replace(".", "_")
            target = edge["target"].replace("-", "_").replace(".", "_")
            polarity = edge.get("polarity", "NEUTRAL")
            weight = edge.get("weight", 1.0)

            if polarity == "POSITIVE":
                color = "#4CAF50"
                style = "solid"
            elif polarity == "NEGATIVE":
                color = "#F44336"
                style = "dashed"
            else:
                color = "#9E9E9E"
                style = "dotted"

            lines.append(
                f'  {source} -> {target} [color="{color}", style={style}, penwidth={1 + weight}];'
            )

        lines.append("}")

        return "\n".join(lines)

    # =========================================================================
    # Interactive HTML Export
    # =========================================================================

    def to_html(
        self,
        options: Optional[ExportOptions] = None,
        title: str = "Belief Network",
        height: int = 800
    ) -> str:
        """
        Export to standalone interactive HTML.

        Generates a self-contained HTML file with embedded vis.js
        that can be opened directly in a browser and shared.
        """
        opts = options or ExportOptions()

        # Prepare node data for vis.js
        vis_nodes = []
        status_colors = {
            "ACCEPTED": "#2E7D32",
            "ESTABLISHED": "#2E7D32",
            "CONTESTED": "#F57C00",
            "STUB": "#9E9E9E",
            "TENTATIVE": "#64B5F6",
            "REJECTED": "#C62828",
        }

        for node in self.nodes:
            status = node.get("status", "STUB")
            credence = node.get("credence", 0.5)

            vis_nodes.append({
                "id": node["id"],
                "label": node.get("label", node["id"]),
                "title": self._build_tooltip(node),
                "color": status_colors.get(status, "#9E9E9E"),
                "size": 10 + credence * 25,
                "credence": credence,
                "status": status,
                "level": node.get("level", ""),
                "theory": node.get("theory", "")
            })

        # Prepare edge data for vis.js
        vis_edges = []
        for edge in self.edges:
            polarity = edge.get("polarity", "NEUTRAL")
            weight = edge.get("weight", 0.5)

            if polarity == "POSITIVE":
                color = "#4CAF50"
                dashes = False
            elif polarity == "NEGATIVE":
                color = "#F44336"
                dashes = True
            else:
                color = "#9E9E9E"
                dashes = False

            vis_edges.append({
                "id": edge["id"],
                "from": edge["source"],
                "to": edge["target"],
                "color": {"color": color},
                "width": 1 + weight * 2,
                "dashes": dashes,
                "title": edge.get("reason", f"{polarity} ({weight:.2f})")
            })

        # Compute metrics
        metrics = self._compute_metrics()

        # Generate HTML
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
        }}
        .header {{
            background: #1a1a2e;
            color: white;
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{ font-size: 20px; font-weight: 500; }}
        .header .stats {{
            display: flex;
            gap: 24px;
            font-size: 13px;
            color: #aaa;
        }}
        .header .stats span {{ color: white; font-weight: 600; }}
        .container {{
            display: flex;
            height: calc(100vh - 60px);
        }}
        .sidebar {{
            width: 280px;
            background: white;
            border-right: 1px solid #e0e0e0;
            padding: 16px;
            overflow-y: auto;
        }}
        .sidebar h3 {{
            font-size: 12px;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
        }}
        .filter-group {{ margin-bottom: 20px; }}
        .filter-group label {{
            display: block;
            font-size: 13px;
            margin-bottom: 6px;
            color: #333;
        }}
        .filter-group select, .filter-group input {{
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 13px;
        }}
        .checkbox-group {{ margin: 8px 0; }}
        .checkbox-group label {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            cursor: pointer;
        }}
        #network {{
            flex: 1;
            background: #fafafa;
        }}
        .legend {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 12px 16px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            font-size: 12px;
        }}
        .legend-title {{
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 4px 0;
        }}
        .legend-color {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        .legend-line {{
            width: 20px;
            height: 2px;
        }}
        .info-panel {{
            position: absolute;
            top: 80px;
            right: 20px;
            background: white;
            padding: 16px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            max-width: 300px;
            display: none;
        }}
        .info-panel.visible {{ display: block; }}
        .info-panel h4 {{ margin-bottom: 8px; font-size: 14px; }}
        .info-panel p {{ font-size: 13px; color: #666; margin: 4px 0; }}
        .btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            margin-right: 8px;
        }}
        .btn-primary {{ background: #1976d2; color: white; }}
        .btn-secondary {{ background: #e0e0e0; color: #333; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="stats">
            Nodes: <span>{metrics['node_count']}</span>
            Edges: <span>{metrics['edge_count']}</span>
            Density: <span>{metrics['density']}</span>
            Avg Degree: <span>{metrics['average_degree']}</span>
        </div>
    </div>
    <div class="container">
        <div class="sidebar">
            <h3>Filters</h3>
            <div class="filter-group">
                <label>Search</label>
                <input type="text" id="search" placeholder="Search beliefs...">
            </div>
            <div class="filter-group">
                <label>Min Credence</label>
                <input type="range" id="credence" min="0" max="1" step="0.1" value="0">
                <span id="credence-value">0.0</span>
            </div>
            <div class="filter-group">
                <label>Status</label>
                <div class="checkbox-group">
                    <label><input type="checkbox" class="status-filter" value="ACCEPTED" checked> Accepted</label>
                </div>
                <div class="checkbox-group">
                    <label><input type="checkbox" class="status-filter" value="CONTESTED" checked> Contested</label>
                </div>
                <div class="checkbox-group">
                    <label><input type="checkbox" class="status-filter" value="STUB" checked> Stub</label>
                </div>
                <div class="checkbox-group">
                    <label><input type="checkbox" class="status-filter" value="REJECTED"> Rejected</label>
                </div>
            </div>
            <div class="filter-group">
                <label>Layout</label>
                <select id="layout">
                    <option value="forceAtlas2Based">Force-Directed</option>
                    <option value="barnesHut">Barnes-Hut</option>
                    <option value="repulsion">Repulsion</option>
                </select>
            </div>
            <div class="filter-group">
                <button class="btn btn-primary" onclick="resetFilters()">Reset</button>
                <button class="btn btn-secondary" onclick="network.fit()">Fit</button>
            </div>
            <h3>Legend</h3>
            <div class="legend-item"><div class="legend-color" style="background: #2E7D32"></div> Accepted</div>
            <div class="legend-item"><div class="legend-color" style="background: #F57C00"></div> Contested</div>
            <div class="legend-item"><div class="legend-color" style="background: #9E9E9E"></div> Stub</div>
            <div class="legend-item"><div class="legend-color" style="background: #C62828"></div> Rejected</div>
            <div style="margin-top: 12px;">
                <div class="legend-item"><div class="legend-line" style="background: #4CAF50"></div> Positive</div>
                <div class="legend-item"><div class="legend-line" style="background: #F44336; border-style: dashed;"></div> Negative</div>
            </div>
        </div>
        <div id="network"></div>
        <div class="info-panel" id="info-panel">
            <h4 id="info-title">Select a node</h4>
            <p id="info-content"></p>
            <p id="info-credence"></p>
            <p id="info-status"></p>
            <p id="info-level"></p>
        </div>
    </div>

    <script>
        // Data
        var allNodes = {json.dumps(vis_nodes)};
        var allEdges = {json.dumps(vis_edges)};

        var nodes = new vis.DataSet(allNodes);
        var edges = new vis.DataSet(allEdges);

        // Network
        var container = document.getElementById('network');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            nodes: {{
                shape: 'dot',
                font: {{ size: 12, face: 'Georgia' }},
                borderWidth: 2
            }},
            edges: {{
                arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }},
                smooth: {{ type: 'curvedCW', roundness: 0.2 }}
            }},
            physics: {{
                enabled: true,
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {{
                    gravitationalConstant: -50,
                    centralGravity: 0.01,
                    springLength: 100
                }},
                stabilization: {{ iterations: 150 }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 100,
                navigationButtons: true,
                keyboard: true
            }}
        }};

        var network = new vis.Network(container, data, options);

        // Node click handler
        network.on('click', function(params) {{
            if (params.nodes.length > 0) {{
                var nodeId = params.nodes[0];
                var node = nodes.get(nodeId);
                showNodeInfo(node);
            }} else {{
                hideNodeInfo();
            }}
        }});

        function showNodeInfo(node) {{
            document.getElementById('info-panel').classList.add('visible');
            document.getElementById('info-title').textContent = node.label;
            document.getElementById('info-content').textContent = 'ID: ' + node.id;
            document.getElementById('info-credence').textContent = 'Credence: ' + (node.credence || 0).toFixed(2);
            document.getElementById('info-status').textContent = 'Status: ' + (node.status || 'Unknown');
            document.getElementById('info-level').textContent = 'Level: ' + (node.level || 'Unknown');
        }}

        function hideNodeInfo() {{
            document.getElementById('info-panel').classList.remove('visible');
        }}

        // Filtering
        document.getElementById('search').addEventListener('input', applyFilters);
        document.getElementById('credence').addEventListener('input', function() {{
            document.getElementById('credence-value').textContent = this.value;
            applyFilters();
        }});
        document.querySelectorAll('.status-filter').forEach(function(cb) {{
            cb.addEventListener('change', applyFilters);
        }});
        document.getElementById('layout').addEventListener('change', function() {{
            network.setOptions({{ physics: {{ solver: this.value }} }});
        }});

        function applyFilters() {{
            var search = document.getElementById('search').value.toLowerCase();
            var minCredence = parseFloat(document.getElementById('credence').value);
            var statuses = Array.from(document.querySelectorAll('.status-filter:checked')).map(function(cb) {{
                return cb.value;
            }});

            var visibleNodes = allNodes.filter(function(node) {{
                if (search && !node.label.toLowerCase().includes(search)) return false;
                if (node.credence < minCredence) return false;
                if (!statuses.includes(node.status)) return false;
                return true;
            }});

            var visibleIds = new Set(visibleNodes.map(function(n) {{ return n.id; }}));

            var visibleEdges = allEdges.filter(function(edge) {{
                return visibleIds.has(edge.from) && visibleIds.has(edge.to);
            }});

            nodes.clear();
            nodes.add(visibleNodes);
            edges.clear();
            edges.add(visibleEdges);
        }}

        function resetFilters() {{
            document.getElementById('search').value = '';
            document.getElementById('credence').value = 0;
            document.getElementById('credence-value').textContent = '0.0';
            document.querySelectorAll('.status-filter').forEach(function(cb) {{
                cb.checked = cb.value !== 'REJECTED';
            }});
            nodes.clear();
            nodes.add(allNodes);
            edges.clear();
            edges.add(allEdges);
            network.fit();
        }}
    </script>
</body>
</html>'''

        return html

    def _build_tooltip(self, node: Dict[str, Any]) -> str:
        """Build HTML tooltip for node."""
        parts = [f"<b>{node.get('label', node['id'])}</b>"]

        if node.get("content"):
            parts.append(f"<br>{node['content'][:100]}...")

        if node.get("credence") is not None:
            parts.append(f"<br>Credence: {node['credence']:.2f}")

        if node.get("status"):
            parts.append(f"<br>Status: {node['status']}")

        if node.get("level"):
            parts.append(f"<br>Level: {node['level']}")

        if node.get("theory"):
            parts.append(f"<br>Theory: {node['theory']}")

        return "".join(parts)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def _compute_metrics(self) -> Dict[str, Any]:
        """Compute basic graph metrics."""
        n = len(self.nodes)
        m = len(self.edges)

        # Degree distribution
        in_degree = {}
        out_degree = {}

        for edge in self.edges:
            out_degree[edge["source"]] = out_degree.get(edge["source"], 0) + 1
            in_degree[edge["target"]] = in_degree.get(edge["target"], 0) + 1

        degrees = [in_degree.get(node["id"], 0) + out_degree.get(node["id"], 0) for node in self.nodes]
        avg_degree = sum(degrees) / n if n > 0 else 0

        # Density
        density = m / (n * (n - 1)) if n > 1 else 0

        return {
            "node_count": n,
            "edge_count": m,
            "density": round(density, 4),
            "average_degree": round(avg_degree, 2),
            "max_degree": max(degrees) if degrees else 0
        }

    def export(
        self,
        format: ExportFormat,
        options: Optional[ExportOptions] = None
    ) -> str:
        """
        Export graph to specified format.

        Args:
            format: Export format (GRAPHML, GEXF, JSON, DOT, HTML)
            options: Export options

        Returns:
            Formatted string output
        """
        if format == ExportFormat.GRAPHML:
            return self.to_graphml(options)
        elif format == ExportFormat.GEXF:
            return self.to_gexf(options)
        elif format == ExportFormat.JSON:
            return self.to_json(options)
        elif format == ExportFormat.DOT:
            return self.to_dot(options)
        elif format == ExportFormat.HTML:
            return self.to_html(options)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def save(
        self,
        filepath: str,
        format: Optional[ExportFormat] = None,
        options: Optional[ExportOptions] = None
    ) -> None:
        """
        Save graph to file.

        Args:
            filepath: Output file path
            format: Export format (auto-detected from extension if not provided)
            options: Export options
        """
        # Auto-detect format from extension
        if format is None:
            ext = filepath.rsplit(".", 1)[-1].lower()
            format_map = {
                "graphml": ExportFormat.GRAPHML,
                "gexf": ExportFormat.GEXF,
                "json": ExportFormat.JSON,
                "dot": ExportFormat.DOT,
                "gv": ExportFormat.DOT,
                "html": ExportFormat.HTML,
                "htm": ExportFormat.HTML,
            }
            format = format_map.get(ext, ExportFormat.GRAPHML)

        content = self.export(format, options)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Saved graph to {filepath} ({format.value})")


# =============================================================================
# Convenience Functions
# =============================================================================

def export_web_to_graphml(filepath: str, options: Optional[ExportOptions] = None) -> int:
    """
    Export current WebOfBelief to GraphML file.

    Returns:
        Number of nodes exported
    """
    exporter = GraphExporter()
    count = exporter.load_from_web(options)
    if count > 0:
        exporter.save(filepath, ExportFormat.GRAPHML, options)
    return count


def export_web_to_gexf(filepath: str, options: Optional[ExportOptions] = None) -> int:
    """
    Export current WebOfBelief to GEXF file.

    Returns:
        Number of nodes exported
    """
    exporter = GraphExporter()
    count = exporter.load_from_web(options)
    if count > 0:
        exporter.save(filepath, ExportFormat.GEXF, options)
    return count


def export_web_to_json(filepath: str, options: Optional[ExportOptions] = None) -> int:
    """
    Export current WebOfBelief to JSON file.

    Returns:
        Number of nodes exported
    """
    exporter = GraphExporter()
    count = exporter.load_from_web(options)
    if count > 0:
        exporter.save(filepath, ExportFormat.JSON, options)
    return count


def export_web_to_html(
    filepath: str,
    title: str = "Belief Network",
    options: Optional[ExportOptions] = None
) -> int:
    """
    Export current WebOfBelief to interactive HTML file.

    The generated HTML file is self-contained and can be:
    - Opened directly in a browser
    - Shared with collaborators
    - Embedded in reports

    Args:
        filepath: Output file path
        title: Title for the HTML page
        options: Export options

    Returns:
        Number of nodes exported
    """
    exporter = GraphExporter()
    count = exporter.load_from_web(options)
    if count > 0:
        html = exporter.to_html(options, title=title)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"Saved interactive HTML to {filepath}")
    return count


def get_graph_exporter() -> GraphExporter:
    """Get a new GraphExporter instance."""
    return GraphExporter()
