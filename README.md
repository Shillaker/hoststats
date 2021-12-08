# hoststats [![Tests](https://github.com/Shillaker/hoststats/workflows/Tests/badge.svg?branch=master)](https://github.com/Shillaker/hoststats/actions) [![License](https://img.shields.io/github/license/Shillaker/hoststats.svg)](https://github.com/Shillaker/hoststats/blob/master/LICENSE.md)  [![Release](https://img.shields.io/github/release/Shillaker/hoststats.svg)](https://github.com/Shillaker/hoststats/releases/)

`hoststats` captures resource usage (CPU, memory, network, disk) on a set of
remote hosts or containers over a period of time, then lets you aggregate and
filter the results using Pandas.

Usage:

1. Start collection from a client host via HTTP or `kubectl` using the Python
   client, or directly over HTTP.
2. Stop collection, at which point `hoststats` pulls the results from all hosts
   into a single CSV file on the client machine.
3. Use `hoststats` to load, aggregate and filter data from this CSV using
   Pandas.

## The `hoststats` server

The `hoststats` server must run on each host/ container from which you wish to
collect metrics, and port `5000` must be accessible to the client if you wish to
use HTTP.

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

### Directly via HTTP API

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

## Proxies

If your client host can't directly access the target hosts, you can specify a
proxy server, which must also have the `hoststats` server running. This proxy
can also be included in the list of target hosts.

To use a proxy, you just need to provide an extra argument to the `HostStats`
constructor:

```python
from hostats.client import HostStats

# List of IPs/ hostnames accessible from the proxy
ip_list = ["1.2.3.4", "5.6.7.8"]

# Proxy IP/ hostname accessible from the client
proxy_ip = "9.8.7.6"

# Set up the client
hs = HostStats(ip_list, proxy=proxy_ip)
```

## Kubectl

If running in a Kubernetes cluster, you can use `kubectl` rather than HTTP. This
is useful if your client host is outside the cluster and you don't have direct
ingress to each container you're gathering stats from.

To use `kubectl`, you need to pass certain arguments to the `HostStats`
constructor, and the list of hosts should be a list of pod names:

```python
from hostats.client import HostStats

# List of pod names
pods = ["pod-a", "pod-b", "pod-c"]

# Set up the client
hs = HostStats(
    pods,
    kubectl=True,
    kubectl_ns="my-namespace", # K8s namespace (optional)
    kubectl_container="my-container", # Container name within the pod (optional)
)
```

## Handling results

If the data has been written to CSV via the Python API, you can access the data
with the `HostStatsResults` class:

```python
from hoststats.results import HostStatsResults

csv_file = "hoststats.csv"
s = HostStatsResults(csv_file)

# Get list of hosts in results
s.get_hosts()

# Get list of available stats
s.get_stats()

# Get timeseries of given stat per host
s.get_stat_per_host("CPU_PCT")

# Get average stat across hosts
s.get_avg_stat("MEMORY_USED")
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

### Developing on a local cluster

If you want to run distributed tests against your local modifications, you can
run the following:

```bash
# Start up some hoststats containers and enter the client container
./bin/dev.sh
```

From within this container, run tests:

```bash
# Non-distributed tests
nosetests hoststats.tests --nocapture

# Distributed tests
nosetests hoststats.disttest --nocapture
```

You can then edit files and restart the target containers with:

```bash
./bin/dev_restart.sh
```

Once restarted, you can rerun the tests against servers with your changes.

See the scripts mentioned above and
[`docker-compose-dev.yml`](docker-compose-dev.yml) for more info.

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
./bin/dist_tests.sh

# Push the package
./bin/release.sh
```

Once everything looks good, create a release manually [on
Github](https://github.com/Shillaker/hoststats/releases/new).

After that, merge the PR, then retag from the master branch.
