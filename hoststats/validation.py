import logging
from os.path import exists

import pandas as pd

from hoststats.stats import CPU_STATS, DISK_STATS, MEM_STATS, NET_STATS


def validate_csv_data(csv_path, expected_hosts):
    if not exists(csv_path):
        logging.error(f"Did not find hoststats file at {csv_path}")
        return False

    data = pd.read_csv(csv_path)

    is_valid = True

    # Check columns are as expected
    expected_cols = (
        ["Timestamp", "Host"] + CPU_STATS + MEM_STATS + DISK_STATS + NET_STATS
    )
    cols = [c for c in data.columns]
    if cols != expected_cols:
        logging.error(
            f"hoststats expected cols {expected_cols}, got {data.columns}"
        )
        is_valid = False

    # Check hosts list
    hosts = set(data["Host"].unique())
    if set(expected_hosts) != hosts:
        logging.error(
            f"hoststats invalid, expected hosts {expected_hosts}, got {hosts}"
        )
        is_valid = False

    if data.isnull().values.any():
        logging.error("Found null values in hoststats")
        is_valid = False

    return is_valid
