"""
Process Table & Resource Profiler for Linux Systems
Directly traverses /proc/[pid] filesystem.
Parses /proc/[pid]/stat, /proc/[pid]/status, and /proc/[pid]/cmdline.
Computes real-time per-process CPU%, RSS Memory, Virtual Memory, and Thread count.
"""

import os
import time
import random

class ProcessMonitor:
    def __init__(self):
        self.is_linux = os.path.exists("/proc")
        self.prev_proc_times = {} # pid -> (utime + stime, timestamp)
        self.total_memory_kb = self._get_total_memory()

    def _get_total_memory(self):
        if self.is_linux and os.path.exists("/proc/meminfo"):
            try:
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            return int(line.split()[1])
            except Exception:
                pass
        return 16 * 1024 * 1024 # 16 GB fallback

    def _parse_proc_stat(self, pid):
        """
        Parse /proc/[pid]/stat.
        Fields: 0:pid, 1:(comm), 2:state, 3:ppid, 13:utime, 14:stime, 19:num_threads
        """
        try:
            with open(f"/proc/{pid}/stat", "r") as f:
                content = f.read()
                # Command name is enclosed in parentheses and may contain spaces
                rparen = content.rfind(")")
                if rparen == -1:
                    return None
                comm = content[content.find("(") + 1:rparen]
                rest = content[rparen + 2:].split()

                state = rest[0]
                ppid = int(rest[1])
                utime = int(rest[11])
                stime = int(rest[12])
                num_threads = int(rest[17])

                return {
                    "comm": comm,
                    "state": state,
                    "ppid": ppid,
                    "utime": utime,
                    "stime": stime,
                    "num_threads": num_threads
                }
        except Exception:
            return None

    def _parse_proc_status(self, pid):
        """Parse /proc/[pid]/status for RSS memory and UID."""
        res = {"rss_kb": 0, "vms_kb": 0, "uid": 0}
        try:
            with open(f"/proc/{pid}/status", "r") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        res["rss_kb"] = int(line.split()[1])
                    elif line.startswith("VmSize:"):
                        res["vms_kb"] = int(line.split()[1])
                    elif line.startswith("Uid:"):
                        res["uid"] = int(line.split()[1])
        except Exception:
            pass
        return res

    def get_top_processes(self, limit=15, sort_by="cpu"):
        """
        Scan all running processes, calculate CPU and memory consumption,
        and return the top consumers.
        """
        processes = []
        curr_time = time.time()
        new_proc_times = {}

        if self.is_linux:
            try:
                pids = [int(p) for p in os.listdir("/proc") if p.isdigit()]
            except Exception:
                pids = []

            # Clock ticks per second (usually 100 on Linux)
            clk_tck = 100.0
            try:
                clk_tck = float(os.sysconf("SC_CLK_TCK"))
            except Exception:
                pass

            for pid in pids:
                stat_data = self._parse_proc_stat(pid)
                if not stat_data:
                    continue

                status_data = self._parse_proc_status(pid)
                total_ticks = stat_data["utime"] + stat_data["stime"]
                new_proc_times[pid] = (total_ticks, curr_time)

                # CPU % calculation
                cpu_pct = 0.0
                if pid in self.prev_proc_times:
                    prev_ticks, prev_t = self.prev_proc_times[pid]
                    delta_ticks = max(0, total_ticks - prev_ticks)
                    delta_sec = max(0.001, curr_time - prev_t)
                    # (delta_ticks / clk_tck) / delta_sec * 100
                    cpu_pct = round(((delta_ticks / clk_tck) / delta_sec) * 100.0, 1)

                rss_mb = round(status_data["rss_kb"] / 1024.0, 1)
                vms_mb = round(status_data["vms_kb"] / 1024.0, 1)
                mem_pct = round((status_data["rss_kb"] / self.total_memory_kb) * 100.0, 2)

                state_desc = {
                    "R": "Running",
                    "S": "Sleeping",
                    "D": "Disk Sleep",
                    "Z": "Zombie",
                    "T": "Stopped"
                }.get(stat_data["state"], stat_data["state"])

                processes.append({
                    "pid": pid,
                    "ppid": stat_data["ppid"],
                    "name": stat_data["comm"],
                    "state": state_desc,
                    "cpu_pct": cpu_pct,
                    "mem_pct": mem_pct,
                    "rss_mb": rss_mb,
                    "vms_mb": vms_mb,
                    "threads": stat_data["num_threads"]
                })

            self.prev_proc_times = new_proc_times
        else:
            # Emulated standard process list for testing
            mock_procs = [
                (1, "systemd", "Sleeping", 0.0, 28.4, 1),
                (450, "kswapd0", "Sleeping", 0.1, 0.0, 1),
                (1024, "dockerd", "Sleeping", 1.8, 142.5, 18),
                (1280, "postgres", "Sleeping", 3.2, 420.1, 8),
                (1420, "nginx", "Sleeping", 0.5, 45.2, 4),
                (2190, "python3", "Running", 14.6, 210.8, 4),
                (3100, "mysqld", "Sleeping", 4.1, 610.4, 24),
                (4210, "node", "Running", 8.9, 320.0, 11),
                (5512, "bash", "Sleeping", 0.0, 12.1, 1),
                (6011, "redis-server", "Sleeping", 1.1, 85.3, 5),
                (7821, "sysmon_agent", "Running", 0.6, 24.5, 3),
                (8920, "prometheus", "Sleeping", 2.4, 185.0, 10),
                (9340, "grafana-server", "Sleeping", 1.5, 115.6, 7),
                (10120, "sshd", "Sleeping", 0.0, 9.8, 1),
                (11420, "journald", "Sleeping", 0.2, 34.0, 1)
            ]
            for pid, name, st, cpu, rss, th in mock_procs:
                jitter = random.uniform(-0.3, 0.3)
                final_cpu = max(0.0, round(cpu + jitter, 1))
                mem_pct = round((rss * 1024 / self.total_memory_kb) * 100.0, 2)
                processes.append({
                    "pid": pid,
                    "ppid": 1,
                    "name": name,
                    "state": st,
                    "cpu_pct": final_cpu,
                    "mem_pct": mem_pct,
                    "rss_mb": rss,
                    "vms_mb": round(rss * 2.5, 1),
                    "threads": th
                })

        # Sort
        sort_key = "cpu_pct" if sort_by == "cpu" else "mem_pct"
        processes.sort(key=lambda x: x[sort_key], reverse=True)
        return processes[:limit]
