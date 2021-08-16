import requests

SERVER_PORT = "5000"


class HostStats:
    def __init__(self, host_list, test_mode=False):
        self.host_list = host_list
        self.test_mode = test_mode

        if self.test_mode:
            from hoststats.app import app

            self.client = app.test_client()

        successful_init = True

        for h in host_list:
            print(f"Pinging {h}")
            status, data = resp = self.get_request(h, "ping")

            if status != 200:
                print(f"Failed to ping {h}, got code {status}")
                successful_init = False

            if data.strip() != "PONG":
                print(f"Got unexpected response to ping: {data}")
                successful_init = False

        if not successful_init:
            raise RuntimeError("hoststats client failed to initialise")

    def get_request(self, host, url):
        if self.test_mode:
            resp = self.client.get(url)
            status_code = resp.status_code

            data = None
            if resp.data:
                data = resp.data.decode("utf-8")
        else:
            resp = requests.get(f"http://{host}:{SERVER_PORT}/{url}")
            status_code = resp.status_code

            data = resp.text()

        return status_code, data

    def start_collection(self):
        successful_start = True

        for h in self.host_list:
            print(f"Starting collection on {h}")
            status, resp = self.get_request(h, "start")

            if status != 200:
                print(f"Failed to start on {h}, got code {resp.status_code}")
                successful_start = False

            if not successful_start:
                raise RuntimeError("hoststats failed to start collection")

    def stop_and_write_to_csv(self, csv_path):
        # TODO - implement
        pass
