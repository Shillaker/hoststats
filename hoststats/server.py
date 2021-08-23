import logging
from multiprocessing import Process, Queue

import requests
from flask import Blueprint, Response, request

from hoststats.collection import collect_metrics
from hoststats.stats import FORWARD_HEADER, SERVER_PORT

metrics_api = Blueprint("metrics_api", __name__)

metrics_process = None
kill_queue = None
result_queue = None


def _get_forward_host():
    for key, value in request.headers.items():
        if key.lower() == FORWARD_HEADER.lower():
            return value

    return None


def _is_forward_request():
    host = _get_forward_host()
    return bool(host)


def _do_forward_request():
    # Note, Flask's request.host field contains the port too
    original_url = request.url
    target_host = _get_forward_host()
    forward_url = original_url.replace(
        request.host, f"{target_host}:{SERVER_PORT}"
    )

    # Strip out forward header and host header
    forward_headers = {
        k: v
        for (k, v) in request.headers
        if k.lower() not in [FORWARD_HEADER.lower(), "host"]
    }

    logging.debug(f"Forwarding request from {original_url} to {forward_url}")
    logging.debug(f"Forwarding headers: {forward_headers}")

    # Make the forward request
    resp = requests.request(
        method=request.method,
        url=forward_url,
        headers=forward_headers,
    )

    # Strip out undesired headers from the forwarded response
    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in resp.headers.items()
        if name.lower() not in excluded_headers
    ]

    # Build Flask response from forwarded response
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
        msg = "Not starting metrics recording, already running"
        logging.warn(msg)
        return msg

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
        msg = "Not stopping metrics recording, not running"
        logging.warn(msg)
        return msg

    kill_queue.put("die")
    metrics_process.join()
    result_json = result_queue.get()

    metrics_process = None
    kill_queue = None
    result_queue = None

    return result_json
