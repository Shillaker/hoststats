import json
import logging
import sys
import time
from os import environ
from time import sleep

import psutil

from hoststats.stats import ONE_MB, get_stats_dfs

SLEEP_INTERVAL_MS = int(environ.get("HOSTSTATS_SLEEP_INTERVAL_MS", "2000"))


def collect_metrics(kill_queue, result_queue):
    cpu_stats, mem_stats, disk_stats, net_stats = get_stats_dfs()

    # cpu_percent will return zeroes to start with, so we want to make an
    # initial call
    # https://psutil.readthedocs.io/en/latest/#psutil.cpu_percent
    psutil.cpu_percent(percpu=False, interval=None)
    psutil.cpu_percent(percpu=True, interval=None)

    # Get CPU count and add columns to df
    cpu_count = psutil.cpu_count()
    for cpu_num in range(cpu_count):
        cpu_stats[f"CPU_{cpu_num}_PCT"] = list()
        cpu_stats[f"CPU_{cpu_num}_TIME_IDLE"] = list()
        cpu_stats[f"CPU_{cpu_num}_TIME_IOWAIT"] = list()
        cpu_stats[f"CPU_{cpu_num}_TIME_USER"] = list()
        cpu_stats[f"CPU_{cpu_num}_TIME_SYSTEM"] = list()

        cpu_stats[f"CPU_{cpu_num}_PCT_IDLE"] = list()
        cpu_stats[f"CPU_{cpu_num}_PCT_IOWAIT"] = list()
        cpu_stats[f"CPU_{cpu_num}_PCT_USER"] = list()
        cpu_stats[f"CPU_{cpu_num}_PCT_SYSTEM"] = list()

    while True:
        # Check queue to see if we need to finish
        if not kill_queue.empty():
            res = kill_queue.get_nowait()

            if res:
                logging.debug("Metrics collection finished")

                full_data = {
                    "cpu": cpu_stats.to_dict(orient="list"),
                    "mem": mem_stats.to_dict(orient="list"),
                    "disk": disk_stats.to_dict(orient="list"),
                    "net": net_stats.to_dict(orient="list"),
                }

                result_queue.put(json.dumps(full_data))

                sys.stdout.flush()
                break

        timestamp = int(time.time() * 1000)

        # CPU
        cpu_pct = psutil.cpu_percent(percpu=False)
        cpu_times = psutil.cpu_times(percpu=False)
        cpu_times_pct = psutil.cpu_times_percent(percpu=False)

        cpu_pct_per_cpu = psutil.cpu_percent(percpu=True)
        cpu_times_per_cpu = psutil.cpu_times(percpu=True)
        cpu_times_pct_per_cpu = psutil.cpu_times_percent(percpu=True)

        cpu_row = [
            timestamp,
            psutil.cpu_count(),
            psutil.cpu_freq().max,
            cpu_pct,
            cpu_times.idle,
            cpu_times.iowait,
            cpu_times.user,
            cpu_times.system,
            cpu_times_pct.idle,
            cpu_times_pct.iowait,
            cpu_times_pct.user,
            cpu_times_pct.system,
        ]

        for cpu_num in range(cpu_count):
            cpu_row.extend(
                [
                    cpu_pct_per_cpu[cpu_num],
                    cpu_times_per_cpu[cpu_num].idle,
                    cpu_times_per_cpu[cpu_num].iowait,
                    cpu_times_per_cpu[cpu_num].user,
                    cpu_times_per_cpu[cpu_num].system,
                    cpu_times_pct_per_cpu[cpu_num].idle,
                    cpu_times_pct_per_cpu[cpu_num].iowait,
                    cpu_times_pct_per_cpu[cpu_num].user,
                    cpu_times_pct_per_cpu[cpu_num].system,
                ]
            )

        cpu_stats.loc[len(cpu_stats.index)] = cpu_row

        # MEMORY
        vmem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        mem_row = [
            timestamp,
            vmem.used / ONE_MB,
            vmem.active / ONE_MB,
            vmem.percent,
            vmem.available / ONE_MB,
            swap.used / ONE_MB,
        ]

        mem_stats.loc[len(mem_stats.index)] = mem_row

        # DISK
        disk = psutil.disk_io_counters(perdisk=False)
        disk_row = [
            timestamp,
            disk.read_bytes / ONE_MB,
            disk.write_bytes / ONE_MB,
        ]
        disk_stats.loc[len(disk_stats.index)] = disk_row

        # NETWORK
        network = psutil.net_io_counters(pernic=False)
        net_row = [
            timestamp,
            network.bytes_sent / ONE_MB,
            network.bytes_recv / ONE_MB,
        ]
        net_stats.loc[len(net_stats.index)] = net_row

        # Sleep until next measurement
        sleep(float(SLEEP_INTERVAL_MS) / 1000)
