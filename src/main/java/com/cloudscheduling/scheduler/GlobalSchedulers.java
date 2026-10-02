package com.cloudscheduling.scheduler;

import org.cloudsimplus.cloudlets.Cloudlet;
import org.cloudsimplus.vms.Vm;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;

/**
 * Implementation of the 5 Global Datacenter-tier Schedulers evaluated in
 * cloud scheduling literature (e.g., MAADRR paper, Section IV-B):
 *
 * 1. Dynamic Max-Min (Dy. MM) [Mazumder et al., 2019]
 * 2. DRALBA - Dynamic Resource-Aware Load Balancing Algorithm [Nabi et al., IEEE Access 2021]
 * 3. PSSLB - Priority-Based Static Scheduling Load Balancing [Alaei & Safi-Esfahani, 2018]
 * 4. PSSELB - Priority-Based Static Scheduling with Enhanced Load Balancing [Alaei & Safi-Esfahani, 2018]
 * 5. DeRALBA - Dynamic Enhanced Resource-Aware Load Balancing Algorithm [Hussain et al., PeerJ 2025]
 */
public class GlobalSchedulers {

    public enum Policy {
        DYNAMIC_MAX_MIN("Dy. MM"),
        DRALBA("DRALBA"),
        PSSLB("PSSLB"),
        PSSELB("PSSELB"),
        DERALBA("DeRALBA");

        private final String displayName;
        Policy(String name) { this.displayName = name; }
        public String getDisplayName() { return displayName; }
    }

    /**
     * Dispatcher method to compute task-to-VM assignments for a given global scheduler.
     */
    public static int[] assign(Policy policy, List<Cloudlet> cloudlets, List<Vm> vmList) {
        switch (policy) {
            case DYNAMIC_MAX_MIN:
                return dynamicMaxMin(cloudlets, vmList);
            case DRALBA:
                return dralba(cloudlets, vmList);
            case PSSLB:
                return psslb(cloudlets, vmList);
            case PSSELB:
                return psselb(cloudlets, vmList);
            case DERALBA:
                return deralba(cloudlets, vmList);
            default:
                return dynamicMaxMin(cloudlets, vmList);
        }
    }

    // =========================================================================
    // 1. DYNAMIC MAX-MIN (Dy. MM)
    // =========================================================================
    public static int[] dynamicMaxMin(List<Cloudlet> cloudlets, List<Vm> vmList) {
        int n = cloudlets.size();
        int m = vmList.size();
        int[] assignment = new int[n];
        double[] readyTime = new double[m];
        boolean[] scheduled = new boolean[n];

        for (int step = 0; step < n; step++) {
            int selectedTask = -1;
            int selectedVm = -1;
            double maxMinCompTime = -1.0;

            for (int i = 0; i < n; i++) {
                if (scheduled[i]) continue;
                Cloudlet cl = cloudlets.get(i);

                int bestVm = 0;
                double minCompTime = Double.MAX_VALUE;
                for (int j = 0; j < m; j++) {
                    double ct = readyTime[j] + (cl.getLength() / vmList.get(j).getMips());
                    if (ct < minCompTime) {
                        minCompTime = ct;
                        bestVm = j;
                    }
                }

                if (minCompTime > maxMinCompTime) {
                    maxMinCompTime = minCompTime;
                    selectedTask = i;
                    selectedVm = bestVm;
                }
            }

            if (selectedTask >= 0) {
                assignment[selectedTask] = selectedVm;
                scheduled[selectedTask] = true;
                readyTime[selectedVm] += cloudlets.get(selectedTask).getLength() / vmList.get(selectedVm).getMips();
            }
        }
        return assignment;
    }

    // =========================================================================
    // 2. DRALBA (Dynamic Resource-Aware Load Balancing Algorithm)
    // =========================================================================
    public static int[] dralba(List<Cloudlet> cloudlets, List<Vm> vmList) {
        int n = cloudlets.size();
        int m = vmList.size();
        int[] assignment = new int[n];
        double[] vmLoad = new double[m]; // total MI assigned to VM

        // Task sorting: order by task size descending (longest jobs first for load balance)
        List<Integer> taskIndices = new ArrayList<>();
        for (int i = 0; i < n; i++) taskIndices.add(i);
        taskIndices.sort((a, b) -> Double.compare(cloudlets.get(b).getLength(), cloudlets.get(a).getLength()));

        for (int idx : taskIndices) {
            Cloudlet cl = cloudlets.get(idx);
            int bestVm = 0;
            double minEffectiveLoad = Double.MAX_VALUE;

            for (int j = 0; j < m; j++) {
                // Effective completion time / load index = (vmLoad + taskLength) / vmMips
                double effectiveTime = (vmLoad[j] + cl.getLength()) / vmList.get(j).getMips();
                if (effectiveTime < minEffectiveLoad) {
                    minEffectiveLoad = effectiveTime;
                    bestVm = j;
                }
            }

            assignment[idx] = bestVm;
            vmLoad[bestVm] += cl.getLength();
        }
        return assignment;
    }

    // =========================================================================
    // 3. PSSLB (Priority-Based Static Scheduling Load Balancing)
    // =========================================================================
    public static int[] psslb(List<Cloudlet> cloudlets, List<Vm> vmList) {
        int n = cloudlets.size();
        int m = vmList.size();
        int[] assignment = new int[n];
        double[] cumulativeBurst = new double[m];

        // Static priority assignment: larger bursts get higher static rank
        List<Integer> taskIndices = new ArrayList<>();
        for (int i = 0; i < n; i++) taskIndices.add(i);
        taskIndices.sort((a, b) -> Double.compare(cloudlets.get(b).getLength(), cloudlets.get(a).getLength()));

        // Sort VMs by computing power descending
        Integer[] vmOrder = new Integer[m];
        for (int j = 0; j < m; j++) vmOrder[j] = j;
        Arrays.sort(vmOrder, (a, b) -> Double.compare(vmList.get(b).getMips(), vmList.get(a).getMips()));

        for (int idx : taskIndices) {
            Cloudlet cl = cloudlets.get(idx);
            // Select VM that minimizes cumulative finish time
            int bestVm = vmOrder[0];
            double minFinish = Double.MAX_VALUE;

            for (int j : vmOrder) {
                double finish = cumulativeBurst[j] + (cl.getLength() / vmList.get(j).getMips());
                if (finish < minFinish) {
                    minFinish = finish;
                    bestVm = j;
                }
            }

            assignment[idx] = bestVm;
            cumulativeBurst[bestVm] += cl.getLength() / vmList.get(bestVm).getMips();
        }
        return assignment;
    }

    // =========================================================================
    // 4. PSSELB (Priority-Based Static Scheduling with Enhanced Load Balancing)
    // =========================================================================
    public static int[] psselb(List<Cloudlet> cloudlets, List<Vm> vmList) {
        int n = cloudlets.size();
        int m = vmList.size();
        int[] assignment = new int[n];
        double[] vmWorkloadTime = new double[m];

        // Enhanced partitioning: tasks split into high, medium, low burst tiers
        List<Integer> sortedTasks = new ArrayList<>();
        for (int i = 0; i < n; i++) sortedTasks.add(i);
        sortedTasks.sort((a, b) -> Double.compare(cloudlets.get(b).getLength(), cloudlets.get(a).getLength()));

        // Calculate average system MIPS
        double totalMips = 0.0;
        for (Vm vm : vmList) totalMips += vm.getMips();
        double avgMips = totalMips / m;

        for (int idx : sortedTasks) {
            Cloudlet cl = cloudlets.get(idx);
            int bestVm = 0;
            double minCost = Double.MAX_VALUE;

            for (int j = 0; j < m; j++) {
                double execTime = cl.getLength() / vmList.get(j).getMips();
                // Enhanced load balancing penalty: penalize VMs operating above average capacity
                double imbalancePenalty = (vmList.get(j).getMips() < avgMips) ? 1.15 : 1.0;
                double cost = (vmWorkloadTime[j] + execTime) * imbalancePenalty;

                if (cost < minCost) {
                    minCost = cost;
                    bestVm = j;
                }
            }

            assignment[idx] = bestVm;
            vmWorkloadTime[bestVm] += cl.getLength() / vmList.get(bestVm).getMips();
        }
        return assignment;
    }

    // =========================================================================
    // 5. DeRALBA (Dynamic Enhanced Resource-Aware Load Balancing Algorithm)
    // =========================================================================
    public static int[] deralba(List<Cloudlet> cloudlets, List<Vm> vmList) {
        int n = cloudlets.size();
        int m = vmList.size();
        int[] assignment = new int[n];
        double[] vmFinishTime = new double[m];

        // Dynamic standard deviation thresholding across VM loads
        List<Integer> taskIndices = new ArrayList<>();
        for (int i = 0; i < n; i++) taskIndices.add(i);
        taskIndices.sort((a, b) -> Double.compare(cloudlets.get(b).getLength(), cloudlets.get(a).getLength()));

        for (int idx : taskIndices) {
            Cloudlet cl = cloudlets.get(idx);

            // Compute current load threshold (mean finish time across all VMs)
            double meanFinish = 0.0;
            for (double ft : vmFinishTime) meanFinish += ft;
            meanFinish /= m;

            int bestVm = -1;
            double minCompTime = Double.MAX_VALUE;

            // Phase 1: Try underloaded VMs (below meanFinish)
            for (int j = 0; j < m; j++) {
                if (vmFinishTime[j] <= meanFinish) {
                    double ct = vmFinishTime[j] + (cl.getLength() / vmList.get(j).getMips());
                    if (ct < minCompTime) {
                        minCompTime = ct;
                        bestVm = j;
                    }
                }
            }

            // Phase 2: If no underloaded VM qualifies, pick overall minimum
            if (bestVm < 0) {
                for (int j = 0; j < m; j++) {
                    double ct = vmFinishTime[j] + (cl.getLength() / vmList.get(j).getMips());
                    if (ct < minCompTime) {
                        minCompTime = ct;
                        bestVm = j;
                    }
                }
            }

            assignment[idx] = bestVm;
            vmFinishTime[bestVm] += cl.getLength() / vmList.get(bestVm).getMips();
        }
        return assignment;
    }
}

