from unittest import TestCase
from time import sleep

from hoststats.client import HostStats


class TestHostStatsAPI(TestCase):
    def test_collection(self):
        hosts = ["localhost"]

        s = HostStats(hosts, test_mode=True)

        sleep(5)

        csv_path = "/tmp/foo.csv"
        s.stop_and_write_to_csv(csv_path)
