package com.cloudscheduling.scheduler;

import org.cloudsimplus.cloudlets.Cloudlet;
import org.cloudsimplus.vms.Vm;

import java.util.ArrayList;
import java.util.List;

/**
 * 3. PSSLB - Priority-Based Static Scheduling Load Balancing
 * Reference: Alaei & Safi-Esfahani, J. Supercomput. 2018.
 *
 * Strategy:
 * Categorizes tasks into static priority tiers (High, Medium, Low) based on workload burst length
 * and maps them to corresponding heterogeneous VM performance tiers (Tier 1: High MIPS >= 3000,
 * Tier 2: Mid MIPS 2000-2800, Tier 3: Standard MIPS < 2000). Within each tier, tasks are assigned
 * to minimize the cumulative finish time, preventing high-priority starvation.
 */
public class PSSLBScheduler implements GlobalScheduler {

    @Override
    public String getName() {
        return "PSSLB";
    }

    @Override
    public int[] schedule(List<Cloudlet> cloudlets, List<Vm> vmList) {
        int n = cloudlets.size();
        int m = vmList.size();
        int[] assignment = new int[n];
        double[] vmReadyTime = new double[m];

        // Partition VM indices into 3 capability tiers
        List<Integer> highTierVms = new ArrayList<>();
        List<Integer> midTierVms = new ArrayList<>();
        List<Integer> lowTierVms = new ArrayList<>();

        for (int j = 0; j < m; j++) {
            double mips = vmList.get(j).getMips();
            if (mips >= 3000.0) {
                highTierVms.add(j);
            } else if (mips >= 2000.0) {
                midTierVms.add(j);
            } else {
                lowTierVms.add(j);
            }
        }

        // Determine dataset burst boundaries for 3 task tiers
        double maxLen = 0.0, minLen = Double.MAX_VALUE;
        for (Cloudlet cl : cloudlets) {
            maxLen = Math.max(maxLen, cl.getLength());
            minLen = Math.min(minLen, cl.getLength());
        }
        double thresholdLow = minLen + (maxLen - minLen) * 0.33;
        double thresholdHigh = minLen + (maxLen - minLen) * 0.67;

        for (int i = 0; i < n; i++) {
            Cloudlet cl = cloudlets.get(i);
            double len = cl.getLength();

            List<Integer> candidateVms;
            if (len >= thresholdHigh && !highTierVms.isEmpty()) {
                candidateVms = highTierVms;
            } else if (len >= thresholdLow && !midTierVms.isEmpty()) {
                candidateVms = midTierVms;
            } else if (!lowTierVms.isEmpty()) {
                candidateVms = lowTierVms;
            } else {
                candidateVms = new ArrayList<>();
                for (int j = 0; j < m; j++) candidateVms.add(j);
            }

            int bestVm = candidateVms.get(0);
            double minFinish = Double.MAX_VALUE;

            for (int vmIdx : candidateVms) {
                double finish = vmReadyTime[vmIdx] + (len / vmList.get(vmIdx).getMips());
                if (finish < minFinish) {
                    minFinish = finish;
                    bestVm = vmIdx;
                }
            }

            assignment[i] = bestVm;
            vmReadyTime[bestVm] += len / vmList.get(bestVm).getMips();
        }

        return assignment;
    }
}
