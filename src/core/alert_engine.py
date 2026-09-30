"""
Alert and Health Assessment Engine
Evaluates real-time metrics against configurable thresholds.
Generates WARNING and CRITICAL incident events.
"""

import time

class AlertEngine:
    def __init__(self, thresholds=None):
        self.thresholds = thresholds or {
            "cpu_warn": 75.0,
            "cpu_crit": 90.0,
            "mem_warn": 80.0,
            "mem_crit": 92.0,
            "disk_warn": 85.0,
            "disk_crit": 95.0,
            "swap_warn": 50.0,
            "swap_crit": 80.0
        }
        self.active_alerts = []
        self.alert_history = []

    def evaluate(self, cpu_metrics, mem_metrics, disk_metrics, net_metrics):
        """Evaluate current system health against defined thresholds."""
        current_alerts = []
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        # 1. CPU Checks
        cpu_usage = cpu_metrics.get("overall", {}).get("total_pct", 0.0)
        if cpu_usage >= self.thresholds["cpu_crit"]:
            current_alerts.append({
                "severity": "CRITICAL",
                "subsystem": "CPU",
                "message": f"CPU utilization critically high at {cpu_usage}% (threshold: {self.thresholds['cpu_crit']}%)",
                "timestamp": now
            })
        elif cpu_usage >= self.thresholds["cpu_warn"]:
            current_alerts.append({
                "severity": "WARNING",
                "subsystem": "CPU",
                "message": f"CPU utilization elevated at {cpu_usage}% (threshold: {self.thresholds['cpu_warn']}%)",
                "timestamp": now
            })

        # 2. Memory Checks
        mem_usage = mem_metrics.get("used_pct", 0.0)
        if mem_usage >= self.thresholds["mem_crit"]:
            current_alerts.append({
                "severity": "CRITICAL",
                "subsystem": "Memory",
                "message": f"RAM consumption critical: {mem_usage}% used (threshold: {self.thresholds['mem_crit']}%)",
                "timestamp": now
            })
        elif mem_usage >= self.thresholds["mem_warn"]:
            current_alerts.append({
                "severity": "WARNING",
                "subsystem": "Memory",
                "message": f"RAM consumption elevated: {mem_usage}% used (threshold: {self.thresholds['mem_warn']}%)",
                "timestamp": now
            })

        # 3. Swap Checks
        swap_pct = mem_metrics.get("swap", {}).get("used_pct", 0.0)
        if swap_pct >= self.thresholds["swap_crit"]:
            current_alerts.append({
                "severity": "CRITICAL",
                "subsystem": "Swap",
                "message": f"High swap thrashing detected: {swap_pct}% swap used",
                "timestamp": now
            })

        # 4. Storage Checks
        for part in disk_metrics.get("partitions", []):
            pct = part.get("used_pct", 0.0)
            mnt = part.get("mountpoint", "unknown")
            if pct >= self.thresholds["disk_crit"]:
                current_alerts.append({
                    "severity": "CRITICAL",
                    "subsystem": "Disk",
                    "message": f"Partition '{mnt}' almost full: {pct}% used",
                    "timestamp": now
                })
            elif pct >= self.thresholds["disk_warn"]:
                current_alerts.append({
                    "severity": "WARNING",
                    "subsystem": "Disk",
                    "message": f"Partition '{mnt}' high usage: {pct}% used",
                    "timestamp": now
                })

        # 5. Network Drop Checks
        for iface, if_data in net_metrics.get("interfaces", {}).items():
            if iface != "lo" and if_data.get("rx_drop", 0) > 100:
                current_alerts.append({
                    "severity": "WARNING",
                    "subsystem": "Network",
                    "message": f"Interface {iface} reporting packet drops ({if_data['rx_drop']} drops)",
                    "timestamp": now
                })

        self.active_alerts = current_alerts
        for a in current_alerts:
            # Keep unique recent history
            if not any(h["message"] == a["message"] and h["timestamp"] == a["timestamp"] for h in self.alert_history):
                self.alert_history.append(a)
                if len(self.alert_history) > 100:
                    self.alert_history.pop(0)

        return current_alerts
