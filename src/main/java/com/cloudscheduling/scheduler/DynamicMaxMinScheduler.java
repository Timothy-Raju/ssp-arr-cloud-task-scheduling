package com.cloudscheduling.scheduler;

import org.cloudsimplus.cloudlets.Cloudlet;
import org.cloudsimplus.vms.Vm;

import java.util.List;

/**
 * 1. Dynamic Max-Min Scheduler (Dy. MM)
 * Reference: Mazumder et al., ICECA 2019.
 *
 * Strategy:
 * Iteratively computes the minimum completion time across all VMs for each unassigned task,
 * then selects the task with the maximum of these minimum completion times (worst-case job),
 * and assigns it to its optimal VM. This avoids short-job starvation while ensuring long jobs
 * get scheduled on high-capacity VMs early.
 */
public class DynamicMaxMinScheduler implements GlobalScheduler {

    @Override
    public String getName() {
        return "Dy. MM";
    }

    @Override
    public int[] schedule(List<Cloudlet> cloudlets, List<Vm> vmList) {
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
}
