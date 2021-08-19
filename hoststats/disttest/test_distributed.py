import socket
from time import sleep
from unittest import TestCase

from hoststats.client import HostStats
from hoststats.validation import validate_csv_data

TEST_HOSTS = ["target-one", "target-two", "target-three"]


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

    def do_dist_checks(self, hosts, proxy=None):
        s = HostStats(hosts, proxy=proxy)
        s.start_collection()

        sleep(5)

        csv_path = "/tmp/hoststats.csv"
        s.stop_and_write_to_csv(csv_path)

        validate_csv_data(csv_path, hosts)
