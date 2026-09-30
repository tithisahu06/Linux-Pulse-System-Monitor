#!/bin/bash
# ==============================================================================
# Workload Generator & Stress Testing Suite
# Used to generate controlled OS subsystem load for monitoring verification
# ==============================================================================

echo "================================================================="
echo " Linux Pulse - Experiential Workload Benchmark Generator"
echo "================================================================="

DURATION=15

case "$1" in
    cpu)
        echo "[*] Triggering CPU Stress Workload for ${DURATION}s..."
        echo "[*] Launching multi-threaded matrix operations on available cores..."
        for i in $(seq 1 $(nproc 2>/dev/null || echo 4)); do
            (while :; do :; done) &
        done
        STRESS_PIDS=$(jobs -p)
        sleep $DURATION
        kill $STRESS_PIDS 2>/dev/null
        echo "[+] CPU Stress Test completed."
        ;;
    memory)
        echo "[*] Triggering RAM Allocation Workload..."
        python3 -c "
import time
print('[*] Allocating 1.5 GB in RAM buffer...')
buf = bytearray(1500 * 1024 * 1024)
for i in range(0, len(buf), 4096):
    buf[i] = 1 # Force physical page allocation (faulting in)
print('[+] Allocation complete. Holding for ${DURATION}s...')
time.sleep(${DURATION})
print('[+] Releasing memory buffer.')
"
        ;;
    disk)
        echo "[*] Triggering Disk I/O Write Stress (Direct I/O Sync)..."
        dd if=/dev/urandom of=/tmp/sysmon_io_test.tmp bs=1M count=300 oflag=direct status=progress
        rm -f /tmp/sysmon_io_test.tmp
        echo "[+] Disk I/O benchmark completed."
        ;;
    all)
        echo "[*] Running comprehensive system stress test..."
        $0 cpu &
        $0 memory &
        $0 disk &
        wait
        echo "[+] Comprehensive benchmark finished."
        ;;
    *)
        echo "Usage: $0 {cpu|memory|disk|all}"
        exit 1
        ;;
esac
