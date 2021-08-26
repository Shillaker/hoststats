import json
import logging
from subprocess import PIPE, run

import pandas as pd
import requests

from hoststats.stats import (
    CPU_STATS,
    DISK_STATS,
    FORWARD_HEADER,
    MEM_STATS,
    NET_STATS,
    SERVER_PORT,
)


class HostStats:
    def __init__(
        self,
        host_list,
        test_mode=False,
        proxy=None,
        proxy_port=SERVER_PORT,
        kubectl=False,
        kubectl_container=None,
        kubectl_ns=None,
    ):
        self.host_list = host_list
        self.test_mode = test_mode
        self.is_running = False
        self.proxy = proxy
        self.proxy_port = proxy_port

        self.kubectl = kubectl
        self.kubectl_container = kubectl_container
        self.kubectl_ns = kubectl_ns

        if self.test_mode:
            from hoststats.app import app

            self.client = app.test_client()

        successful_init = True

        for h in host_list:
            logging.debug(f"Pinging {h}")
            status, data = self.make_request(h, "ping")

            if status != 200:
                logging.error(f"Failed to ping {h}, got code {status}")
                successful_init = False

            if data != "PONG":
                logging.error(f"Got unexpected response to ping: {data}")
                successful_init = False

        if not successful_init:
            raise RuntimeError("hoststats client failed to initialise")

        if self.proxy:
            logging.debug(
                f"Created hoststats proxy on {self.proxy} for {self.host_list}"
            )
        else:
            logging.debug(f"Created hoststats client for {self.host_list}")

    def make_request(self, host, url):
        if self.test_mode:
            resp = self.client.get(url)
            status_code = resp.status_code

            data = None
            if resp.data:
                data = resp.data.decode("utf-8")

            return status_code, data

        if self.kubectl:
            cmd = [
                "kubectl",
                f"-n {self.kubectl_ns}" if self.kubectl_ns else "",
                f"-c {self.kubectl_container}"
                if self.kubectl_container
                else "",
                "exec",
                host,
                "--",
                f"curl -s http://localhost:5000/{url}",
            ]
            cmd_str = " ".join(cmd)
            res = run(cmd_str, shell=True, stdout=PIPE, stderr=PIPE)

            output = res.stdout.decode("utf-8")
            if res.returncode == 0:
                return 200, output
            else:
                return 500, output

        elif self.proxy:
            full_url = f"http://{self.proxy}:{self.proxy_port}/{url}"
            resp = requests.get(full_url, headers={FORWARD_HEADER: host})
        else:
            resp = requests.get(f"http://{host}:{SERVER_PORT}/{url}")

        return resp.status_code, resp.text

    def start_collection(self):
        successful_start = True

        for h in self.host_list:
            logging.debug(f"Starting collection on {h}")
            status, resp = self.make_request(h, "start")

            if status != 200:
                logging.error(
                    f"Failed to start on {h}, got code {resp.status_code}"
                )
                successful_start = False

            if not successful_start:
                raise RuntimeError("hoststats failed to start collection")

        self.is_running = True

    def stop_and_write_to_csv(self, csv_path):
        if not self.is_running:
            raise RuntimeError("Called stop without starting")

        self.is_running = False

        csv_cols = ["Timestamp", "Host"]
        csv_cols.extend(CPU_STATS)
        csv_cols.extend(MEM_STATS)
        csv_cols.extend(DISK_STATS)
        csv_cols.extend(NET_STATS)

        with open(csv_path, "w") as fh:
            fh.write(",".join(csv_cols))
            fh.write("\n")

        for h in self.host_list:
            logging.debug(f"Writing results for {h}")

            # Pull the results
            df = self.pull_results_for_host(h)

            # Append to the CSV file
            df.to_csv(csv_path, header=False, mode="a", index=False)

    def pull_results_for_host(self, host):
        status, data = self.make_request(host, "stop")
        data_json = json.loads(data)

        cpu_stats = pd.read_json(json.dumps(data_json["cpu"]), orient="list")
        mem_stats = pd.read_json(json.dumps(data_json["mem"]), orient="list")
        disk_stats = pd.read_json(json.dumps(data_json["disk"]), orient="list")
        net_stats = pd.read_json(json.dumps(data_json["net"]), orient="list")

        n_readings = len(cpu_stats["timestamp"])
        host_col = [host] * n_readings

        merged = pd.DataFrame(columns=["timestamp", "host"])
        merged["timestamp"] = cpu_stats["timestamp"]
        merged["host"] = host_col

        merged = pd.concat(
            [
                merged,
                cpu_stats[CPU_STATS],
                mem_stats[MEM_STATS],
                disk_stats[DISK_STATS],
                net_stats[NET_STATS],
            ],
            axis=1,
        )

        return merged
