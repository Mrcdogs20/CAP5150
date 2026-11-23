
import sys
import json
import time
import shlex
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# ==========================================
# RESEARCH CONFIGURATION
# ==========================================

BASE = Path.home() / "Desktop/vpn-ssh-research"

KALI_USER = "username_here"
KALI_IP = "X.X.X.X"
WG_IP = "X.X.X.X"

SSH_KEY = Path.home() / ".ssh/vpn_research_key"

IPERF_PORT = 5201
SSH_FORWARD_PORT = 5202
DURATION = 30

VALID_CONFIGS = ("direct", "ssh", "wireguard")

if len(sys.argv) != 2 or sys.argv[1].lower() not in VALID_CONFIGS:
    print("Usage: python3 run_trial.py [direct|ssh|wireguard]")
    sys.exit(1)

CONFIG = sys.argv[1].lower()

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%d_%H%M%S_%f"
)

TRIAL_NAME = f"{CONFIG}_official_{TIMESTAMP}"

# ==========================================
# FILE LOCATIONS
# ==========================================

throughput_dir = BASE / CONFIG
mac_resource_dir = BASE / "resources" / CONFIG

throughput_dir.mkdir(parents=True, exist_ok=True)
mac_resource_dir.mkdir(parents=True, exist_ok=True)

kali_resource_dir = (
    f"$HOME/vpn-ssh-research/resources/{CONFIG}"
)

json_path = throughput_dir / f"{TRIAL_NAME}.json"
mac_log = mac_resource_dir / f"mac_{TRIAL_NAME}.txt"
metadata_path = throughput_dir / f"{TRIAL_NAME}_metadata.json"

kali_vmstat_name = f"kali_vmstat_{TRIAL_NAME}.txt"
kali_pidstat_name = f"kali_pidstat_{TRIAL_NAME}.txt"

# ==========================================
# SSH HELPERS
# ==========================================

SSH_OPTIONS = [
    "-i", str(SSH_KEY),
    "-o", "IdentitiesOnly=yes",
    "-o", "BatchMode=yes",
    "-o", "ConnectTimeout=5"
]

SSH_TARGET = f"{KALI_USER}@{KALI_IP}"


def remote(command, timeout=20):
    result = subprocess.run(
        ["ssh", *SSH_OPTIONS, SSH_TARGET, command],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=True
    )
    return result.stdout.strip()


def start_ssh_tunnel():
    print("Starting SSH forwarding tunnel...")

    command = [
        "ssh",
        *SSH_OPTIONS,
        "-o", "ExitOnForwardFailure=yes",
        "-N",
        "-L",
        f"{SSH_FORWARD_PORT}:127.0.0.1:{IPERF_PORT}",
        SSH_TARGET
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )

    time.sleep(2)

    if process.poll() is not None:
        error = process.stderr.read()
        raise RuntimeError(
            f"SSH tunnel failed to start: {error}"
        )

    print("SSH tunnel started.")
    return process


# ==========================================
# PREREQUISITES
# ==========================================

def check_prerequisites():
    print("\nChecking prerequisites...")

    if not SSH_KEY.is_file():
        raise RuntimeError("Research SSH key not found.")

    print("Kali SSH:", remote("echo READY"))

    for program in ("iperf3", "vmstat", "pidstat"):
        path = remote(f"command -v {program}")
        print(f"Kali {program}: {path}")

    subprocess.run(
        ["iperf3", "--version"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

    # Confirm that Kali's iperf3 server is listening.
    listening = remote(
        "ss -lnt | grep -E '[:.]5201[[:space:]]'"
    )

    if not listening:
        raise RuntimeError(
            "Kali iperf3 server is not listening on port 5201."
        )

    print("Kali iperf3 server: listening")

    if CONFIG == "wireguard":
        print("Checking WireGuard connectivity...")

        subprocess.run(
            ["ping", "-c", "2", "-W", "2000", WG_IP],
            stdout=subprocess.DEVNULL,
            check=True
        )

        print("WireGuard connectivity: verified")


# ==========================================
# REMOTE RESOURCE MONITORING
# ==========================================

def start_kali_monitoring():
    print("\nStarting Kali resource monitoring...")

    directory = kali_resource_dir

    # Remote shell expands $HOME.
    # Filenames are generated locally and contain
    # only safe characters.

    command = (
        f"mkdir -p {directory} && "
        f"nohup vmstat -w -S M 1 {DURATION + 4} "
        f"> {directory}/{kali_vmstat_name} "
        f"2>/dev/null </dev/null & "
        f"nohup pidstat -u -r 1 {DURATION + 3} "
        f"> {directory}/{kali_pidstat_name} "
        f"2>/dev/null </dev/null & "
        f"echo MONITORING_STARTED"
    )

    output = remote(command, timeout=15)
    print(output)


def verify_kali_monitoring():
    print("\nVerifying Kali monitoring files...")

    command = (
        f"wc -l "
        f"{kali_resource_dir}/{kali_vmstat_name} "
        f"{kali_resource_dir}/{kali_pidstat_name}"
    )

    print(remote(command))

# ==========================================
# TEST EXECUTION
# ==========================================

def run_trial():
    print("\n========================================")
    print("VPN VS SSH RESEARCH - PRACTICE TRIAL")
    print("========================================")

    print("Configuration:", CONFIG)
    print("Trial ID:", TRIAL_NAME)

    check_prerequisites()

    tunnel = None
    mac_monitor = None

    if CONFIG == "direct":
        destination = KALI_IP
        port = IPERF_PORT

    elif CONFIG == "ssh":
        destination = "127.0.0.1"
        port = SSH_FORWARD_PORT

    else:
        destination = WG_IP
        port = IPERF_PORT

    try:
        if CONFIG == "ssh":
            tunnel = start_ssh_tunnel()

        start_kali_monitoring()

        print("Starting Mac resource monitoring...")

        with open(mac_log, "w") as output:
            mac_monitor = subprocess.Popen(
                [
                    "top",
                    "-l", str(DURATION + 4),
                    "-s", "1",
                    "-n", "10",
                    "-stats", "pid,command,cpu,mem"
                ],
                stdout=output,
                stderr=subprocess.DEVNULL
            )

            time.sleep(2)

            print("\nRunning iperf3 throughput test...")
            print("Destination:", destination)
            print("Port:", port)

            start_time = datetime.now(
                timezone.utc
            ).isoformat()

            with open(json_path, "w") as json_output:
                subprocess.run(
                    [
                        "iperf3",
                        "-c", destination,
                        "-p", str(port),
                        "-t", str(DURATION),
                        "-J"
                    ],
                    stdout=json_output,
                    check=True,
                    timeout=DURATION + 30
                )

            end_time = datetime.now(
                timezone.utc
            ).isoformat()

            print("Throughput test completed.")
            print("Waiting for Mac monitoring...")

            mac_monitor.wait(timeout=DURATION + 15)

        # Allow Kali monitoring to finish.
        time.sleep(3)
        verify_kali_monitoring()

        with open(json_path) as file:
            data = json.load(file)

        if "error" in data:
            raise RuntimeError(data["error"])

        receiver_mbps = (
            data["end"]["sum_received"]["bits_per_second"]
            / 1_000_000
        )

        retransmissions = (
            data["end"]["sum_sent"].get("retransmits")
        )

        metadata = {
            "trial_id": TRIAL_NAME,
            "configuration": CONFIG,
            "duration_seconds": DURATION,
            "start_time_utc": start_time,
            "end_time_utc": end_time,
            "destination": destination,
            "port": port,
            "receiver_mbps": receiver_mbps,
            "sender_reported_retransmissions": retransmissions,
            "retransmission_note": (
                "For SSH, iperf3 reports retransmissions "
                "on the local forwarded TCP connection, "
                "not the SSH transport's wireless TCP leg."
            )
        }

        with open(metadata_path, "w") as file:
            json.dump(metadata, file, indent=2)

        print("\n========================================")
        print("PRACTICE TRIAL RESULTS")
        print("========================================")

        print("Configuration:", CONFIG)
        print(f"Receiver throughput: {receiver_mbps:.2f} Mbps")
        print("Sender-reported retransmissions:", retransmissions)

        print("\nSaved files:")
        print("Throughput:", json_path)
        print("Mac monitoring:", mac_log)
        print("Metadata:", metadata_path)
        print("Kali monitoring:", kali_resource_dir)

        print("\nPractice trial completed.")

    finally:
        if mac_monitor is not None and mac_monitor.poll() is None:
            mac_monitor.terminate()
            try:
                mac_monitor.wait(timeout=5)
            except subprocess.TimeoutExpired:
                mac_monitor.kill()
                mac_monitor.wait()

        if tunnel is not None:
            print("\nClosing SSH tunnel...")
            tunnel.terminate()

            try:
                tunnel.wait(timeout=5)
            except subprocess.TimeoutExpired:
                tunnel.kill()
                tunnel.wait()

            if tunnel.stderr is not None:
                tunnel.stderr.close()

            print("SSH tunnel closed.")


if __name__ == "__main__":
    try:
        run_trial()
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        RuntimeError,
        OSError,
        KeyError,
        ValueError
    ) as error:
        print(f"\nERROR: {error}", file=sys.stderr)
        sys.exit(1)
