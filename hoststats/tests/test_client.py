import logging
from time import sleep
from unittest import TestCase, mock
from unittest.mock import call

from subprocess import PIPE

from hoststats.client import HostStats
from hoststats.stats import FORWARD_HEADER
from hoststats.validation import validate_csv_data


class MockResponse:
    def __init__(self, text, json_data, status_code):
        self.text = text
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mocked_requests_get(url, *args, **kwargs):
    logging.debug(
        f"Calling mocked GET: {url}, headers={kwargs.get('headers')}"
    )

    if url.endswith("ping"):
        return MockResponse("PONG", None, 200)
    elif url.endswith("start"):
        return MockResponse("hoststats started", None, 200)
    elif url.endswith("stop"):
        return MockResponse(None, {"blah": 123}, 200)
    else:
        raise RuntimeError("Unrecognised mock request")


class MockProcessOutput:
    def __init__(self, returncode, output):
        self.stdout = output
        self.returncode = returncode


def mocked_run(cmd, shell=True, stderr=None, stdout=None, **kwargs):
    logging.debug(f"Calling mocked run: {cmd}")

    if cmd.endswith("ping"):
        return MockProcessOutput(0, bytes("PONG", "utf-8"))
    elif cmd.endswith("start"):
        return MockProcessOutput(0, bytes("hoststats started", "utf-8"))
    else:
        raise RuntimeError("Unrecognised mock request")


class TestHostStatsClient(TestCase):
    def test_collection_locally(self):
        hosts = ["localhost"]

        s = HostStats(hosts, test_mode=True)
        s.start_collection()

        sleep(2)

        csv_path = "/tmp/foo.csv"
        s.stop_and_write_to_csv(csv_path)

        self.assertTrue(validate_csv_data(csv_path, hosts))

    @mock.patch(
        "hoststats.client.requests.get", side_effect=mocked_requests_get
    )
    def test_mocked_requests(self, mock_get):
        hosts = ["1.2.3.4", "5.6.7.8"]

        s = HostStats(hosts)
        s.start_collection()

        self.assertEqual(len(mock_get.call_args_list), 4)

        expected_calls = [
            call(
                "http://1.2.3.4:5000/ping",
            ),
            call(
                "http://5.6.7.8:5000/ping",
            ),
            call(
                "http://1.2.3.4:5000/start",
            ),
            call(
                "http://5.6.7.8:5000/start",
            ),
        ]

        self.assertListEqual(mock_get.call_args_list, expected_calls)

    @mock.patch(
        "hoststats.client.requests.get", side_effect=mocked_requests_get
    )
    def test_proxy_mocked_requests(self, mock_get):
        hosts = ["1.2.3.4", "5.6.7.8"]
        proxy = "8.7.6.5"

        s = HostStats(hosts, proxy=proxy)
        s.start_collection()

        self.assertEqual(len(mock_get.call_args_list), 4)

        expected_calls = [
            call(
                "http://8.7.6.5:5000/ping",
                headers={FORWARD_HEADER: "1.2.3.4"},
            ),
            call(
                "http://8.7.6.5:5000/ping",
                headers={FORWARD_HEADER: "5.6.7.8"},
            ),
            call(
                "http://8.7.6.5:5000/start",
                headers={FORWARD_HEADER: "1.2.3.4"},
            ),
            call(
                "http://8.7.6.5:5000/start",
                headers={FORWARD_HEADER: "5.6.7.8"},
            ),
        ]

        self.assertListEqual(mock_get.call_args_list, expected_calls)

    @mock.patch(
        "hoststats.client.requests.get", side_effect=mocked_requests_get
    )
    def test_proxy_mocked_requests_custom_port(self, mock_get):
        hosts = ["1.2.3.4", "5.6.7.8"]
        proxy = "8.7.6.5"

        s = HostStats(hosts, proxy=proxy, proxy_port=1234)
        s.start_collection()

        self.assertEqual(len(mock_get.call_args_list), 4)

        expected_calls = [
            call(
                "http://8.7.6.5:1234/ping",
                headers={FORWARD_HEADER: "1.2.3.4"},
            ),
            call(
                "http://8.7.6.5:1234/ping",
                headers={FORWARD_HEADER: "5.6.7.8"},
            ),
            call(
                "http://8.7.6.5:1234/start",
                headers={FORWARD_HEADER: "1.2.3.4"},
            ),
            call(
                "http://8.7.6.5:1234/start",
                headers={FORWARD_HEADER: "5.6.7.8"},
            ),
        ]

        self.assertListEqual(mock_get.call_args_list, expected_calls)

    @mock.patch("hoststats.client.run", side_effect=mocked_run)
    def test_kubectl_cmds(self, mock_run):
        hosts = ["pod-a", "pod-b"]

        s = HostStats(
            hosts, kubectl=True, kubectl_container="blah", kubectl_ns="foobar"
        )
        s.start_collection()

        self.assertEqual(len(mock_run.call_args_list), 4)

        expected_calls = [
            call(
                "kubectl -n foobar -c blah exec pod-a -- curl -s http://localhost:5000/ping",
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
            ),
            call(
                "kubectl -n foobar -c blah exec pod-b -- curl -s http://localhost:5000/ping",
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
            ),
            call(
                "kubectl -n foobar -c blah exec pod-a -- curl -s http://localhost:5000/start",
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
            ),
            call(
                "kubectl -n foobar -c blah exec pod-b -- curl -s http://localhost:5000/start",
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
            ),
        ]

        self.assertListEqual(mock_run.call_args_list, expected_calls)
