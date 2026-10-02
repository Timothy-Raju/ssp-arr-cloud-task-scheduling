# Capstone Project Diary / Logbook (12 Weeks)
**Project Title**: Stability-Switched Predictive Adaptive Round Robin (SSP-ARR) for Cloud Task Scheduling  
**Focus**: Comparative Performance Analysis of Classical Round Robin (RR) vs. Proposed SSP-ARR under Real-World Cloud Workloads (GoCJ)

---

### **Week 1: Literature Review & Problem Formulation**
* **Tasks Completed**:
  - Conducted extensive literature survey on classical CPU and cloud scheduling algorithms, focusing on the limitations of fixed time-quantum Round Robin (RR).
  - Studied the impact of cloudlet burst-time heterogeneity on queuing delay, task starvation, and context-switching overhead.
  - Defined the core problem statement: Classical Round Robin causes severe waiting delays under skewed, high-variance cloud workloads due to rigid, static time slicing.
* **Tasks Planned Next Week**:
  - Identify simulation frameworks and select real-world cloud workload trace datasets for experimental evaluation.

---

### **Week 2: Simulation Environment & Dataset Selection**
* **Tasks Completed**:
  - Evaluated discrete-event cloud simulation platforms; selected CloudSim Plus 8.5.7 with Java 21 for modern resource modeling and lifecycle support.
  - Procured and analyzed the real-world Google Cloud Jobs (GoCJ) benchmark dataset across sizes ranging from 100 to 2000 cloudlets.
  - Initialized Maven-based project structure and configured dependency trees for CloudSim Plus.
* **Tasks Planned Next Week**:
  - Design the datacenter and host infrastructure model mirroring realistic enterprise cloud tiers.

---

### **Week 3: Datacenter & Heterogeneous VM Modeling**
* **Tasks Completed**:
  - Implemented the cloud datacenter topology comprising 30 physical hosts (each with 4 processing elements @ 4000 MIPS).
  - Designed an 80-VM heterogeneous cluster with compute capacities scaled across 1000 to 4000 MIPS, alongside standardized RAM, bandwidth, and storage parameters.
  - Integrated dataset parsers to load and validate GoCJ cloudlet traces with lengths spanning 15,000 to 900,000 MI.
* **Tasks Planned Next Week**:
  - Implement baseline Classical Round Robin (RR) scheduler with FIFO queueing at the VM tier.

---

### **Week 4: Baseline Round Robin (RR) Implementation**
* **Tasks Completed**:
  - Developed `RRSimulation.java` implementing standard Classical Round Robin scheduling with a fixed time quantum ($q = 1.0\text{ s}$).
  - Modeled circular FIFO VM queues preserving natural task arrival sequences without pre-sorting.
  - Created execution tracers to measure task arrival, start time, preemption cycles, and completion timestamps.
* **Tasks Planned Next Week**:
  - Design the algorithmic framework and mathematical formulation for the proposed SSP-ARR algorithm.

---

### **Week 5: SSP-ARR Mathematical Formulation & Stability Switching**
* **Tasks Completed**:
  - Formulated the theoretical model for SSP-ARR: Stability-Switched Predictive Adaptive Round Robin.
  - Designed the Coefficient of Variation ($CV = \frac{\sigma}{\mu}$) metric over a sliding window ($W = 5$) of completed tasks to detect workload volatility.
  - Formulated the dual-mode switching policy: Reactive mode ($CV \le 0.30$, stable workload) versus Predictive mode ($CV > 0.30$, volatile burst workload).
* **Tasks Planned Next Week**:
  - Implement the confidence-gated EWMA predictive quantum engine for volatile workload regimes.

---

### **Week 6: Predictive Quantum Engine & Confidence Gating**
* **Tasks Completed**:
  - Designed the Exponentially Weighted Moving Average (EWMA) predictor with dynamic error-driven learning rate $\alpha \in [0.20, 0.80]$.
  - Formulated a prediction confidence gate measuring Normalized Prediction Error (NPE) over recent cycles; falls back safely to median reactive quantum if error exceeds 30%.
  - Embedded Shortest Remaining Processing Time (SRPT) task ranking at the local VM level to minimize head-of-line blocking for short tasks.
* **Tasks Planned Next Week**:
  - Implement and unit-test the complete SSP-ARR scheduler in Java within the CloudSim Plus pipeline.

---

### **Week 7: SSP-ARR Implementation & Standalone Validation**
* **Tasks Completed**:
  - Implemented `SSPARRSimulation.java` combining the stability detector, confidence gate, adaptive EWMA predictor, and bounded time quantum ($q \in [0.001\text{ s}, 60.0\text{ s}]$).
  - Validated queue re-insertion logic maintaining sorted remaining burst order to prevent preemption-induced queue distortion.
  - Conducted preliminary unit runs to verify zero task drops and proper state transitions between reactive and predictive modes.
* **Tasks Planned Next Week**:
  - Develop comparative test harness to run Classical RR and SSP-ARR back-to-back under identical workloads.

---

### **Week 8: Head-to-Head Comparative Simulation (RR vs. SSP-ARR)**
* **Tasks Completed**:
  - Developed `RRvsSSPARRComparison.java` running both schedulers under identical infrastructure and task allocations across 12 GoCJ dataset sizes (100–2000 cloudlets).
  - Configured 5 randomized runs per workload size to ensure statistical significance.
  - Computed preliminary performance metrics: Average Waiting Time (AWT), Average Turnaround Time (ATAT), Makespan, and Throughput.
* **Tasks Planned Next Week**:
  - Expand the experimental setup to evaluate SSP-ARR across multiple global datacenter-level dispatchers.

---

### **Week 9: Multi-Tier Integration with Global Schedulers**
* **Tasks Completed**:
  - Implemented `GlobalSchedulers.java` containing 5 prominent global task-allocation policies: Dynamic Max-Min (Dy. MM), DRALBA, PSSLB, PSSELB, and DeRALBA.
  - Created a modular dispatcher allowing seamless pairing of any global allocation heuristic with local VM schedulers (RR vs. SSP-ARR).
  - Ensured identical task-to-VM mapping across algorithms to isolate and fairly measure local scheduling gains.
* **Tasks Planned Next Week**:
  - Integrate energy consumption modeling based on host power states into the multi-scheduler harness.

---

### **Week 10: Energy Modeling & Multi-Global Simulation**
* **Tasks Completed**:
  - Integrated the SPECpower linear host power consumption model ($P_{\text{idle}} = 150\text{ W}$, $P_{\text{max}} = 250\text{ W}$) to compute total datacenter Energy Consumption in kilowatt-hours ($\text{kWh}$).
  - Developed `MultiGlobalComparisonSimulation.java` evaluating Classical RR vs. SSP-ARR across all 5 global schedulers for all 12 workload sizes.
  - Automated output generation and verified energy calculation formulas: $E_{\text{total}} = \int P(t) dt$.
* **Tasks Planned Next Week**:
  - Consolidate and analyze experimental data; generate summary graphs and comparative performance tables.

---

### **Week 11: Experimental Data Analysis & Empirical Synthesis**
* **Tasks Completed**:
  - Synthesized all experimental findings:
    - **AWT**: SSP-ARR achieved a consistent **~50% reduction** across all 5 global schedulers.
    - **ATAT & ACT**: Scaled from **+5.1%** at 100 cloudlets to **+46.6%** at 2000 cloudlets (**+36.2% average**).
    - **Makespan, Throughput & Energy**: Maintained strict parity, demonstrating that latency cuts were achieved with zero capacity or energy penalty.
  - Exported structured markdown results tables into the workspace `results/` repository.
* **Tasks Planned Next Week**:
  - Complete final capstone project report, documentation, presentation slides, and code archival.

---

### **Week 12: Final Documentation, Paper Structuring & Project Archival**
* **Tasks Completed**:
  - Authored comprehensive project documentation covering algorithm pseudocode, architectural flowcharts, and empirical analysis.
  - Prepared research paper draft titled *"Stability-Switched Predictive Adaptive Round Robin (SSP-ARR) for Heterogeneous Cloud Task Scheduling"*.
  - Cleaned and documented workspace source code, Maven build scripts, and reproducible simulation commands.
  - Finalized capstone presentation slides and verified all deliverables.
* **Tasks Planned Next Week**:
  - Final capstone defense and submission of project report to evaluation committee.
