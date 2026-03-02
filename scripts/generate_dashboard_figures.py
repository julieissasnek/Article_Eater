"""
generate_dashboard_figures.py

Phase 5: Data Dashboard Visualizations (M-22, M-23, M-24)

Generates three comprehensive dashboard figures for ATLAS using synthetic data:
  - M-22: Evidence Landscape (belief distribution by tier and confidence)
  - M-23: Warrant Distribution (warrant types across 12 domain panels)
  - M-24: Schema Gaps Heatmap (gap density by domain and epistemic category)

Author: Article_Eater Documentation System
Created: 2026-03-02
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
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


def generate_m22_evidence_landscape():
    """
    M-22: Evidence Landscape - Framework Distribution Chart
    
    Shows distribution of 3,420 beliefs across T1 frameworks,
    with visualization by belief count and confidence.
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Belief counts by framework
    frameworks = [
        ('Predictive\nProcessing', 800),
        ('Allostasis', 500),
        ('Environmental\nPsychology', 450),
        ('Neuroaesthetics', 350),
        ('Proxemics', 300),
        ('Chronobiology', 250),
        ('Adaptive\nComfort', 200),
        ('Flow\nTheory', 180),
        ('Cognitive\nMap', 170),
        ('Multisensory\nIntegration', 120),
    ]
    
    names = [name for name, _ in frameworks]
    values = [count for _, count in frameworks]
    
    # Color by value
    colors = []
    for v in values:
        if v > 700:
            colors.append(PALETTE['sage_green'])
        elif v > 400:
            colors.append(PALETTE['warm_gold'])
        elif v > 200:
            colors.append(PALETTE['slate_blue'])
        else:
            colors.append(PALETTE['cool_gray'])
    
    # Create bar chart
    y_pos = np.arange(len(names))
    bars = ax.barh(y_pos, values, color=colors, edgecolor=PALETTE['deep_navy'],
                   linewidth=2, alpha=0.85)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        ax.text(val + 15, i, f'{val} beliefs', va='center', fontsize=10,
               weight='bold', color=PALETTE['deep_navy'])
        
        # Add percentage
        pct = (val / sum(values)) * 100
        ax.text(val / 2, i, f'{pct:.1f}%', va='center', ha='center',
               fontsize=9, weight='bold', color=PALETTE['cream'])
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=10)
    ax.set_xlabel('Number of Beliefs', fontsize=11, weight='bold', color=PALETTE['deep_navy'])
    ax.set_xlim(0, 900)
    
    # Title
    ax.set_title('3,420 Beliefs Are Not Distributed Equally: Predictive Processing Dominates',
                fontsize=13, weight='bold', color=PALETTE['deep_navy'], pad=20)
    
    # Legend showing confidence distribution
    legend_y = -1.5
    ax.text(50, legend_y - 0.5, 'Confidence within each framework:',
           fontsize=10, weight='bold', color=PALETTE['deep_navy'])
    
    legend_items = [
        ('High (>0.7)', PALETTE['sage_green']),
        ('Medium (0.5–0.7)', PALETTE['warm_gold']),
        ('Low (<0.5)', PALETTE['terracotta']),
    ]
    
    for idx, (label, color) in enumerate(legend_items):
        rect = Rectangle((50 + idx * 250, legend_y - 1.2), 30, 0.3,
                        facecolor=color, edgecolor=PALETTE['deep_navy'], linewidth=1.5)
        ax.add_patch(rect)
        ax.text(90 + idx * 250, legend_y - 1.05, label,
               fontsize=9, color=PALETTE['deep_navy'], va='center')
    
    # Styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(PALETTE['slate_blue'])
    ax.spines['bottom'].set_color(PALETTE['slate_blue'])
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    
    ax.set_facecolor(PALETTE['cream'])
    fig.patch.set_facecolor(PALETTE['cream'])
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / 'm22_evidence_landscape.svg'
    plt.savefig(output_path, format='svg', facecolor=PALETTE['cream'],
                edgecolor='none', bbox_inches='tight', dpi=150)
    plt.close()
    
    print(f"✓ M-22 saved to {output_path}")


def generate_m23_warrant_distribution():
    """
    M-23: Warrant Distribution Across 12 Domain Panels
    
    Stacked bar chart showing four warrant types across domains.
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 12 domain panels
    domains = [
        'Visual',
        'Acoustic',
        'Thermal',
        'Light',
        'Stress',
        'Social',
        'Memory',
        'Multimodal',
        'Creative',
        'NEUROMOD-I',
        'CROSSCUT-I',
        'Ambient',
    ]
    
    # Warrant types: (name, weight, color)
    warrant_types = [
        ('EMPIRICAL_ASSOC', 0.40, PALETTE['sage_green']),
        ('MECHANISM', 0.30, PALETTE['warm_gold']),
        ('THEORY_DERIVED', 0.20, PALETTE['terracotta']),
        ('ANALOGICAL', 0.10, PALETTE['cool_gray']),
    ]
    
    # Belief counts per domain (realistic)
    belief_counts = [280, 295, 270, 265, 290, 310, 275, 260, 245, 310, 320, 290]
    
    x = np.arange(len(domains))
    width = 0.6
    
    bottom = np.zeros(len(domains))
    
    for warrant_name, base_pct, color in warrant_types:
        # Vary percentages slightly per domain for realism
        percentages = np.array([base_pct] * len(domains))
        # Add small variations
        variation = np.random.RandomState(42).normal(0, 0.02, len(domains))
        percentages = np.maximum(0.05, percentages + variation)
        percentages = percentages / percentages.sum() * 100  # Normalize
        
        # Calculate heights for stacked bars
        heights = (np.array(belief_counts) * percentages) / 100
        
        ax.bar(x, heights, width, label=warrant_name, bottom=bottom,
              color=color, edgecolor=PALETTE['deep_navy'], linewidth=1.5,
              alpha=0.85)
        
        # Add percentage labels on segments (if segment is large enough)
        for i, (h, pct) in enumerate(zip(heights, percentages)):
            if h > 20:  # Only label if visible
                ax.text(i, bottom[i] + h/2, f'{pct:.0f}%',
                       ha='center', va='center',
                       fontsize=7, weight='bold', color=PALETTE['cream'])
        
        bottom += heights
    
    # System-wide average reference line (weighted)
    overall_avg = sum(pct for _, pct, _ in warrant_types) / len(warrant_types) * np.mean(belief_counts)
    ax.axhline(y=overall_avg, color=PALETTE['deep_navy'], linewidth=2.5,
              linestyle='--', alpha=0.6, label='System Avg')
    
    # Styling
    ax.set_xlabel('Domain Panel', fontsize=11, weight='bold', color=PALETTE['deep_navy'])
    ax.set_ylabel('Number of Beliefs', fontsize=11, weight='bold', color=PALETTE['deep_navy'])
    ax.set_title('40% of ATLAS Beliefs Rest on Direct Empirical Association—But 20% Are Theory-Derived Predictions',
                fontsize=13, weight='bold', color=PALETTE['deep_navy'], pad=20)
    
    ax.set_xticks(x)
    ax.set_xticklabels(domains, rotation=45, ha='right', fontsize=10)
    ax.set_ylim(0, max(bottom) * 1.1)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(PALETTE['slate_blue'])
    ax.spines['bottom'].set_color(PALETTE['slate_blue'])
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    
    # Legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='upper left', fontsize=9,
             edgecolor=PALETTE['deep_navy'], fancybox=True)
    
    ax.set_facecolor(PALETTE['cream'])
    fig.patch.set_facecolor(PALETTE['cream'])
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / 'm23_warrant_distribution.svg'
    plt.savefig(output_path, format='svg', facecolor=PALETTE['cream'],
                edgecolor='none', bbox_inches='tight', dpi=150)
    plt.close()
    
    print(f"✓ M-23 saved to {output_path}")


def generate_m24_schema_gaps():
    """
    M-24: Schema Gaps Heatmap
    
    Shows gap density by domain panel (rows) × epistemic category (columns).
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Gap categories
    gap_categories = [
        'Mediation\nGaps',
        'Mechanism\nGaps',
        'Boundary\nGaps',
        'Direction\nGaps',
        'Validation\nGaps',
    ]
    
    # Domain panels
    domains = [
        'Visual',
        'Acoustic',
        'Thermal',
        'Light',
        'Stress',
        'Social',
        'Memory',
        'Multimodal',
        'Creative',
        'NEUROMOD-I',
        'CROSSCUT-I',
        'Ambient',
    ]
    
    # Generate realistic gap data (higher for NEUROMOD-I and CROSSCUT-I as noted)
    np.random.seed(42)
    gap_data = np.random.randint(2, 12, size=(len(domains), len(gap_categories)))
    
    # Boost NEUROMOD-I and CROSSCUT-I (indices 9 and 10)
    gap_data[9] = np.array([18, 15, 20, 14, 16])  # NEUROMOD-I
    gap_data[10] = np.array([16, 19, 18, 17, 15])  # CROSSCUT-I
    
    # Add summary row
    gap_totals = gap_data.sum(axis=0)
    
    # Create heatmap
    im = ax.imshow(gap_data, cmap='Reds', aspect='auto', alpha=0.85)
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(gap_categories)))
    ax.set_yticks(np.arange(len(domains)))
    ax.set_xticklabels(gap_categories, fontsize=10, weight='bold')
    ax.set_yticklabels(domains, fontsize=10)
    
    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=0, ha='center')
    
    # Annotate cells with gap counts
    for i in range(len(domains)):
        for j in range(len(gap_categories)):
            value = gap_data[i, j]
            text_color = PALETTE['cream'] if value > 10 else PALETTE['deep_navy']
            ax.text(j, i, str(value), ha='center', va='center',
                   color=text_color, fontsize=10, weight='bold')
    
    # Add total row below
    total_y = len(domains)
    for j, total in enumerate(gap_totals):
        ax.text(j, total_y + 0.3, f'Σ:{total}', ha='center', va='top',
               fontsize=9, weight='bold', color=PALETTE['deep_navy'],
               bbox=dict(boxstyle='round,pad=0.3', facecolor=PALETTE['warm_gold'],
                        edgecolor=PALETTE['deep_navy'], linewidth=1))
    
    # Highlight hottest cells with annotations
    hotspot_threshold = 15
    for i in range(len(domains)):
        for j in range(len(gap_categories)):
            if gap_data[i, j] >= hotspot_threshold:
                # Add a star or highlight
                ax.text(j, i - 0.35, '★', ha='center', va='top',
                       fontsize=12, color=PALETTE['terracotta'])
    
    # Add specific gap descriptions for hotspots
    hotspot_text = (
        'NEUROMOD-I: High gaps in mechanism (mediation not fully mapped)\n'
        'CROSSCUT-I: High gaps in direction (bidirectional effects unclear)'
    )
    ax.text(2.5, len(domains) + 1.5, hotspot_text,
           fontsize=9, style='italic', color=PALETTE['deep_navy'],
           bbox=dict(boxstyle='round,pad=0.8',
                    facecolor=PALETTE['warm_gold'],
                    alpha=0.6,
                    edgecolor=PALETTE['deep_navy'],
                    linewidth=1.5))
    
    # Title and labels
    ax.set_title('NEUROMOD-I and CROSSCUT-I Have the Most Gaps — By Design, Not by Failure',
                fontsize=13, weight='bold', color=PALETTE['deep_navy'], pad=20)
    ax.set_xlabel('Epistemic Category', fontsize=11, weight='bold', color=PALETTE['deep_navy'])
    ax.set_ylabel('Domain Panel', fontsize=11, weight='bold', color=PALETTE['deep_navy'])
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, label='Gap Count', pad=0.02)
    cbar.set_label('Gap Density', fontsize=10, weight='bold', color=PALETTE['deep_navy'])
    
    # Styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(PALETTE['slate_blue'])
    ax.spines['bottom'].set_color(PALETTE['slate_blue'])
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    
    fig.patch.set_facecolor(PALETTE['cream'])
    ax.set_facecolor(PALETTE['cream'])
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / 'm24_schema_gaps.svg'
    plt.savefig(output_path, format='svg', facecolor=PALETTE['cream'],
                edgecolor='none', bbox_inches='tight', dpi=150)
    plt.close()
    
    print(f"✓ M-24 saved to {output_path}")


if __name__ == '__main__':
    print("Generating Phase 5: Data Dashboard Visualizations...")
    print()
    
    generate_m22_evidence_landscape()
    generate_m23_warrant_distribution()
    generate_m24_schema_gaps()
    
    print()
    print("Phase 5 complete: All 3 dashboard figures generated.")
