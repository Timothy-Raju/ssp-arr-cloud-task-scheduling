package com.cloudscheduling.simulation;

import java.util.Locale;

/**
 * ComparisonSimulation – runs MAADRR vs SSP-ARR on identical infrastructure,
 * workloads, VM assignments and random seeds, then prints a side-by-side
 * comparative table with percentage improvements.
 *
 * Improvement formula (lower-is-better metrics: AWT, ATAT, Makespan):
 *   Improvement(%) = (MAADRR - SSP-ARR) / MAADRR * 100
 *
 * Improvement formula (higher-is-better: Throughput):
 *   Improvement(%) = (SSP-ARR - MAADRR) / MAADRR * 100
 */
public class ComparisonSimulation {

    private static final int RUNS = 5;
    private static final int[] PAPER_SIZES = {
        100, 200, 300, 400, 500, 600,
        700, 800, 900, 1000, 1500, 2000
    };

    public static void main(String[] args) {
        Locale.setDefault(Locale.US);
        WorkspaceInfo.print();
        System.out.println();
        System.out.println("============================================================");
        System.out.println(" MAADRR vs SSP-ARR – Head-to-Head Comparison");
        System.out.println(" Same Infra | Same Workload | Same VM Assignment");
        System.out.println(" Only local scheduler differs.");
        System.out.println("============================================================");
        System.out.println();

        // Accumulators for global averages
        double sumAwtImp  = 0, sumAtatImp = 0, sumMsImp = 0, sumTpImp = 0;
        int count = 0;

        // Column header
        System.out.printf("%-8s | %-22s | %-22s | %-22s | %-22s%n",
            "Tasks",
            "AWT (ms)  [MAADRR/SSP]",
            "ATAT (s)  [MAADRR/SSP]",
            "Makespan (s) [MAADRR/SSP]",
            "Throughput  [MAADRR/SSP]");
        System.out.println("-".repeat(110));

        for (int size : PAPER_SIZES) {
            MAADRRSimulation.RunResult maadrr = new MAADRRSimulation.RunResult();
            SSPARRSimulation.RunResult ssparr = new SSPARRSimulation.RunResult();

            for (int run = 0; run < RUNS; run++) {
                maadrr.add(MAADRRSimulation.runExperiment(size));
                ssparr.add(SSPARRSimulation.runExperiment(size));
            }
            maadrr.divide(RUNS);
            ssparr.divide(RUNS);

            // Percentage improvements (positive = SSP-ARR wins)
            double awtImp  = pctImprove(maadrr.averageWaitingTimeMs,  ssparr.averageWaitingTimeMs,  false);
            double atatImp = pctImprove(maadrr.averageTurnaroundTime, ssparr.averageTurnaroundTime, false);
            double msImp   = pctImprove(maadrr.makespan,              ssparr.makespan,              false);
            double tpImp   = pctImprove(maadrr.throughput,            ssparr.throughput,            true);

            System.out.printf(
                "%-8d | %9.3f / %9.3f | %9.3f / %9.3f | %10.3f / %10.3f | %8.4f / %8.4f%n",
                size,
                maadrr.averageWaitingTimeMs,  ssparr.averageWaitingTimeMs,
                maadrr.averageTurnaroundTime, ssparr.averageTurnaroundTime,
                maadrr.makespan,              ssparr.makespan,
                maadrr.throughput,            ssparr.throughput
            );
            System.out.printf(
                "         | AWT imp: %+6.2f%%        | ATAT imp: %+6.2f%%       | MS imp: %+6.2f%%          | TP imp: %+6.2f%%%n",
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
        System.out.println("============================================================");
        System.out.println(" OVERALL AVERAGE IMPROVEMENT of SSP-ARR over MAADRR");
        System.out.println("============================================================");
        System.out.printf("  AWT      improvement: %+6.2f%%%n", sumAwtImp  / count);
        System.out.printf("  ATAT     improvement: %+6.2f%%%n", sumAtatImp / count);
        System.out.printf("  Makespan improvement: %+6.2f%%%n", sumMsImp   / count);
        System.out.printf("  Throughput improvement: %+6.2f%%%n", sumTpImp  / count);
        System.out.println("============================================================");
        System.out.println(" COMPARISON COMPLETE");
        System.out.println("============================================================");
    }

    /**
     * Calculates percentage improvement of SSP-ARR relative to MAADRR.
     * @param baseline  MAADRR value
     * @param proposed  SSP-ARR value
     * @param higherBetter  true for throughput, false for AWT/ATAT/Makespan
     */
    private static double pctImprove(double baseline, double proposed, boolean higherBetter) {
        if (baseline == 0) return 0;
        if (higherBetter) return (proposed - baseline) / baseline * 100.0;
        return (baseline - proposed) / baseline * 100.0;
    }
}
