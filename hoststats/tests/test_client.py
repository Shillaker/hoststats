from unittest import TestCase

from hoststats.app import app
from hoststats.client.client import HostStats


class TestHostStatsAPI(TestCase):
    def test_collection(self):

        s = HostStats()
        pass
