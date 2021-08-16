from unittest import TestCase
from time import sleep
from os.path import exists

from hoststats.client import HostStats


class TestHostStatsAPI(TestCase):
    def test_collection(self):
        hosts = ["localhost"]

        s = HostStats(hosts, test_mode=True)
        s.start_collection()

        sleep(2)

        csv_path = "/tmp/foo.csv"
        s.stop_and_write_to_csv(csv_path)

        self.assertTrue(exists(csv_path))
