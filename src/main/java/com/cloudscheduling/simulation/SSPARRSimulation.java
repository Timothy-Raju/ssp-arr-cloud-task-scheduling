package com.cloudscheduling.simulation;

import org.cloudsimplus.brokers.DatacenterBrokerSimple;
import org.cloudsimplus.cloudlets.Cloudlet;
import org.cloudsimplus.core.CloudSimPlus;
import org.cloudsimplus.datacenters.DatacenterSimple;
import org.cloudsimplus.hosts.Host;
import org.cloudsimplus.hosts.HostSimple;
import org.cloudsimplus.resources.Pe;
import org.cloudsimplus.resources.PeSimple;
import org.cloudsimplus.schedulers.cloudlet.CloudletSchedulerTimeShared;
import org.cloudsimplus.schedulers.vm.VmSchedulerTimeShared;
import org.cloudsimplus.vms.Vm;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Deque;
import java.util.List;
import java.util.Locale;

/**
 * SSP-ARR v3 – Stability-Switched Predictive Adaptive Round Robin.
 *
 * Local scheduler (per-VM):
 *   - Stable workload   → Reactive quantum = clip(median(RB), Q_MIN, Q_MAX)
 *   - Volatile workload → EWMA prediction (confidence-gated):
 *       reliable  → Predictive quantum = clip(EWMA_pred, Q_MIN, Q_MAX)
 *       otherwise → Reactive quantum
 *
 * EWMA update:  ewma_new = alpha * actual + (1 - alpha) * ewma_old
 *   Adaptive alpha based on normalized prediction error:
 *     err < 10%  → 0.20 | 10-20% → 0.40 | 20-30% → 0.60 | >30% → 0.80
 *
 * Stability: coefficient of variation (CV) of last 5 completed bursts.
 *   CV <= 0.30 → stable
 *
 * Same infrastructure and global scheduler as MAADRR for fair comparison.
 */
public class SSPARRSimulation {

    // ============================================================
    // INFRASTRUCTURE (identical to MAADRR)
    // ============================================================
    private static final int    HOST_COUNT   = 30;
    private static final int    PES_PER_HOST = 4;
    private static final double HOST_PE_MIPS = 4000.0;
    private static final int    VM_COUNT     = 80;

    private static final double[] VM_MIPS_PATTERN = {
        1000, 1200, 1400, 1600, 1800,
        2000, 2200, 2400, 2600, 2800,
        3000, 3200, 3400, 3600, 3800, 4000
    };

    private static final int  VM_RAM        = 8192;
    private static final long VM_BW         = 20000;
    private static final long VM_STORAGE    = 10000;
    private static final int  CLOUDLET_PES  = 1;

    // ============================================================
    // SSP-ARR PARAMETERS
    // ============================================================
    private static final double EWMA_ALPHA_LOW_ERROR       = 0.20;
    private static final double EWMA_ALPHA_MEDIUM_ERROR    = 0.40;
    private static final double EWMA_ALPHA_HIGH_ERROR      = 0.60;
    private static final double EWMA_ALPHA_VERY_HIGH_ERROR = 0.80;

    private static final int    STABILITY_WINDOW          = 5;
    private static final double STABILITY_THRESHOLD       = 0.50;  // CV threshold — raised to 0.50 so predictive mode activates under GoCJ's high variance (CV ≈ 1.24)
    private static final int    PREDICTION_ERROR_WINDOW   = 5;
    private static final double MAX_NORM_PREDICTION_ERROR = 0.20;  // tighter gate: only use EWMA when prediction error < 20%

    private static final double Q_MIN = 0.001;
    private static final double Q_MAX = 60.0;

    // ============================================================
    // EXPERIMENT
    // ============================================================
    private static final int RUNS = 5;
    private static final int[] PAPER_SIZES = {
        100, 200, 300, 400, 500, 600,
        700, 800, 900, 1000, 1500, 2000
    };

    // ============================================================
    // MAIN
    // ============================================================
    public static void main(String[] args) {
        Locale.setDefault(Locale.US);
        WorkspaceInfo.print();
        System.out.println();
        System.out.println("============================================================");
        System.out.println(" SSP-ARR v3 - Stability-Switched Predictive Adaptive RR");
        System.out.println("============================================================");
        System.out.printf("Hosts: %d | VMs: %d | Runs/size: %d%n", HOST_COUNT, VM_COUNT, RUNS);
        System.out.printf("EWMA alpha: adaptive {%.2f, %.2f, %.2f, %.2f}%n",
            EWMA_ALPHA_LOW_ERROR, EWMA_ALPHA_MEDIUM_ERROR,
            EWMA_ALPHA_HIGH_ERROR, EWMA_ALPHA_VERY_HIGH_ERROR);
        System.out.printf("CV threshold: %.2f | Q=[%.3f, %.1f]%n",
            STABILITY_THRESHOLD, Q_MIN, Q_MAX);
        System.out.println("============================================================");

        for (int size : PAPER_SIZES) {
            RunResult total = new RunResult();
            for (int run = 0; run < RUNS; run++) {
                total.add(runExperiment(size));
            }
            total.divide(RUNS);

            System.out.printf(
                "Tasks %4d: AWT=%9.3f ms | ATAT=%9.3f s | Makespan=%9.3f s | Throughput=%.4f tasks/s%n",
                size,
                total.averageWaitingTimeMs,
                total.averageTurnaroundTime,
                total.makespan,
                total.throughput
            );
        }

        System.out.println("============================================================");
        System.out.println(" SSP-ARR EXPERIMENT COMPLETED");
        System.out.println("============================================================");
    }

    // ============================================================
    // EXPERIMENT
    // ============================================================
    static RunResult runExperiment(int workloadSize) {
        CloudSimPlus simulation = new CloudSimPlus();

        // Build datacenter (identical to MAADRR)
        List<Host> hostList = new ArrayList<>();
        for (int h = 0; h < HOST_COUNT; h++) {
            List<Pe> peList = new ArrayList<>();
            for (int p = 0; p < PES_PER_HOST; p++) peList.add(new PeSimple(HOST_PE_MIPS));
            Host host = new HostSimple(32768, 100000, 1_000_000, peList);
            host.setVmScheduler(new VmSchedulerTimeShared());
            hostList.add(host);
        }
        new DatacenterSimple(simulation, hostList);

        DatacenterBrokerSimple broker = new DatacenterBrokerSimple(simulation);
        List<Vm> vmList = MAADRRSimulation.createVms();
        broker.submitVmList(vmList);

        List<Cloudlet> cloudlets = MAADRRSimulation.loadGoCJCloudlets(workloadSize);
        int[] assignment = MAADRRSimulation.dynamicMaxMinAssignment(cloudlets, vmList);

        List<VMQueue> vmQueues = new ArrayList<>();
        for (Vm vm : vmList) vmQueues.add(new VMQueue(vm));

        for (int i = 0; i < cloudlets.size(); i++) {
            Cloudlet cl = cloudlets.get(i);
            int vmIdx = assignment[i];
            double burst = cl.getLength() / vmList.get(vmIdx).getMips();
            vmQueues.get(vmIdx).tasks.add(new TaskState(cl.getId(), cl, burst));
        }

        // Sort by ascending burst (Rank = RB, no priority in GoCJ)
        for (VMQueue vq : vmQueues) {
            List<TaskState> sorted = new ArrayList<>(vq.tasks);
            sorted.sort(Comparator
                .comparingDouble((TaskState t) -> t.originalBurst)
                .thenComparingLong(t -> t.cloudletId));
            vq.tasks.clear();
            vq.tasks.addAll(sorted);
        }

        return simulateLocalScheduling(vmQueues);
    }

    // ============================================================
    // LOCAL SSP-ARR SCHEDULING
    // ============================================================
    private static RunResult simulateLocalScheduling(List<VMQueue> vmQueues) {
        RunResult result = new RunResult();
        double globalMakespan = 0.0;

        for (VMQueue vmQueue : vmQueues) {
            double currentTime = 0.0;

            Deque<Double> completedBurstHistory = new ArrayDeque<>();
            Deque<Double> predictionErrorHistory = new ArrayDeque<>();

            double ewmaPrediction  = 0.0;
            boolean ewmaInitialized = false;

            while (!vmQueue.tasks.isEmpty()) {

                TaskState task = vmQueue.tasks.pollFirst();

                // Reactive quantum = min(median_queue, remaining_burst) to let short tasks finish fast
                double reactiveQuantum = calculateReactiveQuantum(vmQueue, task);

                // Stability detection (CV of last STABILITY_WINDOW completed bursts)
                boolean stable = isStable(completedBurstHistory);

                // Prediction (only when volatile)
                double predictiveEstimate = 0.0;
                boolean predictionGenerated = false;
                if (!stable) {
                    predictiveEstimate = makeEwmaPrediction(ewmaPrediction, ewmaInitialized, completedBurstHistory);
                    predictionGenerated = true;
                    task.predictedBurst    = predictiveEstimate;
                    task.predictionEvaluated = true;
                }

                // Confidence gate
                boolean reliable       = predictionGenerated && isPredictionReliable(predictionErrorHistory);
                boolean predictiveMode = !stable && reliable;

                double quantum;
                if (predictiveMode) {
                    /*
                     * SSP-ARR key insight:
                     * Use EWMA prediction as quantum but cap at the task's remaining burst.
                     * This lets tasks that are shorter than the prediction finish in one
                     * slice, eliminating unnecessary preemptions for short tasks.
                     * For long tasks, it matches MAADRR's adaptive behavior.
                     */
                    double taskBound = Math.min(predictiveEstimate, task.remainingBurst);
                    quantum = clamp(taskBound, Q_MIN, Q_MAX);
                    result.predictiveCount++;
                    result.totalPredictiveQuantum += quantum;
                    task.predictionUsed = true;
                } else {
                    /*
                     * Reactive mode: use min(median, remaining_burst) so short tasks
                     * also get a chance to complete in one slice even without prediction.
                     */
                    double taskBound = Math.min(reactiveQuantum, task.remainingBurst);
                    quantum = clamp(taskBound, Q_MIN, Q_MAX);
                    result.reactiveCount++;
                    result.totalReactiveQuantum += quantum;
                    if (predictionGenerated && !reliable) result.rejectedCount++;
                }

                // Execute slice
                double slice = Math.min(quantum, task.remainingBurst);
                task.remainingBurst -= slice;
                currentTime += slice;

                if (task.remainingBurst <= 1e-9) {
                    task.remainingBurst = 0.0;
                    task.finishTime = currentTime;

                    double waitingTime = Math.max(0.0, task.finishTime - task.originalBurst);
                    result.totalWaitingTime    += waitingTime;
                    result.totalTurnaroundTime += task.finishTime;
                    result.completedTasks++;
                    globalMakespan = Math.max(globalMakespan, task.finishTime);

                    // Update prediction error history
                    if (task.predictionEvaluated && task.predictedBurst > 0.0) {
                        double absErr  = Math.abs(task.originalBurst - task.predictedBurst);
                        double normErr = absErr / Math.max(task.originalBurst, 1e-9);
                        result.totalPredictionError += absErr;
                        result.predictionMeasurements++;
                        predictionErrorHistory.addLast(normErr);
                        while (predictionErrorHistory.size() > PREDICTION_ERROR_WINDOW)
                            predictionErrorHistory.removeFirst();
                    }

                    // EWMA update
                    double actual = task.originalBurst;
                    if (!ewmaInitialized) {
                        ewmaPrediction = actual;
                        ewmaInitialized = true;
                    } else {
                        double alpha = calculateAdaptiveAlpha(predictionErrorHistory);
                        ewmaPrediction = alpha * actual + (1.0 - alpha) * ewmaPrediction;
                    }

                    completedBurstHistory.addLast(actual);
                    while (completedBurstHistory.size() > STABILITY_WINDOW)
                        completedBurstHistory.removeFirst();

                } else {
                    // Re-insert maintaining sorted order by ascending remaining burst
                    // (SSP-ARR advantage: EWMA-tuned quanta reduce preemptions vs MAADRR's median)
                    insertSortedByBurst(vmQueue.tasks, task);
                }
            }
        }

        if (result.completedTasks > 0) {
            result.averageWaitingTimeMs  = (result.totalWaitingTime  / result.completedTasks) * 1000.0;
            result.averageTurnaroundTime = result.totalTurnaroundTime / result.completedTasks;
        }
        result.makespan   = globalMakespan;
        result.throughput = globalMakespan > 0 ? (double) result.completedTasks / globalMakespan : 0.0;
        if (result.predictionMeasurements > 0)
            result.predictionMAE = result.totalPredictionError / result.predictionMeasurements;
        return result;
    }

    /** Insert task maintaining ascending remaining-burst order. */
    private static void insertSortedByBurst(Deque<TaskState> deque, TaskState task) {
        List<TaskState> list = new ArrayList<>(deque);
        deque.clear();
        boolean inserted = false;
        for (TaskState t : list) {
            if (!inserted && t.remainingBurst > task.remainingBurst) {
                deque.addLast(task);
                inserted = true;
            }
            deque.addLast(t);
        }
        if (!inserted) deque.addLast(task);
    }

    // ============================================================
    // REACTIVE QUANTUM
    // ============================================================
    private static double calculateReactiveQuantum(VMQueue vq, TaskState current) {
        List<Double> bursts = new ArrayList<>();
        bursts.add(current.remainingBurst);
        for (TaskState t : vq.tasks) {
            if (t.remainingBurst > 0) bursts.add(t.remainingBurst);
        }
        if (bursts.isEmpty()) return Q_MIN;
        bursts.sort(Double::compareTo);
        int sz = bursts.size();
        double median = (sz % 2 == 0)
            ? (bursts.get(sz / 2 - 1) + bursts.get(sz / 2)) / 2.0
            : bursts.get(sz / 2);
        return clamp(median, Q_MIN, Q_MAX);
    }

    // ============================================================
    // STABILITY DETECTOR
    // ============================================================
    private static boolean isStable(Deque<Double> history) {
        if (history.size() < STABILITY_WINDOW) return true;
        double mean = history.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
        if (mean <= 1e-9) return true;
        double variance = 0.0;
        for (double v : history) { double d = v - mean; variance += d * d; }
        variance /= history.size();
        return Math.sqrt(variance) / mean <= STABILITY_THRESHOLD;
    }

    // ============================================================
    // EWMA PREDICTOR
    // ============================================================
    private static double makeEwmaPrediction(double ewma, boolean initialized, Deque<Double> history) {
        if (!initialized) {
            if (history.isEmpty()) return Q_MIN;
            List<Double> vals = new ArrayList<>(history);
            vals.sort(Double::compareTo);
            int mid = vals.size() / 2;
            return (vals.size() % 2 == 0)
                ? (vals.get(mid - 1) + vals.get(mid)) / 2.0
                : vals.get(mid);
        }
        return clamp(ewma, Q_MIN, Q_MAX);
    }

    // ============================================================
    // ADAPTIVE EWMA ALPHA
    // ============================================================
    private static double calculateAdaptiveAlpha(Deque<Double> errorHistory) {
        if (errorHistory.isEmpty()) return EWMA_ALPHA_LOW_ERROR;
        double mean = errorHistory.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
        if (mean < 0.10) return EWMA_ALPHA_LOW_ERROR;
        if (mean < 0.20) return EWMA_ALPHA_MEDIUM_ERROR;
        if (mean < 0.30) return EWMA_ALPHA_HIGH_ERROR;
        return EWMA_ALPHA_VERY_HIGH_ERROR;
    }

    // ============================================================
    // PREDICTION CONFIDENCE GATE
    // ============================================================
    private static boolean isPredictionReliable(Deque<Double> errorHistory) {
        if (errorHistory.size() < PREDICTION_ERROR_WINDOW) return false;
        double mean = errorHistory.stream().mapToDouble(Double::doubleValue).average()
            .orElse(Double.POSITIVE_INFINITY);
        return mean <= MAX_NORM_PREDICTION_ERROR;
    }

    private static double clamp(double v, double min, double max) {
        return Math.max(min, Math.min(max, v));
    }

    // ============================================================
    // DATA CLASSES
    // ============================================================
    private static class VMQueue {
        @SuppressWarnings("unused")
        final Vm vm;
        final Deque<TaskState> tasks = new ArrayDeque<>();
        VMQueue(Vm vm) { this.vm = vm; }
    }

    private static class TaskState {
        final long      cloudletId;
        @SuppressWarnings("unused")
        final Cloudlet  cloudlet;
        final double    originalBurst;
        double          remainingBurst;
        double          finishTime;
        double          predictedBurst;
        boolean         predictionEvaluated;
        boolean         predictionUsed;

        TaskState(long id, Cloudlet cl, double burst) {
            this.cloudletId         = id;
            this.cloudlet           = cl;
            this.originalBurst      = burst;
            this.remainingBurst     = burst;
        }
    }

    static class RunResult {
        double totalWaitingTime;
        double totalTurnaroundTime;
        double averageWaitingTimeMs;
        double averageTurnaroundTime;
        double makespan;
        double throughput;
        long   completedTasks;
        double predictionMAE;
        double totalPredictionError;
        long   predictionMeasurements;
        long   predictiveCount;
        long   reactiveCount;
        long   rejectedCount;
        double totalReactiveQuantum;
        double totalPredictiveQuantum;

        void add(RunResult o) {
            totalWaitingTime      += o.totalWaitingTime;
            totalTurnaroundTime   += o.totalTurnaroundTime;
            averageWaitingTimeMs  += o.averageWaitingTimeMs;
            averageTurnaroundTime += o.averageTurnaroundTime;
            makespan              += o.makespan;
            throughput            += o.throughput;
            completedTasks        += o.completedTasks;
            predictionMAE         += o.predictionMAE;
            totalPredictionError  += o.totalPredictionError;
            predictionMeasurements+= o.predictionMeasurements;
            predictiveCount       += o.predictiveCount;
            reactiveCount         += o.reactiveCount;
            rejectedCount         += o.rejectedCount;
            totalReactiveQuantum  += o.totalReactiveQuantum;
            totalPredictiveQuantum+= o.totalPredictiveQuantum;
        }

        void divide(int d) {
            if (d <= 0) return;
            totalWaitingTime      /= d;
            totalTurnaroundTime   /= d;
            averageWaitingTimeMs  /= d;
            averageTurnaroundTime /= d;
            makespan              /= d;
            throughput            /= d;
            completedTasks        /= d;
            predictionMAE         /= d;
            totalPredictionError  /= d;
            predictionMeasurements/= d;
            predictiveCount       /= d;
            reactiveCount         /= d;
            rejectedCount         /= d;
            totalReactiveQuantum  /= d;
            totalPredictiveQuantum/= d;
        }
    }
}
