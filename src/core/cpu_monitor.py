"""
CPU Performance Monitor for Linux Systems
Directly parses /proc/stat, /proc/loadavg, and /proc/cpuinfo.
Includes fallback emulation for development/testing on non-Linux platforms.
"""

import os
import time
import random

class CPUMonitor:
    def __init__(self):
        self.is_linux = os.path.exists("/proc/stat")
        self.prev_stat = {}
        self.cpu_info = self._get_static_cpu_info()
        # Initialize baseline readings
        self._read_proc_stat()

    def _get_static_cpu_info(self):
        """Extract CPU model name, physical cores, logical cores, and clock speed."""
        info = {
            "model_name": "Generic x86_64 Processor",
            "cores": 4,
            "mhz": 2400.0,
            "architecture": "x86_64"
        }
        if self.is_linux and os.path.exists("/proc/cpuinfo"):
            try:
                cores = 0
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if ":" in line:
                            key, val = [x.strip() for x in line.split(":", 1)]
                            if key == "model name":
                                info["model_name"] = val
                            elif key == "cpu MHz":
                                info["mhz"] = float(val)
                            elif key == "processor":
                                cores += 1
                if cores > 0:
                    info["cores"] = cores
            except Exception:
                pass
        return info

    def _read_proc_stat(self):
        """Read /proc/stat raw tick counters (jiffies)."""
        raw = {}
        if self.is_linux:
            try:
                with open("/proc/stat", "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        if not parts:
                            continue
                        name = parts[0]
                        if name == "cpu" or (name.startswith("cpu") and name[3:].isdigit()):
                            # fields: user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice
                            vals = [int(x) for x in parts[1:11]]
                            raw[name] = vals
            except Exception:
                pass
        else:
            # Simulated jiffies for non-Linux testing
            cores = self.cpu_info["cores"]
            t = time.time()
            for c in ["cpu"] + [f"cpu{i}" for i in range(cores)]:
                user = int(t * 100 + random.randint(10, 40))
                nice = 2
                system = int(t * 30 + random.randint(5, 15))
                idle = int(t * 500 + random.randint(100, 200))
                iowait = random.randint(1, 5)
                irq = 1
                softirq = 2
                steal = 0
                raw[c] = [user, nice, system, idle, iowait, irq, softirq, steal, 0, 0]
        return raw

    def get_load_average(self):
        """Return 1-min, 5-min, 15-min load averages and running/total processes."""
        if self.is_linux and os.path.exists("/proc/loadavg"):
            try:
                with open("/proc/loadavg", "r") as f:
                    parts = f.read().strip().split()
                    return {
                        "load_1m": float(parts[0]),
                        "load_5m": float(parts[1]),
                        "load_15m": float(parts[2]),
                        "running_entities": parts[3],
                        "last_pid": int(parts[4])
                    }
            except Exception:
                pass
        return {
            "load_1m": round(random.uniform(0.4, 2.1), 2),
            "load_5m": round(random.uniform(0.5, 1.8), 2),
            "load_15m": round(random.uniform(0.6, 1.5), 2),
            "running_entities": "2/342",
            "last_pid": 12890
        }

    def get_metrics(self):
        """
        Calculate percentage utilization for overall CPU and individual cores
        by comparing differential jiffies over elapsed time.
        """
        curr_stat = self._read_proc_stat()
        results = {
            "overall": {
                "total_pct": 0.0,
                "user_pct": 0.0,
                "system_pct": 0.0,
                "idle_pct": 0.0,
                "iowait_pct": 0.0,
                "irq_pct": 0.0
            },
            "per_core": {},
            "load_avg": self.get_load_average(),
            "cpu_info": self.cpu_info,
            "timestamp": time.time()
        }

        if not self.prev_stat:
            self.prev_stat = curr_stat
            time.sleep(0.05)
            curr_stat = self._read_proc_stat()

        for cpu_name, curr_vals in curr_stat.items():
            if cpu_name in self.prev_stat:
                prev_vals = self.prev_stat[cpu_name]
                # Diff jiffies
                diffs = [c - p for c, p in zip(curr_vals, prev_vals)]
                # user(0), nice(1), system(2), idle(3), iowait(4), irq(5), softirq(6), steal(7)
                total_delta = sum(diffs[:8])
                if total_delta > 0:
                    user_delta = diffs[0] + diffs[1]
                    system_delta = diffs[2]
                    idle_delta = diffs[3]
                    iowait_delta = diffs[4]
                    irq_delta = diffs[5] + diffs[6]
                    steal_delta = diffs[7]

                    active_delta = total_delta - idle_delta - iowait_delta
                    active_pct = max(0.0, min(100.0, (active_delta / total_delta) * 100.0))
                    user_pct = max(0.0, min(100.0, (user_delta / total_delta) * 100.0))
                    sys_pct = max(0.0, min(100.0, (system_delta / total_delta) * 100.0))
                    idle_pct = max(0.0, min(100.0, (idle_delta / total_delta) * 100.0))
                    iowait_pct = max(0.0, min(100.0, (iowait_delta / total_delta) * 100.0))
                    irq_pct = max(0.0, min(100.0, (irq_delta / total_delta) * 100.0))

                    metrics = {
                        "total_pct": round(active_pct, 2),
                        "user_pct": round(user_pct, 2),
                        "system_pct": round(sys_pct, 2),
                        "idle_pct": round(idle_pct, 2),
                        "iowait_pct": round(iowait_pct, 2),
                        "irq_pct": round(irq_pct, 2)
                    }

                    if cpu_name == "cpu":
                        results["overall"] = metrics
                    else:
                        results["per_core"][cpu_name] = metrics

        self.prev_stat = curr_stat
        return results
