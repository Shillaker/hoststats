import signal
import socket
from time import sleep
from unittest import TestCase

from hoststats.client import HostStats
from hoststats.validation import validate_csv_data

TEST_HOSTS = ["target-one", "target-two", "target-three"]
TIMEOUT_SEC = 5


def timeout_handler(signum, frame):
   print("Timeout hit!")
   signal.alarm(0)
   raise RuntimeError("Execution timed out")


class TestHostStatsDistributed(TestCase):
    def test_collection_with_ips(self):
        ips = list()
        for h in TEST_HOSTS:
            addr_res = socket.gethostbyaddr(h)
            ips.append(addr_res[2][0])

        print(f"Detected test IPs: {ips}")

        self.do_dist_checks(ips)

    def test_collection_with_hostnames(self):
        self.do_dist_checks(TEST_HOSTS)

    def test_collection_with_proxy_hostname(self):
        proxy = "target-two"
        self.do_dist_checks(TEST_HOSTS, proxy=proxy)

    def test_collection_with_proxy_ip(self):
        proxy = "target-two"
        addr_res = socket.gethostbyaddr(proxy)
        proxy_ip = addr_res[2][0]

        self.do_dist_checks(TEST_HOSTS, proxy=proxy_ip)

    def test_collection_long_run(self):
        time_to_sleep = 20
        print(
            f"Test collecting results after sleeping for {time_to_sleep} seconds"
        )

        with self.assertRaises(RuntimeError):
            self.do_dist_checks(TEST_HOSTS, seconds_to_sleep=time_to_sleep)

    def do_dist_checks(self, hosts, proxy=None, seconds_to_sleep=5):
        s = HostStats(hosts, proxy=proxy)
        s.start_collection()

        sleep(seconds_to_sleep)

        csv_path = "/tmp/hoststats.csv"

        print("stopping and writing...")
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(TIMEOUT_SEC)
        s.stop_and_write_to_csv(csv_path)
        print("deactivating alarm")
        signal.alarm(0)

        validate_csv_data(csv_path, hosts)
