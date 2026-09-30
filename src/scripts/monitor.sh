#!/bin/bash
# ==============================================================================
# Linux System Performance Monitoring Script (Bash Native Edition)
# Course: Operating System Experiential Learning Case Study
# ==============================================================================

INTERVAL=2
CLEAR_CMD="clear"

echo "Starting Native Linux Performance Telemetry..."
sleep 1

while true; do
    $CLEAR_CMD
    echo "=============================================================================="
    echo "       NATIVE LINUX PERFORMANCE MONITOR - TELEMETRY DASHBOARD"
    echo "       Timestamp: $(date '+%Y-%m-%d %H:%M:%S')  | Host: $(hostname)"
    echo "=============================================================================="

    # 1. UPTIME & LOAD AVERAGE
    echo -e "\n[+] SYSTEM LOAD & UPTIME:"
    uptime | awk -F'load average:' '{ print "    Uptime / Users:" $1 "\n    Load Average (1, 5, 15m):" $2 }'

    # 2. CPU UTILIZATION FROM /proc/stat
    echo -e "\n[+] CPU METRICS (/proc/stat):"
    read -r cpu u n s i w irq sirq st < <(grep '^cpu ' /proc/stat)
    prev_idle=$((i + w))
    prev_total=$((u + n + s + i + w + irq + sirq + st))
    sleep 0.5
    read -r cpu u n s i w irq sirq st < <(grep '^cpu ' /proc/stat)
    idle=$((i + w))
    total=$((u + n + s + i + w + irq + sirq + st))

    diff_idle=$((idle - prev_idle))
    diff_total=$((total - prev_total))
    if [ $diff_total -gt 0 ]; then
        cpu_usage=$(( (1000 * (diff_total - diff_idle) / diff_total + 5) / 10 ))
        echo "    Active CPU Utilization: ${cpu_usage}%"
    fi

    # 3. MEMORY BREAKDOWN (/proc/meminfo)
    echo -e "\n[+] MEMORY METRICS (/proc/meminfo):"
    free -h | awk 'NR==1{print "    " $0} NR==2{print "    RAM:  " $0} NR==3{print "    Swap: " $0}'

    # 4. DISK USAGE & INODES
    echo -e "\n[+] STORAGE CAPACITY & INODES:"
    df -h -x tmpfs -x devtmpfs | awk 'NR==1{print "    " $0} NR>1{print "    " $0}'

    # 5. DISK I/O ACTIVITY (/proc/diskstats)
    echo -e "\n[+] DISK I/O ACTIVITY (Active Block Devices):"
    awk '$3 ~ /^(sd[a-z]|nvme[0-9]n[0-9]|vd[a-z])$/ {
        printf "    Device: %-10s Reads: %-8s Sectors Read: %-10s Writes: %-8s Sectors Written: %-10s\n", $3, $4, $6, $8, $10
    }' /proc/diskstats

    # 6. NETWORK BANDWIDTH (/proc/net/dev)
    echo -e "\n[+] NETWORK INTERFACES (/proc/net/dev):"
    awk -F'[: ]+' '/(eth[0-9]|en[a-z0-9]+|wl[a-z0-9]+):/ {
        printf "    Interface: %-10s RX: %-8.2f MB  TX: %-8.2f MB  Drops: %-4s\n", $2, $3/1048576, $11/1048576, $5
    }' /proc/net/dev

    # 7. TOP 5 CONSUMING PROCESSES
    echo -e "\n[+] TOP 5 PROCESSES BY CPU USAGE:"
    ps -eo pid,ppid,user,%cpu,%mem,comm --sort=-%cpu | head -n 6 | awk '{printf "    %-8s %-8s %-10s %-8s %-8s %-15s\n", $1, $2, $3, $4, $5, $6}'

    echo -e "\n=============================================================================="
    echo " Refreshing in ${INTERVAL}s. Press Ctrl+C to terminate."
    sleep $INTERVAL
done
