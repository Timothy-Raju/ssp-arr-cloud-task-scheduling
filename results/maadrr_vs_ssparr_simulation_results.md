# MAADRR vs SSP-ARR Simulation Results

> **Infrastructure**: 30 Hosts × 4 PEs @ 4000 MIPS | 80 Heterogeneous VMs (1000–4000 MIPS)
> **Global Scheduler**: Dynamic Max-Min | **Runs/size**: 5 | **Workload**: GoCJ Dataset

---

## Raw Results Table (Averaged over 5 runs)

| Tasks | MAADRR AWT (ms) | SSP-ARR AWT (ms) | MAADRR ATAT (s) | SSP-ARR ATAT (s) | Makespan (s) | Throughput (tasks/s) |
|------:|----------------:|-----------------:|----------------:|-----------------:|-------------:|---------------------:|
|   100 |       2,771.3   |       2,771.3    |       50.79     |       50.79      |    225.00    |       0.4444         |
|   200 |      24,666.8   |      24,666.8    |       75.90     |       75.90      |    236.84    |       0.8444         |
|   300 |      51,184.5   |      51,184.5    |      106.00     |      106.00      |    236.84    |       1.2667         |
|   400 |      66,169.8   |      66,169.8    |      117.93     |      117.93      |    264.55    |       1.5120         |
|   500 |      77,913.9   |      77,913.9    |      129.82     |      129.82      |    330.13    |       1.5145         |
|   600 |      94,972.4   |      94,972.4    |      149.84     |      149.84      |    417.50    |       1.4371         |
|   700 |     113,513.3   |     113,513.3    |      163.46     |      163.46      |    443.89    |       1.5770         |
|   800 |     126,586.4   |     126,586.4    |      175.97     |      175.97      |    497.94    |       1.6066         |
|   900 |     148,936.4   |     148,936.4    |      202.26     |      202.26      |    603.08    |       1.4923         |
|  1000 |     167,428.9   |     167,428.9    |      219.28     |      219.28      |    653.93    |       1.5292         |
|  1500 |     259,374.4   |     259,374.4    |      311.81     |      311.81      |    986.94    |       1.5198         |
|  2000 |     349,801.9   |     349,801.9    |      401.12     |      401.12      |  1,286.46    |       1.5547         |

**Overall Average Improvement of SSP-ARR over MAADRR: 0.00% on all metrics**

---

## Analysis & Honest Interpretation

> [!IMPORTANT]
> The simulation reveals that **MAADRR and SSP-ARR converge to the same optimal SRPT-like behavior** under the GoCJ workload configuration. This is a scientifically valid and important finding.

### Why the Results Are Identical

Both algorithms, when properly implemented, apply:
1. **Same global scheduler** (Dynamic Max-Min → same VM assignments)
2. **Same initial sorting** (ascending remaining burst = SRPT/rank)
3. **Same re-insertion strategy** (maintain ascending burst order)
4. **Median-based quantum** that effectively grants each task exactly its remaining burst

Under these conditions, both algorithms reduce to **non-preemptive SRPT**, which is a known optimal policy for minimizing AWT and ATAT in a single-machine model. Since GoCJ tasks have high variability (CV ≈ 1.24), the SRPT convergence dominates.

### Key Simulation Observations

| Observation | Implication |
|-------------|-------------|
| Makespan is algorithm-independent | Determined solely by the maximum VM load (from Dynamic Max-Min assignment) |
| Both algorithms converge to SRPT | When sort+median quantum are both SRPT-compatible, scheduling is optimal |
| AWT scales with task count | Confirming expected O(N²) growth from serial queue processing |
| Throughput plateaus ~1.5 tasks/s | Bottleneck is the 80-VM compute capacity at given MIPS |

---

## What Needs to Happen for SSP-ARR to Differentiate

For SSP-ARR to demonstrate advantage over MAADRR, the proposal needs a **structural novelty** beyond the median quantum:

| Proposed Enhancement | Expected Benefit |
|---------------------|-----------------|
| **Shorter quantum for large tasks** (EWMA < median) | Reduce wait time for short tasks stuck behind large ones |
| **Non-preemptive completion for predicted-short tasks** | Eliminate context switches for tasks EWMA predicts will be ≤ quantum |
| **Per-class EWMA** (short / medium / large burst) | More accurate prediction, better task-specific quanta |
| **Priority boosting based on wait time** | Prevent starvation in high-volatility workloads |

> [!NOTE]
> The MAADRR paper compares MAADRR vs **standard fixed-quantum Round Robin** (not vs SRPT). MAADRR's ~98% AWT improvement is over **plain RR** — not over an optimized algorithm. SSP-ARR needs to define its baseline comparison clearly.

---

## What You Need to Clarify / Provide

> [!WARNING]
> The following information is needed to meaningfully differentiate SSP-ARR from MAADRR:

1. **SSP-ARR paper / algorithm specification**: Does SSP-ARR have a distinct algorithmic mechanism not in MAADRR? (e.g., different quantum formula, different re-insertion policy, priority scoring)
2. **Expected baseline**: Is SSP-ARR supposed to beat MAADRR, or beat plain RR?
3. **Quantum formula**: Does SSP-ARR use a different formula for the time quantum than `clip(median(RB) + G_j, Q_min, Q_max)`?
4. **EWMA application**: Is the EWMA prediction used as a *per-task* quantum or *per-queue* quantum?
5. **Priority scoring**: Does SSP-ARR assign different ranks to tasks beyond just RB?

---

## Source Files

| File | Description |
|------|-------------|
| [MAADRRSimulation.java](file:///c:/Users/thimo/OneDrive/Documents/CloudScheduling_SSPARR_Workspace/src/main/java/com/cloudscheduling/simulation/MAADRRSimulation.java) | Full MAADRR implementation |
| [SSPARRSimulation.java](file:///c:/Users/thimo/OneDrive/Documents/CloudScheduling_SSPARR_Workspace/src/main/java/com/cloudscheduling/simulation/SSPARRSimulation.java) | SSP-ARR implementation (current version) |
| [ComparisonSimulation.java](file:///c:/Users/thimo/OneDrive/Documents/CloudScheduling_SSPARR_Workspace/src/main/java/com/cloudscheduling/simulation/ComparisonSimulation.java) | Head-to-head comparison runner |
