#!/usr/bin/env python3
"""
Generate formal architecture diagram for Article Eater reasoning network.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from datetime import datetime

def create_architecture_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(14, 18))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 18)
    ax.set_aspect('equal')
    ax.axis('off')

    # Colors
    colors = {
        'extraction': '#E8F5E9',      # Light green
        'epistemic': '#E3F2FD',        # Light blue
        'social': '#F3E5F5',           # Light purple
        'causal': '#FFF3E0',           # Light orange
        'support': '#FFEBEE',          # Light red
        'output': '#E0F7FA',           # Light cyan
        'archived': '#F5F5F5',         # Light gray
        'border': '#37474F',
        'arrow': '#546E7A',
        'text': '#212121',
        'complete': '#4CAF50',
        'partial': '#FF9800',
    }

    # Title
    ax.text(7, 17.5, 'Article Eater: Layered Reasoning Network Architecture',
            ha='center', va='center', fontsize=16, fontweight='bold', color=colors['text'])
    ax.text(7, 17.0, 'Post-Quinean V23.0.0 — Foundherentist Epistemology',
            ha='center', va='center', fontsize=11, style='italic', color='#616161')

    # Helper function to draw boxes
    def draw_layer(y, height, color, title, items, status_pct, width=12, x=1):
        # Main box
        box = FancyBboxPatch((x, y), width, height,
                             boxstyle="round,pad=0.02,rounding_size=0.3",
                             facecolor=color, edgecolor=colors['border'],
                             linewidth=2)
        ax.add_patch(box)

        # Title bar
        title_bar = FancyBboxPatch((x, y + height - 0.6), width, 0.6,
                                   boxstyle="round,pad=0.02,rounding_size=0.1",
                                   facecolor=colors['border'], edgecolor='none')
        ax.add_patch(title_bar)
        ax.text(x + 0.3, y + height - 0.3, title,
                ha='left', va='center', fontsize=11, fontweight='bold', color='white')

        # Status indicator
        status_color = colors['complete'] if status_pct >= 90 else colors['partial']
        ax.text(x + width - 0.3, y + height - 0.3, f'{status_pct}%',
                ha='right', va='center', fontsize=10, fontweight='bold', color=status_color)

        # Items
        item_y = y + height - 1.0
        for item in items:
            if isinstance(item, tuple):
                text, detail = item
                ax.text(x + 0.4, item_y, f'• {text}', ha='left', va='top',
                        fontsize=9, color=colors['text'])
                ax.text(x + 0.6, item_y - 0.35, detail, ha='left', va='top',
                        fontsize=7, color='#757575', style='italic')
                item_y -= 0.7
            else:
                ax.text(x + 0.4, item_y, f'• {item}', ha='left', va='top',
                        fontsize=9, color=colors['text'])
                item_y -= 0.4

    # Layer 1: Extraction (top)
    draw_layer(15.0, 1.6, colors['extraction'],
               'EXTRACTION LAYER (Track A)', [
                   ('PDF → Claims/Rules', 'extraction_to_web.py: 1,571 lines'),
                   'Theory matching, stub handling, enabling conditions'
               ], 95)

    # Layer 2: Epistemic
    draw_layer(12.2, 2.6, colors['epistemic'],
               'EPISTEMIC LAYER — Quinean Coherentism (Track B)', [
                   ('web_of_belief.py', '2,925 lines — Core coherence engine'),
                   ('Emergent Entrenchment', '40% connectivity + 30% level + 30% coherence'),
                   ('5 Statuses', 'STUB → TENTATIVE → ESTABLISHED → ENTRENCHED → ANOMALOUS'),
                   ('8 Constraint Types', 'SUPPORTS, CONTRADICTS, EXPLAINS, BRIDGES, etc.'),
               ], 95)

    # Layer 3: Social
    draw_layer(10.0, 2.0, colors['social'],
               'SOCIAL EPISTEMOLOGY LAYER (Sprint 2.5)', [
                   ('social_epistemology.py', '1,285 lines — Community-relative credence'),
                   ('Community Hierarchy', 'FIELD > PARADIGM > LAB'),
                   'Contestation tracking, methodological diversity assessment'
               ], 100)

    # Layer 4: Causal
    draw_layer(6.8, 3.0, colors['causal'],
               'CAUSAL LAYER — Epistemic-Causal Bridge (Track B.1)', [
                   ('epistemic_causal_bridge.py', '3,472 lines — Pearlian DAGs'),
                   ('Van Fraassen Contrast Classes', 'DIRECT, BASELINE_SHIFT, POPULATION_SHIFT, MEANING_SHIFT'),
                   ('Counterfactual Inference', 'Theory-relative estimates with robustness'),
                   ('Enabling Conditions', 'Cartwright capacities: threshold, dosage, temporal'),
                   ('Gap Identification', '5 types → VOI search routing'),
               ], 90)

    # Layer 5: Support Services
    draw_layer(4.6, 2.0, colors['support'],
               'SUPPORTING SERVICES', [
                   ('bridge_warrants.py', '1,044 lines — Knowledge transfer warrants'),
                   ('validation.py', 'Multi-theory validation phases'),
                   'scope_extractor, causal_classifier, theory_registry'
               ], 95)

    # Layer 6: Output
    draw_layer(2.0, 2.4, colors['output'],
               'OUTPUT & QUERY LAYER (Sprint 3.0)', [
                   ('Query Engine', 'Natural language → SQL with progressive disclosure'),
                   ('Exports', 'GraphML, GEXF, DOT, HTML, PDF, Markdown'),
                   ('Discovery Funnel', 'VOI-driven research prioritization'),
                   'query_alerts, report_generator, graph_export'
               ], 100)

    # Archived features box (side)
    archived_box = FancyBboxPatch((0.3, 6.8), 4.5, 3.0,
                                  boxstyle="round,pad=0.02,rounding_size=0.2",
                                  facecolor=colors['archived'], edgecolor='#9E9E9E',
                                  linewidth=1.5, linestyle='--')
    ax.add_patch(archived_box)
    ax.text(0.5, 9.5, 'ARCHIVED (quarantine/)', ha='left', va='center',
            fontsize=9, fontweight='bold', color='#616161')
    ax.text(0.5, 9.1, '• argument_attack.py', fontsize=8, color='#757575')
    ax.text(0.5, 8.75, '• individual_differences.py', fontsize=8, color='#757575')
    ax.text(0.5, 8.4, '• cultural_meaning.py', fontsize=8, color='#757575')
    ax.text(0.5, 8.05, '• generalization_elaborate.py', fontsize=8, color='#757575')
    ax.text(0.5, 7.5, 'Ready for reintegration', fontsize=7, style='italic', color='#9E9E9E')

    # Arrows between layers
    arrow_props = dict(arrowstyle='->', color=colors['arrow'], lw=2,
                       connectionstyle='arc3,rad=0')

    # Vertical flow arrows
    ax.annotate('', xy=(7, 15.0), xytext=(7, 14.7),
                arrowprops=dict(arrowstyle='->', color=colors['arrow'], lw=2))
    ax.annotate('', xy=(7, 12.2), xytext=(7, 11.9),
                arrowprops=dict(arrowstyle='->', color=colors['arrow'], lw=2))
    ax.annotate('', xy=(7, 10.0), xytext=(7, 9.7),
                arrowprops=dict(arrowstyle='->', color=colors['arrow'], lw=2))
    ax.annotate('', xy=(7, 6.8), xytext=(7, 6.5),
                arrowprops=dict(arrowstyle='->', color=colors['arrow'], lw=2))
    ax.annotate('', xy=(7, 4.6), xytext=(7, 4.3),
                arrowprops=dict(arrowstyle='->', color=colors['arrow'], lw=2))

    # Feedback arrow (causal → epistemic)
    ax.annotate('', xy=(12.5, 12.2), xytext=(12.5, 9.8),
                arrowprops=dict(arrowstyle='->', color='#4CAF50', lw=2,
                               connectionstyle='arc3,rad=-0.3'))
    ax.text(13.2, 11.0, 'Feedback\n(gated)', fontsize=7, ha='center', color='#4CAF50')

    # Gap routing arrow
    ax.annotate('', xy=(11.5, 2.4), xytext=(11.5, 6.8),
                arrowprops=dict(arrowstyle='->', color='#FF5722', lw=1.5,
                               connectionstyle='arc3,rad=0.3', linestyle='--'))
    ax.text(12.0, 4.6, 'Gap\nrouting', fontsize=7, ha='left', color='#FF5722')

    # Integration arrow from archived
    ax.annotate('', xy=(4.8, 8.3), xytext=(5.2, 8.3),
                arrowprops=dict(arrowstyle='->', color='#9E9E9E', lw=1.5,
                               linestyle='--'))
    ax.text(5.5, 8.3, 'ATK-1\nto\nATK-4', fontsize=6, ha='left', color='#9E9E9E')

    # Legend
    legend_y = 0.8
    ax.add_patch(plt.Rectangle((1, legend_y), 0.3, 0.3, facecolor=colors['complete']))
    ax.text(1.5, legend_y + 0.15, '≥90% Complete', fontsize=8, va='center')
    ax.add_patch(plt.Rectangle((4, legend_y), 0.3, 0.3, facecolor=colors['partial']))
    ax.text(4.5, legend_y + 0.15, '<90% Complete', fontsize=8, va='center')
    ax.add_patch(plt.Rectangle((7, legend_y), 0.3, 0.3, facecolor=colors['archived'],
                               edgecolor='#9E9E9E', linestyle='--'))
    ax.text(7.5, legend_y + 0.15, 'Archived', fontsize=8, va='center')

    # Statistics
    ax.text(10, legend_y + 0.15, '2,100+ tests | 54K+ docs | 21 panel consultations',
            fontsize=8, va='center', color='#616161')

    # Date stamp
    date_str = datetime.now().strftime('%Y-%m-%d')
    ax.text(7, 0.2, f'Generated: {date_str}', ha='center', fontsize=8, color='#9E9E9E')

    # Save
    plt.tight_layout()
    plt.savefig('/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/docs/diagrams/architecture_layers_2026-02-11.png',
                dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.savefig('/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/docs/diagrams/architecture_layers_2026-02-11.pdf',
                bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"Saved: architecture_layers_2026-02-11.png and .pdf")
    plt.close()

if __name__ == '__main__':
    create_architecture_diagram()
