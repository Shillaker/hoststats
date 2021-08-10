from unittest import TestCase
from multiprocessing import Process, Queue
from time import sleep
import json

from hoststats.server.collection import collect_metrics, SLEEP_INTERVAL_SECS


class TestHostStatsCollection(TestCase):
    def test_collection():
        kill_queue = Queue()
        result_queue = Queue()

        bg_proc = Process(collect_metrics, args=(kill_queue, result_queue))
        bg_proc.start()

        sleep(5 * SLEEP_INTERVAL_SECS)

        kill_queue.put("die")
        bg_proc.join()

        actual = result_queue.get()
        actual = json.loads(actual)
