import logging
from os.path import exists

import pandas as pd


class HostStatsResults:
    def __init__(self, csv_file, relative_ts=True, base_ts=None):
        self.csv_file = csv_file

        if not exists(self.csv_file):
            logging.error(f"hoststats result file not found: {self.csv_file}")
            raise RuntimeError("hoststas result file not found")

        self.full_results = pd.read_csv(self.csv_file)

        # Parse timestamps to pd timestamp objects
        self.full_results["Timestamp"] = pd.to_datetime(
            self.full_results["Timestamp"]
        )

        # If no base timestamp given, take the first in the data
        if relative_ts:
            if not base_ts:
                base_ts = self.full_results["Timestamp"][0]

            # Put all timestamps relative to the base timestamp in seconds
            self.full_results["Timestamp"] -= base_ts

        # Merge across hosts for aggregate stats
        self.grouped_results = self.full_results.groupby("Timestamp")

    def get_hosts(self):
        return self.full_results["Host"].unique()

    def get_full_results(self):
        return self.full_results

    def get_grouped_results(self):
        return self.grouped_results

    def get_stats(self):
        stats = [c for c in self.full_results.columns]
        stats.remove("Timestamp")
        stats.remove("Host")

        return stats

    def validate_stat(self, stat):
        stats = self.get_stats()
        if stat not in stats:
            raise RuntimeError(f"{stat} not in {stats}")

    def get_stat_per_host(self, stat):
        self.validate_stat(stat)

        hosts = self.get_hosts()
        stats_per_host = dict()
        for host in hosts:
            host_ts = self.full_results["Host"] == host
            stats_per_host[host] = host_ts[stat]

        return stats_per_host

    def get_avg_stat(self, stat):
        self.validate_stat(stat)
        return self.grouped_results.mean()[stat]

    def get_median_stat(self, stat):
        self.validate_stat(stat)
        return self.grouped_results.median()[stat]

    def get_stat_quantile(self, stat, q):
        self.validate_stat(stat)
        return self.grouped_results.quantile(q)[stat]
