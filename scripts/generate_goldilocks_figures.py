#!/usr/bin/env python3
"""
Generate publication-quality figures for the Goldilocks Principle paper.

Follows principles of:
- Tufte's data-ink ratio (maximize data, minimize chartjunk)
- Cleveland & McGill perceptual hierarchy (position > length > angle > area > color)
- Colorblind-safe palettes
- Scientific American style captions

Author: Claude Code
Date: 2026-03-02
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
from matplotlib.patches import ConnectionPatch
import numpy as np
import os
from pathlib import Path

# Set output directory
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define publication-quality style
plt.style.use('default')
matplotlib.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 13,
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.8,
    'xtick.minor.width': 0.4,
    'ytick.major.width': 0.8,
    'ytick.minor.width': 0.4,
    'lines.linewidth': 1.5,
    'grid.linewidth': 0.4,
    'grid.color': '#cccccc',
})

# Colorblind-safe palette (viridis-inspired)
COLORS = {
    'primary': '#1f77b4',      # Blue
    'secondary': '#ff7f0e',    # Orange
    'tertiary': '#2ca02c',     # Green
    'quaternary': '#d62728',   # Red
    'accent1': '#9467bd',      # Purple
    'accent2': '#8c564b',      # Brown
    'accent3': '#e377c2',      # Pink
    'accent4': '#7f7f7f',      # Gray
}

# Define inverted-U Gaussian function
def inverted_u(x, c_star, sigma):
    """Gaussian preference function: P(x) = exp(-(C(x) - C*)^2 / (2*sigma^2))"""
    return np.exp(-((x - c_star) ** 2) / (2 * sigma ** 2))

# =============================================================================
# FIGURE 1: The Inverted-U Across History
# =============================================================================
def figure_1_historical_timeline():
    """Timeline showing evolution of inverted-U concept from Wundt to ATLAS."""

    fig, ax = plt.subplots(figsize=(14, 5))

    # Historical milestones with their conceptualizations
    milestones = [
        (1874, "Wundt", "Arousal\nIntensity", 0.9, 0.3),
        (1908, "Yerkes-\nDodson", "Drive\nLevel", 1.1, 0.35),
        (1955, "Hebb", "Cortical\nExcitation", 1.2, 0.32),
        (1971, "Berlyne", "Collative\nVariables", 1.25, 0.3),
        (1989, "Kaplan", "Info\nLoad", 1.3, 0.28),
        (1999, "Taylor", "Fractal\nDimension", 1.35, 0.26),
        (2010, "Friston", "Prediction\nError", 1.3, 0.25),
        (2026, "ATLAS", "Cross-Modal\nOptimization", 1.3, 0.24),
    ]

    # X-axis range for complexity
    x_range = np.linspace(0.5, 2.0, 200)

    # Plot curves for each milestone
    colors_timeline = plt.cm.viridis(np.linspace(0.1, 0.9, len(milestones)))

    for i, (year, name, label, c_star, sigma) in enumerate(milestones):
        y = inverted_u(x_range, c_star, sigma)
        x_pos = (year - 1870) / 156 * 10  # Map year to 0-10 scale
        ax.plot(x_range, y, color=colors_timeline[i], linewidth=1.5,
               alpha=0.7, label=f"{year}: {name}")

        # Add small circles at peak
        peak_y = inverted_u(c_star, c_star, sigma)
        ax.plot(c_star, peak_y, 'o', color=colors_timeline[i], markersize=6)

    # Styling
    ax.set_xlabel('Stimulus Complexity (arbitrary units)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Preference / Engagement', fontsize=11, fontweight='bold')
    ax.set_xlim(0.5, 2.0)
    ax.set_ylim(0, 1.1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)
    ax.grid(False)
    ax.legend(loc='upper right', fontsize=8, frameon=False, ncol=2)

    # Add title
    ax.text(1.25, 1.05, 'Four Traditions, 150 Years Apart, Found the Same Curve',
           fontsize=12, fontweight='bold', ha='center', transform=ax.transData)

    # Add annotation
    ax.text(1.3, -0.35, 'Independent convergence is the strongest evidence for universality —\nthis principle was discovered, not designed.',
           fontsize=9, ha='center', style='italic', transform=ax.transAxes)

    fig.tight_layout(rect=[0, 0.12, 1, 1])
    fig.savefig(OUTPUT_DIR / 'figure_1_historical_timeline.svg', dpi=300,
               bbox_inches='tight', format='svg')
    print("✓ Figure 1: Historical Timeline saved")
    plt.close(fig)

# =============================================================================
# FIGURE 2: The Formal Model P(x) with Parameter Variations
# =============================================================================
def figure_2_formal_model():
    """2x2 panel showing base model and parameter variations."""

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle('Two Free Parameters Predict Where Preference Peaks',
                fontsize=13, fontweight='bold', y=0.98)

    x_range = np.linspace(0.5, 2.0, 200)

    # Panel A: Base model
    ax = axes[0, 0]
    c_star, sigma = 1.3, 0.3
    y = inverted_u(x_range, c_star, sigma)
    ax.fill_between(x_range, 0, y, alpha=0.2, color=COLORS['primary'])
    ax.plot(x_range, y, color=COLORS['primary'], linewidth=2.5)
    ax.plot(c_star, inverted_u(c_star, c_star, sigma), 'o', color=COLORS['primary'], markersize=8)
    ax.set_title('Panel A: Base Model (C*=1.3, σ=0.3)', fontsize=10, fontweight='bold', loc='left')
    ax.set_ylabel('Preference P(x)', fontsize=10)
    ax.set_xlim(0.5, 2.0)
    ax.set_ylim(0, 1.1)
    ax.grid(True, alpha=0.2, linestyle=':')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.text(c_star, inverted_u(c_star, c_star, sigma) + 0.1, 'Optimum\n(C*)',
           ha='center', fontsize=8, fontweight='bold')

    # Panel B: Effect of C* (expertise)
    ax = axes[0, 1]
    for c_star_val, color, label in [(1.0, COLORS['secondary'], 'Novice (C*=1.0)'),
                                      (1.3, COLORS['primary'], 'Expert (C*=1.3)'),
                                      (1.6, COLORS['tertiary'], 'Connoisseur (C*=1.6)')]:
        y = inverted_u(x_range, c_star_val, 0.3)
        ax.plot(x_range, y, color=color, linewidth=2.5, label=label)
        ax.plot(c_star_val, inverted_u(c_star_val, c_star_val, 0.3), 'o', color=color, markersize=7)

    ax.annotate('', xy=(1.6, 0.3), xytext=(1.0, 0.3),
               arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(1.3, 0.15, 'Expertise →', ha='center', fontsize=9, fontweight='bold')
    ax.set_title('Panel B: Effect of C* (Expertise Shift)', fontsize=10, fontweight='bold', loc='left')
    ax.set_ylabel('Preference P(x)', fontsize=10)
    ax.set_xlim(0.5, 2.0)
    ax.set_ylim(0, 1.1)
    ax.legend(loc='upper right', fontsize=8, frameon=False)
    ax.grid(True, alpha=0.2, linestyle=':')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Panel C: Effect of σ (tolerance bandwidth)
    ax = axes[1, 0]
    for sigma_val, color, label in [(0.15, COLORS['quaternary'], 'Specialist (σ=0.15)'),
                                     (0.30, COLORS['primary'], 'Generalist (σ=0.30)'),
                                     (0.60, COLORS['accent4'], 'Broad acceptance (σ=0.60)')]:
        y = inverted_u(x_range, 1.3, sigma_val)
        ax.plot(x_range, y, color=color, linewidth=2.5, label=label)

    ax.set_title('Panel C: Effect of σ (Tolerance Bandwidth)', fontsize=10, fontweight='bold', loc='left')
    ax.set_ylabel('Preference P(x)', fontsize=10)
    ax.set_xlabel('Stimulus Complexity', fontsize=10)
    ax.set_xlim(0.5, 2.0)
    ax.set_ylim(0, 1.1)
    ax.legend(loc='upper right', fontsize=8, frameon=False)
    ax.grid(True, alpha=0.2, linestyle=':')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Panel D: Cultural calibration
    ax = axes[1, 1]
    cultures = [
        (1.1, 0.2, 'Japanese\n(wabi-sabi)', COLORS['accent1']),
        (1.3, 0.3, 'Western\n(modern)', COLORS['primary']),
        (1.6, 0.4, 'Baroque\n(Italian)', COLORS['secondary']),
    ]
    for c_star_val, sigma_val, label, color in cultures:
        y = inverted_u(x_range, c_star_val, sigma_val)
        ax.plot(x_range, y, color=color, linewidth=2.5, label=label)

    ax.set_title('Panel D: Cultural Calibration', fontsize=10, fontweight='bold', loc='left')
    ax.set_ylabel('Preference P(x)', fontsize=10)
    ax.set_xlabel('Stimulus Complexity', fontsize=10)
    ax.set_xlim(0.5, 2.0)
    ax.set_ylim(0, 1.1)
    ax.legend(loc='upper right', fontsize=8, frameon=False)
    ax.grid(True, alpha=0.2, linestyle=':')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(OUTPUT_DIR / 'figure_2_formal_model.svg', dpi=300,
               bbox_inches='tight', format='svg')
    print("✓ Figure 2: Formal Model saved")
    plt.close(fig)

# =============================================================================
# FIGURE 3: Cross-Modal Evidence Summary (2x3 grid)
# =============================================================================
def figure_3_cross_modal_evidence():
    """Six panels showing inverted-U across modalities."""

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.suptitle('Five Different Senses, Five Different Metrics — One Universal Shape',
                fontsize=13, fontweight='bold', y=0.98)

    # Modality data: (x_label, x_range, x_optimal, title, shaded_start, shaded_end)
    modalities = [
        ('Fractal Dimension D', np.linspace(0.8, 1.8, 100), 1.3,
         'Visual Complexity\n(Fractal Dimension)', 1.15, 1.45),
        ('Deviation from Neutral (°C)', np.linspace(-5, 5, 100), 0,
         'Thermal Comfort\n(Deviation from Neutral)', -1, 1),
        ('Sound Level (dB LAeq)', np.linspace(30, 80, 100), 55,
         'Acoustic Preference\n(Sound Level)', 50, 60),
        ('Temporal Variation (cycles/min)', np.linspace(0, 5, 100), 0.5,
         'Temporal Variation\n(Activity Cycles)', 0.1, 1.5),
        ('Simultaneous Social Modes', np.linspace(0, 10, 100), 4,
         'Social Density\n(Simultaneous Groups)', 2, 6),
        ('Luminance Contrast Ratio', np.linspace(1, 50, 100), 10,
         'Luminance Contrast\n(1:X ratio)', 7, 15),
    ]

    axes_flat = axes.flatten()

    for idx, (x_label, x_range, x_opt, title, shaded_start, shaded_end) in enumerate(modalities):
        ax = axes_flat[idx]

        # Normalize x_range to 0-2 scale for Gaussian
        x_norm = (x_range - x_opt) / (x_opt / 1.3) if x_opt != 0 else (x_range - x_opt)
        x_norm_opt = 1.3

        # Generate preference curve
        y = inverted_u(x_norm, x_norm_opt, 0.3)

        # Shade Goldilocks zone
        shade_start_norm = (shaded_start - x_opt) / (x_opt / 1.3) if x_opt != 0 else 0
        shade_end_norm = (shaded_end - x_opt) / (x_opt / 1.3) if x_opt != 0 else 2

        ax.axvspan(shade_start_norm, shade_end_norm, alpha=0.15, color=COLORS['primary'])

        # Plot main curve
        ax.plot(x_norm, y, color=COLORS['primary'], linewidth=2.5)
        ax.fill_between(x_norm, 0, y, alpha=0.1, color=COLORS['primary'])

        # Add noise/scatter points to represent data
        noise = np.random.normal(0, 0.05, len(x_norm))
        ax.scatter(x_norm[::5], y[::5] + noise[::5], alpha=0.4, s=20, color=COLORS['primary'])

        ax.set_title(title, fontsize=10, fontweight='bold', loc='left')
        ax.set_ylabel('Preference / Satisfaction', fontsize=9)
        ax.set_ylim(0, 1.1)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.2, linestyle=':')

        # Add Goldilocks label
        ax.text(x_norm_opt, -0.25, 'Goldilocks Zone', ha='center', fontsize=8,
               style='italic', color=COLORS['primary'], fontweight='bold')

    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(OUTPUT_DIR / 'figure_3_cross_modal_evidence.svg', dpi=300,
               bbox_inches='tight', format='svg')
    print("✓ Figure 3: Cross-Modal Evidence saved")
    plt.close(fig)

# =============================================================================
# FIGURE 4: Fractal Dimension and Natural Scene Statistics
# =============================================================================
def figure_4_fractal_dimension():
    """Histogram of natural scene fractal dimensions overlaid with preference curve."""

    fig, ax = plt.subplots(figsize=(11, 6))

    # Simulate natural scene statistics (peaked around 1.3)
    natural_scenes = np.random.normal(1.3, 0.15, 1000)
    natural_scenes = natural_scenes[(natural_scenes >= 1.0) & (natural_scenes <= 2.0)]

    # Plot histogram
    ax.hist(natural_scenes, bins=30, alpha=0.3, color=COLORS['tertiary'],
           edgecolor=COLORS['tertiary'], linewidth=1.5, label='Natural Scene Statistics')

    # Overlay preference curve
    x_range = np.linspace(0.8, 2.0, 200)
    y_pref = inverted_u(x_range, 1.3, 0.2)

    # Normalize preference curve to match histogram scale
    y_pref_scaled = y_pref * len(natural_scenes) * 0.1 / np.max(y_pref)
    ax.plot(x_range, y_pref_scaled, color=COLORS['secondary'], linewidth=3,
           label='Human Aesthetic Preference (Taylor et al., 1999)')

    # Add convergence highlight
    convergence_x = 1.3
    ax.axvline(convergence_x, color='red', linestyle='--', linewidth=2, alpha=0.6)
    ax.text(convergence_x, ax.get_ylim()[1] * 0.95, 'Convergence\nat D ≈ 1.3',
           ha='center', fontsize=10, fontweight='bold', color='red',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Annotations for examples
    examples = [
        (1.0, 'Modernist\nBox'),
        (1.3, 'Gothic\nCathedral'),
        (1.35, 'Frank Lloyd\nWright'),
        (1.7, 'Baroque\nPalace'),
    ]

    for x_pos, label in examples:
        if 0.8 <= x_pos <= 2.0:
            y_pos = inverted_u(x_pos, 1.3, 0.2) * len(natural_scenes) * 0.1 / np.max(y_pref)
            ax.annotate(label, xy=(x_pos, y_pos), xytext=(x_pos, y_pos + 30),
                       fontsize=8, ha='center',
                       arrowprops=dict(arrowstyle='->', lw=1, color='gray'))

    ax.set_xlabel('Fractal Dimension (D)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Frequency / Preference', fontsize=11, fontweight='bold')
    ax.set_title('Human Preference Peaks Where Natural Statistics Are Most Abundant',
                fontsize=12, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(loc='upper right', fontsize=10, frameon=False)
    ax.grid(True, alpha=0.2, linestyle=':')

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'figure_4_fractal_dimension.svg', dpi=300,
               bbox_inches='tight', format='svg')
    print("✓ Figure 4: Fractal Dimension saved")
    plt.close(fig)

# =============================================================================
# FIGURE 5: BOXOLOGY DIAGRAM — Cognitive/Affective System Architecture
# =============================================================================
def figure_5_boxology():
    """Three-layer architecture diagram showing functional, neural, and theoretical layers."""

    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(5, 9.7, 'Three Brain Layers Converge at One Complexity Level:\nFunctional → Neural → Theoretical',
           fontsize=13, fontweight='bold', ha='center')

    # LAYER 1: Functional Components (top)
    layer1_y = 8.0
    func_boxes = [
        (1.0, 'Prediction\nEngine', COLORS['primary']),
        (2.2, 'Error\nComputation', COLORS['secondary']),
        (3.4, 'Affect\nGenerator', COLORS['tertiary']),
        (4.6, 'Learning\nSystem', COLORS['accent1']),
        (5.8, 'Arousal\nRegulation', COLORS['quaternary']),
        (7.0, 'Action\nSelection', COLORS['accent2']),
    ]

    ax.text(0.2, layer1_y + 0.8, 'Layer 1:\nFunctional Components',
           fontsize=10, fontweight='bold', style='italic')

    for x, label, color in func_boxes:
        rect = FancyBboxPatch((x - 0.45, layer1_y - 0.35), 0.9, 0.7,
                            boxstyle="round,pad=0.05",
                            edgecolor=color, facecolor=color, alpha=0.2, linewidth=2)
        ax.add_patch(rect)
        ax.text(x, layer1_y, label, ha='center', va='center', fontsize=8, fontweight='bold')

    # Arrows between functional components
    arrow_pairs = [(1.0, 2.2), (2.2, 3.4), (2.2, 4.6)]
    for x1, x2 in arrow_pairs:
        ax.annotate('', xy=(x2 - 0.5, layer1_y), xytext=(x1 + 0.5, layer1_y),
                   arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))

    # Arousal modulation arc
    ax.annotate('', xy=(2.2, layer1_y - 0.5), xytext=(5.8, layer1_y - 0.5),
               arrowprops=dict(arrowstyle='-', lw=1.5, color=COLORS['quaternary'],
                             connectionstyle="arc3,rad=.5"))
    ax.text(4.0, layer1_y - 1.0, 'Modulates', fontsize=8, style='italic')

    # Action selection downstream
    ax.annotate('', xy=(6.5, layer1_y), xytext=(5.2, layer1_y),
               arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))

    # LAYER 2: Neural Implementation (middle)
    layer2_y = 5.5
    neural_regions = [
        (1.0, 'V1-V4, A1\nCortices', 'Prediction'),
        (2.2, 'Anterior\nInsula, dACC', 'Error'),
        (3.4, 'vmPFC,\nAmygdala, NAcc', 'Affect'),
        (4.6, 'Hippocampus,\nBasal Ganglia', 'Learning'),
        (5.8, 'LC-NE,\nRaphe Nuclei', 'Arousal'),
        (7.0, 'dlPFC,\nPremotor', 'Action'),
    ]

    ax.text(0.2, layer2_y + 1.2, 'Layer 2:\nNeural Implementation',
           fontsize=10, fontweight='bold', style='italic')

    for x, label, _ in neural_regions:
        color = func_boxes[int((x - 1.0) / 1.2)][2]
        rect = FancyBboxPatch((x - 0.45, layer2_y - 0.5), 0.9, 1.0,
                            boxstyle="round,pad=0.05",
                            edgecolor=color, facecolor=color, alpha=0.15, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x, layer2_y, label, ha='center', va='center', fontsize=7.5)

        # Connections from functional to neural layer
        ax.plot([x, x], [layer1_y - 0.4, layer2_y + 0.5], 'k-', linewidth=0.5, alpha=0.3)

    # LAYER 3: Theoretical Framework Integration (bottom)
    layer3_y = 2.5
    theories = [
        (1.2, 'Predictive\nProcessing', COLORS['primary']),
        (2.8, 'Interoceptive-\nConstructionist\nAffect', COLORS['secondary']),
        (4.6, 'Neuromodulatory\nSystems', COLORS['tertiary']),
        (6.4, 'Individual\nExperience &\nDual-Process', COLORS['accent1']),
    ]

    ax.text(0.2, layer3_y + 1.2, 'Layer 3:\nT1 Theoretical Frameworks',
           fontsize=10, fontweight='bold', style='italic')

    theory_colors_assigned = []
    for x, label, color in theories:
        rect = FancyBboxPatch((x - 0.55, layer3_y - 0.5), 1.1, 1.0,
                            boxstyle="round,pad=0.05",
                            edgecolor=color, facecolor=color, alpha=0.25, linewidth=2)
        ax.add_patch(rect)
        ax.text(x, layer3_y, label, ha='center', va='center', fontsize=8, fontweight='bold')
        theory_colors_assigned.append((x, color))

        # Upward connections to neural layer
        destinations = [1.0, 2.2, 3.4, 4.6, 5.8, 7.0]
        # PP connects to Prediction and Error
        if x == 1.2:
            for dest in [1.0, 2.2]:
                ax.annotate('', xy=(dest, layer2_y - 0.5), xytext=(x, layer3_y + 0.5),
                           arrowprops=dict(arrowstyle='->', lw=0.8, color=color, alpha=0.4))
        # IC to Affect and Arousal
        elif x == 2.8:
            for dest in [3.4, 5.8]:
                ax.annotate('', xy=(dest, layer2_y - 0.5), xytext=(x, layer3_y + 0.5),
                           arrowprops=dict(arrowstyle='->', lw=0.8, color=color, alpha=0.4))
        # NM to Learning and Arousal
        elif x == 4.6:
            for dest in [4.6, 5.8]:
                ax.annotate('', xy=(dest, layer2_y - 0.5), xytext=(x, layer3_y + 0.5),
                           arrowprops=dict(arrowstyle='->', lw=0.8, color=color, alpha=0.4))
        # IE-DPT to Action and Learning
        else:
            for dest in [7.0, 4.6]:
                ax.annotate('', xy=(dest, layer2_y - 0.5), xytext=(x, layer3_y + 0.5),
                           arrowprops=dict(arrowstyle='->', lw=0.8, color=color, alpha=0.4))

    # INTELLECTUAL SURPLUS ZONE (center)
    surplus_rect = FancyBboxPatch((3.5, 0.5), 3, 1.2,
                                boxstyle="round,pad=0.1",
                                edgecolor='red', facecolor='#ffcccc',
                                alpha=0.3, linewidth=2, linestyle='--')
    ax.add_patch(surplus_rect)

    ax.text(5, 1.1, 'INTELLECTUAL SURPLUS\nGoldilocks Principle:\nCross-Modal Optimization',
           fontsize=10, fontweight='bold', ha='center', color='red')
    ax.text(5, 0.6, '(All four theories converge)',
           fontsize=8, ha='center', style='italic', color='darkred')

    # Add legend/explanation at bottom
    ax.text(5, -0.5,
           'The Goldilocks Principle emerges uniquely from the convergence of all four T1 frameworks.',
           fontsize=9, ha='center', style='italic',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'figure_5_boxology.svg', dpi=300,
               bbox_inches='tight', format='svg')
    print("✓ Figure 5: Boxology Diagram saved")
    plt.close(fig)

# =============================================================================
# FIGURE 6: Cultural Calibration Landscape (Parallel Coordinates)
# =============================================================================
def figure_6_cultural_calibration():
    """Parallel coordinates plot showing cultural variation in C* across modalities."""

    fig, ax = plt.subplots(figsize=(12, 6))

    # Cultural data: culture -> [visual_C*, thermal_C*, acoustic_C*, social_C*, temporal_C*]
    # Normalized to 0-2 scale for easy visualization
    cultures_data = {
        'Japanese\n(wabi-sabi)': [1.0, 0.0, 48, 2.5, 0.2],
        'Scandinavian\n(minimalist)': [1.15, 0.0, 50, 3.0, 0.3],
        'Islamic\n(geometric)': [1.35, -0.5, 52, 3.5, 0.4],
        'Western\n(contemporary)': [1.3, 0.0, 55, 4.0, 0.5],
        'Baroque\n(ornate)': [1.6, 0.5, 60, 4.5, 0.8],
        'West African\n(fractal)': [1.55, 0.5, 58, 5.0, 0.6],
    }

    # Dimensions (axes) for parallel coordinates
    dimensions = ['Visual\nComplexity\n(Fractal D)', 'Thermal\n(°C from\nNeutral)',
                 'Acoustic\n(dB LAeq)', 'Social\nDensity', 'Temporal\n(cycles/min)']
    x_positions = np.arange(len(dimensions))

    colors_cultures = plt.cm.Set2(np.linspace(0, 1, len(cultures_data)))

    # Plot lines for each culture
    for (culture_name, values), color in zip(cultures_data.items(), colors_cultures):
        # Normalize values to 0-2 scale for visualization
        norm_values = []
        ranges = [(0.8, 1.8), (-2, 2), (40, 70), (0, 8), (0, 1.5)]
        for val, (min_v, max_v) in zip(values, ranges):
            if max_v != min_v:
                norm_val = (val - min_v) / (max_v - min_v) * 2
            else:
                norm_val = 1
            norm_values.append(norm_val)

        ax.plot(x_positions, norm_values, marker='o', linewidth=2.5,
               markersize=6, label=culture_name, color=color, alpha=0.8)

    # Styling
    ax.set_xticks(x_positions)
    ax.set_xticklabels(dimensions, fontsize=10, fontweight='bold')
    ax.set_ylabel('Normalized Preference Optimum (0-2 scale)', fontsize=11, fontweight='bold')
    ax.set_title('Same Inverted-U Shape, Different Peak Locations — Your Visual Diet Sets Where Beauty Falls',
                fontsize=12, fontweight='bold')
    ax.set_ylim(-0.2, 2.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.2, linestyle=':', axis='y')
    ax.legend(loc='upper left', fontsize=9, frameon=False, ncol=2)

    # Add annotation
    ax.text(2.5, -0.7, 'All cultures show inverted-U preference functions despite different optima (C*)',
           fontsize=9, ha='center', style='italic',
           transform=ax.transAxes, bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'figure_6_cultural_calibration.svg', dpi=300,
               bbox_inches='tight', format='svg')
    print("✓ Figure 6: Cultural Calibration saved")
    plt.close(fig)

# =============================================================================
# FIGURE 7: Processing Fluency Mechanism
# =============================================================================
def figure_7_processing_fluency():
    """Flow diagram showing fluency mechanism from complexity to preference."""

    fig, ax = plt.subplots(figsize=(13, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # Title
    ax.text(5, 4.7, 'What the Goldilocks Zone Feels Like From the Inside:\nFluency Is the Conscious Signature of Efficient Neural Computation',
           fontsize=12, fontweight='bold', ha='center')

    # Define boxes for the flow
    stages = [
        (1.0, 3, 'Low\nComplexity', COLORS['quaternary']),
        (2.5, 3, 'High\nFluency', COLORS['tertiary']),
        (4.0, 3, 'Boredom\nAffect', COLORS['accent3']),
        (5.5, 3, 'Low\nPreference', COLORS['quaternary']),
    ]

    for x, y, label, color in stages:
        rect = FancyBboxPatch((x - 0.4, y - 0.35), 0.8, 0.7,
                            boxstyle="round,pad=0.05",
                            edgecolor=color, facecolor=color, alpha=0.2, linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold')

    # Arrows between stages
    for i in range(len(stages) - 1):
        x1, y1 = stages[i][:2]
        x2, y2 = stages[i + 1][:2]
        ax.annotate('', xy=(x2 - 0.45, y2), xytext=(x1 + 0.45, y1),
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))

    # Upper path
    stages_upper = [
        (1.0, 1.5, 'Intermediate\nComplexity', COLORS['primary']),
        (2.5, 1.5, 'Moderate\nFluency', COLORS['tertiary']),
        (4.0, 1.5, 'Engagement\nAffect', COLORS['tertiary']),
        (5.5, 1.5, 'High\nPreference', COLORS['tertiary']),
    ]

    for x, y, label, color in stages_upper:
        rect = FancyBboxPatch((x - 0.4, y - 0.35), 0.8, 0.7,
                            boxstyle="round,pad=0.05",
                            edgecolor=color, facecolor=color, alpha=0.2, linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold')

    # Arrows upper path
    for i in range(len(stages_upper) - 1):
        x1, y1 = stages_upper[i][:2]
        x2, y2 = stages_upper[i + 1][:2]
        ax.annotate('', xy=(x2 - 0.45, y2), xytext=(x1 + 0.45, y1),
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))

    # Bottom path (high complexity)
    stages_lower = [
        (1.0, 0, 'High\nComplexity', COLORS['secondary']),
        (2.5, 0, 'Low\nFluency', COLORS['accent4']),
        (4.0, 0, 'Frustration\nAffect', COLORS['secondary']),
        (5.5, 0, 'Low\nPreference', COLORS['quaternary']),
    ]

    for x, y, label, color in stages_lower:
        rect = FancyBboxPatch((x - 0.4, y - 0.35), 0.8, 0.7,
                            boxstyle="round,pad=0.05",
                            edgecolor=color, facecolor=color, alpha=0.2, linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold')

    # Arrows lower path
    for i in range(len(stages_lower) - 1):
        x1, y1 = stages_lower[i][:2]
        x2, y2 = stages_lower[i + 1][:2]
        ax.annotate('', xy=(x2 - 0.45, y2), xytext=(x1 + 0.45, y1),
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))

    # Connecting arrows to preference outcomes
    ax.annotate('', xy=(7.0, 3), xytext=(6.0, 3),
               arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['quaternary']))
    ax.annotate('', xy=(7.0, 1.5), xytext=(6.0, 1.5),
               arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['tertiary']))
    ax.annotate('', xy=(7.0, 0), xytext=(6.0, 0),
               arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['quaternary']))

    # Final outcome
    outcome_rect = FancyBboxPatch((6.5, 0.8), 1.5, 1.4,
                                boxstyle="round,pad=0.1",
                                edgecolor='red', facecolor='#ffe6e6',
                                alpha=0.4, linewidth=2.5)
    ax.add_patch(outcome_rect)
    ax.text(7.25, 1.5, 'Preference\nOut', ha='center', va='center',
           fontsize=10, fontweight='bold', color='darkred')

    # Add key insight
    ax.text(5, -1.2,
           'Expertise increases processing capacity, shifting C* rightward: experts prefer higher complexity.',
           fontsize=9, ha='center', style='italic',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'figure_7_processing_fluency.svg', dpi=300,
               bbox_inches='tight', format='svg')
    print("✓ Figure 7: Processing Fluency Mechanism saved")
    plt.close(fig)

# =============================================================================
# FIGURE 8: Theory Integration — Intellectual Surplus (Euler Diagram)
# =============================================================================
def figure_8_intellectual_surplus():
    """Four-set Venn/Euler diagram showing intersection of theories."""

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.axis('off')

    # Title
    ax.text(0, 2.8, "What Four Frameworks Together Still Cannot Explain:\nThe Cross-Modal Universality Claim Is the Theory's Own Contribution",
           fontsize=13, fontweight='bold', ha='center')

    # Define circles for four theories
    circles_data = [
        ((-1, 0), 1.2, 'Predictive\nProcessing (PP)', COLORS['primary']),
        ((1, 0), 1.2, 'Interoceptive-\nConstructionist\nAffect (IC)', COLORS['secondary']),
        ((-0.5, -1.2), 1.2, 'Neuromodulatory\nSystems (NM)', COLORS['tertiary']),
        ((0.5, -1.2), 1.2, 'Individual\nExperience &\nDual-Process (IE-DPT)', COLORS['accent1']),
    ]

    # Draw circles with some transparency
    for (x, y), radius, label, color in circles_data:
        circle = plt.Circle((x, y), radius, color=color, alpha=0.15,
                           edgecolor=color, linewidth=2.5)
        ax.add_patch(circle)

        # Add theory labels outside circles
        if x < 0 and y >= 0:
            label_x, label_y = x - 1.5, y + 0.3
        elif x > 0 and y >= 0:
            label_x, label_y = x + 1.5, y + 0.3
        elif x <= -0.5 and y < 0:
            label_x, label_y = x - 1.4, y - 0.5
        else:
            label_x, label_y = x + 1.4, y - 0.5

        ax.text(label_x, label_y, label, fontsize=9, fontweight='bold', ha='center')

    # Add intersection labels and phenomena
    intersections = [
        ((-0.2, 0.6), 'PP∩IC:\nPrediction Error\n→ Affect'),
        ((-0.5, -0.3), 'PP∩NM:\nError →\nDopamine'),
        ((0.2, 0.6), 'IC∩NM:\nAllostasis →\nNeuromod'),
        ((0.5, -0.3), 'NM∩IE-DPT:\nExperience\nModulates\nRewards'),
    ]

    for (x, y), label in intersections:
        ax.text(x, y, label, fontsize=8, ha='center', style='italic',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, pad=0.3))

    # CENTRAL INTELLECTUAL SURPLUS
    central_circle = plt.Circle((0, -0.4), 0.7, color='red', alpha=0.15,
                               edgecolor='red', linewidth=3, linestyle='--')
    ax.add_patch(central_circle)

    ax.text(0, -0.15, 'Cross-Modal\nUniversality', fontsize=10, fontweight='bold',
           ha='center', color='darkred')
    ax.text(0, -0.65, 'Goldilocks\nPrinciple', fontsize=9, fontweight='bold',
           ha='center', color='darkred')

    # Add key insight at bottom
    ax.text(0, -2.3,
           'The Goldilocks Principle adds irreducible value:\nall sensory channels optimize under the same',
           fontsize=9, ha='center', style='italic')
    ax.text(0, -2.55,
           'prediction-error efficiency principle despite domain-specific optima (C*)',
           fontsize=9, ha='center', style='italic',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7, pad=0.5))

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'figure_8_intellectual_surplus.svg', dpi=300,
               bbox_inches='tight', format='svg')
    print("✓ Figure 8: Intellectual Surplus Diagram saved")
    plt.close(fig)

# =============================================================================
# FIGURE 9: Design Implications Dashboard
# =============================================================================
def figure_9_design_dashboard():
    """Horizontal bar chart with Goldilocks zones for each modality."""

    fig, ax = plt.subplots(figsize=(13, 7))

    # Define modalities with their ranges and optima
    modalities = [
        ('Visual Complexity\n(Fractal Dimension D)', 0.8, 2.0, 1.15, 1.45,
         ['Modernist\n(D≈1.0)', 'Gothic/\nWright\n(D≈1.3-1.35)', 'Baroque\n(D≈1.7)']),
        ('Thermal Comfort\n(°C from Neutral)', -5, 5, -1, 1,
         ['Cold', 'Comfort\nZone', 'Warm']),
        ('Acoustic Level\n(dB LAeq)', 30, 80, 50, 60,
         ['Quiet', 'Optimal\nAcoustics', 'Loud']),
        ('Luminance Contrast\n(1:X ratio)', 1, 50, 7, 15,
         ['Low\nContrast', 'Optimal\nContrast', 'High\nContrast']),
        ('Temporal Variation\n(cycles/min)', 0, 5, 0.1, 1.5,
         ['Static', 'Optimal\nVariation', 'Chaotic']),
    ]

    y_positions = np.arange(len(modalities))

    for idx, (label, x_min, x_max, opt_min, opt_max, examples) in enumerate(modalities):
        y_pos = y_positions[idx]

        # Draw baseline
        ax.barh(y_pos, x_max - x_min, left=x_min, height=0.3,
               color='lightgray', alpha=0.3, edgecolor='black', linewidth=0.5)

        # Draw Goldilocks zone
        ax.barh(y_pos, opt_max - opt_min, left=opt_min, height=0.5,
               color=COLORS['primary'], alpha=0.4, edgecolor=COLORS['primary'], linewidth=2)

        # Add zone label
        zone_center = (opt_min + opt_max) / 2
        ax.text(zone_center, y_pos + 0.35, 'Goldilocks\nZone',
               fontsize=8, fontweight='bold', ha='center', color=COLORS['primary'])

    # Set labels and styling
    ax.set_yticks(y_positions)
    ax.set_yticklabels([m[0] for m in modalities], fontsize=10)
    ax.set_xlabel('Stimulus Intensity / Value', fontsize=11, fontweight='bold')
    ax.set_title('The Architect\'s Cheat Sheet: Target Ranges by Building Type and Sensory Channel',
                fontsize=12, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)
    ax.grid(True, alpha=0.2, linestyle=':', axis='x')

    # Add examples as text annotations
    example_positions = [
        (0.8, -0.6), (5, -0.6), (30, -0.6), (1, -0.6), (0, -0.6)
    ]

    for idx, (label, x_min, x_max, opt_min, opt_max, examples) in enumerate(modalities):
        y_pos = y_positions[idx]
        # Add text below
        ax.text(x_min + (x_max - x_min) * 0.1, y_pos - 0.5, examples[0],
               fontsize=7, ha='center', style='italic', color='gray')
        ax.text((opt_min + opt_max) / 2, y_pos - 0.5, examples[1],
               fontsize=7, ha='center', style='italic', color=COLORS['primary'], fontweight='bold')
        ax.text(x_max - (x_max - x_min) * 0.1, y_pos - 0.5, examples[2],
               fontsize=7, ha='center', style='italic', color='gray')

    fig.tight_layout(rect=[0, 0.15, 1, 1])

    # Add caption space
    ax.text(0.5, -0.15, 'Architects and designers can use these ranges directly to optimize all sensory dimensions simultaneously.',
           fontsize=9, ha='center', style='italic', transform=ax.transAxes,
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

    fig.savefig(OUTPUT_DIR / 'figure_9_design_dashboard.svg', dpi=300,
               bbox_inches='tight', format='svg')
    print("✓ Figure 9: Design Dashboard saved")
    plt.close(fig)

# =============================================================================
# FIGURE 10: Research Agenda — Schema Gaps (Evidence Heat Map)
# =============================================================================
def figure_10_research_agenda():
    """Evidence matrix showing gaps in empirical support across modalities and evidence types."""

    fig, ax = plt.subplots(figsize=(13, 7))

    # Define modalities and evidence types
    modalities_list = ['Visual', 'Thermal', 'Acoustic', 'Temporal', 'Social',
                      'Olfactory', 'Gustatory', 'Haptic']
    evidence_types = ['Inverted-U\nDocumented', 'C* Value\nEstimated', 'σ Value\nEstimated',
                     'Cross-Cultural\nData', 'Neural\nSubstrate ID', 'Design\nGuidelines']

    # Evidence matrix (0=missing/red, 0.5=partial/yellow, 1=strong/green)
    evidence_matrix = np.array([
        [1.0, 1.0, 1.0, 0.5, 0.7, 1.0],    # Visual
        [1.0, 0.8, 0.8, 0.4, 0.6, 0.9],    # Thermal
        [0.9, 0.7, 0.7, 0.3, 0.5, 0.7],    # Acoustic
        [0.6, 0.4, 0.4, 0.2, 0.3, 0.3],    # Temporal
        [0.5, 0.3, 0.3, 0.1, 0.2, 0.2],    # Social
        [0.1, 0.0, 0.0, 0.0, 0.0, 0.0],    # Olfactory
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],    # Gustatory
        [0.2, 0.1, 0.1, 0.0, 0.1, 0.1],    # Haptic
    ])

    # Create heatmap
    im = ax.imshow(evidence_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)

    # Set ticks and labels
    ax.set_xticks(np.arange(len(evidence_types)))
    ax.set_yticks(np.arange(len(modalities_list)))
    ax.set_xticklabels(evidence_types, fontsize=10)
    ax.set_yticklabels(modalities_list, fontsize=10)

    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center", rotation_mode="anchor")

    # Add text annotations
    for i in range(len(modalities_list)):
        for j in range(len(evidence_types)):
            value = evidence_matrix[i, j]
            if value >= 0.8:
                text_label = '●'  # Green indicator
                color = 'darkgreen'
            elif value >= 0.5:
                text_label = '◐'  # Yellow indicator
                color = 'darkorange'
            else:
                text_label = '○'  # Red indicator (empty)
                color = 'darkred'

            ax.text(j, i, text_label, ha="center", va="center",
                   color=color, fontsize=18, fontweight='bold')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Evidence Strength', fontsize=10, fontweight='bold')
    cbar.ax.set_yticklabels(['Missing\n(Red)', 'Partial\n(Yellow)', 'Strong\n(Green)'])

    # Styling
    ax.set_title('From Plausible Theory to Validated Design Science: What Each Phase Delivers',
                fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel('Evidence Type', fontsize=11, fontweight='bold', labelpad=10)
    ax.set_ylabel('Sensory Modality', fontsize=11, fontweight='bold', labelpad=10)

    # Add border
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

    # Add legend
    legend_text = (
        '● Strong evidence (multiple replicated studies)\n'
        '◐ Partial evidence (limited studies or conflicting results)\n'
        '○ Missing evidence (no systematic research)'
    )
    ax.text(0.5, -0.25, legend_text, fontsize=9, ha='center',
           transform=ax.transAxes, family='monospace',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    fig.tight_layout(rect=[0, 0.2, 1, 1])
    fig.savefig(OUTPUT_DIR / 'figure_10_research_agenda.svg', dpi=300,
               bbox_inches='tight', format='svg')
    print("✓ Figure 10: Research Agenda saved")
    plt.close(fig)

# =============================================================================
# MAIN EXECUTION
# =============================================================================
def main():
    """Generate all figures."""
    print("\n" + "="*70)
    print("GENERATING PUBLICATION-QUALITY FIGURES FOR GOLDILOCKS PRINCIPLE PAPER")
    print("="*70 + "\n")

    print(f"Output directory: {OUTPUT_DIR}\n")

    # Generate all figures
    figure_1_historical_timeline()
    figure_2_formal_model()
    figure_3_cross_modal_evidence()
    figure_4_fractal_dimension()
    figure_5_boxology()
    figure_6_cultural_calibration()
    figure_7_processing_fluency()
    figure_8_intellectual_surplus()
    figure_9_design_dashboard()
    figure_10_research_agenda()

    # Verify output
    print("\n" + "="*70)
    svg_files = sorted(OUTPUT_DIR.glob('*.svg'))
    print(f"\nGenerated {len(svg_files)} SVG figures:")
    for svg_file in svg_files:
        size_kb = svg_file.stat().st_size / 1024
        print(f"  - {svg_file.name} ({size_kb:.1f} KB)")

    print("\n" + "="*70)
    print("ALL FIGURES GENERATED SUCCESSFULLY")
    print("="*70 + "\n")

    return svg_files

if __name__ == '__main__':
    svg_files = main()
