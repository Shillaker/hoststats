from multiprocessing import Process, Queue

from flask import Blueprint

from hoststats.collection import collect_metrics

metrics_api = Blueprint("metrics_api", __name__)

metrics_process = None
kill_queue = None
result_queue = None


@metrics_api.route("/ping")
def ping():
    return "PONG"


@metrics_api.route("/start")
def start_recording():
    global metrics_process
    global kill_queue
    global result_queue

    if metrics_process is not None:
        print("Not starting, process already running")
        return "Not started"

    kill_queue = Queue()
    result_queue = Queue()

    metrics_process = Process(
        target=collect_metrics, args=(kill_queue, result_queue)
    )
    metrics_process.start()

    return "hoststats started"


@metrics_api.route("/stop")
def stop_recording():
    global metrics_process
    global kill_queue
    global result_queue

    if metrics_process is None:
        print("Not stopping, no process running")
        return

    kill_queue.put("die")
    metrics_process.join()
    result_json = result_queue.get()

    metrics_process = None
    kill_queue = None
    result_queue = None

    return result_json
