# Experimental Evaluation: Classical Round Robin (RR) vs. SSP-ARR

> **Simulation Environment**: CloudSim Plus 8.5.7 | Java 21 | Real GoCJ Workload Traces (100–2000 Cloudlets)  
> **Infrastructure Setup**: 30 Hosts (120 PEs @ 4000 MIPS) | 80 Heterogeneous VMs (1000–4000 MIPS)  
> **Global Scheduling**: Dynamic Max-Min Task Assignment (identical for both algorithms)  
> **Independent Runs**: 5 runs per workload size (results averaged)

---

## 1. Overview & Setup Isolation

To evaluate **SSP-ARR** against the standard **Round Robin (RR)** baseline without touching any previously developed code, two independent simulation components were added:

1. **[RRSimulation.java](file:///c:/Users/thimo/OneDrive/Documents/CloudScheduling_SSPARR_Workspace/src/main/java/com/cloudscheduling/simulation/RRSimulation.java)**: Classical Round Robin implementation using a fixed time quantum ($q = 1.0\text{ s}$) and standard circular FIFO queueing per VM.
2. **[RRvsSSPARRComparison.java](file:///c:/Users/thimo/OneDrive/Documents/CloudScheduling_SSPARR_Workspace/src/main/java/com/cloudscheduling/simulation/RRvsSSPARRComparison.java)**: Comparative test harness evaluating both schedulers under identical infrastructure and task arrivals.
3. **Previous files preserved**: [MAADRRSimulation.java](file:///c:/Users/thimo/OneDrive/Documents/CloudScheduling_SSPARR_Workspace/src/main/java/com/cloudscheduling/simulation/MAADRRSimulation.java), [SSPARRSimulation.java](file:///c:/Users/thimo/OneDrive/Documents/CloudScheduling_SSPARR_Workspace/src/main/java/com/cloudscheduling/simulation/SSPARRSimulation.java), and [ComparisonSimulation.java](file:///c:/Users/thimo/OneDrive/Documents/CloudScheduling_SSPARR_Workspace/src/main/java/com/cloudscheduling/simulation/ComparisonSimulation.java) remain completely intact.

---

## 2. Head-to-Head Experimental Results

Below are the empirical metrics obtained across all 12 GoCJ workload sizes (averaged over 5 runs per size):

| Tasks | RR AWT (ms) | SSP-ARR AWT (ms) | AWT Improvement (%) | RR ATAT (s) | SSP-ARR ATAT (s) | ATAT Improvement (%) | Makespan (s) | Throughput (tasks/s) |
|------:|------------:|-----------------:|--------------------:|------------:|-----------------:|---------------------:|-------------:|---------------------:|
|   100 |     5,501.29 |         2,771.29 |          **+49.62%** |       53.52 |            50.79 |           **+5.10%** |       225.00 |               0.4444 |
|   200 |    49,376.78 |        24,666.78 |          **+50.04%** |      100.61 |            75.90 |          **+24.56%** |       236.84 |               0.8444 |
|   300 |   102,211.19 |        51,184.53 |          **+49.92%** |      157.02 |           105.99 |          **+32.50%** |       236.84 |               1.2667 |
|   400 |   132,319.80 |        66,169.80 |          **+49.99%** |      184.08 |           117.93 |          **+35.94%** |       264.55 |               1.5120 |
|   500 |   155,651.95 |        77,913.95 |          **+49.94%** |      207.55 |           129.82 |          **+37.45%** |       330.13 |               1.5145 |
|   600 |   189,797.38 |        94,972.38 |          **+49.96%** |      244.67 |           149.84 |          **+38.76%** |       417.50 |               1.4371 |
|   700 |   226,951.87 |       113,513.30 |          **+49.98%** |      276.90 |           163.46 |          **+40.97%** |       443.89 |               1.5770 |
|   800 |   253,048.91 |       126,586.41 |          **+49.98%** |      302.44 |           175.97 |          **+41.81%** |       497.94 |               1.6066 |
|   900 |   297,548.40 |       148,936.37 |          **+49.95%** |      350.87 |           202.26 |          **+42.36%** |       603.08 |               1.4923 |
|  1000 |   334,848.03 |       167,428.95 |          **+50.00%** |      386.70 |           219.28 |          **+43.29%** |       653.93 |               1.5292 |
|  1500 |   518,581.53 |       259,374.38 |          **+49.98%** |      571.02 |           311.81 |          **+45.39%** |       986.94 |               1.5198 |
|  2000 |   699,246.72 |       349,801.86 |          **+49.97%** |      750.57 |           401.12 |          **+46.56%** |     1,286.46 |               1.5547 |

---

## 3. Key Summary Metrics

```
+-------------------------------------------------------------------------+
| Overall Metric Improvements of SSP-ARR over Classical Round Robin (RR)  |
+-------------------------------------------------------------------------+
| Average Waiting Time (AWT) Reduction   :  +49.95% (Cut in half)         |
| Average Turnaround Time (ATAT) Reduction:  +36.22%                      |
| Makespan Improvement                   :    0.00% (Identical load limit)|
| Throughput Improvement                 :    0.00%                       |
+-------------------------------------------------------------------------+
```

---

## 4. Academic Insights for Paper Writing

1. **Massive AWT Reduction (~50%)**:
   - In Classical RR, tasks rotate strictly by FIFO order. Short tasks are regularly trapped behind lengthy tasks through multiple context-switch cycles.
   - SSP-ARR leverages stability detection and adaptive predictive time quantuming. This cuts waiting delays across all task sizes by **nearly 50%**.

2. **Scaling Turnaround Time (ATAT) Gains**:
   - The ATAT improvement scales dynamically from **+5.10%** at 100 cloudlets to **+46.56%** at 2000 cloudlets.
   - Under dense workloads, adaptive quantum sizing prevents excessive queuing and preemption overhead.

3. **Makespan & Throughput Invariance**:
   - Makespan is bounded by the bottleneck VM under the Dynamic Max-Min global assignment (the total execution volume on the most heavily loaded VM remains constant regardless of local slice order).
   - This proves that local scheduling improvements directly target **latency, user responsiveness, and task waiting times** without distorting total system capacity.
