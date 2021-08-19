import pandas as pd

# Note - header keys must start with a capital, and be all lower-case otherwise
FORWARD_HEADER = "Forwardhost"
SERVER_PORT = "5000"

ONE_MB = 1024.0 * 1024.0

CPU_STATS = [
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

MEM_STATS = [
    "MEMORY_USED",
    "MEMORY_ACTIVE",
    "MEMORY_USED_PCT",
    "MEMORY_AVAILABLE",
    "SWAP_USED",
]

DISK_STATS = ["DISK_READ_MB", "DISK_WRITE_MB"]

NET_STATS = ["NET_SENT_MB", "NET_RECV_MB"]


def get_stats_dfs():
    cpu_stats = pd.DataFrame(columns=["timestamp"] + CPU_STATS)

    mem_stats = pd.DataFrame(columns=["timestamp"] + MEM_STATS)

    disk_stats = pd.DataFrame(columns=["timestamp"] + DISK_STATS)

    net_stats = pd.DataFrame(columns=["timestamp"] + NET_STATS)

    return cpu_stats, mem_stats, disk_stats, net_stats
