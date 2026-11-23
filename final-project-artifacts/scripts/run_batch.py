import subprocess
import sys
import time
from pathlib import Path

SCRIPT = Path.home() / "Desktop/vpn-ssh-research/scripts/run_trial.py"

if len(sys.argv) != 3:
    print("Usage: python3 run_batch.py <direct|ssh|wireguard> <count>")
    sys.exit(1)

config = sys.argv[1].lower()
count = int(sys.argv[2])

if config not in ("direct", "ssh", "wireguard") or count < 1:
    sys.exit("Invalid configuration or trial count")

for i in range(1, count + 1):
    print(f"\n===== {config.upper()} TRIAL {i}/{count} =====", flush=True)

    result = subprocess.run(
        [sys.executable, str(SCRIPT), config]
    )

    if result.returncode != 0:
        sys.exit(f"Trial {i} failed. Stopping batch.")

    if i < count:
        print("Waiting 15 seconds before next trial...")
        time.sleep(15)

print(f"\nCompleted {count} {config} trials.")