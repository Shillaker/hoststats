import requests


class HostStats:
    def __init__(self, host_list):
        self.host_list = host_list

        successful_init = True

        for h in host_list:
            print(f"Pinging {h}")
            resp = requests.get(f"http://{h}:5000/ping")

            if resp.status_code != 200:
                print(f"Failed to ping {h}, got code {resp.status_code}")
                successful_init = False

            if resp.text().strip() != "PONG":
                print(f"Got unexpected response to ping: {resp.text}")
                successful_init = False

        if not successful_init:
            raise RuntimeError("hoststats client failed to initialise")

    def start_collection(self):
        successful_start = True

        for h in self.host_list:
            print(f"Starting collection on {h}")
            resp = requests.get(f"http://{h}:5000/start")

            if resp.status_code != 200:
                print(f"Failed to start on {h}, got code {resp.status_code}")
                successful_start = False

            if not successful_start:
                raise RuntimeError("hoststats failed to start collection")

    def stop_and_write_to_csv(self, csv_path):
        # TODO - implement
        pass
