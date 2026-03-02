#!/usr/bin/env python3
"""
Generate 12 Domain Panel SVG Figures (M-7 through M-18) for ATLAS Master Documentation

This script creates publication-ready SVG visualizations for each domain panel,
showing framework feed-in, template counts, key parameters, and exemplar findings.

ATLAS Visual Palette:
- Deep Navy: #1B2A4A (titles)
- Slate Blue: #2E5090 (borders, axes)
- Warm Gold: #D4A843 (highlights, key findings)
- Sage Green: #5B8C5A (evidence strength)
- Terracotta: #C17B4A (warnings, uncertainty)
- Cool Gray: #8B9DAF (background, secondary)
- Cream: #F5F0E8 (canvas)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
import numpy as np
from pathlib import Path
import textwrap

# ATLAS Color Palette
COLORS = {
    'navy': '#1B2A4A',
    'slate_blue': '#2E5090',
    'gold': '#D4A843',
    'sage_green': '#5B8C5A',
    'terracotta': '#C17B4A',
    'cool_gray': '#8B9DAF',
    'cream': '#F5F0E8',
}

# T1 Framework Set (10 frameworks used across panels)
T1_FRAMEWORKS = [
    'Predictive Processing',
    'Neuroaesthetics',
    'Environmental Psychology',
    'Chronobiology',
    'Adaptive Comfort Theory',
    'Allostasis',
    'Psychoacoustics',
    'BRECVEMA',
    'Cognitive Map Theory',
    'Multisensory Integration',
]

# Warrant Type Colors
WARRANT_COLORS = {
    'EMPIRICAL_ASSOCIATION': '#5B8C5A',      # sage_green
    'MECHANISM': '#D4A843',                   # gold
    'THEORY_DERIVED': '#2E5090',              # slate_blue
    'ANALOGICAL': '#C17B4A',                  # terracotta
}

# Panel Data Structure
PANELS = {
    7: {
        'name': 'VISUAL-I',
        'title': 'Fractal Dimension Peaks at D ≈ 1.3 Because Natural Scenes Cluster There',
        'section': '§60',
        'frameworks': ['Predictive Processing', 'Neuroaesthetics', 'Environmental Psychology'],
        'templates': 15,
        'warrant_dist': {
            'EMPIRICAL_ASSOCIATION': 8,
            'MECHANISM': 7,
            'THEORY_DERIVED': 0,
            'ANALOGICAL': 0,
        },
        'key_params': [
            ('Fractal Dimension D', 1.2, 1.5, 1.3),
            ('Luminance Contrast', 0.2, 0.8, 0.5),
            ('Visual Complexity', 0.3, 0.9, 0.6),
        ],
        'exemplar': {
            'name': 'Fractal facade → preference',
            'd': 0.80,
            'ω': 0.65,
            'δ': 0.85,
            'credence': 0.68,
        },
    },
    8: {
        'name': 'LIGHT-I',
        'title': 'Two Pathways — Image-Forming Vision and Non-Visual Regulation',
        'section': '§61',
        'frameworks': ['Chronobiology', 'Predictive Processing', 'Environmental Psychology'],
        'templates': 12,
        'warrant_dist': {
            'EMPIRICAL_ASSOCIATION': 5,
            'MECHANISM': 7,
            'THEORY_DERIVED': 0,
            'ANALOGICAL': 0,
        },
        'key_params': [
            ('Melanopic EDI', 200, 500, 350),
            ('CCT', 2700, 6500, 4500),
            ('Daylight Factor', 2, 5, 3.5),
        ],
        'exemplar': {
            'name': 'Daylight multichannel → circadian',
            'd': 0.95,
            'ω': 0.70,
            'δ': 0.90,
            'credence': 0.72,
        },
    },
    9: {
        'name': 'THERMAL-I',
        'title': 'Adaptive Comfort Follows Culture, Not Just Physics',
        'section': '§68',
        'frameworks': ['Adaptive Comfort Theory', 'Predictive Processing', 'Allostasis'],
        'templates': 10,
        'warrant_dist': {
            'EMPIRICAL_ASSOCIATION': 6,
            'MECHANISM': 4,
            'THEORY_DERIVED': 0,
            'ANALOGICAL': 0,
        },
        'key_params': [
            ('Temperature', 20, 26, 23),
            ('Humidity', 40, 60, 50),
            ('Air Velocity (m/s)', 0.1, 0.3, 0.2),
        ],
        'exemplar': {
            'name': 'Adaptive comfort → satisfaction',
            'd': 0.80,
            'ω': 0.72,
            'δ': 0.80,
            'credence': 0.65,
        },
    },
    10: {
        'name': 'ACOUSTIC-I',
        'title': 'Soundscape Quality Modulates the Noise-Annoyance Curve',
        'section': '§64',
        'frameworks': ['Predictive Processing', 'Psychoacoustics', 'Environmental Psychology'],
        'templates': 8,
        'warrant_dist': {
            'EMPIRICAL_ASSOCIATION': 5,
            'MECHANISM': 3,
            'THEORY_DERIVED': 0,
            'ANALOGICAL': 0,
        },
        'key_params': [
            ('Background Noise (dB)', 35, 45, 40),
            ('RT60 (s)', 0.4, 0.8, 0.6),
            ('STI', 0.6, 1.0, 0.8),
        ],
        'exemplar': {
            'name': 'Speech intelligibility → cognition',
            'd': 0.80,
            'ω': 0.68,
            'δ': 0.85,
            'credence': 0.62,
        },
    },
    11: {
        'name': 'MUSIC-I',
        'title': 'Eight BRECVEMA Mechanisms With Different Temporal Signatures',
        'section': '§64',
        'frameworks': ['BRECVEMA', 'Predictive Processing', 'Affective Neuroscience'],
        'templates': 8,
        'warrant_dist': {
            'EMPIRICAL_ASSOCIATION': 2,
            'MECHANISM': 3,
            'THEORY_DERIVED': 3,
            'ANALOGICAL': 0,
        },
        'key_params': [
            ('Tempo (BPM)', 60, 120, 90),
            ('Rhythmic Complexity', 0.12, 0.25, 0.18),
            ('Harmonic Tension', 0.3, 0.9, 0.6),
        ],
        'exemplar': {
            'name': 'Auditory PE from rhythm → mood',
            'd': 0.65,
            'ω': 0.60,
            'δ': 0.70,
            'credence': 0.55,
        },
    },
    12: {
        'name': 'STRESS-I',
        'title': 'Cortisol Dynamics Reveal Allostatic Load Before Symptoms',
        'section': '§63',
        'frameworks': ['Allostasis', 'Predictive Processing', 'Environmental Psychology'],
        'templates': 10,
        'warrant_dist': {
            'EMPIRICAL_ASSOCIATION': 5,
            'MECHANISM': 5,
            'THEORY_DERIVED': 0,
            'ANALOGICAL': 0,
        },
        'key_params': [
            ('Cortisol Recovery λ', 0.02, 0.05, 0.03),
            ('R_h Ratio', 0.25, 0.50, 0.35),
            ('Noise Threshold (dB)', 45, 65, 55),
        ],
        'exemplar': {
            'name': 'Ceiling height → cortisol recovery',
            'd': 0.80,
            'ω': 0.62,
            'δ': 0.75,
            'credence': 0.58,
        },
    },
    13: {
        'name': 'SOCIAL-I',
        'title': 'Proxemics Zones Define Optimal Density',
        'section': '§65',
        'frameworks': ['Proxemics', 'Social Identity', 'Predictive Processing'],
        'templates': 10,
        'warrant_dist': {
            'EMPIRICAL_ASSOCIATION': 6,
            'MECHANISM': 4,
            'THEORY_DERIVED': 0,
            'ANALOGICAL': 0,
        },
        'key_params': [
            ('Intimate Distance (m)', 0, 0.5, 0.25),
            ('Personal Distance (m)', 0.5, 1.2, 0.85),
            ('Social Distance (m)', 1.2, 3.6, 2.4),
        ],
        'exemplar': {
            'name': 'Seating distance → social comfort',
            'd': 0.80,
            'ω': 0.65,
            'δ': 0.80,
            'credence': 0.60,
        },
    },
    14: {
        'name': 'MEMORY-I',
        'title': 'Hippocampal Place Cells Map Architecture Into Cognitive Maps',
        'section': '§66',
        'frameworks': ['Cognitive Map Theory', 'Predictive Processing', 'Episodic Memory'],
        'templates': 10,
        'warrant_dist': {
            'EMPIRICAL_ASSOCIATION': 3,
            'MECHANISM': 4,
            'THEORY_DERIVED': 3,
            'ANALOGICAL': 0,
        },
        'key_params': [
            ('Landmark Distinctiveness', 0.35, 0.95, 0.65),
            ('Path Integration', 0.4, 0.9, 0.65),
            ('Boundary Vector Weight', 0.3, 0.8, 0.55),
        ],
        'exemplar': {
            'name': 'Spatial distinctiveness → wayfinding',
            'd': 0.65,
            'ω': 0.58,
            'δ': 0.80,
            'credence': 0.52,
        },
    },
    15: {
        'name': 'MULTI-I',
        'title': 'Cross-Modal Interactions Are the Rule, Not the Exception',
        'section': '§67',
        'frameworks': ['Multisensory Integration', 'Predictive Processing', 'Material Perception'],
        'templates': 9,
        'warrant_dist': {
            'EMPIRICAL_ASSOCIATION': 4,
            'MECHANISM': 5,
            'THEORY_DERIVED': 0,
            'ANALOGICAL': 0,
        },
        'key_params': [
            ('Congruence Index', 0.7, 1.0, 0.85),
            ('Temporal Window (ms)', 150, 250, 200),
            ('Spatial Coincidence', 0.5, 1.0, 0.75),
        ],
        'exemplar': {
            'name': 'Visual-haptic congruence → material',
            'd': 0.65,
            'ω': 0.55,
            'δ': 0.75,
            'credence': 0.50,
        },
    },
    16: {
        'name': 'CREATIVE-I',
        'title': 'Flow States Require Specific Environmental Conditions',
        'section': '§69',
        'frameworks': ['Flow Theory', 'Predictive Processing', 'Neuroaesthetics'],
        'templates': 8,
        'warrant_dist': {
            'EMPIRICAL_ASSOCIATION': 2,
            'MECHANISM': 3,
            'THEORY_DERIVED': 3,
            'ANALOGICAL': 0,
        },
        'key_params': [
            ('Challenge-Skill Ratio', 0.8, 1.2, 1.0),
            ('Ambient Noise (dB)', 50, 70, 60),
            ('Visual Complexity', 0.3, 0.7, 0.5),
        ],
        'exemplar': {
            'name': 'Environmental conditions → divergence',
            'd': 0.55,
            'ω': 0.50,
            'δ': 0.65,
            'credence': 0.45,
        },
    },
    17: {
        'name': 'NEUROMOD-I',
        'title': 'Three Neuromodulators Converge at the Complexity Optimum',
        'section': '§70',
        'frameworks': ['Neuromodulation', 'Allostasis', 'Predictive Processing'],
        'templates': 12,
        'warrant_dist': {
            'EMPIRICAL_ASSOCIATION': 2,
            'MECHANISM': 3,
            'THEORY_DERIVED': 7,
            'ANALOGICAL': 0,
        },
        'key_params': [
            ('DA Anticipated Reward', 0.3, 0.8, 0.55),
            ('5-HT Wellbeing', 0.4, 0.9, 0.65),
            ('OXT Social Bonding', 0.3, 0.8, 0.55),
        ],
        'exemplar': {
            'name': 'Nature view → DA + cortisol control',
            'd': 0.55,
            'ω': 0.45,
            'δ': 0.70,
            'credence': 0.42,
        },
    },
    18: {
        'name': 'CROSSCUT-I',
        'title': 'Cross-Panel Interactions Form a Dense Network',
        'section': '§71',
        'frameworks': ['Predictive Processing', 'Allostasis', 'Cognitive Map Theory'],
        'templates': 17,
        'warrant_dist': {
            'EMPIRICAL_ASSOCIATION': 4,
            'MECHANISM': 6,
            'THEORY_DERIVED': 7,
            'ANALOGICAL': 0,
        },
        'key_params': [
            ('AX4 Control Modifier', 0.6, 1.4, 1.0),
            ('Dose-Response Slope', 0.5, 1.5, 1.0),
            ('Habituation Rate', 0.01, 0.05, 0.03),
        ],
        'exemplar': {
            'name': 'Perceived control → stress modulation',
            'd': 0.65,
            'ω': 0.55,
            'δ': 0.80,
            'credence': 0.52,
        },
    },
}


def draw_framework_feed_in(ax, panel_num, frameworks, x_start=0.05, y_start=0.70, box_width=0.25):
    """
    Draw T1 Framework feed-in on the left side showing which frameworks feed this panel.
    Each framework is a colored box with an arrow to the central region.
    """
    ax.text(
        x_start,
        y_start + 0.08,
        'T1 Framework Feed-In',
        fontsize=9,
        fontweight='bold',
        color=COLORS['navy'],
        transform=ax.transAxes,
    )

    # Color palette for frameworks
    framework_colors = plt.cm.Set3(np.linspace(0, 1, len(T1_FRAMEWORKS)))

    y_pos = y_start
    for i, framework in enumerate(frameworks):
        y_pos = y_start - (i * 0.15)
        
        # Find the framework in the full list to assign consistent color
        fw_idx = T1_FRAMEWORKS.index(framework) if framework in T1_FRAMEWORKS else i
        color = plt.cm.Set3(fw_idx / len(T1_FRAMEWORKS))
        
        # Draw framework box
        box = FancyBboxPatch(
            (x_start, y_pos - 0.04),
            box_width,
            0.05,
            boxstyle='round,pad=0.003',
            transform=ax.transAxes,
            edgecolor=COLORS['slate_blue'],
            facecolor=color,
            alpha=0.7,
            linewidth=1,
        )
        ax.add_patch(box)

        # Add framework label
        label = framework[:20]  # Truncate if too long
        ax.text(
            x_start + box_width / 2,
            y_pos,
            label,
            fontsize=7,
            ha='center',
            va='center',
            transform=ax.transAxes,
        )

        # Draw arrow to center
        arrow = FancyArrowPatch(
            (x_start + box_width, y_pos),
            (0.35, 0.45),
            arrowstyle='->',
            mutation_scale=15,
            color=COLORS['slate_blue'],
            alpha=0.5,
            linewidth=1,
            transform=ax.transAxes,
        )
        ax.add_patch(arrow)


def draw_template_count_and_warrants(ax, templates, warrant_dist, x_center=0.48, y_center=0.52):
    """
    Draw template count and warrant type distribution in the center.
    Uses a stacked bar showing count and proportional warrant breakdown.
    """
    ax.text(
        x_center - 0.05,
        y_center + 0.13,
        'Templates & Warrants',
        fontsize=9,
        fontweight='bold',
        color=COLORS['navy'],
        ha='left',
        transform=ax.transAxes,
    )

    # Total warranty count
    total_warrants = sum(warrant_dist.values())
    
    # Draw main template count box
    box = FancyBboxPatch(
        (x_center - 0.08, y_center + 0.05),
        0.16,
        0.06,
        boxstyle='round,pad=0.005',
        transform=ax.transAxes,
        edgecolor=COLORS['slate_blue'],
        facecolor=COLORS['cream'],
        linewidth=2,
    )
    ax.add_patch(box)

    ax.text(
        x_center,
        y_center + 0.08,
        f'{templates} Templates',
        fontsize=10,
        fontweight='bold',
        ha='center',
        va='center',
        transform=ax.transAxes,
        color=COLORS['navy'],
    )

    # Draw stacked warrant bar
    y_bar = y_center - 0.02
    x_bar_start = x_center - 0.08
    bar_height = 0.03
    total_width = 0.16

    warrant_types = ['EMPIRICAL_ASSOCIATION', 'MECHANISM', 'THEORY_DERIVED', 'ANALOGICAL']
    x_pos = x_bar_start

    for warrant_type in warrant_types:
        count = warrant_dist.get(warrant_type, 0)
        if count > 0:
            width = (count / total_warrants) * total_width if total_warrants > 0 else 0
            rect = Rectangle(
                (x_pos, y_bar),
                width,
                bar_height,
                transform=ax.transAxes,
                facecolor=WARRANT_COLORS[warrant_type],
                edgecolor=COLORS['slate_blue'],
                linewidth=0.5,
                alpha=0.8,
            )
            ax.add_patch(rect)

            # Add count label if segment is wide enough
            if width > 0.02:
                ax.text(
                    x_pos + width / 2,
                    y_bar + bar_height / 2,
                    str(count),
                    fontsize=6,
                    ha='center',
                    va='center',
                    transform=ax.transAxes,
                    color='white',
                    fontweight='bold',
                )
            x_pos += width

    # Add legend below
    legend_y = y_bar - 0.05
    legend_items = [
        ('EA', WARRANT_COLORS['EMPIRICAL_ASSOCIATION']),
        ('M', WARRANT_COLORS['MECHANISM']),
        ('TD', WARRANT_COLORS['THEORY_DERIVED']),
        ('AN', WARRANT_COLORS['ANALOGICAL']),
    ]
    x_legend = x_bar_start
    for label, color in legend_items:
        if warrant_dist.get(
            {
                'EA': 'EMPIRICAL_ASSOCIATION',
                'M': 'MECHANISM',
                'TD': 'THEORY_DERIVED',
                'AN': 'ANALOGICAL',
            }[label],
            0,
        ) > 0:
            small_rect = Rectangle(
                (x_legend, legend_y),
                0.02,
                0.015,
                transform=ax.transAxes,
                facecolor=color,
                alpha=0.8,
            )
            ax.add_patch(small_rect)
            ax.text(
                x_legend + 0.025,
                legend_y + 0.0075,
                label,
                fontsize=5,
                ha='left',
                va='center',
                transform=ax.transAxes,
            )
            x_legend += 0.05


def draw_key_parameters(ax, key_params, x_right=0.70, y_start=0.70):
    """
    Draw key parameters with Goldilocks ranges on the right side.
    Shows min-optimal-max range for each parameter.
    """
    ax.text(
        x_right,
        y_start + 0.08,
        'Key Parameters',
        fontsize=9,
        fontweight='bold',
        color=COLORS['navy'],
        ha='left',
        transform=ax.transAxes,
    )

    y_pos = y_start
    for param_name, min_val, max_val, opt_val in key_params:
        y_pos -= 0.16

        # Shorten parameter name if needed
        short_name = param_name[:20]
        ax.text(
            x_right,
            y_pos + 0.08,
            short_name,
            fontsize=7,
            ha='left',
            transform=ax.transAxes,
            color=COLORS['navy'],
            fontweight='bold',
        )

        # Draw parameter range bar
        bar_x = x_right
        bar_y = y_pos + 0.02
        bar_width = 0.18
        bar_height = 0.015

        # Normalize for visualization
        range_val = max_val - min_val
        opt_pos = ((opt_val - min_val) / range_val * bar_width) if range_val > 0 else bar_width / 2

        # Background bar
        bg_rect = Rectangle(
            (bar_x, bar_y),
            bar_width,
            bar_height,
            transform=ax.transAxes,
            facecolor=COLORS['cool_gray'],
            alpha=0.3,
            edgecolor=COLORS['slate_blue'],
            linewidth=1,
        )
        ax.add_patch(bg_rect)

        # Optimal range (middle 60%)
        opt_width = bar_width * 0.6
        opt_start = bar_x + (bar_width - opt_width) / 2
        opt_rect = Rectangle(
            (opt_start, bar_y),
            opt_width,
            bar_height,
            transform=ax.transAxes,
            facecolor=COLORS['sage_green'],
            alpha=0.6,
            edgecolor=COLORS['sage_green'],
            linewidth=0.5,
        )
        ax.add_patch(opt_rect)

        # Optimal point marker
        marker_x = bar_x + opt_pos
        ax.plot(
            [marker_x, marker_x],
            [bar_y - 0.005, bar_y + bar_height + 0.005],
            color=COLORS['gold'],
            linewidth=2,
            transform=ax.transAxes,
        )

        # Value labels
        min_label = f'{min_val:.2g}' if isinstance(min_val, float) else str(min_val)
        max_label = f'{max_val:.2g}' if isinstance(max_val, float) else str(max_val)
        opt_label = f'{opt_val:.2g}' if isinstance(opt_val, float) else str(opt_val)

        ax.text(
            bar_x - 0.01,
            bar_y - 0.015,
            min_label,
            fontsize=5,
            ha='right',
            va='top',
            transform=ax.transAxes,
            color=COLORS['cool_gray'],
        )
        ax.text(
            bar_x + bar_width + 0.01,
            bar_y - 0.015,
            max_label,
            fontsize=5,
            ha='left',
            va='top',
            transform=ax.transAxes,
            color=COLORS['cool_gray'],
        )
        ax.text(
            marker_x,
            bar_y + bar_height + 0.025,
            opt_label,
            fontsize=6,
            ha='center',
            va='bottom',
            transform=ax.transAxes,
            color=COLORS['gold'],
            fontweight='bold',
        )


def draw_exemplar_finding(ax, exemplar, y_exemplar=0.12):
    """
    Draw one exemplar finding at the bottom with credence trace.
    Shows: Finding → d → ω → δ → final credence
    """
    ax.text(
        0.5,
        y_exemplar + 0.08,
        'Exemplar Finding with Credence Trace',
        fontsize=9,
        fontweight='bold',
        color=COLORS['navy'],
        ha='center',
        transform=ax.transAxes,
    )

    # Main exemplar box
    ex_box = FancyBboxPatch(
        (0.05, y_exemplar - 0.02),
        0.90,
        0.055,
        boxstyle='round,pad=0.005',
        transform=ax.transAxes,
        edgecolor=COLORS['gold'],
        facecolor=COLORS['cream'],
        linewidth=2,
    )
    ax.add_patch(ex_box)

    # Finding text
    finding_text = exemplar['name']
    ax.text(
        0.08,
        y_exemplar + 0.015,
        finding_text,
        fontsize=8,
        ha='left',
        va='center',
        transform=ax.transAxes,
        color=COLORS['navy'],
        fontweight='bold',
    )

    # Credence trace: d → ω → δ → credence
    trace_x_start = 0.55
    trace_y = y_exemplar + 0.008
    trace_values = [
        ('d', exemplar['d']),
        ('ω', exemplar['ω']),
        ('δ', exemplar['δ']),
        ('credence', exemplar['credence']),
    ]

    x_pos = trace_x_start
    for i, (label, value) in enumerate(trace_values):
        # Value box
        val_box = FancyBboxPatch(
            (x_pos, trace_y - 0.012),
            0.08,
            0.024,
            boxstyle='round,pad=0.002',
            transform=ax.transAxes,
            edgecolor=COLORS['slate_blue'],
            facecolor=COLORS['cool_gray'],
            alpha=0.3,
            linewidth=0.5,
        )
        ax.add_patch(val_box)

        # Label and value
        ax.text(
            x_pos + 0.04,
            trace_y + 0.010,
            label,
            fontsize=6,
            ha='center',
            va='bottom',
            transform=ax.transAxes,
            color=COLORS['navy'],
            fontweight='bold',
        )
        ax.text(
            x_pos + 0.04,
            trace_y - 0.002,
            f'{value:.2f}',
            fontsize=7,
            ha='center',
            va='center',
            transform=ax.transAxes,
            color=COLORS['navy'],
        )

        # Arrow between values
        if i < len(trace_values) - 1:
            arrow = FancyArrowPatch(
                (x_pos + 0.085, trace_y),
                (x_pos + 0.095, trace_y),
                arrowstyle='->',
                mutation_scale=10,
                color=COLORS['slate_blue'],
                alpha=0.5,
                linewidth=0.8,
                transform=ax.transAxes,
            )
            ax.add_patch(arrow)

        x_pos += 0.10


def create_domain_panel_figure(panel_num):
    """
    Create a single domain panel figure with all components.
    """
    panel_data = PANELS[panel_num]

    fig, ax = plt.subplots(figsize=(10.67, 8), dpi=100)
    fig.patch.set_facecolor(COLORS['cream'])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # ========== HEADER ==========
    # Panel label and section
    ax.text(
        0.05,
        0.95,
        f"{panel_data['name']} ({panel_data['section']})",
        fontsize=12,
        fontweight='bold',
        color=COLORS['navy'],
        transform=ax.transAxes,
    )

    # Main finding title (statement, not topic)
    wrapped_title = textwrap.fill(panel_data['title'], width=80)
    ax.text(
        0.05,
        0.88,
        wrapped_title,
        fontsize=11,
        fontweight='bold',
        color=COLORS['gold'],
        transform=ax.transAxes,
        wrap=True,
    )

    # Horizontal divider
    ax.plot(
        [0.05, 0.95],
        [0.86, 0.86],
        color=COLORS['slate_blue'],
        linewidth=2,
        transform=ax.transAxes,
    )

    # ========== LEFT: Framework Feed-In ==========
    draw_framework_feed_in(ax, panel_num, panel_data['frameworks'])

    # ========== CENTER: Template Count & Warrants ==========
    draw_template_count_and_warrants(ax, panel_data['templates'], panel_data['warrant_dist'])

    # ========== RIGHT: Key Parameters ==========
    draw_key_parameters(ax, panel_data['key_params'])

    # ========== BOTTOM: Exemplar Finding ==========
    draw_exemplar_finding(ax, panel_data['exemplar'])

    # Bottom border
    ax.plot(
        [0.05, 0.95],
        [0.06, 0.06],
        color=COLORS['slate_blue'],
        linewidth=1.5,
        transform=ax.transAxes,
    )

    # Source/ID footer
    ax.text(
        0.95,
        0.02,
        f'M-{panel_num} | ATLAS Master',
        fontsize=7,
        ha='right',
        va='bottom',
        transform=ax.transAxes,
        color=COLORS['cool_gray'],
        style='italic',
    )

    return fig


def main():
    """
    Generate all 12 domain panel figures (M-7 through M-18).
    """
    output_dir = Path('/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/figures')
    output_dir.mkdir(parents=True, exist_ok=True)

    panel_filenames = {
        7: 'm7_visual_panel.svg',
        8: 'm8_light_panel.svg',
        9: 'm9_thermal_panel.svg',
        10: 'm10_acoustic_panel.svg',
        11: 'm11_music_panel.svg',
        12: 'm12_stress_panel.svg',
        13: 'm13_social_panel.svg',
        14: 'm14_memory_panel.svg',
        15: 'm15_multi_panel.svg',
        16: 'm16_creative_panel.svg',
        17: 'm17_neuromod_panel.svg',
        18: 'm18_crosscut_panel.svg',
    }

    print('Generating 12 ATLAS Domain Panel Figures...\n')

    for panel_num in range(7, 19):
        print(f'  Generating M-{panel_num}: {PANELS[panel_num]["name"]}...', end=' ', flush=True)

        fig = create_domain_panel_figure(panel_num)

        output_path = output_dir / panel_filenames[panel_num]
        fig.savefig(output_path, format='svg', bbox_inches='tight', dpi=100)
        plt.close(fig)

        file_size = output_path.stat().st_size
        status = 'OK' if file_size > 30000 else 'SMALL'
        print(f'[{status}] {file_size:,} bytes')

    print(f'\nAll figures saved to: {output_dir}')
    print(f'Total files generated: 12')

    # Verify all files exist
    files_created = list(output_dir.glob('m*.svg'))
    print(f'Verified: {len(files_created)} SVG files present')

    return output_dir


if __name__ == '__main__':
    main()
