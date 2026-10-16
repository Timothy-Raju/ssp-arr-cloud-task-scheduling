package com.cloudscheduling.scheduler;

import org.cloudsimplus.cloudlets.Cloudlet;
import org.cloudsimplus.vms.Vm;

import java.util.List;

/**
 * 2. DRALBA - Dynamic Resource-Aware Load Balancing Algorithm
 * Reference: Nabi, Ibrahim, & Jimenez, IEEE Access 2021.
 *
 * Strategy:
 * Evaluates multi-dimensional resource metrics (CPU computing capacity, RAM consumption,
 * and Bandwidth utilization) dynamically in arrival sequence. It avoids bottlenecks by calculating
 * a multi-resource load index for each VM and routing incoming tasks to the VM with the lowest
 * projected composite load.
 */
public class DRALBAScheduler implements GlobalScheduler {

    private static final double W_CPU = 0.60;
    private static final double W_RAM = 0.25;
    private static final double W_BW  = 0.15;

    @Override
    public String getName() {
        return "DRALBA";
    }

    @Override
    public int[] schedule(List<Cloudlet> cloudlets, List<Vm> vmList) {
        int n = cloudlets.size();
        int m = vmList.size();
        int[] assignment = new int[n];

        double[] vmCpuBusyTime = new double[m];
        double[] vmAllocatedRam = new double[m];
        double[] vmAllocatedBw = new double[m];

        // Process in dynamic arrival sequence
        for (int i = 0; i < n; i++) {
            Cloudlet cl = cloudlets.get(i);
            int bestVm = 0;
            double minCompositeScore = Double.MAX_VALUE;

            for (int j = 0; j < m; j++) {
                Vm vm = vmList.get(j);
                double execTime = cl.getLength() / vm.getMips();
                double projCpuTime = vmCpuBusyTime[j] + execTime;

                // Multi-resource normalized indices
                double cpuIndex = projCpuTime / (vm.getMips() / 1000.0);
                double ramIndex = (vmAllocatedRam[j] + 1.0) / (vm.getRam().getCapacity() > 0 ? vm.getRam().getCapacity() : 8192);
                double bwIndex  = (vmAllocatedBw[j] + 1.0) / (vm.getBw().getCapacity() > 0 ? vm.getBw().getCapacity() : 20000);

                double compositeScore = (W_CPU * cpuIndex) + (W_RAM * ramIndex * 100.0) + (W_BW * bwIndex * 100.0);

                if (compositeScore < minCompositeScore) {
                    minCompositeScore = compositeScore;
                    bestVm = j;
                }
            }

            assignment[i] = bestVm;
            Vm chosen = vmList.get(bestVm);
            vmCpuBusyTime[bestVm] += cl.getLength() / chosen.getMips();
            vmAllocatedRam[bestVm] += 100.0; // Dynamic RAM footprint
            vmAllocatedBw[bestVm]  += 50.0;  // Dynamic BW footprint
        }

        return assignment;
    }
}
