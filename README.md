# Evaluating Security and Performance Trade-offs Between WireGuard VPN and SSH Tunneling in LAN Environments

## Project Overview

This project evaluates the security and performance trade-offs between WireGuard VPN and SSH tunneling in a local area network (LAN) environment. Three network configurations were compared:

1. **Direct LAN:** Communication without an encrypted tunnel, serving as the baseline.
2. **SSH Tunneling:** Application-layer tunneling using OpenSSH local TCP port forwarding.
3. **WireGuard VPN:** Network-layer tunneling using WireGuard.

The evaluation focuses on throughput, TCP latency, CPU and memory utilization, packet visibility, and deployment complexity.

This research was conducted as part of the CAP 5150 Computer Security course at the University of Central Florida.

## Experimental Environment

The experiments were conducted using two devices connected to the same wireless LAN.

| Component | Configuration |
|---|---|
| Client | MacBook Air M4, macOS |
| Server | Dell Inspiron, Kali Linux |
| Network | Home Wi-Fi LAN (eero 6+ mesh network) |
| SSH | OpenSSH local TCP port forwarding |
| VPN | WireGuard |
| Throughput testing | iperf3 |
| Latency testing | Python TCP echo client/server |
| Resource monitoring | top, vmstat, pidstat |
| Packet analysis | Wireshark |

Both devices remained stationary during testing to help reduce wireless variability.

## Methodology

### Throughput

Throughput was measured using `iperf3`, with the macOS device acting as the client and Kali Linux as the server.

- 10 trials per configuration
- 30 seconds per trial
- Receiver-side throughput recorded in Mbps
- 15-second intervals between trials

### TCP Latency

Latency was measured using a Python TCP echo client and server.

- 10 runs per configuration
- 100 measured exchanges per run
- 10 warm-up exchanges excluded from each run
- 64-byte payloads
- Round-trip times recorded in milliseconds

### CPU and Memory Utilization

System resource utilization was monitored during throughput experiments using `top` on macOS and `vmstat` and `pidstat` on Kali Linux.

### Packet Visibility

Wireshark captures were collected for Direct LAN, SSH tunneling, and WireGuard VPN configurations to compare visible network information and encrypted application traffic.

## Summary of Results

### Throughput

| Configuration | Average Throughput (Mbps) |
|---|---:|
| Direct LAN | 123.66 |
| SSH Tunneling | 124.99 |
| WireGuard VPN | 97.65 |

SSH tunneling achieved throughput comparable to Direct LAN, while WireGuard showed lower throughput in the tested wireless environment.

### TCP Echo Latency

| Configuration | Mean RTT (ms) | Median RTT (ms) |
|---|---:|---:|
| Direct LAN | 9.78 | 5.75 |
| SSH Tunneling | 10.60 | 6.51 |
| WireGuard VPN | 9.75 | 6.87 |

The latency results showed relatively small differences between configurations, although wireless variability and occasional outliers affected the measurements.

### Security Observations

Direct LAN HTTP traffic exposed application contents in packet captures. SSH tunneling and WireGuard VPN encrypted the tunneled application traffic while still exposing some outer network metadata.

SSH provided application-specific TCP forwarding, while WireGuard supported broader IP-level tunneling.

## Repository Structure

```text
wireguard-ssh-lan-evaluation/
├── README.md
├── scripts/
│   ├── run_batch.py
│   ├── run_trial.py
│   ├── run_latency_batch.py
│   ├── tcp_latency_client.py
│   └── tcp_latency_server.py
├── results/
│   ├── throughput/
│   │   ├── Direct/
│   │   ├── SSH/
│   │   └── WireGuard/
│   ├── latency/
│   │   ├── Direct/
│   │   ├── SSH/
│   │   └── WireGuard/
│   └── CPU & Memory/
│       ├── Kali_Linux/
│       │   ├── Direct/
│       │   ├── SSH/
│       │   └── WireGuard/
│       └── macOS/
│           ├── Direct/
│           ├── SSH/
│           └── WireGuard/
├── captures/
├── config-examples/
└── report/
    └── final_report.pdf
```

### Directory Descriptions

- **`scripts/`** — Python scripts used to automate throughput and latency experiments.
- **`results/throughput/`** — Throughput measurements for Direct LAN, SSH tunneling, and WireGuard VPN.
- **`results/latency/`** — TCP echo RTT measurements for each configuration.
- **`results/CPU & Memory/`** — Resource monitoring logs organized by operating system and network configuration.
- **`captures/`** — Wireshark packet captures collected during the packet visibility evaluation.
- **`config-examples/`** — Sanitized examples of SSH and WireGuard tunnel configurations.
- **`report/`** — Final research paper containing the complete methodology, evaluation, discussion, and references.

## Reproducing the Experiments

### Prerequisites

- macOS client and Linux server connected to the same LAN
- Python 3
- OpenSSH
- WireGuard
- iperf3
- `sysstat` utilities (`pidstat`) and `vmstat`
- Wireshark for packet capture analysis

### Throughput Testing

Start an `iperf3` server on Kali Linux:

```bash
iperf3 -s -p 5201
```

After configuring the SSH and WireGuard connections and updating the local settings in `run_trial.py`, execute:

```bash
python3 scripts/run_batch.py direct 10
python3 scripts/run_batch.py ssh 10
python3 scripts/run_batch.py wireguard 10
```

Each command runs ten throughput trials for the selected configuration.

### TCP Latency Testing

Start the TCP echo server on Kali Linux using the included server script, then execute the following commands on macOS:

```bash
python3 scripts/run_latency_batch.py direct 10
python3 scripts/run_latency_batch.py ssh 10
python3 scripts/run_latency_batch.py wireguard 10
```

These commands perform ten latency runs for each configuration and save the measured RTT values to CSV files.

**Note:** The scripts use local paths, SSH credentials, and network addresses that must be configured for the testing environment. Private keys are not included in this repository.

## Limitations

All experiments were conducted on a shared wireless LAN, where background network activity and wireless conditions could influence results. CPU and memory measurements reflect system-wide activity rather than isolated tunnel overhead. Packet visibility observations were based on captures from the macOS client's network interface.

The results represent the tested environment and should not be generalized to all network conditions or hardware configurations.

## Research Report

The complete methodology, results, discussion, and references are provided in the final research paper in the `report/` directory.
