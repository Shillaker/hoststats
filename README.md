# hoststats [![Tests](https://github.com/Shillaker/hoststats/workflows/Tests/badge.svg?branch=master)](https://github.com/Shillaker/hoststats/actions) [![License](https://img.shields.io/github/license/Shillaker/hoststats.svg)](https://github.com/Shillaker/hoststats/blob/master/LICENSE.md)  [![Release](https://img.shields.io/github/release/Shillaker/hoststats.svg)](https://github.com/Shillaker/hoststats/releases/)

`hoststats` captures resource usage (CPU, memory, network, disk) on a set of
remote hosts over a period of time.

Collection can be started and stopped from a client host via HTTP or the
included Python API. Results are written to a CSV file on the client machine.

## Usage

Install:

```bash
pip3 install hoststats
```

Start the hoststats server (must be done on each host on which you wish to
collect stats). Note that this runs in the foreground, so you can put it to the
background however you see fit, e.g.

```bash
hoststats start 2>&1 > /tmp/hoststats.log
```

Check it's up with:

```bash
curl <hostname>:5000/ping
```

Create a client on another host with:

```python
# Get list of IPs/ hostnames for hosts to be monitored
ip_list = ["1.2.3.4", "5.6.7.8"]

# Set up the client
hs = HostStats(ip_list)

# Start collection
hs.start_collection()

# Wait some time

# Write stats to CSV
hs.stop_and_write_to_csv("hoststats.csv")
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
