# hoststats

hoststats captures resource usage (memory usage, CPU cycles, network transfers)
for a set of hosts over a period of time.

A Python API is provided for starting and finishing collection, and pulling the
results to a CSV file.

## Usage

Start the hoststats server on each host with:

```bash
python3 -m hoststats start
```

Create a client on another host with:

```python
# Set up the client
ip_list = ["1.2.3.4", "5.6.7.8"]
hs = HostStats(ip_list)

# Start collection
hs.start_collection()

# Wait some time

# Write stats to CSV
hs.stop_and_write_to_csv("hoststats.csv")
```

## Development

Ensure `pip` and `setuptools` are up to date and install requirements.

To release:

```bash
./release.sh
```
