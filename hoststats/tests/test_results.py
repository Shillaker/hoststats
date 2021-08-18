from time import sleep
from unittest import TestCase

from hoststats.client import HostStats
from hoststats.results import HostStatsResults
from hoststats.stats import CPU_STATS, MEM_STATS, DISK_STATS, NET_STATS


class TestHostStatsResults(TestCase):
    def test_results_on_real_data(self):
        hosts = ["localhost"]

        s = HostStats(hosts, test_mode=True)
        s.start_collection()

        sleep(2)

        csv_path = "/tmp/foo.csv"
        s.stop_and_write_to_csv(csv_path)

        r = HostStatsResults(csv_path)
        self.assertEqual(r.csv_file, csv_path)
        self.assertEqual(r.get_hosts(), hosts)
        self.assertEqual(
            r.get_stats(), CPU_STATS + MEM_STATS + DISK_STATS + NET_STATS
        )

        self.assertRaises(RuntimeError, r.get_stat_per_host, "blahblah")
        self.assertRaises(RuntimeError, r.get_median_stat, "blahblah")
        self.assertRaises(RuntimeError, r.get_avg_stat, "blahblah")
        self.assertRaises(RuntimeError, r.get_stat_quantile, "blahblah", 10)
