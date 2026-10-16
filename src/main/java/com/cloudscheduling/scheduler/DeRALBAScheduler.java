package com.cloudscheduling.scheduler;

import org.cloudsimplus.cloudlets.Cloudlet;
import org.cloudsimplus.vms.Vm;

import java.util.List;

/**
 * 5. DeRALBA - Dynamic Enhanced Resource-Aware Load Balancing Algorithm
 * Reference: Hussain et al., PeerJ Computer Science 2025.
 *
 * Strategy:
 * Uses dynamic statistical dispersion (mean mu and standard deviation sigma) across VM finish times.
 * Classifies VMs dynamically into:
 *   - Underloaded: FT_j < mu - 0.5 * sigma
 *   - Balanced:    mu - 0.5 * sigma <= FT_j <= mu + 0.5 * sigma
 *   - Overloaded:  FT_j > mu + 0.5 * sigma
 * Tasks are routed strictly to the underloaded pool first, then balanced pool, preventing variance
 * escalation across VM queue lengths.
 */
public class DeRALBAScheduler implements GlobalScheduler {

    @Override
    public String getName() {
        return "DeRALBA";
    }

    @Override
    public int[] schedule(List<Cloudlet> cloudlets, List<Vm> vmList) {
        int n = cloudlets.size();
        int m = vmList.size();
        int[] assignment = new int[n];
        double[] vmFinishTime = new double[m];

        for (int i = 0; i < n; i++) {
            Cloudlet cl = cloudlets.get(i);
            double len = cl.getLength();

            // Compute mean finish time
            double mean = 0.0;
            for (double ft : vmFinishTime) mean += ft;
            mean /= m;

            // Compute standard deviation
            double variance = 0.0;
            for (double ft : vmFinishTime) variance += (ft - mean) * (ft - mean);
            double sigma = Math.sqrt(variance / m);

            double underloadedBound = (mean > 0) ? (mean - 0.5 * sigma) : Double.MAX_VALUE;
            double balancedBound    = (mean > 0) ? (mean + 0.5 * sigma) : Double.MAX_VALUE;

            int bestVm = -1;
            double minCompTime = Double.MAX_VALUE;

            // Phase 1: Try underloaded VMs (FT < mu - 0.5 * sigma)
            for (int j = 0; j < m; j++) {
                if (vmFinishTime[j] <= underloadedBound) {
                    double ct = vmFinishTime[j] + (len / vmList.get(j).getMips());
                    if (ct < minCompTime) {
                        minCompTime = ct;
                        bestVm = j;
                    }
                }
            }

            // Phase 2: If none underloaded, try balanced VMs (FT <= mu + 0.5 * sigma)
            if (bestVm < 0) {
                for (int j = 0; j < m; j++) {
                    if (vmFinishTime[j] <= balancedBound) {
                        double ct = vmFinishTime[j] + (len / vmList.get(j).getMips());
                        if (ct < minCompTime) {
                            minCompTime = ct;
                            bestVm = j;
                        }
                    }
                }
            }

            // Phase 3: Absolute fallback
            if (bestVm < 0) {
                for (int j = 0; j < m; j++) {
                    double ct = vmFinishTime[j] + (len / vmList.get(j).getMips());
                    if (ct < minCompTime) {
                        minCompTime = ct;
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
