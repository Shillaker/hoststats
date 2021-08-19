from multiprocessing import Process, Queue

from flask import Blueprint, request, Response

import requests

from hoststats.stats import FORWARD_HEADER, SERVER_PORT
from hoststats.collection import collect_metrics

metrics_api = Blueprint("metrics_api", __name__)

metrics_process = None
kill_queue = None
result_queue = None


def _is_forward_request():
    return bool(request.headers.get(FORWARD_HEADER))


def _do_forward_request():
    # Note, Flask's request.host field contains the port too
    target_host = request.headers[FORWARD_HEADER]
    forward_url = (
        request.url.replace(request.host, f"{target_host}:{SERVER_PORT}"),
    )

    forward_headers = {
        key: value for (key, value) in request.headers if key != FORWARD_HEADER
    }

    resp = requests.request(
        method=request.method,
        url=forward_url,
        headers=forward_headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )

    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]

    # Build Flask response
    return Response(resp.content, resp.status_code, headers)


@metrics_api.route("/ping")
def ping():
    if _is_forward_request():
        return _do_forward_request()

    return "PONG"


@metrics_api.route("/start")
def start_recording():
    if _is_forward_request():
        return _do_forward_request()

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
    if _is_forward_request():
        return _do_forward_request()

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
