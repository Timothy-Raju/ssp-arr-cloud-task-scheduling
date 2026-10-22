"""
generate_ieee_paper_figures.py
Generates IEEE-style percentage improvement graphs for each metric:
  Fig. 1 – AWT percentage improvement
  Fig. 2 – ATAT percentage improvement
  Fig. 3 – Throughput percentage improvement
  Fig. 4 – TCT percentage improvement
  Fig. 5 – Energy percentage improvement
  Fig. 6 – Consolidated bar chart at 2000 cloudlets
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# IEEE typography
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Times']
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 9.5
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 7.5
plt.rcParams['figure.dpi'] = 300

FIGURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Common data
WORKLOAD_SIZES = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1500, 2000]
WORKLOAD_LABELS = ['100','200','300','400','500','600','700','800','900','1000','1500','2000']

COLORS = {
    'DyMM':    '#2563EB',  # Blue
    'DRALBA':  '#DC2626',  # Red
    'PSSLB':   '#7C3AED',  # Purple
    'PSSELB':  '#0891B2',  # Cyan
    'DeRALBA': '#059669',  # Green
}
MARKERS = {'DyMM': 'o', 'DRALBA': 's', 'PSSLB': 'D', 'PSSELB': 'v', 'DeRALBA': '^'}

# ─── PERCENTAGE IMPROVEMENT DATA ───

# AWT Improvement (%)
AWT_IMP = {
    'DyMM':    [51.9, 50.5, 50.3, 50.3, 50.3, 50.3, 50.3, 50.3, 50.2, 50.3, 50.3, 50.2],
    'DRALBA':  [50.1, 50.2, 50.1, 50.1, 50.1, 50.2, 50.2, 50.2, 50.1, 50.2, 50.2, 50.2],
    'PSSLB':   [50.2, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2],
    'PSSELB':  [50.6, 50.4, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2],
    'DeRALBA': [51.2, 50.3, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2, 50.2],
}

# ATAT Improvement (%)
ATAT_IMP = {
    'DyMM':    [5.6, 24.9, 32.8, 36.2, 37.8, 39.1, 41.3, 42.1, 42.6, 43.6, 45.7, 46.8],
    'DRALBA':  [18.2, 29.4, 34.4, 39.0, 41.0, 42.2, 43.7, 44.5, 44.9, 45.5, 47.1, 47.8],
    'PSSLB':   [31.3, 39.9, 43.2, 45.2, 46.0, 46.6, 47.4, 47.7, 47.9, 48.2, 48.8, 49.2],
    'PSSELB':  [14.5, 26.8, 33.7, 37.4, 40.0, 41.5, 42.9, 43.8, 44.4, 45.0, 46.7, 47.6],
    'DeRALBA': [6.9, 23.4, 31.5, 36.7, 39.1, 40.8, 42.5, 43.4, 43.6, 44.6, 46.4, 47.4],
}

# Throughput Improvement (%)
THROUGHPUT_IMP = {
    'DyMM':    [0.5]*12,
    'DRALBA':  [0.5]*12,
    'PSSLB':   [0.5]*12,
    'PSSELB':  [0.5]*12,
    'DeRALBA': [0.5]*12,
}

# TCT Improvement (%) – same as ATAT since TCT = N × ACT
TCT_IMP = {
    'DyMM':    [5.6, 24.9, 32.8, 36.2, 37.8, 39.1, 41.3, 42.1, 42.6, 43.6, 45.7, 46.8],
    'DRALBA':  [18.2, 29.4, 34.4, 39.0, 41.0, 42.2, 43.7, 44.5, 44.9, 45.5, 47.1, 47.8],
    'PSSLB':   [31.3, 39.9, 43.2, 45.2, 46.0, 46.6, 47.4, 47.7, 47.9, 48.2, 48.8, 49.2],
    'PSSELB':  [14.5, 26.8, 33.7, 37.4, 40.0, 41.5, 42.9, 43.8, 44.4, 45.0, 46.7, 47.6],
    'DeRALBA': [6.9, 23.4, 31.5, 36.7, 39.1, 40.8, 42.5, 43.4, 43.6, 44.6, 46.4, 47.4],
}

# Energy Improvement (%)
ENERGY_IMP = {
    'DyMM':    [0.5]*12,
    'DRALBA':  [0.5]*12,
    'PSSLB':   [0.5]*12,
    'PSSELB':  [0.5]*12,
    'DeRALBA': [0.5]*12,
}


def create_percentage_improvement_line_chart(data, metric_name, y_label, fig_num, filename,
                                              y_lim=None, annotation_text=None, annotation_pos=None):
    """Creates a multi-line percentage improvement chart for a given metric."""
    fig, ax = plt.subplots(figsize=(7.0, 3.2), dpi=300)

    x = np.arange(len(WORKLOAD_SIZES))

    for name, values in data.items():
        ax.plot(x, values, color=COLORS[name], marker=MARKERS[name],
                label=f'{name}', lw=1.6, ms=5, markeredgecolor='white', markeredgewidth=0.5)

    ax.set_xlabel('Number of Cloudlets (Workload Size)')
    ax.set_ylabel(y_label)
    ax.set_xticks(x)
    ax.set_xticklabels(WORKLOAD_LABELS, rotation=45, ha='right')

    if y_lim:
        ax.set_ylim(y_lim)

    ax.grid(True, linestyle=':', alpha=0.5, color='#CBD5E0')
    ax.legend(loc='best', frameon=True, fancybox=True, shadow=False,
              edgecolor='#A0AEC0', ncol=3)

    if annotation_text and annotation_pos:
        ax.text(annotation_pos[0], annotation_pos[1], annotation_text,
                transform=ax.transAxes, fontsize=8, fontweight='bold',
                color='#1A365D', ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.4", fc="#FEFCBF", ec="#B7791F", lw=0.9, alpha=0.9))

    # Add overall mean line if relatively constant
    means = {k: np.mean(v) for k, v in data.items()}
    overall_mean = np.mean(list(means.values()))

    plt.tight_layout(pad=0.8)
    out_path = os.path.join(FIGURES_DIR, filename)
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  [OK] Fig. {fig_num}: {out_path}")


def create_grouped_bar_chart(data, metric_name, y_label, fig_num, filename, y_lim=None):
    """Creates a grouped bar chart for percentage improvement."""
    fig, ax = plt.subplots(figsize=(7.0, 3.2), dpi=300)

    x = np.arange(len(WORKLOAD_SIZES))
    n_groups = len(data)
    bar_width = 0.15
    offsets = np.linspace(-(n_groups-1)*bar_width/2, (n_groups-1)*bar_width/2, n_groups)

    for i, (name, values) in enumerate(data.items()):
        bars = ax.bar(x + offsets[i], values, bar_width, label=name,
                      color=COLORS[name], edgecolor='white', linewidth=0.3, alpha=0.85)

    ax.set_xlabel('Number of Cloudlets (Workload Size)')
    ax.set_ylabel(y_label)
    ax.set_xticks(x)
    ax.set_xticklabels(WORKLOAD_LABELS, rotation=45, ha='right')

    if y_lim:
        ax.set_ylim(y_lim)

    ax.grid(True, axis='y', linestyle=':', alpha=0.5, color='#CBD5E0')
    ax.legend(loc='best', frameon=True, fancybox=True, shadow=False,
              edgecolor='#A0AEC0', ncol=5, fontsize=7)

    plt.tight_layout(pad=0.8)
    out_path = os.path.join(FIGURES_DIR, filename)
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  [OK] Fig. {fig_num}: {out_path}")


def create_consolidated_performance_chart():
    """Fig. 6: Consolidated makespan, throughput, energy at 2000 cloudlets."""
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.8), dpi=300)

    policies = ['Dy.MM', 'DRALBA', 'PSSLB', 'PSSELB', 'DeRALBA']
    x = np.arange(len(policies))
    w = 0.32

    # Panel A: Makespan
    ms_rr  = [1292.83, 2061.35, 4632.27, 1715.43, 1476.24]
    ms_ssp = [1286.49, 2051.25, 4609.67, 1707.11, 1469.03]
    axes[0].bar(x - w/2, ms_rr, w, label='RR', color='#E2E8F0', edgecolor='#4A5568')
    axes[0].bar(x + w/2, ms_ssp, w, label='SSP-ARR', color='#3182CE', edgecolor='#2B6CB0')
    axes[0].set_xticks(x); axes[0].set_xticklabels(policies, rotation=45, ha='right', fontsize=7)
    axes[0].set_ylabel('Makespan (s)')
    axes[0].set_title('(a) Makespan', fontsize=9)
    axes[0].legend(fontsize=6.5, frameon=True)
    axes[0].grid(True, axis='y', linestyle=':', alpha=0.5)

    # Panel B: Throughput
    thp_rr  = [1.5470, 0.9702, 0.4318, 1.1659, 1.3548]
    thp_ssp = [1.5546, 0.9750, 0.4339, 1.1716, 1.3614]
    axes[1].bar(x - w/2, thp_rr, w, label='RR', color='#E2E8F0', edgecolor='#4A5568')
    axes[1].bar(x + w/2, thp_ssp, w, label='SSP-ARR', color='#38A169', edgecolor='#22543D')
    axes[1].set_xticks(x); axes[1].set_xticklabels(policies, rotation=45, ha='right', fontsize=7)
    axes[1].set_ylabel('Throughput (tasks/s)')
    axes[1].set_title('(b) Throughput', fontsize=9)
    axes[1].legend(fontsize=6.5, frameon=True)
    axes[1].grid(True, axis='y', linestyle=':', alpha=0.5)

    # Panel C: Energy
    en_rr  = [2.3323, 3.2021, 6.8111, 2.8926, 2.5566]
    en_ssp = [2.3209, 3.1864, 6.7779, 2.8785, 2.5441]
    axes[2].bar(x - w/2, en_rr, w, label='RR', color='#CBD5E0', edgecolor='#718096')
    axes[2].bar(x + w/2, en_ssp, w, label='SSP-ARR', color='#D69E2E', edgecolor='#975A16')
    axes[2].set_xticks(x); axes[2].set_xticklabels(policies, rotation=45, ha='right', fontsize=7)
    axes[2].set_ylabel('Energy (kWh)')
    axes[2].set_title('(c) Energy', fontsize=9)
    axes[2].legend(fontsize=6.5, frameon=True)
    axes[2].grid(True, axis='y', linestyle=':', alpha=0.5)

    plt.tight_layout(pad=0.6)
    out_path = os.path.join(FIGURES_DIR, "fig6_consolidated_2000.png")
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  [OK] Fig. 6: {out_path}")


if __name__ == '__main__':
    print("Generating IEEE Conference Paper Figures...\n")

    # Fig. 1: AWT Percentage Improvement
    create_percentage_improvement_line_chart(
        AWT_IMP, "AWT",
        "AWT Improvement of SSP-ARR over RR (%)",
        fig_num=1,
        filename="fig1_awt_improvement.png",
        y_lim=(49.0, 52.5),
        annotation_text="Consistent ~50.2% AWT\nReduction Across All\nGlobal Schedulers",
        annotation_pos=(0.78, 0.35)
    )

    # Fig. 2: ATAT Percentage Improvement
    create_percentage_improvement_line_chart(
        ATAT_IMP, "ATAT",
        "ATAT Improvement of SSP-ARR over RR (%)",
        fig_num=2,
        filename="fig2_atat_improvement.png",
        y_lim=(0, 55),
        annotation_text="Load-Proportional Scaling\n+5.6% to +49.2%",
        annotation_pos=(0.25, 0.85)
    )

    # Fig. 3: Throughput Percentage Improvement (grouped bar)
    create_grouped_bar_chart(
        THROUGHPUT_IMP, "Throughput",
        "Throughput Improvement of SSP-ARR over RR (%)",
        fig_num=3,
        filename="fig3_throughput_improvement.png",
        y_lim=(0, 1.2)
    )

    # Fig. 4: TCT Percentage Improvement
    create_percentage_improvement_line_chart(
        TCT_IMP, "TCT",
        "TCT Improvement of SSP-ARR over RR (%)",
        fig_num=4,
        filename="fig4_tct_improvement.png",
        y_lim=(0, 55),
        annotation_text="Scaling from +5.6%\nto +49.2%",
        annotation_pos=(0.25, 0.85)
    )

    # Fig. 5: Energy Percentage Improvement (grouped bar)
    create_grouped_bar_chart(
        ENERGY_IMP, "Energy",
        "Energy Improvement of SSP-ARR over RR (%)",
        fig_num=5,
        filename="fig5_energy_improvement.png",
        y_lim=(0, 1.2)
    )

    # Fig. 6: Consolidated Performance at 2000 Cloudlets
    create_consolidated_performance_chart()

    print("\n[DONE] All 6 IEEE figures generated successfully in figures/ directory!")
