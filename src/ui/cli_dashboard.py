"""
Terminal ANSI CLI Dashboard for Linux Performance Monitoring
Renders high-refresh interactive gauges, metrics tables, and top process rankings.
"""

import os
import sys
import time

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BG_BLUE = "\033[44m"

def make_bar(percent, width=25):
    """Render a graphical ASCII progress gauge."""
    clamped = max(0.0, min(100.0, percent))
    filled = int(round((clamped / 100.0) * width))
    empty = width - filled
    
    if clamped < 60:
        color = GREEN
    elif clamped < 85:
        color = YELLOW
    else:
        color = RED

    bar_str = f"{color}{'█' * filled}{DIM}{'░' * empty}{RESET}"
    return f"[{bar_str}] {clamped:5.1f}%"

def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

class CLIDashboard:
    def __init__(self, cpu_mon, mem_mon, disk_mon, net_mon, proc_mon, alert_engine):
        self.cpu = cpu_mon
        self.mem = mem_mon
        self.disk = disk_mon
        self.net = net_mon
        self.proc = proc_mon
        self.alert = alert_engine

    def render(self):
        clear_screen()
        cpu_m = self.cpu.get_metrics()
        mem_m = self.mem.get_metrics()
        disk_m = self.disk.get_metrics()
        net_m = self.net.get_metrics()
        top_procs = self.proc.get_top_processes(limit=8, sort_by="cpu")
        alerts = self.alert.evaluate(cpu_m, mem_m, disk_m, net_m)

        lines = []
        term_width = 80
        header_title = " LINUX SYSTEM PERFORMANCE MONITOR (PULSE) "
        lines.append(f"{BOLD}{BG_BLUE}{WHITE}{header_title.center(term_width)}{RESET}")
        
        load = cpu_m["load_avg"]
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"{CYAN}Time:{RESET} {ts}  |  {CYAN}Load Avg (1/5/15m):{RESET} {load['load_1m']:.2f}, {load['load_5m']:.2f}, {load['load_15m']:.2f}  |  {CYAN}Tasks:{RESET} {load['running_entities']}")
        lines.append(f"{DIM}{'─' * term_width}{RESET}")

        # CPU Section
        overall_cpu = cpu_m["overall"]["total_pct"]
        lines.append(f"{BOLD}CPU UTILIZATION{RESET}  {make_bar(overall_cpu, 30)}   (User: {cpu_m['overall']['user_pct']}% | Sys: {cpu_m['overall']['system_pct']}% | IOwait: {cpu_m['overall']['iowait_pct']}%)")
        cores = cpu_m["per_core"]
        core_line = "  "
        for idx, (core_name, c_data) in enumerate(cores.items()):
            core_line += f"{core_name}: {make_bar(c_data['total_pct'], 10)}   "
            if (idx + 1) % 2 == 0:
                lines.append(core_line)
                core_line = "  "
        if core_line.strip():
            lines.append(core_line)

        lines.append(f"{DIM}{'─' * term_width}{RESET}")

        # Memory Section
        lines.append(f"{BOLD}MEMORY & SWAP{RESET}")
        ram_bar = make_bar(mem_m["used_pct"], 30)
        lines.append(f"  Physical RAM : {ram_bar}  [{mem_m['used_mb']:.0f} MB / {mem_m['total_mb']:.0f} MB]  (Avail: {mem_m['available_mb']:.0f} MB, Buff/Cache: {mem_m['cached_mb']:.0f} MB)")
        swap_bar = make_bar(mem_m["swap"]["used_pct"], 30)
        lines.append(f"  Swap Space   : {swap_bar}  [{mem_m['swap']['used_mb']:.0f} MB / {mem_m['swap']['total_mb']:.0f} MB]")

        lines.append(f"{DIM}{'─' * term_width}{RESET}")

        # Storage & Network Section in 2 columns
        lines.append(f"{BOLD}STORAGE PARTITIONS & I/O{RESET} {' ' * 16} {BOLD}NETWORK ACTIVITY{RESET}")
        parts = disk_m["partitions"]
        p_str = ""
        if parts:
            p = parts[0]
            p_str = f"{p['mountpoint']}: {p['used_gb']:.1f}/{p['total_gb']:.1f} GB ({p['used_pct']}%)"
        
        io_rates = disk_m["io_rates"]
        io_str = "No I/O"
        if io_rates:
            dev = list(io_rates.keys())[0]
            io = io_rates[dev]
            io_str = f"{dev}: R:{io['read_kb_s']} KB/s W:{io['write_kb_s']} KB/s"

        net_ext = net_m["aggregate_external"]
        net_str = f"RX: {net_ext['rx_kb_s']} KB/s | TX: {net_ext['tx_kb_s']} KB/s"
        socks = net_m["sockets"]
        sock_str = f"TCP Sockets: {socks['ESTABLISHED']} Estab, {socks['LISTEN']} Listen"

        lines.append(f"  Mount: {p_str:<32}  Bandwidth: {net_str}")
        lines.append(f"  Rates: {io_str:<32}  Sockets  : {sock_str}")

        lines.append(f"{DIM}{'─' * term_width}{RESET}")

        # Top Processes Table
        lines.append(f"{BOLD}TOP CONSUMER PROCESSES{RESET}")
        lines.append(f"  {'PID':<7} {'NAME':<18} {'STATE':<11} {'CPU %':<8} {'MEM %':<8} {'RSS (MB)':<10} {'THREADS':<8}")
        for p in top_procs:
            lines.append(f"  {p['pid']:<7} {p['name'][:16]:<18} {p['state']:<11} {p['cpu_pct']:<8.1f} {p['mem_pct']:<8.1f} {p['rss_mb']:<10.1f} {p['threads']:<8}")

        # Active Alerts Section
        if alerts:
            lines.append(f"{DIM}{'─' * term_width}{RESET}")
            lines.append(f"{BOLD}{RED}ACTIVE SYSTEM ALERTS ({len(alerts)}){RESET}")
            for a in alerts:
                sev_color = RED if a["severity"] == "CRITICAL" else YELLOW
                lines.append(f"  {sev_color}[{a['severity']}]{RESET} {BOLD}{a['subsystem']}:{RESET} {a['message']} ({a['timestamp']})")

        lines.append(f"{DIM}{'─' * term_width}{RESET}")
        lines.append(f"{DIM}Press Ctrl+C to exit monitoring.{RESET}")

        print("\n".join(lines))
