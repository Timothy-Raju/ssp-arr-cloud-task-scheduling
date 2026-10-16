package com.cloudscheduling.scheduler;

import org.cloudsimplus.cloudlets.Cloudlet;
import org.cloudsimplus.vms.Vm;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/**
 * Facade and Factory for the 5 Tier-1 Global Cloud Schedulers:
 *
 * 1. Dynamic Max-Min (Dy. MM) [Mazumder et al., ICECA 2019] -> DynamicMaxMinScheduler
 * 2. DRALBA [Nabi et al., IEEE Access 2021]                   -> DRALBAScheduler
 * 3. PSSLB [Alaei & Safi-Esfahani, 2018]                     -> PSSLBScheduler
 * 4. PSSELB [Alaei & Safi-Esfahani, 2018]                    -> PSSELBScheduler
 * 5. DeRALBA [Hussain et al., PeerJ 2025]                    -> DeRALBAScheduler
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

    private static final Map<Policy, GlobalScheduler> REGISTRY = new EnumMap<>(Policy.class);

    static {
        REGISTRY.put(Policy.DYNAMIC_MAX_MIN, new DynamicMaxMinScheduler());
        REGISTRY.put(Policy.DRALBA,          new DRALBAScheduler());
        REGISTRY.put(Policy.PSSLB,           new PSSLBScheduler());
        REGISTRY.put(Policy.PSSELB,          new PSSELBScheduler());
        REGISTRY.put(Policy.DERALBA,         new DeRALBAScheduler());
    }

    public static GlobalScheduler get(Policy policy) {
        return REGISTRY.getOrDefault(policy, REGISTRY.get(Policy.DYNAMIC_MAX_MIN));
    }

    /**
     * Dispatcher method to compute task-to-VM assignments for a given global scheduler.
     */
    public static int[] assign(Policy policy, List<Cloudlet> cloudlets, List<Vm> vmList) {
        return get(policy).schedule(cloudlets, vmList);
    }

    // Direct helper delegators for legacy backward compatibility
    public static int[] dynamicMaxMin(List<Cloudlet> cloudlets, List<Vm> vmList) {
        return REGISTRY.get(Policy.DYNAMIC_MAX_MIN).schedule(cloudlets, vmList);
    }

    public static int[] dralba(List<Cloudlet> cloudlets, List<Vm> vmList) {
        return REGISTRY.get(Policy.DRALBA).schedule(cloudlets, vmList);
    }

    public static int[] psslb(List<Cloudlet> cloudlets, List<Vm> vmList) {
        return REGISTRY.get(Policy.PSSLB).schedule(cloudlets, vmList);
    }

    public static int[] psselb(List<Cloudlet> cloudlets, List<Vm> vmList) {
        return REGISTRY.get(Policy.PSSELB).schedule(cloudlets, vmList);
    }

    public static int[] deralba(List<Cloudlet> cloudlets, List<Vm> vmList) {
        return REGISTRY.get(Policy.DERALBA).schedule(cloudlets, vmList);
    }
}
