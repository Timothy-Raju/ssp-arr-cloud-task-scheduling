"""
generate_paper_assets.py
Generates high-resolution IEEE publication figures for the SSP-ARR research paper.
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Set IEEE typography styles
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Times']
plt.rcParams['font.size'] = 8
plt.rcParams['axes.labelsize'] = 8.5
plt.rcParams['axes.titlesize'] = 9
plt.rcParams['xtick.labelsize'] = 7.5
plt.rcParams['ytick.labelsize'] = 7.5
plt.rcParams['legend.fontsize'] = 7.5
plt.rcParams['figure.titlesize'] = 9.5
plt.rcParams['figure.dpi'] = 300

FIGURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# ── 1. FIGURE 1: ARCHITECTURAL WORKFLOW ──
def create_fig1_architecture():
    out_path = os.path.join(FIGURES_DIR, "fig1_architecture.png")
    
    fig, ax = plt.subplots(figsize=(3.5, 4.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Box Styles
    box_blue = dict(boxstyle="round,pad=0.35", fc="#EBF3FB", ec="#2B6CB0", lw=1.1)
    box_tier1 = dict(boxstyle="round,pad=0.35", fc="#EDF2F7", ec="#4A5568", lw=1.1)
    box_sub = dict(boxstyle="round,pad=0.3", fc="#F7FAFC", ec="#718096", lw=0.8)
    box_green = dict(boxstyle="round,pad=0.3", fc="#E6FFFA", ec="#234E52", lw=1.0)
    box_orange = dict(boxstyle="round,pad=0.3", fc="#FFFAF0", ec="#9C4221", lw=1.0)
    box_purple = dict(boxstyle="round,pad=0.3", fc="#FAF5FF", ec="#553C9A", lw=1.0)

    arrow_props = dict(facecolor='#4A5568', edgecolor='#4A5568', width=0.7, headwidth=3.5, headlength=4.5)

    # 1. Top Input
    ax.text(50, 96, "Real-World Workload Trace Submissions\nGoogle Cloud Jobs (GoCJ: 100–2000 Cloudlets)",
            ha="center", va="center", bbox=box_blue, fontsize=6.8, fontweight='bold', color="#1A365D")
    
    ax.annotate("", xy=(50, 89.5), xytext=(50, 92.5), arrowprops=arrow_props)

    # 2. Tier 1 Global Scheduler
    ax.text(50, 86, "TIER 1: GLOBAL DATACENTER DISPATCHER\nDy. Max-Min | DRALBA | PSSLB | PSSELB | DeRALBA",
            ha="center", va="center", bbox=box_tier1, fontsize=6.5, fontweight='bold', color="#2D3748")

    ax.annotate("", xy=(50, 79.5), xytext=(50, 82.5), arrowprops=arrow_props)

    # Big Tier 2 Container Box
    rect = plt.Rectangle((3, 3), 94, 75, fill=True, fc="#FFFFFF", ec="#2B6CB0", lw=1.2, ls="--", zorder=1)
    ax.add_patch(rect)
    ax.text(50, 75.5, "TIER 2: PROPOSED LOCAL VM SCHEDULER (SSP-ARR)",
            ha="center", va="center", fontsize=7.0, fontweight='bold', color="#2B6CB0", zorder=2)

    # Sub-step 1: Variance Sensing
    ax.text(50, 69, "1. Volatility Sensing via Sliding Window (W = 5)\nCompute: μ_j, σ_j  →  CV_j = σ_j / μ_j",
            ha="center", va="center", bbox=box_sub, fontsize=6.3, zorder=2)

    # Branching arrows
    ax.annotate("", xy=(26, 57.5), xytext=(38, 65.5), arrowprops=arrow_props, zorder=2)
    ax.annotate("", xy=(74, 57.5), xytext=(62, 65.5), arrowprops=arrow_props, zorder=2)

    ax.text(23, 62.5, "CV_j ≤ 0.50\n(Stable)", ha="center", va="center", fontsize=5.8, fontweight='bold', color="#234E52")
    ax.text(77, 62.5, "CV_j > 0.50\n(Volatile)", ha="center", va="center", fontsize=5.8, fontweight='bold', color="#9C4221")

    # Safe Reactive Mode Box
    ax.text(26, 52, "Safe Reactive Mode\nQ_reactive = median(RB)\nBounded queue median",
            ha="center", va="center", bbox=box_green, fontsize=6.0, zorder=2)

    # Predictive EWMA Mode Box
    ax.text(74, 52, "Predictive EWMA Mode\nB_pred = α·B_t + (1-α)·EWMA\nα in [0.20, 0.80] by NPE",
            ha="center", va="center", bbox=box_orange, fontsize=6.0, zorder=2)

    # Arrow from Predictive to Confidence Gating
    ax.annotate("", xy=(74, 43.5), xytext=(74, 47), arrowprops=arrow_props, zorder=2)

    # Confidence Gating Box
    ax.text(74, 39.5, "Confidence Gating\nIs NPE_t ≤ 0.20?",
            ha="center", va="center", bbox=box_purple, fontsize=6.0, fontweight='bold', zorder=2)

    # Arrow from Confidence Gating (Pass to Clamping)
    ax.annotate("", xy=(56, 26.5), xytext=(70, 36), arrowprops=arrow_props, zorder=2)
    ax.text(72, 30.5, "Pass (NPE ≤ 0.20)", ha="center", va="center", fontsize=5.5, color="#2F855A", fontweight='bold')

    # Arrow fallback from Confidence Gating to Reactive Mode
    ax.annotate("", xy=(36, 49), xytext=(62, 40),
                arrowprops=dict(facecolor='#E53E3E', edgecolor='#E53E3E', width=0.7, headwidth=3.5, headlength=4), zorder=2)
    ax.text(50, 45, "NPE > 20% (Fallback)", ha="center", va="center", fontsize=5.4, color="#C53030", fontweight='bold')

    # Arrow from Reactive to Clamping
    ax.annotate("", xy=(44, 26.5), xytext=(26, 47), arrowprops=arrow_props, zorder=2)

    # Boundary Clamping Box
    ax.text(50, 23, "2. Bounded Quantum Clamping\nQ = max(Q_min, min(Q_max, min(Q_target, RB(t))))",
            ha="center", va="center", bbox=box_sub, fontsize=6.2, zorder=2)

    ax.annotate("", xy=(50, 16.5), xytext=(50, 19.5), arrowprops=arrow_props, zorder=2)

    # Final Execution & Feedback Box
    ax.text(50, 10, "3. SRPT Queue Execution & Preemption Penalty (δ_cs = 5 ms)\nExecute slice → Record Stats & EWMA Update → Re-insert if remaining",
            ha="center", va="center", bbox=box_blue, fontsize=6.0, fontweight='bold', zorder=2)

    plt.tight_layout(pad=0.2)
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Created {out_path}")


# ── 2. FIGURE 2: AWT COMPARISON GRAPH ──
def create_fig2_awt():
    out_path = os.path.join(FIGURES_DIR, "fig2_awt_comparison.png")
    tasks = np.array([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1500, 2000])

    # AWT in seconds (divide ms by 1000 for standard readability)
    dy_rr  = np.array([5765.8, 49874.6, 102988.2, 133231.8, 156679.2, 191008.6, 228322.1, 254545.1, 299284.6, 336762.6, 521407.7, 702960.8]) / 1000.0
    dy_ssp = np.array([2772.2, 24668.5, 51186.9, 66172.5, 77917.0, 94976.2, 113516.4, 126589.9, 148940.1, 167432.3, 259379.7, 349808.1]) / 1000.0

    dr_rr  = np.array([22693.7, 61263.2, 100659.5, 151684.9, 197079.1, 246101.1, 290042.1, 334175.5, 394850.2, 438695.9, 688228.1, 917731.0]) / 1000.0
    dr_ssp = np.array([11328.0, 30534.6, 50255.3, 75666.0, 98246.3, 122625.2, 144457.9, 166471.1, 196937.3, 218642.4, 342754.1, 457304.4]) / 1000.0

    ps_rr  = np.array([116334.5, 275424.3, 448395.9, 665658.3, 808551.5, 962942.6, 1224204.4, 1362292.0, 1544405.6, 1794498.4, 2638693.8, 3483784.5]) / 1000.0
    ps_ssp = np.array([57897.5, 137041.9, 223455.5, 331459.1, 402747.9, 479514.9, 609752.6, 678675.1, 769353.2, 893700.1, 1314404.0, 1735493.6]) / 1000.0

    der_rr = np.array([8438.5, 46702.0, 90363.5, 135808.3, 179113.8, 230371.1, 272900.6, 313603.2, 349380.6, 402340.2, 631669.3, 853777.7]) / 1000.0
    der_ssp = np.array([4121.1, 23202.8, 44994.7, 67657.2, 89269.3, 114756.8, 135887.0, 156246.8, 174111.3, 200398.4, 314529.6, 425255.1]) / 1000.0

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.7), dpi=300)

    # Panel A: Absolute AWT (seconds)
    ax1.plot(tasks, dy_rr, 'b--', label='Dy.MM (RR)', lw=1.2, marker='o', ms=3)
    ax1.plot(tasks, dy_ssp, 'b-', label='Dy.MM (SSP-ARR)', lw=1.6, marker='o', ms=3)
    ax1.plot(tasks, dr_rr, 'r--', label='DRALBA (RR)', lw=1.2, marker='s', ms=3)
    ax1.plot(tasks, dr_ssp, 'r-', label='DRALBA (SSP-ARR)', lw=1.6, marker='s', ms=3)
    ax1.plot(tasks, der_rr, 'g--', label='DeRALBA (RR)', lw=1.2, marker='^', ms=3)
    ax1.plot(tasks, der_ssp, 'g-', label='DeRALBA (SSP-ARR)', lw=1.6, marker='^', ms=3)

    ax1.set_xlabel('Workload Size (Cloudlets)')
    ax1.set_ylabel('Average Waiting Time (seconds)')
    ax1.set_title('(a) AWT vs. Task Load (Dy.MM, DRALBA, DeRALBA)')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper left', ncol=2, frameon=True, fontsize=6.5)

    # Panel B: PSSLB & PSSELB comparison + Mean Improvement
    pss_rr  = np.array([22927.5, 65179.7, 118992.2, 160237.3, 218120.9, 271872.6, 304865.7, 352715.0, 429463.5, 465520.6, 736677.5, 976446.4]) / 1000.0
    pss_ssp = np.array([11324.5, 32309.2, 59259.2, 79724.1, 108575.9, 135386.9, 151751.1, 175517.9, 213955.4, 231755.8, 366742.1, 486231.8]) / 1000.0

    ax2.plot(tasks, ps_rr, 'm--', label='PSSLB (RR)', lw=1.2, marker='d', ms=3)
    ax2.plot(tasks, ps_ssp, 'm-', label='PSSLB (SSP-ARR)', lw=1.6, marker='d', ms=3)
    ax2.plot(tasks, pss_rr, 'c--', label='PSSELB (RR)', lw=1.2, marker='v', ms=3)
    ax2.plot(tasks, pss_ssp, 'c-', label='PSSELB (SSP-ARR)', lw=1.6, marker='v', ms=3)

    # Inset / Annotation: Consistent ~50.2% improvement
    ax2.set_xlabel('Workload Size (Cloudlets)')
    ax2.set_ylabel('Average Waiting Time (seconds)')
    ax2.set_title('(b) AWT vs. Task Load (PSSLB & PSSELB)')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper left', frameon=True, fontsize=6.5)

    ax2.text(0.55, 0.40, "Consistent ~50.2% Reduction\nAcross All 5 Policies\nvia Predictive SRPT Consolidation",
             transform=ax2.transAxes, fontsize=6.8, fontweight='bold', color="#1A365D",
             bbox=dict(boxstyle="round,pad=0.3", fc="#FEFCBF", ec="#B7791F", lw=0.9))

    plt.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Created {out_path}")


# ── 3. FIGURE 3: ATAT COMPARISON GRAPH ──
def create_fig3_atat():
    out_path = os.path.join(FIGURES_DIR, "fig3_atat_comparison.png")
    tasks = np.array([100, 200, 400, 600, 800, 1000, 1500, 2000])

    # Percentage Improvements
    dy_imp  = [5.6, 24.9, 36.2, 39.1, 42.1, 43.6, 45.7, 46.8]
    dr_imp  = [18.2, 29.4, 39.0, 42.2, 44.5, 45.5, 47.1, 47.8]
    ps_imp  = [31.3, 39.9, 45.2, 46.6, 47.7, 48.2, 48.8, 49.2]
    pss_imp = [14.5, 26.8, 37.4, 41.5, 43.8, 45.0, 46.7, 47.6]
    der_imp = [6.9, 23.4, 36.7, 40.8, 43.4, 44.6, 46.4, 47.4]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.7), dpi=300)

    # Panel A: Absolute ATAT for Dy.MM and DRALBA
    dy_rr  = [53.78, 101.10, 184.99, 245.88, 303.93, 388.61, 573.84, 754.28]
    dy_ssp = [50.79, 75.90, 117.93, 149.85, 175.98, 219.28, 311.81, 401.13]
    dr_rr  = [62.53, 104.52, 194.97, 292.44, 376.75, 483.13, 733.87, 962.54]
    dr_ssp = [51.17, 73.79, 118.95, 168.96, 209.05, 263.07, 388.40, 502.11]

    ax1.plot(tasks, dy_rr, 'b--', label='Dy.MM (RR)', lw=1.2, marker='o', ms=3)
    ax1.plot(tasks, dy_ssp, 'b-', label='Dy.MM (SSP-ARR)', lw=1.6, marker='o', ms=3)
    ax1.plot(tasks, dr_rr, 'r--', label='DRALBA (RR)', lw=1.2, marker='s', ms=3)
    ax1.plot(tasks, dr_ssp, 'r-', label='DRALBA (SSP-ARR)', lw=1.6, marker='s', ms=3)
    ax1.set_xlabel('Workload Size (Cloudlets)')
    ax1.set_ylabel('Average Turnaround Time (seconds)')
    ax1.set_title('(a) Absolute ATAT (Dy.MM & DRALBA)')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper left', frameon=True, fontsize=6.8)

    # Panel B: Load-Proportional Scaling Trend
    ax2.plot(tasks, ps_imp, 'm-o', label='PSSLB (+31.3% → +49.2%)', lw=1.5, ms=3)
    ax2.plot(tasks, dr_imp, 'r-s', label='DRALBA (+18.2% → +47.8%)', lw=1.5, ms=3)
    ax2.plot(tasks, pss_imp, 'c-v', label='PSSELB (+14.5% → +47.6%)', lw=1.5, ms=3)
    ax2.plot(tasks, der_imp, 'g-^', label='DeRALBA (+6.9% → +47.4%)', lw=1.5, ms=3)
    ax2.plot(tasks, dy_imp, 'b-d', label='Dy.MM (+5.6% → +46.8%)', lw=1.5, ms=3)

    ax2.set_xlabel('Workload Size (Cloudlets)')
    ax2.set_ylabel('ATAT Improvement (%)')
    ax2.set_title('(b) Load-Proportional ATAT Improvement Scaling')
    ax2.set_ylim(0, 55)
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='lower right', frameon=True, fontsize=6.5)

    plt.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Created {out_path}")


# ── 4. FIGURE 4: TCT & MAKESPAN/ENERGY ──
def create_fig4_tct_and_cluster():
    out_path = os.path.join(FIGURES_DIR, "fig4_tct_and_cluster.png")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.7), dpi=300)

    # Panel A: TCT at 2000 Cloudlets (Million Seconds)
    policies = ['Dy.MM', 'DRALBA', 'PSSLB', 'PSSELB', 'DeRALBA']
    tct_rr_m = np.array([1.508, 1.925, 7.114, 2.060, 1.809])
    tct_ssp_m = np.array([0.802, 1.004, 3.617, 1.080, 0.952])
    x = np.arange(len(policies))
    w = 0.35

    rects1 = ax1.bar(x - w/2, tct_rr_m, w, label='Classical RR', color='#E2E8F0', edgecolor='#4A5568')
    rects2 = ax1.bar(x + w/2, tct_ssp_m, w, label='SSP-ARR', color='#3182CE', edgecolor='#2B6CB0')

    ax1.set_xticks(x)
    ax1.set_xticklabels(policies)
    ax1.set_ylabel('Total Completion Time (Million s)')
    ax1.set_title('(a) TCT Reduction at 2000 GoCJ Cloudlets')
    ax1.legend(frameon=True, fontsize=6.8)
    ax1.grid(True, axis='y', linestyle=':', alpha=0.6)

    # Add delta label on top of PSSLB
    ax1.annotate('Saved 3.49M s', xy=(2 + w/2, 3.65), xytext=(2, 5.5),
                 arrowprops=dict(facecolor='#C53030', edgecolor='#C53030', width=0.8, headwidth=4, headlength=4),
                 fontsize=6.5, fontweight='bold', color='#C53030', ha='center')

    # Panel B: Energy & Makespan Savings at 2000 Tasks
    energy_rr = np.array([2.332, 3.202, 6.811, 2.893, 2.557])
    energy_ssp = np.array([2.321, 3.186, 6.778, 2.879, 2.544])

    rects3 = ax2.bar(x - w/2, energy_rr, w, label='RR Energy (kWh)', color='#CBD5E0', edgecolor='#718096')
    rects4 = ax2.bar(x + w/2, energy_ssp, w, label='SSP-ARR Energy (kWh)', color='#38A169', edgecolor='#22543D')

    ax2.set_xticks(x)
    ax2.set_xticklabels(policies)
    ax2.set_ylabel('SPECpower Energy Consumption (kWh)')
    ax2.set_title('(b) Datacenter Host Energy at 2000 Cloudlets')
    ax2.legend(frameon=True, fontsize=6.8)
    ax2.grid(True, axis='y', linestyle=':', alpha=0.6)

    plt.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Created {out_path}")


if __name__ == '__main__':
    create_fig1_architecture()
    create_fig2_awt()
    create_fig3_atat()
    create_fig4_tct_and_cluster()
    print("All figures successfully created in figures/ directory!")
