# SSP-ARR: Stability-Switched Predictive Adaptive Round Robin for Cloud Task Scheduling

A discrete-event cloud task scheduling research framework implemented on **CloudSim Plus 8.5.7** and **Java 21**, evaluating the proposed **SSP-ARR** local VM scheduler against classical Round Robin (RR) and adaptive baselines under real-world Google Cloud Jobs (**GoCJ**) workload traces.

---

## 🚀 Key Features & Novelty

* **Stability-Switched Dual Mode**: Uses the Coefficient of Variation ($CV = \sigma / \mu$) over recent task completions to dynamically switch between:
  * **Reactive Mode** ($CV \le 0.30$): Safe, queue-median dynamic time quantum.
  * **Predictive Mode** ($CV > 0.30$): Adaptive Exponentially Weighted Moving Average (EWMA) quantuming.
* **Confidence Gating**: Evaluates Normalized Prediction Error (NPE); automatically falls back to reactive median slicing if prediction confidence falls below threshold.
* **Multi-Global Schedulers**: Integrates and evaluates 5 datacenter-level dispatchers:
  1. Dynamic Max-Min (Dy. MM)
  2. Dynamic Resource-Aware Load Balancing Algorithm (DRALBA)
  3. Priority-Based Static Scheduling Load Balancing (PSSLB)
  4. Priority-Based Static Scheduling with Enhanced Load Balancing (PSSELB)
  5. Dynamic Enhanced Resource-Aware Load Balancing Algorithm (DeRALBA)
* **Comprehensive Metrics**: Evaluates Average Waiting Time (AWT), Average Turnaround Time (ATAT), Average Completion Time (ACT), Throughput, Makespan, and SPECpower-based Host Energy Consumption ($\text{kWh}$).

---

## 🛠️ Infrastructure Configuration

* **Datacenter Hosts**: 30 Hosts, each with 4 Processing Elements (PEs) @ 4000 MIPS (120 PEs total)
* **Host Power Profile**: Linear SPECpower model ($P_{\text{idle}} = 150\text{ W}$, $P_{\text{max}} = 250\text{ W}$)
* **Heterogeneous VMs**: 80 VMs with computing capacities from 1000 to 4000 MIPS
* **Workload Benchmark**: Real-world Google Cloud Jobs (GoCJ) dataset across 12 scales (100 to 2000 cloudlets)

---

## 💻 Prerequisites & Build

* **Java**: Version 21 or higher
* **Maven**: Version 3.9 or higher

```bash
# Build the project
mvn clean compile
```

---

## 🔬 Running Experiments

### 1. Classical RR vs. SSP-ARR Comparison (Primary Benchmark)
Runs the direct head-to-head evaluation across 12 GoCJ workload sizes:
```bash
mvn exec:java -D"exec.mainClass"="com.cloudscheduling.simulation.RRvsSSPARRComparison"
```

### 2. Multi-Global Schedulers Evaluation (5 Dispatchers)
Runs RR vs. SSP-ARR across all 5 global schedulers (Dy. MM, DRALBA, PSSLB, PSSELB, DeRALBA) measuring AWT, ATAT, ACT, Throughput, and Energy (kWh):
```bash
mvn exec:java -D"exec.mainClass"="com.cloudscheduling.simulation.MultiGlobalComparisonSimulation"
```

### 3. Individual Simulation Runners
```bash
# Classical Round Robin baseline
mvn exec:java -D"exec.mainClass"="com.cloudscheduling.simulation.RRSimulation"

# SSP-ARR proposed scheduler
mvn exec:java -D"exec.mainClass"="com.cloudscheduling.simulation.SSPARRSimulation"

# RR vs. MAADRR across 5 global schedulers
mvn exec:java -D"exec.mainClass"="com.cloudscheduling.simulation.RRvsMAADRRMultiGlobalComparison"
```

---

## 📊 Results Summary

All experimental reports, raw data logs, and capstone diary documentation are archived in the `results/` directory:
* `results/rr_vs_ssparr_results.md`: Detailed tables showing ~50% AWT reduction and up to 46.6% ATAT reduction.
* `results/multi_global_scheduler_results.md`: Complete metrics across all 5 global schedulers including Energy (kWh).
* `results/capstone_diary_12_weeks.md`: Complete 12-week capstone project logbook entries.

