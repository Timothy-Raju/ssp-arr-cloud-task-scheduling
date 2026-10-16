package com.cloudscheduling.scheduler;

import org.cloudsimplus.cloudlets.Cloudlet;
import org.cloudsimplus.vms.Vm;

import java.util.List;

/**
 * Common contract for all Tier-1 Global Cloud Schedulers (Broker-level task dispatchers).
 */
public interface GlobalScheduler {
    String getName();
    int[] schedule(List<Cloudlet> cloudlets, List<Vm> vmList);
}
