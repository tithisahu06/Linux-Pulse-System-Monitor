# Linux Pulse - Enterprise System Performance Monitoring Suite
## Operating System Experiential Learning Case Study Project (CS-302)

[![Platform: Linux](https://img.shields.io/badge/Platform-Linux%20%2F%20WSL-blue.svg)](https://www.kernel.org)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://python.org)
[![Report: 47 Pages](https://img.shields.io/badge/Academic%20Report-47%20Pages%20DOCX-purple.svg)](output/Linux_System_Performance_Monitoring_Report.docx)

---

## 📌 Project Overview
**Linux Pulse** is a lightweight, real-time, non-invasive system performance monitoring suite engineered natively for Linux operating systems. Developed as an academic experiential learning case study, the application directly introspects the Linux Virtual Filesystem (`/proc` and `/sys`) to capture, calculate, correlate, and visualize performance telemetry across five critical OS subsystems:

1. **CPU Utilization & Scheduling**: Multi-core percentage utilization, user/system/idle/iowait breakdown via `/proc/stat`, and run-queue load averages via `/proc/loadavg`.
2. **Memory & Virtual Memory**: True available vs free RAM, page cache retention, filesystem buffers, slab reclaimable structures, dirty writeback queues, and swap thrashing via `/proc/meminfo` and `/proc/vmstat`.
3. **Storage Space & Block Device I/O**: Filesystem partition usage and inode exhaustion via `statvfs`, combined with real-time read/write throughput (KB/s, MB/s) and IOPS via `/proc/diskstats`.
4. **Network Activity & Sockets**: Ingress (RX) and egress (TX) bandwidth, packet transmission rates (PPS), hardware ring drops, and TCP socket connection state distribution via `/proc/net/dev` and `/proc/net/tcp`.
5. **Process Table & Resource Profiler**: Live traversal of `/proc/[pid]`, calculating per-process CPU%, resident set size (RSS), virtual memory (VMS), and thread counts.

The suite includes an **Intelligent Alert Engine**, an **Interactive ANSI CLI Dashboard**, a **Real-Time Glassmorphism Web Dashboard** with Chart.js line charts, a standalone **Native Linux Bash Script**, and a **Systemd Service Descriptor** with cgroup sandboxing.

---

## 📁 Repository Directory Structure

```
OS CASE STUDY/
├── diagrams/                                  # 11 High-Resolution 300-DPI Architectural & Benchmark Figures
│   ├── fig1_linux_kernel_proc.png             # Linux Kernel & /proc Telemetry Architecture
│   ├── fig2_sysmon_architecture.png           # Modular Monitoring Suite Architecture
│   ├── fig3_cpu_jiffies_flowchart.png         # Mathematical Differential Jiffies Flowchart
│   ├── fig4_memory_hierarchy.png              # Linux Physical & Page Cache Allocation Topology
│   ├── fig5_storage_io_pipeline.png           # Storage Block I/O Layer & /proc/diskstats
│   ├── fig6_network_packet_flow.png           # Network Stack Packet Lifecycle & Hooks
│   ├── fig7_benchmark_cpu.png                 # Benchmark 1: CPU Saturation under Stress
│   ├── fig8_benchmark_memory.png              # Benchmark 2: Memory & Page Cache Dynamics
│   ├── fig9_benchmark_disk.png                # Benchmark 3: Storage IOPS & Block Size Scaling
│   ├── fig10_benchmark_network.png            # Benchmark 4: Network Saturation & Drops
│   └── fig11_daemon_overhead.png              # 24-Hour Continuous Monitoring Overhead Profile
├── output/                                    # Generated Formal Submissions
│   ├── Linux_System_Performance_Monitoring_Report.docx  # 47-Page Academic Word Document Report
│   ├── Linux_System_Performance_Monitoring_Report.pdf   # Publication-Quality PDF Document
│   └── test_snap.json                         # Telemetry Snapshot Export Verification
├── src/                                       # Application Source Code
│   ├── core/                                  # Telemetry Collector Modules
│   │   ├── cpu_monitor.py                     # CPU & Load Average Collector
│   │   ├── memory_monitor.py                  # RAM, Page Cache, and Swap Collector
│   │   ├── disk_monitor.py                    # Partition & Block I/O Collector
│   │   ├── network_monitor.py                 # Network Bandwidth & Socket Collector
│   │   ├── process_monitor.py                 # /proc/[pid] Process Table Traverser
│   │   └── alert_engine.py                    # Multi-Tier Health Assessment Engine
│   ├── ui/                                    # Presentation & Exporter Layer
│   │   ├── cli_dashboard.py                   # High-Density ANSI Console Dashboard
│   │   └── web_server.py                      # Embedded HTTP Telemetry Server & REST API
│   ├── web_static/                            # Frontend Web Assets
│   │   └── index.html                         # Modern Glassmorphism Web Dashboard with Chart.js
│   ├── scripts/                               # Native Shell & Testing Scripts
│   │   ├── monitor.sh                         # Standalone Pure Bash Monitoring Script
│   │   └── stress_benchmark.sh                # Synthetic Workload Generator (CPU/Mem/Disk/Net)
│   ├── systemd/                               # Enterprise Daemon Sandboxing
│   │   └── linux-sysmon.service               # Systemd Unit File with cgroup Limits
│   └── main.py                                # Main CLI Entrypoint Orchestrator
├── build_full_report.py                       # Automated 30+ Page Word Report Compiler
├── generate_diagrams.py                       # Automated Technical Figure Generator
└── report_builder_lib.py                      # Report Styling & Academic Formatter Library
```

---

## 🚀 Quickstart & Execution Instructions

### 1. Interactive Terminal ANSI Dashboard (CLI Mode)
Launches the high-refresh terminal console with graphical ASCII gauge bars, multi-core metrics, storage/network tables, top process rankings, and live alerts:
```bash
python src/main.py --mode cli --interval 1.5
```

### 2. Real-Time Web Dashboard (Web Mode)
Starts the embedded lightweight HTTP server and REST API:
```bash
python src/main.py --mode web --port 8080
```
Open your web browser and navigate to:
👉 **`http://localhost:8080/`**
- REST API endpoint: `http://localhost:8080/api/metrics`
- Process API endpoint: `http://localhost:8080/api/processes`
- Alerts API endpoint: `http://localhost:8080/api/alerts`

### 3. Headless Daemon Logger Mode
Runs silently in the background, logging JSON Lines (JSONL) records at regular intervals:
```bash
python src/main.py --mode daemon --interval 2.0 --log-file system_metrics.jsonl
```

### 4. Single-Shot Performance Snapshot Export
Dumps a comprehensive instantaneous system snapshot to JSON and exits:
```bash
python src/main.py --snapshot system_snapshot.json
```

### 5. Native Linux Bash Monitoring Script
For minimal environments without Python:
```bash
chmod +x src/scripts/monitor.sh
./src/scripts/monitor.sh
```

### 6. Synthetic Stress Benchmark Generator
In a secondary terminal window, inject controlled workloads to verify telemetry:
```bash
chmod +x src/scripts/stress_benchmark.sh
./src/scripts/stress_benchmark.sh cpu     # Stress logical cores for 15s
./src/scripts/stress_benchmark.sh memory  # Allocate 1.5 GB in RAM
./src/scripts/stress_benchmark.sh disk    # Direct I/O write stress (dd)
./src/scripts/stress_benchmark.sh all     # Run full stress suite
```

---

## 📊 Formal Academic Report Details

The primary deliverable for this experiential learning project is located in:
📄 **`output/Linux_System_Performance_Monitoring_Report.docx`**
📄 **`output/Linux_System_Performance_Monitoring_Report.pdf`**

- **Official Rendered Page Count**: **47 Pages** (Exceeds the 30-page requirement)
- **Total Word Count**: **9,172 Words**
- **Embedded Architectural Figures**: **11 High-Resolution Diagrams & Benchmark Graphs**
- **Formal Academic Tables**: **15 Detailed Specification & Comparison Tables**
- **Source Code Listings**: **Complete Unabridged Implementations**

### Report Structure
- **Title Page & Academic Front Matter**: Certificate of Originality, Candidate Declaration, Acknowledgement, Abstract, Table of Contents, List of Figures, List of Tables.
- **Chapter 1**: Introduction, Problem Statement, Objectives, and Monitored Subsystem Scope.
- **Chapter 2**: Theoretical Foundations, Unix Philosophy, and Linux Kernel Internals (`procfs`, CPU jiffies, page cache, block I/O, network stack, task structs).
- **Chapter 3**: Functional & Non-Functional Requirements, Architecture, and Mathematical Telemetry Formulations.
- **Chapter 4**: Component Engineering Walkthrough (CPU, Memory, Disk, Network, Process, Alerting, CLI, Web).
- **Chapter 5**: Complete Source Code Listings and Implementation Artifacts.
- **Chapter 6**: Experimental Setup, Testing, and Verification Methodology.
- **Chapter 7**: Benchmark Results, Accuracy Verification vs `top`/`iostat`/`vmstat`, and Daemon Overhead Profiling.
- **Chapter 8**: Security Considerations, Cgroup Sandboxing (`CPUQuota=5%`, `MemoryLimit=64M`), and Systemd Deployment.
- **Chapter 9**: Comparative Evaluation against Industry Frameworks (Prometheus, Zabbix, Netdata, Glances).
- **Chapter 10**: Experiential Learning Outcomes, Conclusions, and Future Scope (eBPF, OpenMetrics).
- **References**: IEEE Academic Bibliography.
- **Appendices**: Linux CLI Cheatsheet (Table 14), `/proc` Specification (Table 15), and Step-by-Step Deployment Guide.
