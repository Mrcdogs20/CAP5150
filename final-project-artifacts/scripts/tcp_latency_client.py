
import socket
import time
import statistics
import argparse
import csv
import os

parser = argparse.ArgumentParser()
parser.add_argument("--host", required=True)
parser.add_argument("--port", type=int, default=5001)
parser.add_argument("--count", type=int, default=100)
parser.add_argument("--output", default=None)
args = parser.parse_args()

payload = b"X" * 64
latencies = []

with socket.create_connection((args.host, args.port), timeout=5) as sock:
    sock.settimeout(5)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    # Warm up the connection.
    for _ in range(10):
        sock.sendall(payload)
        received = b""
        while len(received) < len(payload):
            chunk = sock.recv(len(payload) - len(received))
            if not chunk:
                raise ConnectionError("Connection closed")
            received += chunk

    # Collect TCP round-trip measurements.
    for i in range(args.count):
        start = time.perf_counter_ns()
        sock.sendall(payload)

        received = b""
        while len(received) < len(payload):
            chunk = sock.recv(len(payload) - len(received))
            if not chunk:
                raise ConnectionError("Connection closed")
            received += chunk

        end = time.perf_counter_ns()
        rtt = (end - start) / 1_000_000
        latencies.append(rtt)
        time.sleep(0.2)

print(f"\nTCP Latency Results ({args.host}:{args.port})")
print(f"Samples: {len(latencies)}")
print(f"Minimum RTT: {min(latencies):.3f} ms")
print(f"Average RTT: {statistics.mean(latencies):.3f} ms")
print(f"Maximum RTT: {max(latencies):.3f} ms")
print(f"Std. Deviation: {statistics.stdev(latencies):.3f} ms")

# Save each RTT sample to CSV.
if args.output:
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    with open(args.output, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["sample", "rtt_ms"])

        for i, rtt in enumerate(latencies, start=1):
            writer.writerow([i, round(rtt, 3)])

    print(f"Results saved to: {args.output}")

      
