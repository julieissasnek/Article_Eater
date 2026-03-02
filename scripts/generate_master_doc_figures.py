#!/usr/bin/env python3
"""
Generate the three critical architecture overview figures for the ATLAS master document.

These are the "60-second understanding" figures that readers see first.
They establish the three-layer architecture, tier hierarchy, and epistemic pipeline.

Figures:
  M-1: The ATLAS Three-Layer Architecture (EN → π → BN)
  M-2: The Tier Hierarchy (10 frameworks → 3,420 beliefs)
  M-3: The ATLAS Pipeline (7 stages of epistemic scrutiny)

Style:
  - ATLAS color palette (blue, brick red, green, amber, purple, gray)
  - Tufte principles: maximize data-ink, minimize chartjunk
  - Cleveland & McGill hierarchy: position > length > angle > area > color
  - Direct labeling, no legend required
  - SVG output, 14x10 inches, publication quality

Author: Claude Code
Date: 2026-03-02
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, Wedge, Polygon
from matplotlib.patches import ConnectionPatch, Arc
import matplotlib.lines as mlines
import numpy as np
import os
from pathlib import Path

# Set output directory
SCRIPT_DIR = Path(__file__).parent
REPO_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = REPO_DIR / "docs" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Configure matplotlib for publication quality (follows VISUALIZATION_NORMS.md)
matplotlib.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': '#333333',
    'axes.linewidth': 0.8,
    'axes.grid': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.spines.bottom': False,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'lines.linewidth': 1.5,
    'lines.markersize': 5,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
})

# ATLAS color palette (colorblind-safe, from VISUALIZATION_NORMS.md)
COLORS = {
    'primary': '#2171B5',      # Blue
    'secondary': '#CB4335',    # Brick red
    'tertiary': '#27AE60',     # Green
    'quaternary': '#F39C12',   # Amber
    'accent': '#8E44AD',       # Purple
    'neutral': '#7F8C8D',      # Gray
    'light_gray': '#ECF0F1',   # Light background
    'dark_gray': '#34495E',    # Dark text
}

# =============================================================================
# FIGURE M-1: The ATLAS Three-Layer Architecture
# =============================================================================

def figure_m1_three_layer_architecture():
    """
    ATLAS architecture with IE-DPT as superordinate envelope wrapping three
    computational layers: EN → π → BN.

    LEFT SIDE: The three computational layers (EN, π, BN) stacked vertically
    OUTER ENVELOPE: IE-DPT drawn as a translucent bounding region with
        modulation arrows showing how explicit channel configures implicit processing
    RIGHT SIDE: Kirsh × Kahneman 2×2 matrix showing the four architectural cells

    The key insight: IE-DPT is not a fourth pipeline stage — it is a superordinate
    configuring mechanism that determines WHICH implicit-level processes are active,
    based on activity frame, goal state, and regulatory demands.
    """

    fig, ax = plt.subplots(figsize=(16, 11))
    ax.set_xlim(0, 16)
    ax.set_ylim(-0.5, 11)
    ax.axis('off')

    # =========== IE-DPT SUPERORDINATE ENVELOPE ===========
    # Large translucent rectangle wrapping all three layers
    ie_color = '#7D3C98'  # Rich purple for IE-DPT (distinct from layer colors)

    # Outer envelope rectangle
    envelope = FancyBboxPatch((0.2, 0.3), 9.0, 9.0,
                               boxstyle="round,pad=0.15",
                               facecolor=ie_color, alpha=0.04,
                               edgecolor=ie_color, linewidth=2.5,
                               linestyle='dashed')
    ax.add_patch(envelope)

    # IE-DPT label at top of envelope
    ax.text(4.7, 9.55, "Interpretive Envelope (IE-DPT)",
            fontsize=14, fontweight='bold', color=ie_color, ha='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                     edgecolor=ie_color, linewidth=2, alpha=0.95))
    ax.text(4.7, 9.15, "The 'conductor' — decides which unconscious processes are active based on what you're doing and why",
            fontsize=8, ha='center', style='italic', color=ie_color)

    # =========== LAYER 1: EPISTEMIC NETWORK (TOP) ===========
    layer1_y = 7.5

    ax.text(0.6, layer1_y + 1.0, "Layer 1: Evidence Store (Epistemic Network)",
            fontsize=12, fontweight='bold', color=COLORS['primary'])

    en_box = FancyBboxPatch((0.7, layer1_y - 0.8), 5.0, 1.5,
                             boxstyle="round,pad=0.1",
                             facecolor=COLORS['light_gray'],
                             edgecolor=COLORS['primary'], linewidth=1.5, alpha=0.3)
    ax.add_patch(en_box)

    belief_positions = [
        (1.5, layer1_y, "B₁: Visual\nComplexity"),
        (3.0, layer1_y, "B₂: Arousal\nLevel"),
        (4.5, layer1_y, "B₃: Prediction\nError"),
    ]

    for x, y, label in belief_positions:
        circle = Circle((x, y), 0.28, facecolor=COLORS['primary'],
                       edgecolor=COLORS['primary'], linewidth=1.5, alpha=0.8)
        ax.add_patch(circle)
        ax.text(x, y - 0.6, label, fontsize=7, ha='center',
               color=COLORS['dark_gray'], fontweight='bold')

    warrant_types = [
        (1.5, layer1_y, 2.5, layer1_y, "EMPIRICAL", COLORS['secondary']),
        (3.0, layer1_y, 4.5, layer1_y, "MECHANISM", COLORS['tertiary']),
    ]

    for x1, y1, x2, y2, wt, color in warrant_types:
        ax.arrow(x1 + 0.32, y1, x2 - x1 - 0.65, 0, head_width=0.1,
                head_length=0.12, fc=color, ec=color, linewidth=1.2, alpha=0.7)
        mid_x = (x1 + x2) / 2
        ax.text(mid_x, y1 + 0.32, wt, fontsize=6.5, ha='center',
               bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                        edgecolor='none', alpha=0.8), color=color, fontweight='bold')

    ax.text(5.5, layer1_y + 0.3, "Do these\nfindings\nagree?",
           fontsize=7, ha='left', style='italic',
           bbox=dict(boxstyle='round,pad=0.2', facecolor=COLORS['accent'],
                    alpha=0.2, edgecolor=COLORS['accent'], linewidth=1))

    # =========== ARROW: EN → π ===========
    ax.annotate('', xy=(3.2, 5.95), xytext=(3.2, 6.65),
                arrowprops=dict(arrowstyle='->', lw=1.8, color=COLORS['neutral']))

    # =========== LAYER 2: PROJECTION (MIDDLE) ===========
    layer2_y = 5.0

    ax.text(0.6, layer2_y + 1.0, "Layer 2: Lab-to-Building Transfer (Projection)",
           fontsize=12, fontweight='bold', color=COLORS['secondary'])

    pi_box = FancyBboxPatch((0.7, layer2_y - 0.7), 5.0, 1.4,
                            boxstyle="round,pad=0.1",
                            facecolor=COLORS['light_gray'],
                            edgecolor=COLORS['secondary'], linewidth=1.5, alpha=0.3)
    ax.add_patch(pi_box)

    # Plain English summary of the transfer function
    ax.text(3.2, layer2_y + 0.3, "How confident should we be in a real building,",
           fontsize=9, ha='center', fontweight='bold', color=COLORS['dark_gray'])
    ax.text(3.2, layer2_y + 0.05, "given what a lab study found?",
           fontsize=9, ha='center', fontweight='bold', color=COLORS['dark_gray'])

    factors = [
        (1.0, layer2_y - 0.5, "Study\nDesign"),
        (2.2, layer2_y - 0.5, "Evidence\nQuality"),
        (3.4, layer2_y - 0.5, "Population\nMatch"),
        (4.6, layer2_y - 0.5, "Lab\nFinding"),
    ]
    for x, y, label in factors:
        ax.text(x, y, label, fontsize=7, ha='center', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.25', facecolor=COLORS['quaternary'],
                        alpha=0.2, edgecolor=COLORS['quaternary'], linewidth=1),
               color=COLORS['dark_gray'])

    # =========== ARROW: π → BN ===========
    ax.annotate('', xy=(3.2, 3.5), xytext=(3.2, 4.25),
                arrowprops=dict(arrowstyle='->', lw=1.8, color=COLORS['neutral']))

    # =========== LAYER 3: BAYESIAN NETWORK (BOTTOM) ===========
    layer3_y = 2.5

    ax.text(0.6, layer3_y + 1.0, "Layer 3: Causal Model (Bayesian Network)",
           fontsize=12, fontweight='bold', color=COLORS['tertiary'])

    bn_box = FancyBboxPatch((0.7, layer3_y - 0.8), 5.0, 1.5,
                            boxstyle="round,pad=0.1",
                            facecolor=COLORS['light_gray'],
                            edgecolor=COLORS['tertiary'], linewidth=1.5, alpha=0.3)
    ax.add_patch(bn_box)

    bn_nodes = [
        (1.5, layer3_y, "Complexity"),
        (3.0, layer3_y, "Engagement"),
        (4.5, layer3_y, "Preference"),
    ]

    for x, y, label in bn_nodes:
        rect = FancyBboxPatch((x - 0.32, y - 0.2), 0.64, 0.4,
                             boxstyle="round,pad=0.05",
                             facecolor=COLORS['tertiary'],
                             edgecolor=COLORS['tertiary'], linewidth=1.2, alpha=0.8)
        ax.add_patch(rect)
        ax.text(x, y, label, fontsize=7, ha='center', va='center',
               color='white', fontweight='bold')

    bn_edges = [
        (1.5, layer3_y, 2.65, layer3_y),
        (3.0, layer3_y, 4.15, layer3_y),
    ]
    for x1, y1, x2, y2 in bn_edges:
        ax.arrow(x1 + 0.32, y1, x2 - x1 - 0.65, 0, head_width=0.12,
                head_length=0.12, fc=COLORS['tertiary'], ec=COLORS['tertiary'],
                linewidth=1.2, alpha=0.7)

    ax.text(5.5, layer3_y + 0.3, "Updates beliefs\nas evidence\narrives",
           fontsize=7, ha='left', style='italic',
           bbox=dict(boxstyle='round,pad=0.2', facecolor=COLORS['accent'],
                    alpha=0.2, edgecolor=COLORS['accent'], linewidth=1))

    # =========== FEEDBACK LOOP (BN → EN) ===========
    ax.annotate('', xy=(6.5, 7.0), xytext=(6.5, 1.7),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['accent'],
                               linestyle='dashed'))
    ax.text(6.7, 4.5, "Gaps &\ncontradictions\nfeed back", fontsize=7,
           style='italic', color=COLORS['accent'], fontweight='bold')

    # =========== IE-DPT MODULATION ARROWS ===========
    # Three curved arrows from the envelope boundary into each layer
    # These show IE-DPT configuring which processes are active

    # Arrow: IE-DPT → EN (selects which beliefs activate)
    ax.annotate('', xy=(0.75, 7.5), xytext=(-0.1, 8.5),
                arrowprops=dict(arrowstyle='->', lw=1.8, color=ie_color,
                               connectionstyle='arc3,rad=0.2'))
    ax.text(-0.3, 8.7, "Picks which\nevidence matters\nright now", fontsize=7,
           color=ie_color, style='italic', ha='center')

    # Arrow: IE-DPT → π (modulates transfer parameters)
    ax.annotate('', xy=(0.75, 5.0), xytext=(-0.1, 5.5),
                arrowprops=dict(arrowstyle='->', lw=1.8, color=ie_color,
                               connectionstyle='arc3,rad=0.15'))
    ax.text(-0.3, 5.7, "Adjusts how\nmuch evidence\ntransfers", fontsize=7,
           color=ie_color, style='italic', ha='center')

    # Arrow: IE-DPT → BN (sets activity frame for inference)
    ax.annotate('', xy=(0.75, 2.5), xytext=(-0.1, 2.0),
                arrowprops=dict(arrowstyle='->', lw=1.8, color=ie_color,
                               connectionstyle='arc3,rad=-0.15'))
    ax.text(-0.3, 1.7, "Sets the scenario\nfor prediction", fontsize=7,
           color=ie_color, style='italic', ha='center')

    # =========== KIRSH × KAHNEMAN MATRIX (RIGHT SIDE) ===========
    mat_x = 10.0  # left edge of matrix
    mat_y = 3.0   # bottom edge of matrix
    mat_w = 5.2   # width
    mat_h = 5.0   # height
    cell_w = mat_w / 2
    cell_h = mat_h / 2

    # Matrix title
    ax.text(mat_x + mat_w/2, mat_y + mat_h + 1.3, "How Buildings Affect People: Four Ways",
           fontsize=12, fontweight='bold', ha='center', color=ie_color)
    ax.text(mat_x + mat_w/2, mat_y + mat_h + 0.9,
           "Information accessibility × processing mode → four kinds of experience",
           fontsize=8, ha='center', style='italic', color=COLORS['dark_gray'])

    # Column headers
    ax.text(mat_x + cell_w/2, mat_y + mat_h + 0.3, "Automatic\n(unconscious)",
           fontsize=9, ha='center', fontweight='bold', color=COLORS['dark_gray'])
    ax.text(mat_x + cell_w + cell_w/2, mat_y + mat_h + 0.3, "Deliberate\n(conscious effort)",
           fontsize=9, ha='center', fontweight='bold', color=COLORS['dark_gray'])
    ax.text(mat_x + mat_w/2, mat_y + mat_h + 0.6, "← How the brain processes it →",
           fontsize=8, ha='center', color=COLORS['neutral'])

    # Row headers
    ax.text(mat_x - 0.3, mat_y + cell_h + cell_h/2, "Easy to\nnotice",
           fontsize=9, ha='right', fontweight='bold', color=COLORS['dark_gray'], va='center')
    ax.text(mat_x - 0.3, mat_y + cell_h/2, "Hard to\nnotice",
           fontsize=9, ha='right', fontweight='bold', color=COLORS['dark_gray'], va='center')

    # Cell A: top-left (Kirsh-Explicit + Type 1) — THE DESIGN IDEAL
    cell_a = FancyBboxPatch((mat_x, mat_y + cell_h), cell_w, cell_h,
                            boxstyle="round,pad=0.05",
                            facecolor='#d4edda', edgecolor=COLORS['secondary'],
                            linewidth=1.5, alpha=0.7)
    ax.add_patch(cell_a)
    ax.text(mat_x + cell_w/2, mat_y + cell_h + cell_h*0.7, "Cell A",
           fontsize=10, ha='center', fontweight='bold', color=COLORS['secondary'])
    ax.text(mat_x + cell_w/2, mat_y + cell_h + cell_h*0.45,
           "DESIGN IDEAL", fontsize=8, ha='center', fontweight='bold', color='#155724')
    ax.text(mat_x + cell_w/2, mat_y + cell_h + cell_h*0.2,
           "It just works —\nyou feel right without trying",
           fontsize=7, ha='center', color=COLORS['dark_gray'], style='italic')

    # Cell B: top-right (Kirsh-Explicit + Type 2)
    cell_b = FancyBboxPatch((mat_x + cell_w, mat_y + cell_h), cell_w, cell_h,
                            boxstyle="round,pad=0.05",
                            facecolor='#fff3cd', edgecolor=COLORS['quaternary'],
                            linewidth=1.5, alpha=0.7)
    ax.add_patch(cell_b)
    ax.text(mat_x + cell_w + cell_w/2, mat_y + cell_h + cell_h*0.7, "Cell B",
           fontsize=10, ha='center', fontweight='bold', color=COLORS['quaternary'])
    ax.text(mat_x + cell_w + cell_w/2, mat_y + cell_h + cell_h*0.45,
           "Learning phase", fontsize=8, ha='center', fontweight='bold',
           color='#856404')
    ax.text(mat_x + cell_w + cell_w/2, mat_y + cell_h + cell_h*0.2,
           "You can see what to do,\nbut it takes effort",
           fontsize=7, ha='center', color=COLORS['dark_gray'], style='italic')

    # Cell C: bottom-left (Kirsh-Implicit + Type 1) — HABITUATION TRAP
    cell_c = FancyBboxPatch((mat_x, mat_y), cell_w, cell_h,
                            boxstyle="round,pad=0.05",
                            facecolor='#f8d7da', edgecolor=COLORS['quaternary'],
                            linewidth=1.5, alpha=0.7)
    ax.add_patch(cell_c)
    ax.text(mat_x + cell_w/2, mat_y + cell_h*0.7, "Cell C",
           fontsize=10, ha='center', fontweight='bold', color='#721c24')
    ax.text(mat_x + cell_w/2, mat_y + cell_h*0.45,
           "HABITUATION TRAP", fontsize=8, ha='center', fontweight='bold',
           color='#721c24')
    ax.text(mat_x + cell_w/2, mat_y + cell_h*0.2,
           "Something's wrong but\nyou can't tell what",
           fontsize=7, ha='center', color=COLORS['dark_gray'], style='italic')

    # Cell D: bottom-right (Kirsh-Implicit + Type 2)
    cell_d = FancyBboxPatch((mat_x + cell_w, mat_y), cell_w, cell_h,
                            boxstyle="round,pad=0.05",
                            facecolor='#ffeeba', edgecolor=COLORS['quaternary'],
                            linewidth=1.5, alpha=0.5)
    ax.add_patch(cell_d)
    ax.text(mat_x + cell_w + cell_w/2, mat_y + cell_h*0.7, "Cell D",
           fontsize=10, ha='center', fontweight='bold', color=COLORS['dark_gray'])
    ax.text(mat_x + cell_w + cell_w/2, mat_y + cell_h*0.45,
           "Cognitive overload", fontsize=8, ha='center', fontweight='bold',
           color='#856404')
    ax.text(mat_x + cell_w + cell_w/2, mat_y + cell_h*0.2,
           "Exhausting — nothing\nis obvious, everything\ntakes work",
           fontsize=7, ha='center', color=COLORS['dark_gray'], style='italic')

    # Design direction arrow: D → A (the goal of good design)
    ax.annotate('', xy=(mat_x + 0.5, mat_y + cell_h + cell_h*0.5),
                xytext=(mat_x + cell_w + cell_w/2, mat_y + cell_h*0.5),
                arrowprops=dict(arrowstyle='->', lw=2.5, color=ie_color,
                               connectionstyle='arc3,rad=-0.3'))
    ax.text(mat_x + cell_w, mat_y + cell_h - 0.1, "Good design\nmoves people\nfrom D → A",
           fontsize=7, ha='center', fontweight='bold', color=ie_color,
           bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                    edgecolor=ie_color, alpha=0.9, linewidth=1))

    # =========== CONNECTING LINE: Envelope to Matrix ===========
    ax.annotate('', xy=(mat_x, mat_y + mat_h/2 + 1.0),
                xytext=(9.2, 5.5),
                arrowprops=dict(arrowstyle='->', lw=1.5, color=ie_color,
                               linestyle='dotted', connectionstyle='arc3,rad=-0.1'))
    ax.text(9.5, 6.6, "Your activity and\ngoals determine\nwhich cell you're in", fontsize=7,
           color=ie_color, style='italic', ha='center',
           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9,
                    edgecolor=ie_color, linewidth=0.8))

    # =========== TWO PROCESSING CHANNELS LABELS ===========
    chan_y = 1.0
    ax.text(8.0, chan_y + 0.4, "Two Processing Channels:", fontsize=8,
           fontweight='bold', color=ie_color)
    ax.text(8.0, chan_y, "UNCONSCIOUS: Body-budget regulation, aesthetic response,",
           fontsize=7, color=COLORS['dark_gray'])
    ax.text(8.0, chan_y - 0.3, "    spatial navigation, stress reactions — fast, automatic",
           fontsize=7, color=COLORS['dark_gray'])
    ax.text(8.0, chan_y - 0.7, "CONSCIOUS: Goal-directed attention, reasoning,",
           fontsize=7, color=COLORS['dark_gray'])
    ax.text(8.0, chan_y - 1.0, "    deliberate override, meaning-making — slow, effortful",
           fontsize=7, color=COLORS['dark_gray'])

    # =========== FIGURE TITLE ===========
    fig_title = "Three Computational Layers Inside a Superordinate Interpretive Envelope"
    ax.text(8, 10.5, fig_title, fontsize=14, fontweight='bold', ha='center',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                    edgecolor=COLORS['primary'], linewidth=2, alpha=0.95))

    subtitle = "IE-DPT Configures Which Implicit Processes Are Active — The Layers Compute Within That Frame"
    ax.text(8, 10.05, subtitle, fontsize=9, ha='center', style='italic',
           color=COLORS['dark_gray'])

    # Save
    fig.savefig(OUTPUT_DIR / "m1_three_layer_architecture.svg", format='svg')
    print(f"✓ Generated: m1_three_layer_architecture.svg")
    plt.close(fig)


# =============================================================================
# FIGURE M-2: The Tier Hierarchy
# =============================================================================

def figure_m2_tier_hierarchy():
    """
    Four horizontal bands showing the tier hierarchy:
    T1: 10 frameworks → T1.5: 14 theories → T2: 93 templates → T3: 3,420 beliefs
    
    Shows REDUCES_TO, INSTANTIATES, and EXTRACTED_FROM relationships.
    """
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # =========== TIER 1: 10 FRAMEWORKS (TOP) ===========
    tier1_y = 8.0
    
    ax.text(0.3, tier1_y + 0.7, "T1: 10 Foundational Frameworks", 
           fontsize=12, fontweight='bold', color=COLORS['primary'])
    
    tier1_frameworks = [
        "PP", "SN", "DP", "DT", "NM", "IC", "MS", "EC", "CB", "MSI"
    ]
    tier1_full_names = [
        "Predictive\nProcessing",
        "Spatial\nNavigation",
        "Dual\nProcess",
        "Dynamic\nSystems",
        "Neuro\nMetabolism",
        "Implicit\nCognition",
        "Motor\nSimulation",
        "Error\nCorrection",
        "Cognitive\nBinding",
        "Meta-Strategic\nInteraction"
    ]
    
    # Space 10 circles across the width
    x_positions_t1 = np.linspace(1.0, 12.5, 10)
    
    for i, (x, abbr, full_name) in enumerate(zip(x_positions_t1, tier1_frameworks, tier1_full_names)):
        # Circle node
        circle = Circle((x, tier1_y), 0.35, facecolor=COLORS['primary'],
                       edgecolor=COLORS['primary'], linewidth=1.5, alpha=0.85)
        ax.add_patch(circle)
        # Label (abbreviated)
        ax.text(x, tier1_y, abbr, fontsize=9, ha='center', va='center',
               color='white', fontweight='bold')
        # Full name below
        ax.text(x, tier1_y - 0.7, full_name, fontsize=7, ha='center',
               color=COLORS['dark_gray'])
    
    # =========== ARROW AND LABEL ===========
    ax.annotate('', xy=(7, 6.9), xytext=(7, 7.5),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['neutral']))
    ax.text(7.5, 7.2, "REDUCES_TO", fontsize=9, fontweight='bold',
           color=COLORS['secondary'], style='italic')
    
    # =========== TIER 1.5: 14 DOMAIN THEORIES (SECOND) ===========
    tier15_y = 6.0
    
    ax.text(0.3, tier15_y + 0.7, "T1.5: 14 Domain Theories", 
           fontsize=12, fontweight='bold', color=COLORS['secondary'])
    
    tier15_theories = [
        "ART", "SRT", "Biophilia", "Goldilocks", "Prospect-Refuge",
        "Fluency", "Conceptual Metaphor", "Embodied Cognition", "Flow",
        "Attention Restoration", "Fractal Scaling", "Color Psychology",
        "Semantic Priming", "Cross-Modal Integration"
    ]
    
    # Arrange in two rows (7 theories per row)
    x_positions_t15 = np.linspace(1.0, 12.5, 7)
    
    for row in range(2):
        y = tier15_y - (row * 0.9)
        start_idx = row * 7
        end_idx = min(start_idx + 7, len(tier15_theories))
        
        for i, x in enumerate(x_positions_t15[:end_idx - start_idx]):
            theory = tier15_theories[start_idx + i]
            
            # Oval node
            oval = mpatches.Ellipse((x, y), 0.9, 0.35, 
                                   facecolor=COLORS['secondary'],
                                   edgecolor=COLORS['secondary'], linewidth=1.2,
                                   alpha=0.75)
            ax.add_patch(oval)
            # Label
            ax.text(x, y, theory, fontsize=7, ha='center', va='center',
                   color='white', fontweight='bold')
    
    # Draw reduction edges from T1.5 to T1
    # Sample connections (not all, to avoid clutter)
    sample_connections = [
        (1.0, 5.6, 1.0, 8.0),    # ART → PP
        (3.5, 5.6, 3.5, 8.0),    # Goldilocks → DP
        (6.0, 5.6, 6.0, 8.0),    # Prospect-Refuge → SN
        (9.0, 5.6, 9.0, 8.0),    # Flow → IC
        (12.5, 4.7, 12.5, 8.0),  # Cross-Modal → CB
    ]
    
    for x1, y1, x2, y2 in sample_connections:
        ax.plot([x1, x2], [y1, y2], color=COLORS['secondary'], 
               linewidth=1.0, alpha=0.4, linestyle='--')
    
    # =========== ARROW AND LABEL ===========
    ax.annotate('', xy=(7, 3.9), xytext=(7, 4.5),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['neutral']))
    ax.text(7.5, 4.2, "INSTANTIATES", fontsize=9, fontweight='bold',
           color=COLORS['tertiary'], style='italic')
    
    # =========== TIER 2: ~93 EXTRACTION TEMPLATES (THIRD) ===========
    tier2_y = 3.3
    
    ax.text(0.3, tier2_y + 0.6, "T2: ~93 Extraction Templates (Grouped by Domain)", 
           fontsize=12, fontweight='bold', color=COLORS['tertiary'])
    
    # Show grouped template blocks
    template_groups = [
        ("Visual", 18, 1.5),
        ("Auditory", 12, 3.5),
        ("Spatial", 15, 5.5),
        ("Motor", 10, 7.0),
        ("Cognitive", 20, 9.0),
        ("Social", 8, 11.0),
    ]
    
    for group_name, count, x_center in template_groups:
        # Bar showing template count
        bar_width = 0.8
        bar = Rectangle((x_center - bar_width/2, tier2_y - 0.3), bar_width, 0.35,
                       facecolor=COLORS['tertiary'], edgecolor=COLORS['tertiary'],
                       linewidth=1.0, alpha=0.7)
        ax.add_patch(bar)
        # Group label and count
        ax.text(x_center, tier2_y + 0.25, f"{group_name}\n({count})", 
               fontsize=7, ha='center', color=COLORS['dark_gray'], fontweight='bold')
    
    # =========== ARROW AND LABEL ===========
    ax.annotate('', xy=(7, 2.1), xytext=(7, 2.7),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['neutral']))
    ax.text(7.5, 2.4, "EXTRACTED_FROM", fontsize=9, fontweight='bold',
           color=COLORS['quaternary'], style='italic')
    
    # =========== TIER 3: 3,420 BELIEFS (BOTTOM) ===========
    tier3_y = 1.2
    
    ax.text(0.3, tier3_y + 0.6, "T3: 3,420 Beliefs (from 813 scientific papers)", 
           fontsize=12, fontweight='bold', color=COLORS['quaternary'])
    
    # Large scatter/density representation of 3,420 beliefs
    # Use a pseudo-scatter effect (grid of small points)
    np.random.seed(42)
    
    # Create a density visualization across the width
    for x in np.linspace(1.0, 12.5, 25):
        # Variable height to show density concentration
        density = np.random.randint(5, 20)
        for i in range(density):
            y_offset = np.random.uniform(-0.3, 0.3)
            dot = Circle((x, tier3_y + y_offset), 0.04, 
                        facecolor=COLORS['quaternary'], alpha=0.6)
            ax.add_patch(dot)
    
    # Density label
    ax.text(13.0, tier3_y, "~3,420\nbeliefs", fontsize=8, ha='left',
           fontweight='bold', color=COLORS['quaternary'])
    
    # =========== FIGURE TITLE AND CAPTION ===========
    fig_title = "The Tier Hierarchy: 10 Frameworks → 14 Theories → 93 Templates → 3,420 Beliefs"
    ax.text(7, 9.3, fig_title, fontsize=14, fontweight='bold', ha='center',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                    edgecolor=COLORS['primary'], linewidth=2, alpha=0.95))
    
    subtitle = "From 10 Foundational Frameworks to 3,420 Evidence-Backed Beliefs"
    ax.text(7, 8.85, subtitle, fontsize=11, ha='center', style='italic',
           color=COLORS['dark_gray'])
    
    # Save
    fig.savefig(OUTPUT_DIR / "m2_tier_hierarchy.svg", format='svg')
    print(f"✓ Generated: m2_tier_hierarchy.svg")
    plt.close(fig)


# =============================================================================
# FIGURE M-3: The ATLAS Pipeline
# =============================================================================

def figure_m3_pipeline_flowchart():
    """
    Horizontal flowchart showing the 7 stages of epistemic scrutiny:
    PDF → Extraction → Validation → Credence → BN Integration → Coherence Check → QA
    
    Plus: OVERSEER monitoring (above) and Recommendation Loop (below).
    """
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # =========== MAIN PIPELINE (CENTER) ===========
    pipeline_y = 5.0
    pipeline_stages = [
        ("1. PDF", 1.0, "Input"),
        ("2. Extraction\n(Gemini)", 2.8, "extract_papers"),
        ("3. Validation\n(FieldValidator)", 4.6, "extraction_field_validator"),
        ("4. Credence\nComputation", 6.4, "warrant strength"),
        ("5. BN Integration\n(ConjugatePrior)", 8.2, "update_bn"),
        ("6. Coherence Check\n(full recomputation)", 10.0, "cohere_state"),
        ("7. QA System\n(user-facing)", 11.8, "answer gen"),
    ]
    
    # Draw pipeline stages
    for i, (stage_name, x, module_name) in enumerate(pipeline_stages):
        # Stage box
        if i == 0:
            # Input box (document icon style)
            input_box = Rectangle((x - 0.35, pipeline_y - 0.35), 0.7, 0.7,
                                 facecolor=COLORS['primary'], 
                                 edgecolor=COLORS['primary'],
                                 linewidth=1.5, alpha=0.8)
            ax.add_patch(input_box)
            ax.text(x, pipeline_y, "📄", fontsize=20, ha='center', va='center')
        else:
            # Stage box
            stage_box = FancyBboxPatch((x - 0.45, pipeline_y - 0.35), 0.9, 0.7,
                                      boxstyle="round,pad=0.05",
                                      facecolor=COLORS['primary'],
                                      edgecolor=COLORS['primary'],
                                      linewidth=1.5, alpha=0.8)
            ax.add_patch(stage_box)
        
        # Stage label
        ax.text(x, pipeline_y + 0.6, stage_name, fontsize=8, ha='center',
               fontweight='bold', color=COLORS['primary'])
        
        # Module/function name below
        ax.text(x, pipeline_y - 0.8, module_name, fontsize=7, ha='center',
               style='italic', color=COLORS['dark_gray'])
        
        # Arrow between stages
        if i < len(pipeline_stages) - 1:
            next_x = pipeline_stages[i + 1][1]
            ax.arrow(x + 0.45, pipeline_y, next_x - x - 0.9, 0,
                    head_width=0.15, head_length=0.15,
                    fc=COLORS['primary'], ec=COLORS['primary'],
                    linewidth=1.5, alpha=0.7)
    
    # Quality gate annotation (between extraction and validation)
    ax.text(3.7, 4.2, "Quality Gate\n(threshold = 0.75)", fontsize=7, ha='center',
           style='italic', bbox=dict(boxstyle='round,pad=0.3',
           facecolor=COLORS['secondary'], alpha=0.2,
           edgecolor=COLORS['secondary'], linewidth=1))
    
    # =========== OVERSEER MONITORING (ABOVE) ===========
    overseer_y = 7.5
    
    ax.text(0.3, overseer_y + 0.6, "OVERSEER Monitoring", 
           fontsize=11, fontweight='bold', color=COLORS['accent'])
    
    # OVERSEER box spanning entire pipeline
    overseer_box = FancyBboxPatch((0.8, overseer_y - 0.35), 11.0, 0.7,
                                 boxstyle="round,pad=0.05",
                                 facecolor=COLORS['accent'],
                                 edgecolor=COLORS['accent'],
                                 linewidth=1.5, alpha=0.15)
    ax.add_patch(overseer_box)
    
    # Health checks
    ax.text(3.0, overseer_y, "Health Checks", fontsize=8, ha='center',
           fontweight='bold', color=COLORS['accent'])
    ax.text(7.0, overseer_y, "AESHI Scoring", fontsize=8, ha='center',
           fontweight='bold', color=COLORS['accent'])
    ax.text(11.0, overseer_y, "Error Tracking", fontsize=8, ha='center',
           fontweight='bold', color=COLORS['accent'])
    
    # Connection lines from OVERSEER to pipeline
    ax.plot([3.0, 3.0], [overseer_y - 0.35, pipeline_y + 0.35], 
           color=COLORS['accent'], linewidth=0.8, alpha=0.4, linestyle=':')
    ax.plot([7.0, 7.0], [overseer_y - 0.35, pipeline_y + 0.35],
           color=COLORS['accent'], linewidth=0.8, alpha=0.4, linestyle=':')
    ax.plot([11.0, 11.0], [overseer_y - 0.35, pipeline_y + 0.35],
           color=COLORS['accent'], linewidth=0.8, alpha=0.4, linestyle=':')
    
    # =========== RECOMMENDATION LOOP (BELOW) ===========
    loop_y = 2.5
    
    ax.text(0.3, loop_y + 0.8, "Recommendation Loop", 
           fontsize=11, fontweight='bold', color=COLORS['secondary'])
    
    loop_stages = [
        ("Gap Detection", 1.8),
        ("VOI Scoring", 3.6),
        ("Search Dispatch", 5.4),
        ("↻ Loop Back to PDF", 7.2),
    ]
    
    for stage_name, x in loop_stages:
        # Stage circle
        circle = Circle((x, loop_y), 0.3, facecolor=COLORS['secondary'],
                       edgecolor=COLORS['secondary'], linewidth=1.2, alpha=0.7)
        ax.add_patch(circle)
        # Label
        ax.text(x, loop_y - 0.7, stage_name, fontsize=7, ha='center',
               color=COLORS['dark_gray'], fontweight='bold')
    
    # Curved arrows showing loop
    loop_x_positions = [1.8, 3.6, 5.4, 7.2]
    for i in range(len(loop_x_positions) - 1):
        x1, x2 = loop_x_positions[i], loop_x_positions[i + 1]
        ax.annotate('', xy=(x2 - 0.3, loop_y), xytext=(x1 + 0.3, loop_y),
                   arrowprops=dict(arrowstyle='->', lw=1.5, 
                                  color=COLORS['secondary'], alpha=0.7))
    
    # Loop back arrow
    ax.annotate('', xy=(1.5, loop_y), xytext=(7.5, loop_y),
               arrowprops=dict(arrowstyle='->', lw=1.5, 
                              color=COLORS['secondary'], alpha=0.6,
                              connectionstyle="arc3,rad=0.5"))
    
    # Connection from main pipeline to recommendation loop
    ax.plot([6.4, 6.4], [pipeline_y - 0.35, loop_y + 0.3],
           color=COLORS['secondary'], linewidth=1.0, alpha=0.5, linestyle=':')
    ax.text(6.8, 3.8, "Trigger\nGap", fontsize=7, style='italic',
           color=COLORS['secondary'])
    
    # =========== FIGURE TITLE AND CAPTION ===========
    fig_title = "The ATLAS Pipeline: From PDF to Belief to Design Guidance"
    ax.text(7, 9.3, fig_title, fontsize=14, fontweight='bold', ha='center',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                    edgecolor=COLORS['primary'], linewidth=2, alpha=0.95))
    
    subtitle = "Every Belief Passes Through Seven Stages of Epistemic Scrutiny"
    ax.text(7, 8.85, subtitle, fontsize=11, ha='center', style='italic',
           color=COLORS['dark_gray'])
    
    # Bottom legend
    legend_y = 0.4
    ax.text(0.5, legend_y, "Green path = main epistemic pipeline  |  Red path = feedback loop  |  Purple = continuous monitoring",
           fontsize=8, style='italic', color=COLORS['dark_gray'])
    
    # Save
    fig.savefig(OUTPUT_DIR / "m3_pipeline_flowchart.svg", format='svg')
    print(f"✓ Generated: m3_pipeline_flowchart.svg")
    plt.close(fig)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Generate all three master document figures."""
    
    print("\n" + "="*70)
    print("ATLAS Master Document: Generating Architecture Overview Figures")
    print("="*70)
    
    print("\nOutput directory:", OUTPUT_DIR)
    print("\nGenerating figures...")
    
    figure_m1_three_layer_architecture()
    figure_m2_tier_hierarchy()
    figure_m3_pipeline_flowchart()
    
    print("\n" + "="*70)
    print("SUCCESS: All 3 master document figures generated!")
    print("="*70)
    print("\nFiles created:")
    print("  1. m1_three_layer_architecture.svg")
    print("  2. m2_tier_hierarchy.svg")
    print("  3. m3_pipeline_flowchart.svg")
    print("\nLocation:", OUTPUT_DIR)
    print("\nThese are the '60-second understanding' figures for readers.\n")


if __name__ == '__main__':
    main()
