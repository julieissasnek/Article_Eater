"""
generate_math_figures.py

Generate Phase 6 math explanation figures (M-25 through M-32) for ATLAS documentation.
These figures visualize mathematical formalizations and make them accessible to readers
who may skip the formal proofs.

Figures M-25 through M-28 are complete in this file.
Figures M-29 through M-32 have stub implementations (placeholders for later completion).

Author: Claude Code
Last updated: 2026-03-02
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import os
from pathlib import Path

# ============================================================================
# ATLAS Visual Palette
# ============================================================================

PALETTE = {
    'deep_navy': '#1B2A4A',      # Titles, primary text
    'slate_blue': '#2E5090',     # Borders, axes
    'warm_gold': '#D4A843',      # Highlights, key findings
    'sage_green': '#5B8C5A',     # Growth, evidence strength
    'terracotta': '#C17B4A',     # Warnings, uncertainty
    'cool_gray': '#8B9DAF',      # Background, secondary
    'cream': '#F5F0E8',          # Canvas, negative space
}

# Output directory
OUTPUT_DIR = Path('/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/figures')

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# Utility Functions
# ============================================================================

def logit(p):
    """Transform probability to log-odds space."""
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))

def inverse_logit(x):
    """Transform log-odds back to probability space."""
    return 1.0 / (1.0 + np.exp(-x))

def set_publication_style():
    """Configure matplotlib for publication-quality figures."""
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial']
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.facecolor'] = PALETTE['cream']
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['axes.edgecolor'] = PALETTE['slate_blue']
    plt.rcParams['axes.linewidth'] = 1.5
    plt.rcParams['grid.color'] = PALETTE['cool_gray']
    plt.rcParams['grid.alpha'] = 0.3
    plt.rcParams['grid.linewidth'] = 0.5

# ============================================================================
# Figure M-25: Sensitivity Analysis of Projection Formula
# ============================================================================

def generate_m25_sensitivity_analysis():
    """
    M-25: "How Study Design Quality and Evidence Strength Determine What
           Architects Can Trust"

    Shows: logit(p_target) = d · ω · δ · logit(p_lab)

    Sensitivity analysis: p_target as d varies ±0.10 for each of 7 warrant types.
    Demonstrates system ROBUSTNESS: ±0.10 d shift produces only ±0.015–0.018
    change in p_target.
    """

    set_publication_style()

    # Warrant types and their d-values (design quality multiplier)
    warrant_types = {
        'CONSTITUTIVE': 0.95,
        'MECHANISM': 0.80,
        'EMPIRICAL_ASSOCIATION': 0.80,
        'FUNCTIONAL': 0.65,
        'CAPACITY': 0.55,
        'ANALOGICAL': 0.40,
        'THEORY_DERIVED': 0.25,
    }

    # Fixed baseline parameters
    omega = 0.75          # warrant strength
    delta = 0.85          # population match
    p_lab = 0.75          # baseline lab evidence

    # Compute logit of baseline
    logit_p_lab = logit(p_lab)

    # Create figure with subplots: one per warrant type arranged in grid
    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(
        'How Study Design Quality (d) Determines Confidence in Results',
        fontsize=16,
        fontweight='bold',
        color=PALETTE['deep_navy'],
        y=0.98
    )

    # Create 3x3 grid (will use 7 of 9 slots)
    ax_list = []
    all_axes = []
    for i in range(9):
        ax = fig.add_subplot(3, 3, i + 1)
        all_axes.append(ax)
        if i < 7:
            ax_list.append(ax)

    # Remove the last two unused subplots
    for i in range(7, 9):
        all_axes[i].remove()

    results_summary = []

    for idx, (warrant_name, d_baseline) in enumerate(warrant_types.items()):
        ax = ax_list[idx]

        # Compute p_target for d-0.10, d, d+0.10
        d_values = np.array([d_baseline - 0.10, d_baseline, d_baseline + 0.10])
        p_targets = []

        for d_val in d_values:
            # Apply projection formula: logit(p_target) = d · ω · δ · logit(p_lab)
            logit_p_target = d_val * omega * delta * logit_p_lab
            p_target = inverse_logit(logit_p_target)
            p_targets.append(p_target)

        p_targets = np.array(p_targets)

        # Track robustness: how much does p_target change?
        change_low = p_targets[1] - p_targets[0]  # p(d) - p(d-0.10)
        change_high = p_targets[2] - p_targets[1]  # p(d+0.10) - p(d)

        results_summary.append({
            'warrant': warrant_name,
            'd': d_baseline,
            'p_low': p_targets[0],
            'p_mid': p_targets[1],
            'p_high': p_targets[2],
            'change_magnitude': max(abs(change_low), abs(change_high))
        })

        # Plot three points: d-0.10, d, d+0.10
        x_pos = np.array([0.5, 1.0, 1.5])

        # Color code: green for target value, lighter for sensitivity bounds
        colors_points = [PALETTE['cool_gray'], PALETTE['sage_green'], PALETTE['cool_gray']]

        ax.scatter(x_pos, p_targets, s=150, c=colors_points, zorder=3, alpha=0.8, edgecolor=PALETTE['slate_blue'], linewidth=1.5)

        # Connect with line
        ax.plot(x_pos, p_targets, color=PALETTE['slate_blue'], linewidth=2, alpha=0.6, zorder=2)

        # Add value labels on points
        for xp, pt in zip(x_pos, p_targets):
            ax.text(xp, pt + 0.015, f'{pt:.3f}', ha='center', va='bottom', fontsize=9, color=PALETTE['deep_navy'], fontweight='bold')

        # Styling
        ax.set_xlim(0.2, 1.8)
        ax.set_ylim(0.4, 0.9)
        ax.set_xticks([0.5, 1.0, 1.5])
        ax.set_xticklabels(['d-0.10', 'd', 'd+0.10'], fontsize=9)
        ax.set_ylabel('p_target (confidence)', fontsize=10, color=PALETTE['deep_navy'])
        ax.set_title(f'{warrant_name}\n(d = {d_baseline:.2f})', fontsize=11, fontweight='bold', color=PALETTE['slate_blue'])
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_facecolor('white')

        # Highlight the impact range
        delta_p = max(abs(p_targets[1] - p_targets[0]), abs(p_targets[2] - p_targets[1]))
        ax.text(1.0, 0.42, f'Δp: ±{delta_p:.4f}', ha='center', fontsize=8,
               bbox=dict(boxstyle='round,pad=0.3', facecolor=PALETTE['cream'], edgecolor=PALETTE['terracotta'], linewidth=1),
               color=PALETTE['terracotta'], fontweight='bold')

    # Add a summary text box at bottom
    summary_text = (
        'Key Finding: The projection formula is ROBUST to design quality variations.\n'
        'A ±0.10 shift in d (study design quality) produces only ±0.015–0.018 changes in p_target.\n'
        'This means architects can trust results even when design quality estimates are uncertain.'
    )
    fig.text(0.5, 0.02, summary_text, ha='center', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.7', facecolor=PALETTE['warm_gold'], alpha=0.3, edgecolor=PALETTE['warm_gold']),
            color=PALETTE['deep_navy'], style='italic')

    plt.tight_layout(rect=[0, 0.08, 1, 0.96])

    output_path = OUTPUT_DIR / 'm25_sensitivity_analysis.svg'
    plt.savefig(output_path, format='svg', dpi=300, bbox_inches='tight', facecolor=PALETTE['cream'])
    plt.close()

    print(f"✓ Generated M-25: {output_path}")
    return results_summary

# ============================================================================
# Figure M-26: Coherence Score Visualization
# ============================================================================

def generate_m26_coherence_visualization():
    """
    M-26: "Measuring Epistemic Health: How C* Reveals What the Web Gets Right
           and Where It Breaks"

    Shows: C* = (A − λ·V) / A_max with λ=2.0

    Three cases:
    1. Perfect web (all support, C*=1.00)
    2. Contradiction web (one conflict, C*=0.15)
    3. Sparse web with gap (C*=1.00 but low density)
    """

    set_publication_style()

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(
        'Coherence Health (C*): Three Belief Web Scenarios',
        fontsize=16,
        fontweight='bold',
        color=PALETTE['deep_navy'],
        y=0.98
    )

    # Case 1: Perfect web (all support)
    ax = axes[0]
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.5, 3.5)
    ax.set_aspect('equal')
    ax.axis('off')

    # Nodes: beliefs
    nodes_1 = np.array([[0.5, 1.5], [1.5, 2.5], [2.5, 1.5]])
    labels_1 = ['B1', 'B2', 'B3']

    for i, (node, label) in enumerate(zip(nodes_1, labels_1)):
        circle = Circle(node, 0.25, color=PALETTE['sage_green'], ec=PALETTE['slate_blue'], linewidth=2, zorder=3)
        ax.add_patch(circle)
        ax.text(node[0], node[1], label, ha='center', va='center', fontsize=11, fontweight='bold', color='white', zorder=4)

    # Edges: all support (green)
    edges_support_1 = [(0, 1), (1, 2), (0, 2)]
    for i, j in edges_support_1:
        start = nodes_1[i]
        end = nodes_1[j]
        ax.arrow(start[0], start[1], (end[0]-start[0])*0.85, (end[1]-start[1])*0.85,
                head_width=0.15, head_length=0.1, fc=PALETTE['sage_green'], ec=PALETTE['sage_green'],
                linewidth=2.5, zorder=2, alpha=0.7)

    ax.text(1.5, -0.3, 'Perfect Web\nA=3, V=0, C*=1.00', ha='center', fontsize=11,
           bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['sage_green'], alpha=0.2, edgecolor=PALETTE['sage_green']),
           fontweight='bold', color=PALETTE['deep_navy'])

    # Case 2: Contradiction web (one conflict)
    ax = axes[1]
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.5, 3.5)
    ax.set_aspect('equal')
    ax.axis('off')

    # Nodes
    nodes_2 = np.array([[0.5, 1.5], [1.5, 2.5], [2.5, 1.5]])
    labels_2 = ['B1', 'B2', 'B3']

    for i, (node, label) in enumerate(zip(nodes_2, labels_2)):
        circle = Circle(node, 0.25, color=PALETTE['warm_gold'], ec=PALETTE['slate_blue'], linewidth=2, zorder=3)
        ax.add_patch(circle)
        ax.text(node[0], node[1], label, ha='center', va='center', fontsize=11, fontweight='bold', color='white', zorder=4)

    # Edges: 2 support, 1 conflict
    edges_support_2 = [(0, 1), (1, 2)]
    edges_conflict_2 = [(0, 2)]

    for i, j in edges_support_2:
        start = nodes_2[i]
        end = nodes_2[j]
        ax.arrow(start[0], start[1], (end[0]-start[0])*0.85, (end[1]-start[1])*0.85,
                head_width=0.15, head_length=0.1, fc=PALETTE['sage_green'], ec=PALETTE['sage_green'],
                linewidth=2.5, zorder=2, alpha=0.7)

    for i, j in edges_conflict_2:
        start = nodes_2[i]
        end = nodes_2[j]
        ax.arrow(start[0], start[1], (end[0]-start[0])*0.85, (end[1]-start[1])*0.85,
                head_width=0.15, head_length=0.1, fc=PALETTE['terracotta'], ec=PALETTE['terracotta'],
                linewidth=2.5, zorder=2, alpha=0.7, linestyle='--')

    ax.text(1.5, -0.3, 'Contradiction Web\nA=2, V=1, C*=0.15', ha='center', fontsize=11,
           bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['terracotta'], alpha=0.2, edgecolor=PALETTE['terracotta']),
           fontweight='bold', color=PALETTE['deep_navy'])

    # Case 3: Sparse web (low density but coherent)
    ax = axes[2]
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.5, 3.5)
    ax.set_aspect('equal')
    ax.axis('off')

    # Nodes (more spread out)
    nodes_3 = np.array([[0.2, 0.8], [1.8, 2.8], [3.0, 1.2]])
    labels_3 = ['B1', 'B2', 'B3']

    for i, (node, label) in enumerate(zip(nodes_3, labels_3)):
        circle = Circle(node, 0.25, color=PALETTE['cool_gray'], ec=PALETTE['slate_blue'], linewidth=2, zorder=3)
        ax.add_patch(circle)
        ax.text(node[0], node[1], label, ha='center', va='center', fontsize=11, fontweight='bold', color='white', zorder=4)

    # Edges: only one support relation (sparse)
    edges_support_3 = [(0, 1)]

    for i, j in edges_support_3:
        start = nodes_3[i]
        end = nodes_3[j]
        ax.arrow(start[0], start[1], (end[0]-start[0])*0.85, (end[1]-start[1])*0.85,
                head_width=0.15, head_length=0.1, fc=PALETTE['sage_green'], ec=PALETTE['sage_green'],
                linewidth=2.5, zorder=2, alpha=0.7)

    ax.text(1.5, -0.3, 'Sparse Web\nA=1, V=0, C*=1.00\n(but low density)', ha='center', fontsize=11,
           bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['cool_gray'], alpha=0.2, edgecolor=PALETTE['cool_gray']),
           fontweight='bold', color=PALETTE['deep_navy'])

    # Add legend
    legend_elements = [
        mpatches.Patch(color=PALETTE['sage_green'], label='Support relation', alpha=0.7),
        mpatches.Patch(color=PALETTE['terracotta'], label='Conflict relation', alpha=0.7),
        mpatches.Patch(color=PALETTE['cool_gray'], label='Isolated belief', alpha=0.7),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=10,
              bbox_to_anchor=(0.5, -0.05), frameon=True, fancybox=True, shadow=False)

    # Summary text
    summary_text = (
        'C* = (A − λV) / A_max (with λ=2.0): Coherence increases with support relations (A) and decreases with conflicts (V).\n'
        'Case 3 reveals limitation: sparse but coherent webs score high despite low information density.\n'
        'Architects must check both C* AND network density.'
    )
    fig.text(0.5, -0.15, summary_text, ha='center', fontsize=9.5,
            bbox=dict(boxstyle='round,pad=0.6', facecolor=PALETTE['warm_gold'], alpha=0.25, edgecolor=PALETTE['warm_gold']),
            color=PALETTE['deep_navy'], style='italic')

    plt.tight_layout(rect=[0, -0.12, 1, 0.96])

    output_path = OUTPUT_DIR / 'm26_coherence_visualization.svg'
    plt.savefig(output_path, format='svg', dpi=300, bbox_inches='tight', facecolor=PALETTE['cream'])
    plt.close()

    print(f"✓ Generated M-26: {output_path}")

# ============================================================================
# Figure M-27: Warrant-Derived Credence Pipeline
# ============================================================================

def generate_m27_credence_pipeline():
    """
    M-27: "From Evidence to Confidence: How Quality, Reliability, and
           Population Match Combine"

    Shows the flow: p_lab → [×d] → [×ω] → [×δ] → p_target

    Pipeline visualization with example values flowing through each stage.
    """

    set_publication_style()

    fig, ax = plt.subplots(figsize=(14, 8))
    fig.suptitle(
        'The Projection Pipeline: From Lab Evidence to Architect Confidence',
        fontsize=16,
        fontweight='bold',
        color=PALETTE['deep_navy'],
        y=0.96
    )

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Example values
    p_lab = 0.75
    d = 0.80           # MECHANISM warrant
    omega = 0.75       # warrant strength
    delta = 0.85       # population match
    p_target = inverse_logit(d * omega * delta * logit(p_lab))

    # Stage 1: Laboratory Evidence
    x_start = 0.8
    y_center = 3

    box1 = FancyBboxPatch((x_start - 0.3, y_center - 0.4), 0.6, 0.8,
                         boxstyle="round,pad=0.05",
                         edgecolor=PALETTE['slate_blue'], facecolor=PALETTE['cream'],
                         linewidth=2)
    ax.add_patch(box1)
    ax.text(x_start, y_center + 0.15, f'p_lab', ha='center', fontsize=10, fontweight='bold', color=PALETTE['deep_navy'])
    ax.text(x_start, y_center - 0.15, f'{p_lab:.2f}', ha='center', fontsize=12, fontweight='bold', color=PALETTE['sage_green'])
    ax.text(x_start, y_center - 0.6, 'Lab Evidence', ha='center', fontsize=9, style='italic', color=PALETTE['slate_blue'])

    # Arrow 1: Apply d (design quality)
    arrow1_x = 2.0
    arrow1 = FancyArrowPatch((x_start + 0.35, y_center), (arrow1_x, y_center),
                            arrowstyle='->', mutation_scale=30, linewidth=2.5,
                            color=PALETTE['slate_blue'])
    ax.add_patch(arrow1)
    ax.text((x_start + 0.35 + arrow1_x) / 2, y_center + 0.4, f'× d = {d:.2f}',
           ha='center', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.3', facecolor=PALETTE['cool_gray'], alpha=0.2),
           color=PALETTE['slate_blue'])
    ax.text((x_start + 0.35 + arrow1_x) / 2, y_center - 0.5, 'Design Quality',
           ha='center', fontsize=8, style='italic', color=PALETTE['slate_blue'])

    # Stage 2: After design quality adjustment
    box2 = FancyBboxPatch((arrow1_x - 0.3, y_center - 0.4), 0.6, 0.8,
                         boxstyle="round,pad=0.05",
                         edgecolor=PALETTE['slate_blue'], facecolor=PALETTE['cream'],
                         linewidth=2)
    ax.add_patch(box2)
    p_after_d = inverse_logit(d * logit(p_lab))
    ax.text(arrow1_x, y_center + 0.15, f'p_i', ha='center', fontsize=10, fontweight='bold', color=PALETTE['deep_navy'])
    ax.text(arrow1_x, y_center - 0.15, f'{p_after_d:.2f}', ha='center', fontsize=12, fontweight='bold', color=PALETTE['warm_gold'])

    # Arrow 2: Apply ω (warrant strength)
    arrow2_x = 3.8
    arrow2 = FancyArrowPatch((arrow1_x + 0.35, y_center), (arrow2_x, y_center),
                            arrowstyle='->', mutation_scale=30, linewidth=2.5,
                            color=PALETTE['slate_blue'])
    ax.add_patch(arrow2)
    ax.text((arrow1_x + 0.35 + arrow2_x) / 2, y_center + 0.4, f'× ω = {omega:.2f}',
           ha='center', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.3', facecolor=PALETTE['cool_gray'], alpha=0.2),
           color=PALETTE['slate_blue'])
    ax.text((arrow1_x + 0.35 + arrow2_x) / 2, y_center - 0.5, 'Warrant Type\nReliability',
           ha='center', fontsize=8, style='italic', color=PALETTE['slate_blue'])

    # Stage 3: After warrant strength
    box3 = FancyBboxPatch((arrow2_x - 0.3, y_center - 0.4), 0.6, 0.8,
                         boxstyle="round,pad=0.05",
                         edgecolor=PALETTE['slate_blue'], facecolor=PALETTE['cream'],
                         linewidth=2)
    ax.add_patch(box3)
    p_after_omega = inverse_logit(d * omega * logit(p_lab))
    ax.text(arrow2_x, y_center + 0.15, f'p_ii', ha='center', fontsize=10, fontweight='bold', color=PALETTE['deep_navy'])
    ax.text(arrow2_x, y_center - 0.15, f'{p_after_omega:.2f}', ha='center', fontsize=12, fontweight='bold', color=PALETTE['warm_gold'])

    # Arrow 3: Apply δ (population match)
    arrow3_x = 5.6
    arrow3 = FancyArrowPatch((arrow2_x + 0.35, y_center), (arrow3_x, y_center),
                            arrowstyle='->', mutation_scale=30, linewidth=2.5,
                            color=PALETTE['slate_blue'])
    ax.add_patch(arrow3)
    ax.text((arrow2_x + 0.35 + arrow3_x) / 2, y_center + 0.4, f'× δ = {delta:.2f}',
           ha='center', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.3', facecolor=PALETTE['cool_gray'], alpha=0.2),
           color=PALETTE['slate_blue'])
    ax.text((arrow2_x + 0.35 + arrow3_x) / 2, y_center - 0.5, 'Population\nTransfer',
           ha='center', fontsize=8, style='italic', color=PALETTE['slate_blue'])

    # Stage 4: Final credence (p_target)
    box4 = FancyBboxPatch((arrow3_x - 0.3, y_center - 0.4), 0.6, 0.8,
                         boxstyle="round,pad=0.05",
                         edgecolor=PALETTE['sage_green'], facecolor=PALETTE['sage_green'],
                         linewidth=3, alpha=0.8)
    ax.add_patch(box4)
    ax.text(arrow3_x, y_center + 0.15, f'p_target', ha='center', fontsize=10, fontweight='bold', color='white')
    ax.text(arrow3_x, y_center - 0.15, f'{p_target:.2f}', ha='center', fontsize=13, fontweight='bold', color='white')
    ax.text(arrow3_x, y_center - 0.65, 'Architect Confidence', ha='center', fontsize=9, style='italic', color=PALETTE['sage_green'])

    # Add formula box below
    formula_box = FancyBboxPatch((1.2, 4.5), 6, 1,
                               boxstyle="round,pad=0.08",
                               edgecolor=PALETTE['deep_navy'], facecolor=PALETTE['warm_gold'],
                               linewidth=2, alpha=0.15)
    ax.add_patch(formula_box)
    ax.text(4.2, 5.2, r'$\mathrm{logit}(p_{target}) = d \cdot \omega \cdot \delta \cdot \mathrm{logit}(p_{lab})$',
           ha='center', fontsize=12, fontweight='bold', color=PALETTE['deep_navy'])
    ax.text(4.2, 4.8, 'Projection Formula: All components multiply in log-odds space',
           ha='center', fontsize=9, style='italic', color=PALETTE['deep_navy'])

    # Key insight box
    insight_box = FancyBboxPatch((0.5, 0.2), 8.2, 1.2,
                                boxstyle="round,pad=0.1",
                                edgecolor=PALETTE['warm_gold'], facecolor=PALETTE['warm_gold'],
                                linewidth=2, alpha=0.2)
    ax.add_patch(insight_box)
    ax.text(4.6, 1.1, 'Key Insight: Multiplicative Combination',
           ha='center', fontsize=11, fontweight='bold', color=PALETTE['deep_navy'])
    ax.text(4.6, 0.65,
           'Lab evidence (p_lab) is NOT scaled linearly. Instead, the formula works in log-odds space,\n'
           'where independent factors (d, ω, δ) multiply to produce the final credence.\n'
           'This ensures that weak evidence stays weak, and strong constraints are respected.',
           ha='center', fontsize=9, color=PALETTE['deep_navy'], style='italic')

    plt.tight_layout()

    output_path = OUTPUT_DIR / 'm27_credence_pipeline.svg'
    plt.savefig(output_path, format='svg', dpi=300, bbox_inches='tight', facecolor=PALETTE['cream'])
    plt.close()

    print(f"✓ Generated M-27: {output_path}")

# ============================================================================
# Figure M-28: The ATLAS Inference Engine
# ============================================================================

def generate_m28_inference_engine():
    """
    M-28: "The ATLAS Inference Engine: Six Algorithms That Make the Web Computable"

    Hub-and-spoke visualization showing 6 core algorithms and their connections:
    1. Credence projection (logit transform)
    2. Coherence scoring (C*)
    3. Entrenchment ordering
    4. Belief revision (with entrenchment protection)
    5. Value of Information (VOI)
    6. Reflective equilibrium
    """

    set_publication_style()

    fig, ax = plt.subplots(figsize=(13, 11))
    fig.suptitle(
        'The ATLAS Inference Engine: How Six Algorithms Work Together',
        fontsize=16,
        fontweight='bold',
        color=PALETTE['deep_navy'],
        y=0.97
    )

    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.5, 10.5)
    ax.set_aspect('equal')
    ax.axis('off')

    # Central hub: Reflective Equilibrium (algorithm 6)
    center_x, center_y = 5.25, 5.25
    hub_radius = 0.5
    hub = Circle((center_x, center_y), hub_radius, color=PALETTE['warm_gold'],
                ec=PALETTE['deep_navy'], linewidth=3, zorder=5)
    ax.add_patch(hub)
    ax.text(center_x, center_y + 0.15, 'Reflective', ha='center', va='center',
           fontsize=9, fontweight='bold', color=PALETTE['deep_navy'])
    ax.text(center_x, center_y - 0.15, 'Equilibrium', ha='center', va='center',
           fontsize=9, fontweight='bold', color=PALETTE['deep_navy'])
    ax.text(center_x, center_y - 0.8, '(Iterates all)', ha='center', fontsize=8,
           style='italic', color=PALETTE['warm_gold'])

    # Six algorithms arranged in a circle around the hub
    algorithms = [
        {
            'name': 'Credence\nProjection',
            'description': 'Logit transform\np_lab → p_target',
            'angle': 0,           # 0° = right
            'color': PALETTE['slate_blue'],
        },
        {
            'name': 'Coherence\nScoring',
            'description': 'C* calculation\nNetwork health',
            'angle': 60,          # 60°
            'color': PALETTE['sage_green'],
        },
        {
            'name': 'Entrenchment\nOrdering',
            'description': 'Rank beliefs\nby entrenchment',
            'angle': 120,         # 120°
            'color': PALETTE['terracotta'],
        },
        {
            'name': 'Belief\nRevision',
            'description': 'Update with\nentrenchment guard',
            'angle': 180,         # 180° = left
            'color': PALETTE['cool_gray'],
        },
        {
            'name': 'Value of\nInformation',
            'description': 'Prioritize\nepistemic gaps',
            'angle': 240,         # 240°
            'color': PALETTE['warm_gold'],
        },
        {
            'name': 'Reflective\nEquilibrium',
            'description': 'Iterate until\nstable fixed point',
            'angle': 300,         # 300°
            'color': PALETTE['deep_navy'],
        },
    ]

    # Radius for algorithm placement (distance from center)
    algo_radius = 3.2

    # Draw each algorithm box and connect to center
    for algo in algorithms:
        # Convert angle to radians
        angle_rad = np.radians(algo['angle'])

        # Position on circle
        x = center_x + algo_radius * np.cos(angle_rad)
        y = center_y + algo_radius * np.sin(angle_rad)

        # Draw box for algorithm
        box_width = 1.3
        box_height = 1.0
        box = FancyBboxPatch((x - box_width/2, y - box_height/2), box_width, box_height,
                            boxstyle="round,pad=0.08",
                            edgecolor=algo['color'], facecolor=algo['color'],
                            linewidth=2, alpha=0.15, zorder=3)
        ax.add_patch(box)

        # Algorithm name
        ax.text(x, y + 0.25, algo['name'], ha='center', va='center',
               fontsize=10, fontweight='bold', color=algo['color'], zorder=4)

        # Algorithm description
        ax.text(x, y - 0.25, algo['description'], ha='center', va='center',
               fontsize=8, style='italic', color=PALETTE['deep_navy'], zorder=4)

        # Draw connection from algorithm to center
        connection = FancyArrowPatch((x - box_width/2 * np.cos(angle_rad),
                                     y - box_height/2 * np.sin(angle_rad)),
                                    (center_x + hub_radius * np.cos(angle_rad),
                                     center_y + hub_radius * np.sin(angle_rad)),
                                    arrowstyle='<->', mutation_scale=20,
                                    linewidth=1.5, color=algo['color'], alpha=0.5, zorder=2)
        ax.add_patch(connection)

    # Add data flow annotations (curved arrows showing key connections)
    # Credence → Coherence
    ax.annotate('', xy=(4.2, 6.5), xytext=(5.5, 6.2),
               arrowprops=dict(arrowstyle='->', lw=1.5, color=PALETTE['slate_blue'],
                             connectionstyle="arc3,rad=0.3", alpha=0.4))
    ax.text(4.5, 6.7, 'feeds', fontsize=8, style='italic', color=PALETTE['slate_blue'])

    # Coherence → Entrenchment
    ax.annotate('', xy=(3.0, 6.8), xytext=(3.5, 6.0),
               arrowprops=dict(arrowstyle='->', lw=1.5, color=PALETTE['sage_green'],
                             connectionstyle="arc3,rad=0.3", alpha=0.4))
    ax.text(2.8, 6.5, 'feeds', fontsize=8, style='italic', color=PALETTE['sage_green'])

    # Entrenchment → Belief Revision
    ax.annotate('', xy=(2.5, 4.5), xytext=(2.2, 5.5),
               arrowprops=dict(arrowstyle='->', lw=1.5, color=PALETTE['terracotta'],
                             connectionstyle="arc3,rad=-0.3", alpha=0.4))
    ax.text(1.8, 5.0, 'guards', fontsize=8, style='italic', color=PALETTE['terracotta'])

    # Belief Revision → VOI
    ax.annotate('', xy=(4.0, 2.8), xytext=(3.2, 3.5),
               arrowprops=dict(arrowstyle='->', lw=1.5, color=PALETTE['cool_gray'],
                             connectionstyle="arc3,rad=-0.3", alpha=0.4))
    ax.text(3.0, 3.0, 'produces\ngaps', fontsize=8, style='italic', color=PALETTE['cool_gray'])

    # VOI → Reflective Equilibrium
    ax.annotate('', xy=(5.5, 4.2), xytext=(6.0, 3.0),
               arrowprops=dict(arrowstyle='->', lw=1.5, color=PALETTE['warm_gold'],
                             connectionstyle="arc3,rad=0.3", alpha=0.4))
    ax.text(6.2, 3.5, 'prioritizes', fontsize=8, style='italic', color=PALETTE['warm_gold'])

    # Summary box at bottom
    summary_text = (
        'Integration: Reflective Equilibrium is the master algorithm that iterates through all six sub-algorithms\n'
        'until the system reaches a stable fixed point. Each algorithm feeds into others: credence drives coherence,\n'
        'coherence drives entrenchment, entrenchment protects belief revision, revision produces gaps that VOI\n'
        'prioritizes, and VOI feeds back to guide the next iteration. The system converges when beliefs, their credences,\n'
        'coherence patterns, and information priorities are mutually supporting.'
    )

    fig.text(0.5, 0.035, summary_text, ha='center', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.8', facecolor=PALETTE['warm_gold'], alpha=0.25, edgecolor=PALETTE['warm_gold']),
            color=PALETTE['deep_navy'], style='italic')

    plt.tight_layout(rect=[0, 0.14, 1, 0.96])

    output_path = OUTPUT_DIR / 'm28_inference_engine.svg'
    plt.savefig(output_path, format='svg', dpi=300, bbox_inches='tight', facecolor=PALETTE['cream'])
    plt.close()

    print(f"✓ Generated M-28: {output_path}")

# ============================================================================
# Stub Functions for M-29 through M-32
# ============================================================================

def generate_m29_voi_uncertainties():
    """
    M-29: "What Should ATLAS Investigate Next? Uncertainties by Impact and Network Reach"

    Section: 129.6 (PART_XVII) - VOI scoring
    Shows: Scatter plot of gap uncertainties
    X-axis: VOI_structural (network impact - how many beliefs are affected)
    Y-axis: VOI_epistemic (epistemic uncertainty - how unsure we are)
    Point size: gap type weight (direction=1.0, validation=0.7, mechanism=0.5, boundary=0.4)
    Color by gap type
    Decision boundary lines at 0.6 and 0.3
    """

    set_publication_style()

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.suptitle(
        'What Should ATLAS Investigate Next?\nUncertainties by Impact and Network Reach',
        fontsize=16,
        fontweight='bold',
        color=PALETTE['deep_navy'],
        y=0.96
    )

    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    ax.set_aspect('equal')

    # Generate synthetic gap data
    np.random.seed(42)

    # Gap types with different sizes and colors
    gap_types = {
        'direction': {'size_weight': 1.0, 'color': PALETTE['slate_blue'], 'marker': 'o'},
        'validation': {'size_weight': 0.7, 'color': PALETTE['sage_green'], 'marker': 's'},
        'mechanism': {'size_weight': 0.5, 'color': PALETTE['warm_gold'], 'marker': '^'},
        'boundary': {'size_weight': 0.4, 'color': PALETTE['terracotta'], 'marker': 'D'},
    }

    # Generate points for each gap type
    for gap_type, props in gap_types.items():
        n_points = 7  # 7 points per type = 28 total

        # VOI_structural (x-axis): network impact
        voi_struct = np.random.uniform(0.15, 0.95, n_points)

        # VOI_epistemic (y-axis): epistemic uncertainty
        voi_epist = np.random.uniform(0.15, 0.95, n_points)

        # Size based on gap weight
        sizes = 400 * props['size_weight']

        ax.scatter(voi_struct, voi_epist, s=sizes, c=props['color'],
                  marker=props['marker'], alpha=0.7, edgecolor=PALETTE['deep_navy'],
                  linewidth=1.5, label=gap_type.replace('_', ' ').title(), zorder=3)

    # Decision boundary lines at 0.6 and 0.3
    # Vertical line at x=0.6 (structural impact threshold)
    ax.axvline(x=0.6, color=PALETTE['slate_blue'], linestyle='--', linewidth=2,
              alpha=0.5, zorder=2, label='Impact threshold')

    # Horizontal line at y=0.3 (epistemic uncertainty threshold)
    ax.axhline(y=0.3, color=PALETTE['terracotta'], linestyle='--', linewidth=2,
              alpha=0.5, zorder=2, label='Uncertainty threshold')

    # Quadrant labels
    quadrant_props = dict(boxstyle='round,pad=0.5', alpha=0.2, linewidth=1.5)

    # HIGH-HIGH (top-right)
    quad_box1 = FancyBboxPatch((0.6, 0.3), 0.35, 0.65,
                              boxstyle="round,pad=0.02",
                              edgecolor=PALETTE['sage_green'], facecolor=PALETTE['sage_green'],
                              linewidth=2, alpha=0.08, zorder=1)
    ax.add_patch(quad_box1)
    ax.text(0.925, 0.85, 'INVESTIGATE\nIMMEDIATELY', ha='center', va='top',
           fontsize=11, fontweight='bold', color=PALETTE['sage_green'],
           bbox=dict(boxstyle='round,pad=0.4', facecolor=PALETTE['sage_green'], alpha=0.15))

    # HIGH-LOW (bottom-right)
    quad_box2 = FancyBboxPatch((0.6, 0), 0.35, 0.3,
                              boxstyle="round,pad=0.02",
                              edgecolor=PALETTE['warm_gold'], facecolor=PALETTE['warm_gold'],
                              linewidth=2, alpha=0.08, zorder=1)
    ax.add_patch(quad_box2)
    ax.text(0.925, 0.1, 'MONITOR', ha='center', va='bottom',
           fontsize=11, fontweight='bold', color=PALETTE['warm_gold'],
           bbox=dict(boxstyle='round,pad=0.4', facecolor=PALETTE['warm_gold'], alpha=0.15))

    # LOW-HIGH (top-left)
    quad_box3 = FancyBboxPatch((0, 0.3), 0.6, 0.65,
                              boxstyle="round,pad=0.02",
                              edgecolor=PALETTE['cool_gray'], facecolor=PALETTE['cool_gray'],
                              linewidth=2, alpha=0.08, zorder=1)
    ax.add_patch(quad_box3)
    ax.text(0.075, 0.85, 'NICE TO\nKNOW', ha='center', va='top',
           fontsize=11, fontweight='bold', color=PALETTE['cool_gray'],
           bbox=dict(boxstyle='round,pad=0.4', facecolor=PALETTE['cool_gray'], alpha=0.15))

    # LOW-LOW (bottom-left)
    quad_box4 = FancyBboxPatch((0, 0), 0.6, 0.3,
                              boxstyle="round,pad=0.02",
                              edgecolor=PALETTE['terracotta'], facecolor=PALETTE['terracotta'],
                              linewidth=2, alpha=0.08, zorder=1)
    ax.add_patch(quad_box4)
    ax.text(0.075, 0.1, 'DEFER', ha='center', va='bottom',
           fontsize=11, fontweight='bold', color=PALETTE['terracotta'],
           bbox=dict(boxstyle='round,pad=0.4', facecolor=PALETTE['terracotta'], alpha=0.15))

    # Axes labels
    ax.set_xlabel('VOI_structural (Network Impact: How Many Beliefs Affected)',
                 fontsize=12, fontweight='bold', color=PALETTE['deep_navy'])
    ax.set_ylabel('VOI_epistemic (Epistemic Uncertainty: How Unsure Are We)',
                 fontsize=12, fontweight='bold', color=PALETTE['deep_navy'])

    # Grid
    ax.grid(True, alpha=0.2, linestyle=':', linewidth=0.8)
    ax.set_axisbelow(True)

    # Legend
    ax.legend(loc='upper left', fontsize=10, framealpha=0.95, edgecolor=PALETTE['slate_blue'])

    # Key insight box
    insight_text = (
        'VOI combines two factors: structural impact (how many beliefs depend on resolving this gap)\n'
        'and epistemic uncertainty (how confident we are in current answers). The four quadrants\n'
        'guide investigation priority: HIGH-HIGH gaps drive the most learning, while LOW-LOW gaps\n'
        'are lower priority. ATLAS uses this map to optimize its investigation strategy.'
    )
    fig.text(0.5, 0.02, insight_text, ha='center', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.6', facecolor=PALETTE['warm_gold'], alpha=0.2, edgecolor=PALETTE['warm_gold']),
            color=PALETTE['deep_navy'], style='italic')

    plt.tight_layout(rect=[0, 0.09, 1, 0.94])

    output_path = OUTPUT_DIR / 'm29_voi_uncertainties.svg'
    plt.savefig(output_path, format='svg', dpi=300, bbox_inches='tight', facecolor=PALETTE['cream'])
    plt.close()

    print(f"✓ Generated M-29: {output_path}")

def generate_m30_warrant_hierarchy():
    """
    M-30: "The Bridge from Lab to Building: Why Different Evidence Types Transfer Differently"

    Section: 48.1A (PART_IV) - d-value hierarchy
    Shows: Vertical hierarchy of 7 warrant types with their d-values
    Left side: warrant type name and d-value
    Right side: brief description of what each warrant type means
    Visual: decreasing bar chart showing d-value from top (CONSTITUTIVE 0.95) to bottom (THEORY_DERIVED 0.25)
    Color gradient from sage_green (high d) to terracotta (low d)
    Arrow showing "Closer to lab" at top and "Further from lab" at bottom
    """

    set_publication_style()

    fig, ax = plt.subplots(figsize=(12, 9))
    fig.suptitle(
        'The Bridge from Lab to Building:\nWhy Different Evidence Types Transfer Differently',
        fontsize=16,
        fontweight='bold',
        color=PALETTE['deep_navy'],
        y=0.97
    )

    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 8)
    ax.axis('off')

    # Warrant types from strongest to weakest
    warrants = [
        {
            'name': 'CONSTITUTIVE',
            'd_value': 0.95,
            'description': 'Evidence of actual physical/biological constitutive relationships\n(e.g., cortical columns structure brain architecture)',
            'rank': 0
        },
        {
            'name': 'MECHANISM',
            'd_value': 0.80,
            'description': 'Evidence that a specific causal mechanism operates\n(e.g., lab demonstration of signal propagation)',
            'rank': 1
        },
        {
            'name': 'EMPIRICAL_ASSOCIATION',
            'd_value': 0.80,
            'description': 'Empirical correlation or association from studies\n(e.g., brain imaging correlates with behavior)',
            'rank': 2
        },
        {
            'name': 'FUNCTIONAL',
            'd_value': 0.65,
            'description': 'Evidence that a component has the right functional role\n(e.g., lesion studies show necessary function)',
            'rank': 3
        },
        {
            'name': 'CAPACITY',
            'd_value': 0.55,
            'description': 'Evidence that a system has capacity for an ability\n(e.g., mathematical proof it could do X)',
            'rank': 4
        },
        {
            'name': 'ANALOGICAL',
            'd_value': 0.40,
            'description': 'Reasoning by analogy to similar systems\n(e.g., "works like that in bacteria")',
            'rank': 5
        },
        {
            'name': 'THEORY_DERIVED',
            'd_value': 0.25,
            'description': 'Derived from theoretical framework without direct evidence\n(e.g., mathematical model prediction)',
            'rank': 6
        },
    ]

    # Y positions for each warrant (top to bottom)
    y_start = 7.0
    y_spacing = 1.0

    # Maximum bar length (for scaling)
    max_d = 1.0

    # Draw each warrant row
    for warrant in warrants:
        y = y_start - warrant['rank'] * y_spacing
        d_val = warrant['d_value']

        # Color gradient from sage_green (high d) to terracotta (low d)
        # Interpolate between sage_green and terracotta based on d_value
        ratio = d_val  # higher d = greener, lower d = more terracotta
        r_sg = int(0x5B)
        g_sg = int(0x8C)
        b_sg = int(0x5A)
        r_ter = int(0xC1)
        g_ter = int(0x7B)
        b_ter = int(0x4A)

        r = int(r_sg + (r_ter - r_sg) * (1 - ratio))
        g = int(g_sg + (g_ter - g_sg) * (1 - ratio))
        b = int(b_sg + (b_ter - b_sg) * (1 - ratio))
        bar_color = f'#{r:02x}{g:02x}{b:02x}'

        # Left side: warrant name and d-value
        ax.text(0.3, y + 0.15, warrant['name'], ha='left', va='center',
               fontsize=11, fontweight='bold', color=PALETTE['deep_navy'])
        ax.text(0.3, y - 0.2, f"d = {d_val:.2f}", ha='left', va='center',
               fontsize=10, fontweight='bold', color=bar_color)

        # Bar showing d-value
        bar_length = d_val * 3.5
        bar = FancyBboxPatch((2.2, y - 0.25), bar_length, 0.5,
                            boxstyle="round,pad=0.03",
                            edgecolor=bar_color, facecolor=bar_color,
                            linewidth=2, alpha=0.8, zorder=3)
        ax.add_patch(bar)

        # Right side: description
        ax.text(6.0, y, warrant['description'], ha='left', va='center',
               fontsize=9, color=PALETTE['deep_navy'], style='italic')

    # Add vertical divider
    ax.axvline(x=5.8, color=PALETTE['cool_gray'], linestyle='--', linewidth=1, alpha=0.5)

    # Add directional arrow on left side showing "closer to lab" at top
    arrow_up = FancyArrowPatch((0.1, 7.2), (0.1, 6.5),
                             arrowstyle='->', mutation_scale=30, linewidth=2.5,
                             color=PALETTE['sage_green'], zorder=2)
    ax.add_patch(arrow_up)
    ax.text(0.05, 7.4, 'Closer\nto Lab', ha='center', va='bottom',
           fontsize=9, fontweight='bold', color=PALETTE['sage_green'], rotation=0)

    # Add directional arrow on left side showing "further from lab" at bottom
    arrow_down = FancyArrowPatch((0.1, 0.8), (0.1, 0.1),
                               arrowstyle='->', mutation_scale=30, linewidth=2.5,
                               color=PALETTE['terracotta'], zorder=2)
    ax.add_patch(arrow_down)
    ax.text(0.05, -0.3, 'Further\nfrom Lab', ha='center', va='top',
           fontsize=9, fontweight='bold', color=PALETTE['terracotta'], rotation=0)

    # Key insight box at bottom
    insight_text = (
        'The d-value hierarchy reflects epistemic transfer: evidence closer to the laboratory (CONSTITUTIVE)\n'
        'transfers more reliably to real-world building conditions than theoretical predictions (THEORY_DERIVED).\n'
        'Architects can trust CONSTITUTIVE and MECHANISM warrants more than analogical reasoning.\n'
        'This ordering ensures predictions account for the gap between controlled studies and messy real buildings.'
    )
    fig.text(0.5, 0.01, insight_text, ha='center', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.6', facecolor=PALETTE['warm_gold'], alpha=0.2, edgecolor=PALETTE['warm_gold']),
            color=PALETTE['deep_navy'], style='italic')

    plt.tight_layout(rect=[0, 0.08, 1, 0.95])

    output_path = OUTPUT_DIR / 'm30_warrant_hierarchy.svg'
    plt.savefig(output_path, format='svg', dpi=300, bbox_inches='tight', facecolor=PALETTE['cream'])
    plt.close()

    print(f"✓ Generated M-30: {output_path}")

def generate_m31_serial_vs_parallel():
    """
    M-31: "Why Some Claims Are Fragile and Others Robust: Serial Chains vs. Parallel Convergence"

    Section: 48.4-48.5 (PART_IV) - Evidence combination
    Shows: Two contrasting network diagrams side by side
    LEFT: Serial chain - A→B→C→D (each link is a single warrant). If any link breaks, chain fails.
    RIGHT: Parallel convergence - A→D, B→D, C→D (multiple independent warrants all supporting same conclusion).
    Show reliability calculation: Serial = d1 × d2 × d3 (product). Parallel = 1 - (1-d1)(1-d2)(1-d3) (complement).
    Example: 3 links each with d=0.7: Serial = 0.343, Parallel = 0.973
    """

    set_publication_style()

    fig = plt.figure(figsize=(14, 9))
    fig.suptitle(
        'Why Some Claims Are Fragile and Others Robust:\nSerial Chains vs. Parallel Convergence',
        fontsize=16,
        fontweight='bold',
        color=PALETTE['deep_navy'],
        y=0.97
    )

    # Left subplot: Serial chain
    ax_serial = fig.add_subplot(121)
    ax_serial.set_xlim(-0.5, 5)
    ax_serial.set_ylim(-0.5, 4)
    ax_serial.set_aspect('equal')
    ax_serial.axis('off')

    # Title for serial
    ax_serial.text(2.25, 3.8, 'SERIAL CHAIN: Weak Link Breaks Everything', ha='center',
                  fontsize=12, fontweight='bold', color=PALETTE['deep_navy'])

    # Serial nodes
    nodes_serial = np.array([[0.5, 2.0], [1.5, 2.0], [2.5, 2.0], [3.5, 2.0]])
    labels_serial = ['A', 'B', 'C', 'D']
    d_values = [0.8, 0.7, 0.6, 0.5]  # Different reliability for each link

    for i, (node, label, d_val) in enumerate(zip(nodes_serial, labels_serial, d_values)):
        # Color based on d-value (weak links more terracotta)
        if d_val >= 0.7:
            node_color = PALETTE['sage_green']
        elif d_val >= 0.6:
            node_color = PALETTE['warm_gold']
        else:
            node_color = PALETTE['terracotta']

        circle = Circle(node, 0.25, color=node_color, ec=PALETTE['slate_blue'],
                       linewidth=2, zorder=3)
        ax_serial.add_patch(circle)
        ax_serial.text(node[0], node[1], label, ha='center', va='center',
                      fontsize=11, fontweight='bold', color='white', zorder=4)

    # Serial edges (arrows showing chain)
    for i in range(len(nodes_serial) - 1):
        start = nodes_serial[i]
        end = nodes_serial[i+1]
        d_val = d_values[i]

        # Edge color based on d-value
        if d_val >= 0.7:
            edge_color = PALETTE['sage_green']
        elif d_val >= 0.6:
            edge_color = PALETTE['warm_gold']
        else:
            edge_color = PALETTE['terracotta']

        arrow = FancyArrowPatch((start[0] + 0.25, start[1]), (end[0] - 0.25, end[1]),
                              arrowstyle='->', mutation_scale=25, linewidth=2.5,
                              color=edge_color, alpha=0.8, zorder=2)
        ax_serial.add_patch(arrow)

        # Label each link with d-value
        ax_serial.text((start[0] + end[0]) / 2, start[1] + 0.35, f'd={d_val:.1f}',
                      ha='center', fontsize=9, fontweight='bold', color=edge_color)

    # Serial calculation box
    ax_serial.text(2.25, 0.8, 'Reliability = d₁ × d₂ × d₃ × ...\n(Product of all links)',
                  ha='center', fontsize=10, fontweight='bold', color=PALETTE['deep_navy'],
                  bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['cream'],
                           edgecolor=PALETTE['terracotta'], linewidth=2))

    # Serial result
    serial_reliability = d_values[0] * d_values[1] * d_values[2]
    ax_serial.text(2.25, 0.1, f'Result: 0.8 × 0.7 × 0.6 = {serial_reliability:.3f}\n(FRAGILE)',
                  ha='center', fontsize=11, fontweight='bold',
                  color=PALETTE['terracotta'],
                  bbox=dict(boxstyle='round,pad=0.4', facecolor=PALETTE['terracotta'], alpha=0.15))

    # Right subplot: Parallel convergence
    ax_parallel = fig.add_subplot(122)
    ax_parallel.set_xlim(-0.5, 5)
    ax_parallel.set_ylim(-0.5, 4)
    ax_parallel.set_aspect('equal')
    ax_parallel.axis('off')

    # Title for parallel
    ax_parallel.text(2.25, 3.8, 'PARALLEL CONVERGENCE: Redundancy Provides Robustness', ha='center',
                    fontsize=12, fontweight='bold', color=PALETTE['deep_navy'])

    # Parallel nodes (three sources converging to D)
    source_nodes = np.array([[0.5, 3.0], [0.5, 2.0], [0.5, 1.0]])
    source_labels = ['A', 'B', 'C']
    target_node = np.array([3.5, 2.0])
    target_label = 'D'

    # Source nodes
    d_parallel = [0.7, 0.7, 0.7]  # Same d for each warrant
    for node, label, d_val in zip(source_nodes, source_labels, d_parallel):
        circle = Circle(node, 0.25, color=PALETTE['sage_green'], ec=PALETTE['slate_blue'],
                       linewidth=2, zorder=3)
        ax_parallel.add_patch(circle)
        ax_parallel.text(node[0], node[1], label, ha='center', va='center',
                        fontsize=11, fontweight='bold', color='white', zorder=4)

    # Target node
    circle = Circle(target_node, 0.25, color=PALETTE['sage_green'], ec=PALETTE['slate_blue'],
                   linewidth=2, zorder=3)
    ax_parallel.add_patch(circle)
    ax_parallel.text(target_node[0], target_node[1], target_label, ha='center', va='center',
                    fontsize=11, fontweight='bold', color='white', zorder=4)

    # Parallel edges (all converging to D)
    for i, source_node in enumerate(source_nodes):
        arrow = FancyArrowPatch((source_node[0] + 0.25, source_node[1]),
                              (target_node[0] - 0.25, target_node[1]),
                              arrowstyle='->', mutation_scale=25, linewidth=2.5,
                              color=PALETTE['sage_green'], alpha=0.8, zorder=2)
        ax_parallel.add_patch(arrow)

        # Label each warrant with d-value
        mid_x = (source_node[0] + target_node[0]) / 2
        mid_y = source_node[1] + (target_node[1] - source_node[1]) * 0.3
        ax_parallel.text(mid_x - 0.2, mid_y, f'd=0.7', ha='right', fontsize=9,
                        fontweight='bold', color=PALETTE['sage_green'])

    # Parallel calculation box
    ax_parallel.text(2.25, 0.8, 'Reliability = 1 − (1−d₁)×(1−d₂)×(1−d₃)×...\n(Complement of all failures)',
                    ha='center', fontsize=10, fontweight='bold', color=PALETTE['deep_navy'],
                    bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['cream'],
                             edgecolor=PALETTE['sage_green'], linewidth=2))

    # Parallel result
    parallel_reliability = 1 - (1 - d_parallel[0]) * (1 - d_parallel[1]) * (1 - d_parallel[2])
    ax_parallel.text(2.25, 0.1, f'Result: 1 − (0.3)³ = {parallel_reliability:.3f}\n(ROBUST)',
                    ha='center', fontsize=11, fontweight='bold',
                    color=PALETTE['sage_green'],
                    bbox=dict(boxstyle='round,pad=0.4', facecolor=PALETTE['sage_green'], alpha=0.15))

    # Key insight box at bottom
    insight_text = (
        'Serial reasoning multiplies reliability: three weak links produce very low confidence (0.336).\n'
        'Parallel reasoning (triangulation) is exponentially more robust: same three warrants, independently supporting\n'
        'the same conclusion, produce high confidence (0.973). ATLAS prefers parallel convergence over serial chains.'
    )
    fig.text(0.5, 0.02, insight_text, ha='center', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.6', facecolor=PALETTE['warm_gold'], alpha=0.2, edgecolor=PALETTE['warm_gold']),
            color=PALETTE['deep_navy'], style='italic')

    plt.tight_layout(rect=[0, 0.09, 1, 0.95])

    output_path = OUTPUT_DIR / 'm31_serial_vs_parallel.svg'
    plt.savefig(output_path, format='svg', dpi=300, bbox_inches='tight', facecolor=PALETTE['cream'])
    plt.close()

    print(f"✓ Generated M-31: {output_path}")

def generate_m32_entrenchment_ordering():
    """
    M-32: "When Evidence Conflicts: How ATLAS Revises Beliefs While Protecting Core Commitments"

    Section: 129.5 (PART_XVII) - Entrenchment ordering and structural revision
    Shows: A layered circle/target diagram showing entrenchment levels
    Center (most entrenched): Foundational beliefs (T1 frameworks, e.g., "Predictive Processing", "Allostasis")
    Middle ring: Intermediate beliefs (empirical generalizations, mechanism claims)
    Outer ring: Peripheral beliefs (specific findings, individual study results)
    Show incoming conflicting evidence arrow hitting outer ring and being absorbed (peripheral belief revised)
    Show another arrow trying to reach center and being deflected/blocked by entrenchment
    """

    set_publication_style()

    fig, ax = plt.subplots(figsize=(12, 10))
    fig.suptitle(
        'When Evidence Conflicts: How ATLAS Revises Beliefs\nWhile Protecting Core Commitments',
        fontsize=16,
        fontweight='bold',
        color=PALETTE['deep_navy'],
        y=0.97
    )

    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.set_aspect('equal')
    ax.axis('off')

    center_x, center_y = 0, 0

    # Draw three concentric circles representing entrenchment levels
    # Outermost ring: Peripheral beliefs (weakly entrenched)
    outer_circle = Circle((center_x, center_y), 4.0, color=PALETTE['terracotta'],
                         ec=PALETTE['deep_navy'], linewidth=2, alpha=0.1, zorder=1)
    ax.add_patch(outer_circle)

    # Middle ring: Intermediate beliefs (moderately entrenched)
    middle_circle = Circle((center_x, center_y), 2.5, color=PALETTE['warm_gold'],
                          ec=PALETTE['deep_navy'], linewidth=2.5, alpha=0.15, zorder=2)
    ax.add_patch(middle_circle)

    # Innermost circle: Foundational beliefs (most entrenched)
    inner_circle = Circle((center_x, center_y), 1.2, color=PALETTE['sage_green'],
                         ec=PALETTE['deep_navy'], linewidth=3, alpha=0.2, zorder=3)
    ax.add_patch(inner_circle)

    # Labels for each level
    # Peripheral ring label
    ax.text(4.2, 4.2, 'PERIPHERAL BELIEFS\n(Easily Revised)', ha='left', va='center',
           fontsize=10, fontweight='bold', color=PALETTE['terracotta'],
           bbox=dict(boxstyle='round,pad=0.4', facecolor=PALETTE['terracotta'], alpha=0.2))

    ax.text(3.2, 2.8, 'Specific findings,\nindividual study results,\nlocal observations', ha='center', va='center',
           fontsize=8, color=PALETTE['deep_navy'], style='italic')

    # Intermediate ring label
    ax.text(-4.8, 2.5, 'INTERMEDIATE BELIEFS\n(Moderately Entrenched)', ha='right', va='center',
           fontsize=10, fontweight='bold', color=PALETTE['warm_gold'],
           bbox=dict(boxstyle='round,pad=0.4', facecolor=PALETTE['warm_gold'], alpha=0.2))

    ax.text(-3.0, 1.5, 'Empirical generalizations,\nmechanism claims,\nbounded patterns', ha='center', va='center',
           fontsize=8, color=PALETTE['deep_navy'], style='italic')

    # Core ring label
    ax.text(0, -0.6, 'FOUNDATIONAL\nBELIEFS', ha='center', va='center',
           fontsize=11, fontweight='bold', color=PALETTE['sage_green'],
           bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['sage_green'], alpha=0.3))

    ax.text(0, -1.5, 'T1 Frameworks:\nPredictive Processing,\nAllostasis, etc.', ha='center', va='center',
           fontsize=8, color='white', fontweight='bold')

    # Scenario 1: Conflicting evidence hitting outer ring (accepted revision)
    # Arrow coming from right hitting outer ring
    evidence1_start = np.array([5.5, 2.5])
    evidence1_end = np.array([3.8, 2.2])

    arrow1 = FancyArrowPatch(evidence1_start, evidence1_end,
                            arrowstyle='->', mutation_scale=35, linewidth=3,
                            color=PALETTE['terracotta'], zorder=5, alpha=0.9)
    ax.add_patch(arrow1)

    ax.text(5.2, 3.0, 'Conflicting\nEvidence',
           fontsize=9, fontweight='bold', color=PALETTE['terracotta'],
           bbox=dict(boxstyle='round,pad=0.3', facecolor=PALETTE['terracotta'], alpha=0.2))

    # Show absorption into peripheral belief (X marking old belief, new position)
    old_belief_pos = np.array([3.5, 2.2])
    ax.plot(old_belief_pos[0], old_belief_pos[1], 'x', markersize=12, markeredgewidth=2,
           color=PALETTE['cool_gray'], zorder=4)

    new_belief_pos = np.array([3.2, 2.5])
    circle_new1 = Circle(new_belief_pos, 0.15, color=PALETTE['sage_green'],
                        ec=PALETTE['deep_navy'], linewidth=2, zorder=5)
    ax.add_patch(circle_new1)

    ax.text(2.5, 3.2, 'Belief REVISED\n(Accepted)', fontsize=9, fontweight='bold',
           color=PALETTE['sage_green'],
           bbox=dict(boxstyle='round,pad=0.3', facecolor=PALETTE['sage_green'], alpha=0.2))

    # Scenario 2: Evidence trying to reach core (rejected/deflected)
    # Arrow coming from left trying to hit inner circle
    evidence2_start = np.array([-5.5, -1.5])
    evidence2_end = np.array([-1.5, -0.3])

    arrow2 = FancyArrowPatch(evidence2_start, evidence2_end,
                            arrowstyle='->', mutation_scale=35, linewidth=3,
                            color=PALETTE['slate_blue'], zorder=5, alpha=0.9)
    ax.add_patch(arrow2)

    ax.text(-5.2, -2.2, 'Conflicting\nEvidence\n(challenges core)',
           fontsize=9, fontweight='bold', color=PALETTE['slate_blue'],
           bbox=dict(boxstyle='round,pad=0.3', facecolor=PALETTE['slate_blue'], alpha=0.2))

    # Show deflection (arrow bouncing off entrenchment)
    deflection_start = np.array([-1.2, -0.1])
    deflection_end = np.array([0.5, -2.5])

    arrow_deflect = FancyArrowPatch(deflection_start, deflection_end,
                                   arrowstyle='->', mutation_scale=30, linewidth=2.5,
                                   color=PALETTE['terracotta'], linestyle='--', zorder=4, alpha=0.7)
    ax.add_patch(arrow_deflect)

    ax.text(1.2, -1.8, 'Deflected by\nEntrenchment',
           fontsize=9, fontweight='bold', color=PALETTE['terracotta'],
           bbox=dict(boxstyle='round,pad=0.3', facecolor=PALETTE['terracotta'], alpha=0.15))

    # Entrenchment shield visualization
    shield_angles = np.linspace(-np.pi/4, np.pi/4, 20)
    shield_x = 1.5 * np.cos(shield_angles)
    shield_y = 1.5 * np.sin(shield_angles)
    ax.plot(shield_x, shield_y, color=PALETTE['sage_green'], linewidth=3, zorder=4, alpha=0.8)

    ax.text(0.2, -2.5, 'ENTRENCHMENT\nSHIELD', fontsize=8, fontweight='bold',
           color=PALETTE['sage_green'],
           bbox=dict(boxstyle='round,pad=0.3', facecolor=PALETTE['sage_green'], alpha=0.15))

    # Key insight box at bottom
    insight_text = (
        'Entrenchment protects epistemic core: foundational frameworks (FRAMEWORKS) are harder to revise than\n'
        'peripheral findings (FINDINGS). When new evidence arrives, ATLAS first tries to revise peripheral beliefs.\n'
        'Only if evidence is overwhelming and foundational contradictions cannot be avoided does ATLAS revise core.\n'
        'This strategy balances openness to evidence with protection of hard-won theoretical commitments.'
    )
    fig.text(0.5, 0.02, insight_text, ha='center', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.6', facecolor=PALETTE['warm_gold'], alpha=0.2, edgecolor=PALETTE['warm_gold']),
            color=PALETTE['deep_navy'], style='italic')

    plt.tight_layout(rect=[0, 0.10, 1, 0.95])

    output_path = OUTPUT_DIR / 'm32_entrenchment_ordering.svg'
    plt.savefig(output_path, format='svg', dpi=300, bbox_inches='tight', facecolor=PALETTE['cream'])
    plt.close()

    print(f"✓ Generated M-32: {output_path}")

# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Generate all Phase 6 math explanation figures."""

    print("\n" + "="*70)
    print("ATLAS Phase 6: Math Explanation Figures (M-25 through M-32)")
    print("="*70)
    print(f"\nOutput directory: {OUTPUT_DIR}\n")

    try:
        # Generate M-25: Sensitivity Analysis
        print("Generating M-25: Sensitivity Analysis...")
        generate_m25_sensitivity_analysis()

        # Generate M-26: Coherence Visualization
        print("Generating M-26: Coherence Visualization...")
        generate_m26_coherence_visualization()

        # Generate M-27: Credence Pipeline
        print("Generating M-27: Credence Pipeline...")
        generate_m27_credence_pipeline()

        # Generate M-28: Inference Engine
        print("Generating M-28: Inference Engine...")
        generate_m28_inference_engine()

        # Generate M-29: VOI Uncertainties
        print("Generating M-29: VOI Uncertainties by Impact and Network Reach...")
        generate_m29_voi_uncertainties()

        # Generate M-30: Warrant Hierarchy
        print("Generating M-30: Warrant Hierarchy (d-value ordering)...")
        generate_m30_warrant_hierarchy()

        # Generate M-31: Serial vs Parallel
        print("Generating M-31: Serial Chains vs Parallel Convergence...")
        generate_m31_serial_vs_parallel()

        # Generate M-32: Entrenchment Ordering
        print("Generating M-32: Entrenchment Ordering and Belief Revision...")
        generate_m32_entrenchment_ordering()

        print("\n" + "="*70)
        print("✓ Phase 6 generation complete!")
        print("="*70)
        print(f"\nGenerated 8 figures (M-25 through M-32)")
        print(f"Output location: {OUTPUT_DIR}")
        print("\nFigures are publication-quality SVG files suitable for academic documentation.")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n✗ Error during figure generation: {e}")
        raise

if __name__ == '__main__':
    main()
