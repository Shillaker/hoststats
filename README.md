# hoststats [![Tests](https://github.com/Shillaker/hoststats/workflows/Tests/badge.svg?branch=master)](https://github.com/Shillaker/hoststats/actions) [![License](https://img.shields.io/github/license/Shillaker/hoststats.svg)](https://github.com/Shillaker/hoststats/blob/master/LICENSE.md)  [![Release](https://img.shields.io/github/release/Shillaker/hoststats.svg)](https://github.com/Shillaker/hoststats/releases/)

`hoststats` captures resource usage (CPU, memory, network, disk) on a set of
remote hosts over a period of time.

Collection can be started and stopped from a client host via HTTP or the
included Python API. Results are written to a CSV file on the client machine.

## The `hoststats` server

The `hoststats` server must run on each host from which you wish to collect
metrics, and port `5000` must be accessible to the client.

### Using Docker

```bash
# Run container in background
docker run -d --rm -p 5000:5000 shillaker/hoststats:0.0.5

# Check
curl http://localhost:5000/ping
```

### Using Pip

```bash
# Install
pip3 install hoststats

# Start the server in the background, e.g.
nohup hoststats start > /var/log/hoststats.log 2>&1 &

# Check
curl http://localhost:5000/ping
```

## The `hoststats` client

The `hoststats` client host can access `hoststats` servers in two ways.

### Python API

```python
from hostats.client import HostStats

# Create list of IPs/ hostnames for target hosts
ip_list = ["1.2.3.4", "5.6.7.8"]

# Set up the client
hs = HostStats(ip_list)

# Start collection
hs.start_collection()

# Wait some time

# Write stats to CSV
hs.stop_and_write_to_csv("hoststats.csv")
```

### HTTP API

Note that although the HTTP API works, the data that comes out requires more
processing.

```bash
# Check a given host is running the server and accessible
curl http://<target_host>:5000/ping

# Start the recording
curl http://<target_host>:5000/start

# Wait some time

# Get stats as JSON
curl http://<target_host>:5000/stop > /tmp/hoststats.json
```

## Development

Ensure `pip` and `setuptools` are up to date and install requirements.

To develop:

```bash
pip3 install -e .
```

Run tests:

```bash
./bin/tests.sh
```

## Releasing

To push to PyPI, make sure you have set up [Twine keyring
support](https://twine.readthedocs.io/en/latest/#keyring-support), or a
[`pypirc`](https://packaging.python.org/specifications/pypirc/).

Then increment the version in `VERSION`.

Then:

```bash
# Tag the code
./bin/tag.sh

# Build the Docker image
./bin/build.sh

# Check the distributed tests passs
./bin/dist_test.sh

# Push the package
./bin/release.sh
```

Once everything looks good, create a release manually [on
Github](https://github.com/Shillaker/hoststats/releases/new).
