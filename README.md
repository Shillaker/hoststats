# hoststats

hoststats captures resource usage (memory usage, CPU cycles, network transfers)
for a set of hosts over a period of time.

A Python API is provided for starting and finishing collection, and pulling the
results to a CSV file.

This is just hacked together to support experiments on distributed systems, and
is not intended for anything more serious.

## Usage

Install:

```bash
pip3 install hoststats
```

Start the hoststats server (must be done on each host on which you wish to
collect stats):

```bash
hoststats start
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

To release, make sure you have set up [Twine keyring
support](https://twine.readthedocs.io/en/latest/#keyring-support), or a
[`pypirc`](https://packaging.python.org/specifications/pypirc/), then:

```bash
./release.sh
```
