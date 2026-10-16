package com.cloudscheduling.scheduler;

import org.cloudsimplus.cloudlets.Cloudlet;
import org.cloudsimplus.vms.Vm;

import java.util.ArrayList;
import java.util.List;

/**
 * 4. PSSELB - Priority-Based Static Scheduling with Enhanced Load Balancing
 * Reference: Alaei & Safi-Esfahani, J. Supercomput. 2018.
 *
 * Strategy:
 * Builds upon PSSLB by adding dynamic thresholding and load overflow protection. When a target
 * VM's cumulative workload exceeds an imbalance threshold (1.20x cluster mean finish time),
 * tasks dynamically overflow to the least-loaded alternate VM across adjacent performance tiers,
 * preventing capacity hotspots on peak VMs.
 */
public class PSSELBScheduler implements GlobalScheduler {

    private static final double OVERLOAD_FACTOR = 1.20;

    @Override
    public String getName() {
        return "PSSELB";
    }

    @Override
    public int[] schedule(List<Cloudlet> cloudlets, List<Vm> vmList) {
        int n = cloudlets.size();
        int m = vmList.size();
        int[] assignment = new int[n];
        double[] vmFinishTime = new double[m];

        List<Integer> highTier = new ArrayList<>();
        List<Integer> midTier  = new ArrayList<>();
        List<Integer> lowTier  = new ArrayList<>();

        for (int j = 0; j < m; j++) {
            double mips = vmList.get(j).getMips();
            if (mips >= 3000.0) highTier.add(j);
            else if (mips >= 2000.0) midTier.add(j);
            else lowTier.add(j);
        }

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

            // Calculate current cluster mean finish time
            double meanFinish = 0.0;
            for (double ft : vmFinishTime) meanFinish += ft;
            meanFinish /= m;
            double overloadThreshold = (meanFinish > 0) ? meanFinish * OVERLOAD_FACTOR : Double.MAX_VALUE;

            List<Integer> primaryTier;
            if (len >= thresholdHigh && !highTier.isEmpty()) primaryTier = highTier;
            else if (len >= thresholdLow && !midTier.isEmpty()) primaryTier = midTier;
            else primaryTier = lowTier;

            int bestVm = -1;
            double minFinish = Double.MAX_VALUE;

            // Phase 1: Try finding non-overloaded VM in primary tier
            for (int vmIdx : primaryTier) {
                if (vmFinishTime[vmIdx] <= overloadThreshold) {
                    double finish = vmFinishTime[vmIdx] + (len / vmList.get(vmIdx).getMips());
                    if (finish < minFinish) {
                        minFinish = finish;
                        bestVm = vmIdx;
                    }
                }
            }

            // Phase 2: Dynamic Overflow to global least-loaded VM if primary tier is saturated
            if (bestVm < 0) {
                for (int j = 0; j < m; j++) {
                    double finish = vmFinishTime[j] + (len / vmList.get(j).getMips());
                    if (finish < minFinish) {
                        minFinish = finish;
                        bestVm = j;
                    }
                }
            }

            assignment[i] = bestVm;
            vmFinishTime[bestVm] += len / vmList.get(bestVm).getMips();
        }

        return assignment;
    }
}
