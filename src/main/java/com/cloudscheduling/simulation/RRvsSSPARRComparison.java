package com.cloudscheduling.simulation;

import java.util.Locale;

/**
 * RRvsSSPARRComparison – Head-to-Head Comparison: Classical Round Robin vs. SSP-ARR.
 *
 * Both algorithms run under completely identical conditions:
 *   - Same Datacenter (30 Hosts, 120 PEs @ 4000 MIPS)
 *   - Same Heterogeneous VMs (80 VMs, 1000–4000 MIPS)
 *   - Same GoCJ Workload Traces (100 to 2000 tasks)
 *   - Same Dynamic Max-Min Global Scheduling Task Assignment
 *
 * Differences (local VM-level tier):
 *   - RR: Classical fixed time quantum (10.0 s) with FIFO queue (baseline)
 *   - SSP-ARR: Stability-switched, confidence-gated predictive quantum with SRPT ranking
 *
 * Improvement formulas:
 *   - AWT, ATAT, Makespan (lower is better): (RR - SSP_ARR) / RR * 100
 *   - Throughput (higher is better): (SSP_ARR - RR) / RR * 100
 */
public class RRvsSSPARRComparison {

    private static final int RUNS = 5;
    private static final double RR_QUANTUM = 10.0; // 10 second fixed quantum for RR (realistic batch cloud environment)
    private static final int[] PAPER_SIZES = {
        100, 200, 300, 400, 500, 600,
        700, 800, 900, 1000, 1500, 2000
    };

    public static void main(String[] args) {
        Locale.setDefault(Locale.US);
        WorkspaceInfo.print();
        System.out.println();
        System.out.println("==========================================================================================");
        System.out.println(" EXPERIMENTAL EVALUATION: Classical Round Robin (RR) vs. SSP-ARR");
        System.out.println(" Benchmark: Real-world GoCJ Workload Traces (100 - 2000 cloudlets)");
        System.out.println(" Baseline: Classical RR (Fixed Quantum = " + RR_QUANTUM + "s, FIFO)");
        System.out.println(" Proposed: SSP-ARR v3 (Adaptive Predictive Quantum, Stability-Switched)");
        System.out.println("==========================================================================================");
        System.out.println();

        double sumAwtImp = 0, sumAtatImp = 0, sumMsImp = 0, sumTpImp = 0;
        int count = 0;

        System.out.printf("%-6s | %-24s | %-24s | %-24s | %-20s%n",
            "Tasks",
            "AWT (ms) [RR / SSP-ARR]",
            "ATAT (s) [RR / SSP-ARR]",
            "Makespan (s) [RR / SSP]",
            "Throughput [RR / SSP]");
        System.out.println("-".repeat(110));

        for (int size : PAPER_SIZES) {
            RRSimulation.RunResult rrResult = new RRSimulation.RunResult();
            SSPARRSimulation.RunResult sspResult = new SSPARRSimulation.RunResult();

            for (int r = 0; r < RUNS; r++) {
                rrResult.add(RRSimulation.runExperiment(size, RR_QUANTUM));
                sspResult.add(SSPARRSimulation.runExperiment(size));
            }
            rrResult.divide(RUNS);
            sspResult.divide(RUNS);

            double awtImp  = pctImprove(rrResult.averageWaitingTimeMs,  sspResult.averageWaitingTimeMs,  false);
            double atatImp = pctImprove(rrResult.averageTurnaroundTime, sspResult.averageTurnaroundTime, false);
            double msImp   = pctImprove(rrResult.makespan,              sspResult.makespan,              false);
            double tpImp   = pctImprove(rrResult.throughput,            sspResult.throughput,            true);

            System.out.printf(
                "%-6d | %10.2f / %10.2f | %10.2f / %10.2f | %10.2f / %10.2f | %8.4f / %8.4f%n",
                size,
                rrResult.averageWaitingTimeMs,  sspResult.averageWaitingTimeMs,
                rrResult.averageTurnaroundTime, sspResult.averageTurnaroundTime,
                rrResult.makespan,              sspResult.makespan,
                rrResult.throughput,            sspResult.throughput
            );
            System.out.printf(
                "       | AWT imp: %+6.2f%%        | ATAT imp: %+6.2f%%       | MS imp: %+6.2f%%          | TP imp: %+6.2f%%%n",
                awtImp, atatImp, msImp, tpImp
            );
            System.out.println("-".repeat(110));

            sumAwtImp  += awtImp;
            sumAtatImp += atatImp;
            sumMsImp   += msImp;
            sumTpImp   += tpImp;
            count++;
        }

        System.out.println();
        System.out.println("==========================================================================================");
        System.out.println(" SUMMARY: AVERAGE PERCENTAGE IMPROVEMENT OF SSP-ARR OVER CLASSICAL RR");
        System.out.println("==========================================================================================");
        System.out.printf("  Average Waiting Time (AWT) Reduction   : %+6.2f%%%n", sumAwtImp  / count);
        System.out.printf("  Average Turnaround Time (ATAT) Reduction: %+6.2f%%%n", sumAtatImp / count);
        System.out.printf("  Makespan Improvement                   : %+6.2f%%%n", sumMsImp   / count);
        System.out.printf("  Throughput Improvement                 : %+6.2f%%%n", sumTpImp  / count);
        System.out.println("==========================================================================================");
    }

    private static double pctImprove(double baseline, double proposed, boolean higherBetter) {
        if (baseline == 0) return 0;
        if (higherBetter) {
            return (proposed - baseline) / baseline * 100.0;
        }
        return (baseline - proposed) / baseline * 100.0;
    }
}

