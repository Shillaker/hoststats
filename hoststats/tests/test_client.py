from time import sleep
from unittest import TestCase

from hoststats.client import HostStats
from hoststats.validation import validate_csv_data


class TestHostStatsClient(TestCase):
    def test_collection_locally(self):
        hosts = ["localhost"]

        s = HostStats(hosts, test_mode=True)
        s.start_collection()

        sleep(2)

        csv_path = "/tmp/foo.csv"
        s.stop_and_write_to_csv(csv_path)

        self.assertTrue(validate_csv_data(csv_path, hosts))
