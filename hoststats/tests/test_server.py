import json
import logging
import time
from multiprocessing import Process, Queue
from time import sleep
from unittest import TestCase, mock
from unittest.mock import call

from hoststats.app import app
from hoststats.collection import SLEEP_INTERVAL_MS, collect_metrics
from hoststats.stats import FORWARD_HEADER

SLEEP_INTERVAL_SECS = SLEEP_INTERVAL_MS / 1000


class MockResponse:
    def __init__(self, text, status_code):
        self.text = text
        self.content = text
        self.data = bytes(text, "utf-8")
        self.status_code = status_code

        self.headers = {
            "content-encoding": "blah",
            "content-length": 123,
            "some-other-header": "hi there",
        }


def mocked_requests_request(method, url, headers):
    logging.debug(f"Calling mocked request: {method}, {url}, {headers}")

    if url.endswith("ping"):
        return MockResponse("mocked ping", 200)
    elif url.endswith("start"):
        return MockResponse("mocked start", 200)
    elif url.endswith("stop"):
        return MockResponse("mocked stop", 200)
    else:
        raise RuntimeError("Unrecognised mock request")


class TestHostStatsCollection(TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_ping(self):
        res = self.client.get("ping")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.decode("utf-8"), "PONG")

    def test_api(self):
        # Start the collection
        start_time_millis = int(time.time() * 1000)
        self.client.get("start")

        # Sleep for a couple of intervals
        n_intervals = 2
        sleep(n_intervals * SLEEP_INTERVAL_SECS + 1)

        # Stop the collection
        res = self.client.get("stop")
        end_time_millis = int(time.time() * 1000)

        actual = json.loads(res.data.decode("utf-8"))

        self.check_collection_response(
            n_intervals, start_time_millis, end_time_millis, actual
        )

    def test_collection(self):
        # Start metrics collection in background
        kill_queue = Queue()
        result_queue = Queue()

        start_time_millis = int(time.time() * 1000)

        bg_proc = Process(
            target=collect_metrics, args=(kill_queue, result_queue)
        )
        bg_proc.start()

        # Allow a number of intervals to have happened
        n_intervals = 2
        sleep(n_intervals * SLEEP_INTERVAL_SECS + 1)

        # Kill the background collection process
        kill_queue.put("die")
        bg_proc.join()

        end_time_millis = int(time.time() * 1000)

        # Get and parse result
        actual = result_queue.get()
        actual = json.loads(actual)

        self.check_collection_response(
            n_intervals, start_time_millis, end_time_millis, actual
        )

    def check_collection_response(
        self, n_intervals, start_time_millis, end_time_millis, actual
    ):
        # Check it has the entries we expect
        self.assertListEqual(
            list(actual.keys()), ["cpu", "mem", "disk", "net"]
        )

        # Check contents
        cpu = actual["cpu"]
        mem = actual["mem"]
        disk = actual["disk"]
        net = actual["net"]

        # Pick a known stat, check we have expected number of readings
        expected_intervals = n_intervals + 1
        write_mb_values = disk["DISK_WRITE_MB"]
        self.assertEqual(len(write_mb_values), expected_intervals)

        # Sense-check timestamps
        cpu_timestamps = cpu["timestamp"]
        self.assertEqual(len(cpu_timestamps), expected_intervals)
        last_ts = 0
        for ts in cpu_timestamps:
            self.assertGreater(ts, last_ts)
            self.assertGreater(ts, start_time_millis)
            self.assertLess(ts, end_time_millis)
            last_ts = ts

        self.assertListEqual(mem["timestamp"], cpu_timestamps)
        self.assertListEqual(disk["timestamp"], cpu_timestamps)
        self.assertListEqual(net["timestamp"], cpu_timestamps)

        # Sense-check some percentages
        for cpu_pct in cpu["CPU_PCT"]:
            self.assertGreaterEqual(cpu_pct, 0)
            self.assertLessEqual(cpu_pct, 100)

        for cpu_pct in cpu["CPU_0_PCT_IOWAIT"]:
            self.assertGreaterEqual(cpu_pct, 0)
            self.assertLessEqual(cpu_pct, 100)

        for mem_pct in mem["MEMORY_USED_PCT"]:
            self.assertGreaterEqual(mem_pct, 0)
            self.assertLessEqual(mem_pct, 100)

    def _check_mocked_request(self, mock_req, url, expected_response):
        # Without setting our own user agent we get something chosen by the
        # underlying Flask mock client which we would have to hard code.
        user_agent = "foobar-agent"

        resp = self.client.get(
            url,
            headers={
                FORWARD_HEADER: "3.3.3.3",
            },
            environ_base={"HTTP_USER_AGENT": user_agent},
        )

        self.assertEqual(resp.data.decode("utf-8"), expected_response)

        expected_calls = [
            call(
                method="GET",
                url=f"http://3.3.3.3:5000/{url}",
                headers={"User-Agent": user_agent},
            ),
        ]

        self.assertListEqual(mock_req.call_args_list, expected_calls)

        # Check headers filtered on response
        expected_headers = {
            "Content-Length": f"{len(expected_response)}",
            "Content-Type": "text/html; charset=utf-8",
            "some-other-header": "hi there",
        }
        actual_headers = {k: v for (k, v) in resp.headers}
        self.assertEqual(actual_headers, expected_headers)

    @mock.patch(
        "hoststats.server.requests.request",
        side_effect=mocked_requests_request,
    )
    def test_mocked_ping_request(self, mock_req):
        self._check_mocked_request(mock_req, "ping", "mocked ping")

    @mock.patch(
        "hoststats.server.requests.request",
        side_effect=mocked_requests_request,
    )
    def test_mocked_start_request(self, mock_req):
        self._check_mocked_request(mock_req, "start", "mocked start")

    @mock.patch(
        "hoststats.server.requests.request",
        side_effect=mocked_requests_request,
    )
    def test_mocked_stop_request(self, mock_req):
        self._check_mocked_request(mock_req, "stop", "mocked stop")
