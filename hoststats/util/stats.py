import pandas as pd

ONE_MB = 1024.0 * 1024.0


def get_stats_dfs():
    cpu_stats = pd.DataFrame(
        columns=[
            "timestamp",
            "CPU_COUNT",
            "CPU_FREQ",
            "CPU_PCT",
            "CPU_TIME_IDLE",
            "CPU_TIME_IOWAIT",
            "CPU_TIME_USER",
            "CPU_TIME_SYSTEM",
            "CPU_PCT_IDLE",
            "CPU_PCT_IOWAIT",
            "CPU_PCT_USER",
            "CPU_PCT_SYSTEM",
        ]
    )

    mem_stats = pd.DataFrame(
        columns=[
            "timestamp",
            "MEMORY_USED",
            "MEMORY_ACTIVE",
            "MEMORY_USED_PCT",
            "MEMORY_AVAILABLE",
            "SWAP_USED",
        ]
    )

    disk_stats = pd.DataFrame(
        columns=["timestamp", "DISK_READ_MB", "DISK_WRITE_MB"]
    )

    net_stats = pd.DataFrame(
        columns=["timestamp", "NET_SENT_MB", "NET_RECV_MB"]
    )

    return cpu_stats, mem_stats, disk_stats, net_stats
