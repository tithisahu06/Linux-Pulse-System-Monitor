"""
Memory & Virtual Memory Performance Monitor for Linux Systems
Directly parses /proc/meminfo and /proc/vmstat.
Analyzes physical RAM, Linux page cache, slab reclaimable, dirty pages, and swap.
"""

import os
import random

class MemoryMonitor:
    def __init__(self):
        self.is_linux = os.path.exists("/proc/meminfo")

    def _read_meminfo(self):
        """Parse key-value pairs from /proc/meminfo."""
        data = {}
        if self.is_linux:
            try:
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if ":" in line:
                            parts = line.split(":")
                            key = parts[0].strip()
                            val_parts = parts[1].strip().split()
                            val = int(val_parts[0])  # in kB
                            data[key] = val
            except Exception:
                pass
        else:
            # Emulated values in kB for testing
            total_kb = 16 * 1024 * 1024 # 16 GB
            used_kb = int(total_kb * random.uniform(0.40, 0.65))
            free_kb = int(total_kb * 0.15)
            avail_kb = total_kb - used_kb
            buffers_kb = int(total_kb * 0.05)
            cached_kb = int(total_kb * 0.20)
            swap_total_kb = 8 * 1024 * 1024
            swap_free_kb = int(swap_total_kb * 0.85)

            data = {
                "MemTotal": total_kb,
                "MemFree": free_kb,
                "MemAvailable": avail_kb,
                "Buffers": buffers_kb,
                "Cached": cached_kb,
                "SReclaimable": int(total_kb * 0.03),
                "SwapTotal": swap_total_kb,
                "SwapFree": swap_free_kb,
                "Dirty": random.randint(1024, 15000),
                "Writeback": random.randint(0, 1024),
                "Active": int(used_kb * 0.6),
                "Inactive": int(used_kb * 0.4)
            }
        return data

    def _read_vmstat(self):
        """Parse paging and swapping stats from /proc/vmstat."""
        vm = {
            "pgpgin": 0,
            "pgpgout": 0,
            "pswpin": 0,
            "pswpout": 0,
            "pgfault": 0,
            "pgmajfault": 0
        }
        if self.is_linux and os.path.exists("/proc/vmstat"):
            try:
                with open("/proc/vmstat", "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 2 and parts[0] in vm:
                            vm[parts[0]] = int(parts[1])
            except Exception:
                pass
        return vm

    def get_metrics(self):
        """Compute human-friendly memory statistics in MB/GB and percentage."""
        info = self._read_meminfo()
        vm = self._read_vmstat()

        total_kb = info.get("MemTotal", 1)
        avail_kb = info.get("MemAvailable", info.get("MemFree", 0) + info.get("Cached", 0))
        free_kb = info.get("MemFree", 0)
        buffers_kb = info.get("Buffers", 0)
        cached_kb = info.get("Cached", 0)
        sreclaim_kb = info.get("SReclaimable", 0)
        total_cached_kb = cached_kb + buffers_kb + sreclaim_kb
        used_kb = max(0, total_kb - avail_kb)

        used_pct = round((used_kb / total_kb) * 100.0, 2)
        avail_pct = round((avail_kb / total_kb) * 100.0, 2)

        # Swap metrics
        swap_total_kb = info.get("SwapTotal", 0)
        swap_free_kb = info.get("SwapFree", 0)
        swap_used_kb = swap_total_kb - swap_free_kb
        swap_pct = round((swap_used_kb / swap_total_kb) * 100.0, 2) if swap_total_kb > 0 else 0.0

        return {
            "total_mb": round(total_kb / 1024, 2),
            "used_mb": round(used_kb / 1024, 2),
            "free_mb": round(free_kb / 1024, 2),
            "available_mb": round(avail_kb / 1024, 2),
            "cached_mb": round(total_cached_kb / 1024, 2),
            "buffers_mb": round(buffers_kb / 1024, 2),
            "dirty_mb": round(info.get("Dirty", 0) / 1024, 2),
            "used_pct": used_pct,
            "available_pct": avail_pct,
            "swap": {
                "total_mb": round(swap_total_kb / 1024, 2),
                "used_mb": round(swap_used_kb / 1024, 2),
                "free_mb": round(swap_free_kb / 1024, 2),
                "used_pct": swap_pct
            },
            "paging": vm
        }
