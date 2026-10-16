# Experimental Evaluation: Classical Round Robin (RR) vs. SSP-ARR

> **Simulation Environment**: CloudSim Plus 8.5.7 | Java 21 | Real GoCJ Workload Traces (100-2000 Cloudlets)
> **Infrastructure Setup**: 30 Hosts (120 PEs @ 4000 MIPS) | 80 Heterogeneous VMs (1000-4000 MIPS)
> **Global Scheduling**: Dynamic Max-Min Task Assignment (identical for both algorithms)
> **Independent Runs**: 5 runs per workload size (results averaged)
> **RR Quantum**: Fixed q = 10.0 s (realistic batch cloud environment)
> **SSP-ARR Stability Threshold**: CV = 0.50 (predictive EWMA mode activates under high-variance GoCJ workload)

---

## 1. Overview & Setup Isolation

To evaluate **SSP-ARR** against the standard **Round Robin (RR)** baseline, two independent simulation components were used:

1. **RRSimulation.java**: Classical Round Robin implementation using a fixed time quantum (q = 10.0 s) and standard circular FIFO queueing per VM.
2. **RRvsSSPARRComparison.java**: Comparative test harness evaluating both schedulers under identical infrastructure and task arrivals.

---

## 2. Head-to-Head Experimental Results

Below are the empirical metrics obtained across all 12 GoCJ workload sizes (averaged over 5 runs per size):

| Tasks | RR AWT (ms) | SSP-ARR AWT (ms) | AWT Improvement (%) | RR ATAT (s) | SSP-ARR ATAT (s) | ATAT Improvement (%) | Makespan (s) | Throughput (tasks/s) |
|------:|------------:|-----------------:|--------------------:|------------:|-----------------:|---------------------:|-------------:|---------------------:|
|   100 |     5,071.29 |         2,771.29 |          **+45.35%** |       53.09 |            50.79 |           **+4.33%** |       225.00 |               0.4444 |
|   200 |    49,266.78 |        24,666.78 |          **+49.93%** |      100.50 |            75.90 |          **+24.48%** |       236.84 |               0.8444 |
|   300 |   102,558.44 |        51,184.53 |          **+50.09%** |      157.36 |           105.99 |          **+32.65%** |       236.84 |               1.2667 |
|   400 |   132,034.25 |        66,169.80 |          **+49.88%** |      183.79 |           117.93 |          **+35.84%** |       264.55 |               1.5120 |
|   500 |   155,092.58 |        77,913.95 |          **+49.76%** |      207.00 |           129.82 |          **+37.29%** |       330.13 |               1.5145 |
|   600 |   188,845.09 |        94,972.38 |          **+49.71%** |      243.72 |           149.84 |          **+38.52%** |       417.50 |               1.4371 |
|   700 |   226,132.72 |       113,513.30 |          **+49.80%** |      276.08 |           163.46 |          **+40.79%** |       443.89 |               1.5770 |
|   800 |   250,515.67 |       126,586.41 |          **+49.47%** |      299.90 |           175.97 |          **+41.32%** |       497.94 |               1.6066 |
|   900 |   293,116.01 |       148,936.37 |          **+49.19%** |      346.44 |           202.26 |          **+41.62%** |       603.08 |               1.4923 |
|  1000 |   332,117.36 |       167,428.95 |          **+49.59%** |      383.97 |           219.28 |          **+42.89%** |       653.93 |               1.5292 |
|  1500 |   512,525.72 |       259,374.38 |          **+49.39%** |      564.96 |           311.81 |          **+44.81%** |       986.94 |               1.5198 |
|  2000 |   690,345.29 |       349,801.86 |          **+49.33%** |      741.66 |           401.12 |          **+45.92%** |    1,286.46 |               1.5547 |

---

## 3. Key Summary Metrics

```
+-------------------------------------------------------------------------+
| Overall Metric Improvements of SSP-ARR over Classical Round Robin (RR)  |
+-------------------------------------------------------------------------+
| Average Waiting Time (AWT) Reduction   :  +49.29% (Cut in half)         |
| Average Turnaround Time (ATAT) Reduction:  +35.87%                      |
| Makespan Improvement                   :    0.00% (Identical load limit)|
| Throughput Improvement                 :    0.00%                       |
+-------------------------------------------------------------------------+
```

> **Configuration**: RR quantum = 10.0 s (fixed FIFO) | SSP-ARR CV threshold = 0.50 | Prediction error gate = 20%

---

## 4. Academic Insights for Paper Writing

1. **Strong AWT Reduction (~49%)**:
   - In Classical RR with a 10 s fixed quantum, tasks rotate strictly by FIFO arrival order. Short tasks are trapped behind lengthy tasks for up to 10 seconds per preemption cycle.
   - SSP-ARR uses stability detection (CV threshold = 0.50) and EWMA-based adaptive predictive quantuming. Under GoCJ high-variance workload (CV ~1.24), predictive mode activates early, cutting waiting by nearly 50%.

2. **Scaling ATAT Gains**:
   - ATAT improvement scales from **+4.33%** at 100 cloudlets to **+45.92%** at 2000 cloudlets.
   - Adaptive quantum sizing combined with SRPT re-insertion prevents queuing overhead at scale.

3. **Makespan & Throughput Invariance**:
   - Makespan is bounded by the bottleneck VM (Dynamic Max-Min assignment is identical for both).
   - Local scheduling improvements target latency and responsiveness, not raw capacity.
