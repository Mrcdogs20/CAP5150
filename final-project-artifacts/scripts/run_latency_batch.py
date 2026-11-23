
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path.home() / "Desktop/vpn-ssh-research"
CLIENT = BASE / "tcp_latency_client.py"
SSH_KEY = Path.home() / ".ssh/vpn_research_key"

KALI_IP = "192.168.4.36"
WG_IP = "10.10.0.2"
KALI_USER = "mrcdogs20"

COUNT = 100
DELAY = 15

if len(sys.argv) != 3:
    sys.exit(
        "Usage: python3 run_latency_batch.py "
        "<direct|ssh|wireguard> <runs>"
    )

config = sys.argv[1].lower()

if config not in ("direct", "ssh", "wireguard"):
    sys.exit("Invalid configuration")

try:
    runs = int(sys.argv[2])
    if runs < 1:
        raise ValueError
except ValueError:
    sys.exit("Runs must be a positive integer")

output_dir = BASE / "latency" / config
output_dir.mkdir(parents=True, exist_ok=True)

for i in range(1, runs + 1):
    print(f"\n===== {config.upper()} LATENCY RUN {i}/{runs} =====",
          flush=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    output = output_dir / f"{config}_official_{timestamp}.csv"

    tunnel = None

    try:
        if config == "ssh":
            tunnel = subprocess.Popen([
                "ssh",
                "-i", str(SSH_KEY),
                "-o", "IdentitiesOnly=yes",
                "-o", "BatchMode=yes",
                "-o", "ExitOnForwardFailure=yes",
                "-N",
                "-L", "5002:127.0.0.1:5001",
                f"{KALI_USER}@{KALI_IP}"
            ], stdout=subprocess.DEVNULL,
               stderr=subprocess.PIPE)

            time.sleep(2)

            if tunnel.poll() is not None:
                sys.exit("SSH tunnel failed to start")

            host, port = "127.0.0.1", "5002"

        elif config == "wireguard":
            host, port = WG_IP, "5001"

        else:
            host, port = KALI_IP, "5001"

        command = [
            sys.executable,
            str(CLIENT),
            "--host", host,
            "--port", port,
            "--count", str(COUNT),
            "--output", str(output)
        ]

        subprocess.run(command, check=True)

        if not output.is_file() or output.stat().st_size == 0:
            sys.exit("Latency CSV was not saved correctly")

        print(f"Saved: {output}", flush=True)

    except subprocess.CalledProcessError:
        sys.exit(
            f"Latency run {i} failed. Stopping batch."
        )

    finally:
        if tunnel is not None:
            tunnel.terminate()
            try:
                tunnel.wait(timeout=5)
            except subprocess.TimeoutExpired:
                tunnel.kill()
                tunnel.wait()

    if i < runs:
        print(f"Waiting {DELAY} seconds...", flush=True)
        time.sleep(DELAY)

print(f"\nCompleted {runs} {config} latency runs.")
