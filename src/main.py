#!/usr/bin/env python3
"""
Linux Pulse - Enterprise System Performance Monitoring Suite
Main Application Entrypoint
Supports CLI ANSI Dashboard, Web Dashboard, and Headless Daemon Logging.
"""

import sys
import time
import argparse
import json
import os

from core.cpu_monitor import CPUMonitor
from core.memory_monitor import MemoryMonitor
from core.disk_monitor import DiskMonitor
from core.network_monitor import NetworkMonitor
from core.process_monitor import ProcessMonitor
from core.alert_engine import AlertEngine
from ui.cli_dashboard import CLIDashboard
from ui.web_server import run_web_server

def run_cli_mode(cpu_m, mem_m, disk_m, net_m, proc_m, alert_eng, interval):
    dashboard = CLIDashboard(cpu_m, mem_m, disk_m, net_m, proc_m, alert_eng)
    print("Initializing Linux Pulse Telemetry Engine...")
    time.sleep(0.5)
    try:
        while True:
            dashboard.render()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nExiting Linux Pulse. Goodbye!")
        sys.exit(0)

def run_daemon_mode(cpu_m, mem_m, disk_m, net_m, proc_m, alert_eng, interval, log_file):
    print(f"[*] Starting Linux Pulse Daemon mode. Logging every {interval}s to {log_file}...")
    try:
        with open(log_file, "a") as f:
            while True:
                cpu_data = cpu_m.get_metrics()
                mem_data = mem_m.get_metrics()
                disk_data = disk_m.get_metrics()
                net_data = net_m.get_metrics()
                procs = proc_m.get_top_processes(limit=5)
                alerts = alert_eng.evaluate(cpu_data, mem_data, disk_data, net_data)

                record = {
                    "timestamp": time.time(),
                    "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "cpu_overall_pct": cpu_data["overall"]["total_pct"],
                    "mem_used_pct": mem_data["used_pct"],
                    "swap_used_pct": mem_data["swap"]["used_pct"],
                    "net_rx_kb_s": net_data["aggregate_external"]["rx_kb_s"],
                    "net_tx_kb_s": net_data["aggregate_external"]["tx_kb_s"],
                    "alerts_count": len(alerts)
                }
                f.write(json.dumps(record) + "\n")
                f.flush()
                time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[*] Daemon terminated.")
        sys.exit(0)

def export_snapshot(cpu_m, mem_m, disk_m, net_m, proc_m, alert_eng, filename):
    cpu_data = cpu_m.get_metrics()
    mem_data = mem_m.get_metrics()
    disk_data = disk_m.get_metrics()
    net_data = net_m.get_metrics()
    procs = proc_m.get_top_processes(limit=20)
    alerts = alert_eng.evaluate(cpu_data, mem_data, disk_data, net_data)

    snapshot = {
        "timestamp": time.time(),
        "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
        "cpu": cpu_data,
        "memory": mem_data,
        "disk": disk_data,
        "network": net_data,
        "processes": procs,
        "alerts": alerts
    }

    with open(filename, "w") as f:
        json.dump(snapshot, f, indent=2)
    print(f"[+] Performance snapshot exported successfully to: {filename}")

def main():
    parser = argparse.ArgumentParser(
        description="Linux Pulse: Real-time System Performance Monitoring Suite for Linux"
    )
    parser.add_argument(
        "--mode",
        choices=["cli", "web", "daemon"],
        default="cli",
        help="Interface mode: 'cli' (terminal dashboard), 'web' (browser dashboard), or 'daemon' (headless logger)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="HTTP port for web dashboard mode (default: 8080)"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.5,
        help="Telemetry sampling interval in seconds (default: 1.5)"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default="system_metrics.jsonl",
        help="File path for daemon log outputs (default: system_metrics.jsonl)"
    )
    parser.add_argument(
        "--snapshot",
        type=str,
        default=None,
        help="Capture a single system performance snapshot to JSON file and exit"
    )

    args = parser.parse_args()

    # Instantiate subsystem monitors
    cpu_m = CPUMonitor()
    mem_m = MemoryMonitor()
    disk_m = DiskMonitor()
    net_m = NetworkMonitor()
    proc_m = ProcessMonitor()
    alert_eng = AlertEngine()

    if args.snapshot:
        export_snapshot(cpu_m, mem_m, disk_m, net_m, proc_m, alert_eng, args.snapshot)
        return

    if args.mode == "cli":
        run_cli_mode(cpu_m, mem_m, disk_m, net_m, proc_m, alert_eng, args.interval)
    elif args.mode == "web":
        run_web_server(args.port, cpu_m, mem_m, disk_m, net_m, proc_m, alert_eng)
    elif args.mode == "daemon":
        run_daemon_mode(cpu_m, mem_m, disk_m, net_m, proc_m, alert_eng, args.interval, args.log_file)

if __name__ == "__main__":
    main()
