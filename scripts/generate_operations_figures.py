"""
generate_operations_figures.py

Phase 4: System Operations Visualizations (M-19, M-20, M-21)

Generates three comprehensive operational figures for ATLAS:
  - M-19: The Nightly Pipeline (13 stages)
  - M-20: The Recommendation Loop (circular flow)
  - M-21: AESHI Score (system health index)

Author: Article_Eater Documentation System
Created: 2026-03-02
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Wedge
from matplotlib.collections import PatchCollection
import numpy as np
from pathlib import Path

# ATLAS Visual Palette
PALETTE = {
    'deep_navy': '#1B2A4A',
    'slate_blue': '#2E5090',
    'warm_gold': '#D4A843',
    'sage_green': '#5B8C5A',
    'terracotta': '#C17B4A',
    'cool_gray': '#8B9DAF',
    'cream': '#F5F0E8',
}

OUTPUT_DIR = Path('/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/figures')


def generate_m19_nightly_pipeline():
    """
    M-19: The Nightly Pipeline - 13 Stages
    
    A flowchart showing all stages of the nightly scheduled pipeline with
    color-coding by function and failure mode annotations.
    """
    fig = plt.figure(figsize=(16, 10))
    ax = fig.add_subplot(111)
    
    # Pipeline stages with metadata
    stages = [
        {'num': 1, 'name': 'DOI Duplicate\nCheck', 'duration': '2 min', 'color': 'slate_blue'},
        {'num': 2, 'name': 'Triage Queue\nScan', 'duration': '1 min', 'color': 'slate_blue'},
        {'num': 3, 'name': 'Priority\nScoring', 'duration': '3 min', 'color': 'warm_gold'},
        {'num': 4, 'name': 'Gemini\nExtraction', 'duration': '8 min', 'color': 'slate_blue'},
        {'num': 5, 'name': 'Quality Gate\nValidation', 'duration': '4 min', 'color': 'sage_green'},
        {'num': 6, 'name': 'Credence\nComputation', 'duration': '5 min', 'color': 'warm_gold'},
        {'num': 7, 'name': 'BN\nIntegration', 'duration': '6 min', 'color': 'slate_blue'},
        {'num': 8, 'name': 'Coherence\nCheck', 'duration': '4 min', 'color': 'sage_green'},
        {'num': 9, 'name': 'Conflict\nResolution', 'duration': '5 min', 'color': 'warm_gold'},
        {'num': 10, 'name': 'Web of Belief\nUpdate', 'duration': '7 min', 'color': 'slate_blue'},
        {'num': 11, 'name': 'Gap\nDetection', 'duration': '3 min', 'color': 'warm_gold'},
        {'num': 12, 'name': 'Recommendation\nGeneration', 'duration': '4 min', 'color': 'warm_gold'},
        {'num': 13, 'name': 'Health Metrics\nReport', 'duration': '2 min', 'color': 'sage_green'},
    ]
    
    # Failure modes for annotation
    failure_modes = {
        1: 'Duplicate not detected',
        2: 'Articles missed',
        3: 'Bad scoring',
        4: 'Extraction fails',
        5: 'Invalid beliefs pass',
        6: 'Credence miscalibrated',
        7: 'Network error',
        8: 'Coherence conflict',
        9: 'Unresolved conflicts',
        10: 'Beliefs not persisted',
        11: 'Gaps not found',
        12: 'Bad recommendations',
        13: 'Metrics inaccurate',
    }
    
    # Function type colors
    color_map = {
        'slate_blue': PALETTE['slate_blue'],
        'sage_green': PALETTE['sage_green'],
        'warm_gold': PALETTE['warm_gold'],
    }
    
    # Draw OVERSEER monitoring bar at top
    overseer_y = 9.5
    overseer_bar = FancyBboxPatch((0.5, overseer_y - 0.3), 14, 0.6,
                                   boxstyle="round,pad=0.05",
                                   edgecolor=PALETTE['terracotta'],
                                   facecolor=PALETTE['cream'],
                                   linewidth=2)
    ax.add_patch(overseer_bar)
    ax.text(7.5, overseer_y, 'OVERSEER: Monitoring All 13 Stages in Real-Time',
            ha='center', va='center', fontsize=11, weight='bold',
            color=PALETTE['terracotta'])
    
    # Draw stages in 2 rows
    box_width = 0.9
    box_height = 1.0
    row_y_positions = [6.5, 3.5]
    x_start = 0.5
    x_spacing = 1.1
    
    stage_boxes = {}
    
    for i, stage in enumerate(stages):
        if i < 7:
            row_idx = 0
            col_idx = i
        else:
            row_idx = 1
            col_idx = i - 7
        
        x = x_start + col_idx * x_spacing
        y = row_y_positions[row_idx]
        
        # Draw stage box
        box = FancyBboxPatch((x - box_width/2, y - box_height/2),
                             box_width, box_height,
                             boxstyle="round,pad=0.08",
                             edgecolor=PALETTE['deep_navy'],
                             facecolor=color_map[stage['color']],
                             linewidth=1.5,
                             alpha=0.85)
        ax.add_patch(box)
        stage_boxes[stage['num']] = (x, y)
        
        # Stage number
        ax.text(x, y + 0.35, f"S{stage['num']}", ha='center', va='center',
                fontsize=9, weight='bold', color=PALETTE['cream'])
        
        # Stage name
        ax.text(x, y - 0.05, stage['name'], ha='center', va='center',
                fontsize=8, color=PALETTE['cream'])
        
        # Duration
        ax.text(x, y - 0.4, stage['duration'], ha='center', va='center',
                fontsize=7, style='italic', color=PALETTE['cream'])
    
    # Draw arrows connecting stages within rows
    for i in range(6):
        x1 = x_start + i * x_spacing + box_width/2
        x2 = x_start + (i+1) * x_spacing - box_width/2
        arrow = FancyArrowPatch((x1 + 0.05, row_y_positions[0]),
                               (x2 - 0.05, row_y_positions[0]),
                               arrowstyle='->', mutation_scale=15,
                               color=PALETTE['slate_blue'],
                               linewidth=1.5, zorder=1)
        ax.add_patch(arrow)
    
    for i in range(5):
        x1 = x_start + (i+7) * x_spacing + box_width/2
        x2 = x_start + (i+8) * x_spacing - box_width/2
        arrow = FancyArrowPatch((x1 + 0.05, row_y_positions[1]),
                               (x2 - 0.05, row_y_positions[1]),
                               arrowstyle='->', mutation_scale=15,
                               color=PALETTE['slate_blue'],
                               linewidth=1.5, zorder=1)
        ax.add_patch(arrow)
    
    # Arrow from row 1 to row 2
    arrow_down = FancyArrowPatch((x_start + 6 * x_spacing, row_y_positions[0] - 0.6),
                                (x_start + 7 * x_spacing, row_y_positions[1] + 0.6),
                                arrowstyle='->', mutation_scale=20,
                                color=PALETTE['slate_blue'],
                                linewidth=2, zorder=1)
    ax.add_patch(arrow_down)
    
    # Add failure mode annotations on alternating sides
    for num, failure in failure_modes.items():
        if num <= 7:
            x, y = stage_boxes[num]
            ax.text(x, y + 0.65, f'⚠ {failure}',
                   ha='center', va='bottom', fontsize=7,
                   color=PALETTE['terracotta'], style='italic')
        else:
            x, y = stage_boxes[num]
            ax.text(x, y - 0.75, f'⚠ {failure}',
                   ha='center', va='top', fontsize=7,
                   color=PALETTE['terracotta'], style='italic')
    
    # Legend
    legend_y = 1.5
    ax.text(0.5, legend_y + 0.3, 'Function Types:', fontsize=10, weight='bold',
            color=PALETTE['deep_navy'])
    
    colors_to_show = [
        ('Data Flow', PALETTE['slate_blue']),
        ('Quality Checks', PALETTE['sage_green']),
        ('Computation', PALETTE['warm_gold']),
    ]
    
    for idx, (label, color) in enumerate(colors_to_show):
        rect = Rectangle((0.5 + idx * 3.5, legend_y - 0.5), 0.3, 0.3,
                         facecolor=color, edgecolor=PALETTE['deep_navy'], linewidth=1)
        ax.add_patch(rect)
        ax.text(0.9 + idx * 3.5, legend_y - 0.35, label, fontsize=9,
                color=PALETTE['deep_navy'], va='center')
    
    # Total runtime at bottom
    ax.text(7.5, 0.3, 'Total Nightly Runtime: ~54 minutes | Optimal: <60 min',
            ha='center', va='center', fontsize=10, weight='bold',
            color=PALETTE['deep_navy'],
            bbox=dict(boxstyle='round', facecolor=PALETTE['warm_gold'], alpha=0.6))
    
    # Title
    ax.text(7.5, 10.8, '13 Stages Run Every Night to Keep 3,420 Beliefs Current',
            ha='center', va='top', fontsize=14, weight='bold',
            color=PALETTE['deep_navy'])
    
    # Styling
    ax.set_xlim(-0.5, 15)
    ax.set_ylim(-0.5, 11.5)
    ax.axis('off')
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / 'm19_nightly_pipeline.svg'
    plt.savefig(output_path, format='svg', facecolor=PALETTE['cream'], 
                edgecolor='none', bbox_inches='tight', dpi=150)
    plt.close()
    
    print(f"✓ M-19 saved to {output_path}")


def generate_m20_recommendation_loop():
    """
    M-20: The Recommendation Loop - Circular Flow
    
    Shows the cycle: Gap Detection → VOI Scoring → Search → Discovery →
    Triage → Extraction → Validation → Integration → (back to Gap Detection)
    """
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection='polar')
    
    # 8 stages in the recommendation loop
    stages = [
        {'name': 'Gap\nDetection', 'metric': 'VOI > 0.0', 'script': 'detect_gaps.py'},
        {'name': 'VOI\nScoring', 'metric': 'VOI Score', 'script': 'score_gaps.py'},
        {'name': 'Search\nDispatch', 'metric': 'Query Gen', 'script': 'dispatch.py'},
        {'name': 'Article\nDiscovery', 'metric': '15-20/day', 'script': 'crawl.py'},
        {'name': 'Triage\nQueue', 'metric': 'Quality > 0.6', 'script': 'triage.py'},
        {'name': 'Evidence\nExtraction', 'metric': 'Credence', 'script': 'extract.py'},
        {'name': 'Validation\nGate', 'metric': 'Quality > 0.75', 'script': 'validate.py'},
        {'name': 'Integration\nLoop', 'metric': '~50 new/day', 'script': 'integrate.py'},
    ]
    
    n_stages = len(stages)
    angles = np.linspace(0, 2*np.pi, n_stages, endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle
    
    # Switch to Cartesian for drawing
    ax_cart = fig.add_subplot(111)
    
    # Draw circular flow
    center_x, center_y = 6, 6
    radius = 4.5
    inner_radius = 2.5
    
    # Draw stages around the circle
    stage_positions = {}
    for i, (angle, stage) in enumerate(zip(angles[:-1], stages)):
        x = center_x + radius * np.cos(angle - np.pi/2)
        y = center_y + radius * np.sin(angle - np.pi/2)
        stage_positions[i] = (x, y, angle)
        
        # Stage box
        box = FancyBboxPatch((x - 0.5, y - 0.5), 1.0, 1.0,
                            boxstyle="round,pad=0.1",
                            edgecolor=PALETTE['deep_navy'],
                            facecolor=PALETTE['slate_blue'],
                            linewidth=2,
                            alpha=0.9)
        ax_cart.add_patch(box)
        
        # Stage name
        ax_cart.text(x, y + 0.15, stage['name'], ha='center', va='center',
                    fontsize=9, weight='bold', color=PALETTE['cream'])
        
        # Metric
        ax_cart.text(x, y - 0.25, stage['metric'], ha='center', va='center',
                    fontsize=7, color=PALETTE['warm_gold'], style='italic')
    
    # Draw arrows connecting stages
    for i in range(n_stages):
        x1, y1, angle1 = stage_positions[i]
        x2, y2, angle2 = stage_positions[(i + 1) % n_stages]
        
        # Curve the arrow along the circle
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle='->', mutation_scale=20,
                               color=PALETTE['warm_gold'],
                               linewidth=2.5, zorder=1,
                               connectionstyle="arc3,rad=0.3")
        ax_cart.add_patch(arrow)
    
    # Central circle with steady-state annotation
    center_circle = plt.Circle((center_x, center_y), inner_radius,
                               color=PALETTE['cream'],
                               edgecolor=PALETTE['deep_navy'],
                               linewidth=2.5,
                               alpha=0.95)
    ax_cart.add_patch(center_circle)
    
    ax_cart.text(center_x, center_y + 0.3, 'STEADY STATE',
                ha='center', va='center', fontsize=11, weight='bold',
                color=PALETTE['deep_navy'])
    ax_cart.text(center_x, center_y - 0.3, '~15-20 Articles/Day\n~50 New Beliefs/Day',
                ha='center', va='center', fontsize=9,
                color=PALETTE['terracotta'], style='italic')
    
    # Add script annotations between stages
    for i in range(n_stages):
        x1, y1, _ = stage_positions[i]
        x2, y2, _ = stage_positions[(i + 1) % n_stages]
        mid_x = (x1 + x2) / 2 + 0.5 * np.cos(np.arctan2(y2 - y1, x2 - x1) + np.pi/2)
        mid_y = (y1 + y2) / 2 + 0.5 * np.sin(np.arctan2(y2 - y1, x2 - x1) + np.pi/2)
        
        script = stages[i]['script']
        ax_cart.text(mid_x, mid_y, script, ha='center', va='center',
                    fontsize=6.5, color=PALETTE['slate_blue'],
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=PALETTE['cream'],
                             edgecolor=PALETTE['cool_gray'], linewidth=0.5))
    
    # Title
    ax_cart.text(center_x, 11.5, 'Evidence Flows in Circles: Every Gap Creates a Search,\nEvery Search Fills a Gap',
                ha='center', va='top', fontsize=13, weight='bold',
                color=PALETTE['deep_navy'])
    
    # Styling
    ax_cart.set_xlim(0, 12)
    ax_cart.set_ylim(0, 12)
    ax_cart.axis('off')
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / 'm20_recommendation_loop.svg'
    plt.savefig(output_path, format='svg', facecolor=PALETTE['cream'],
                edgecolor='none', bbox_inches='tight', dpi=150)
    plt.close()
    
    print(f"✓ M-20 saved to {output_path}")


def generate_m21_aeshi_score():
    """
    M-21: AESHI Score - System Health Index
    
    Shows 6 weighted subscores combining into one system health number.
    Each subscale is a colored horizontal bar.
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # AESHI subscores: (name, weight, current_score)
    subscores = [
        ('Extraction Quality', 0.20, 3.5),
        ('Tagging Accuracy', 0.15, 3.5),
        ('Evidence Coverage', 0.20, 6.0),
        ('Coherence Level', 0.20, 7.0),
        ('Pipeline Reliability', 0.15, 5.0),
        ('Calibration Accuracy', 0.10, 6.2),
    ]
    
    y_positions = np.arange(len(subscores))
    bar_height = 0.6
    
    # Color function based on score
    def get_color(score):
        if score < 4:
            return PALETTE['terracotta']  # Red
        elif score < 6:
            return PALETTE['warm_gold']   # Yellow
        else:
            return PALETTE['sage_green']  # Green
    
    # Draw bars
    for i, (name, weight, score) in enumerate(subscores):
        color = get_color(score)
        
        # Background bar (0-10 scale)
        bg_bar = ax.barh(i, 10, bar_height, left=0,
                        color=PALETTE['cool_gray'], alpha=0.2,
                        edgecolor=PALETTE['deep_navy'], linewidth=1)
        
        # Score bar
        score_bar = ax.barh(i, score, bar_height, left=0,
                           color=color, alpha=0.85,
                           edgecolor=PALETTE['deep_navy'], linewidth=1.5)
        
        # Weight and score label
        ax.text(score + 0.3, i, f'{score}/10 (w={weight})',
               va='center', fontsize=10, weight='bold',
               color=PALETTE['deep_navy'])
        
        # Name label
        ax.text(-0.5, i, name, ha='right', va='center',
               fontsize=10, color=PALETTE['deep_navy'], weight='bold')
    
    # Calculate weighted score
    total_weight = sum(w for _, w, _ in subscores)
    weighted_sum = sum(w * s for _, w, s in subscores)
    aeshi_score = weighted_sum / total_weight
    
    # Add target line (7.5/10)
    ax.axvline(x=7.5, color=PALETTE['sage_green'], linewidth=2.5,
              linestyle='--', alpha=0.7, label='Target: 7.5/10')
    
    # Current composite score box
    composite_text = f'AESHI Score: {aeshi_score:.1f}/10'
    ax.text(5, -1.2, composite_text, ha='center', va='top',
           fontsize=13, weight='bold', color=PALETTE['cream'],
           bbox=dict(boxstyle='round,pad=0.8',
                    facecolor=PALETTE['deep_navy'],
                    edgecolor=PALETTE['warm_gold'],
                    linewidth=2))
    
    # Formula annotation
    formula = 'AESHI = Σ(w_i × s_i) where w_i = weight, s_i = score'
    ax.text(10, 6.2, formula, ha='right', va='bottom',
           fontsize=9, style='italic', color=PALETTE['slate_blue'],
           bbox=dict(boxstyle='round,pad=0.5',
                    facecolor=PALETTE['cream'],
                    edgecolor=PALETTE['slate_blue'],
                    linewidth=1))
    
    # Color legend
    legend_y = 6.5
    colors_info = [
        ('< 4.0', PALETTE['terracotta']),
        ('4.0–6.0', PALETTE['warm_gold']),
        ('> 6.0', PALETTE['sage_green']),
    ]
    
    ax.text(-0.5, legend_y + 0.5, 'Score Ranges:', fontsize=9, weight='bold',
           ha='right', color=PALETTE['deep_navy'])
    
    for idx, (range_label, color) in enumerate(colors_info):
        rect = Rectangle((-0.5 + idx * 2.5, legend_y - 0.3), 0.4, 0.4,
                        facecolor=color, edgecolor=PALETTE['deep_navy'],
                        linewidth=1)
        ax.add_patch(rect)
        ax.text(0.1 + idx * 2.5, legend_y - 0.1, range_label, fontsize=8,
               color=PALETTE['deep_navy'], va='center')
    
    # Title
    ax.set_title('System Health at a Glance: Where ATLAS Is Strong and Where It Needs Work',
                fontsize=13, weight='bold', color=PALETTE['deep_navy'], pad=20)
    
    # Styling
    ax.set_xlim(-2, 11)
    ax.set_ylim(-2, len(subscores))
    ax.set_xlabel('Score (0–10)', fontsize=10, color=PALETTE['deep_navy'], weight='bold')
    ax.set_xticks(range(0, 11, 2))
    ax.set_xticklabels(['0', '2', '4', '6', '8', '10'])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color(PALETTE['slate_blue'])
    ax.spines['bottom'].set_linewidth(1.5)
    
    ax.set_facecolor(PALETTE['cream'])
    fig.patch.set_facecolor(PALETTE['cream'])
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / 'm21_aeshi_score.svg'
    plt.savefig(output_path, format='svg', facecolor=PALETTE['cream'],
                edgecolor='none', bbox_inches='tight', dpi=150)
    plt.close()
    
    print(f"✓ M-21 saved to {output_path}")


if __name__ == '__main__':
    print("Generating Phase 4: System Operations Visualizations...")
    print()
    
    generate_m19_nightly_pipeline()
    generate_m20_recommendation_loop()
    generate_m21_aeshi_score()
    
    print()
    print("Phase 4 complete: All 3 operational figures generated.")
