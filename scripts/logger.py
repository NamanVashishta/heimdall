#!/usr/bin/env python3
"""
HEIMDALL — Data Logger
Records live 8x8 depth frames from VL53L8CX to a timestamped CSV file.
Usage: ~/venv/bin/python3 scripts/logger.py [optional_label]
"""

import csv
import os
import sys
import time
import datetime

from vl53l8cx_ctypes import VL53L8CX, RESOLUTION_8X8

# -------------------------------------------------------------------
# Setup
# -------------------------------------------------------------------
label = sys.argv[1] if len(sys.argv) > 1 else "session"

sensor = VL53L8CX()
sensor.set_resolution(RESOLUTION_8X8)
sensor.start_ranging()

log_dir = os.path.expanduser("~/heimdall/data")
os.makedirs(log_dir, exist_ok=True)

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{log_dir}/{label}_{ts}.csv"

# CSV columns: time_ms, z0_0 ... z7_7 (row-major, 64 zones)
header = ["time_ms"] + [f"z{r}_{c}" for r in range(8) for c in range(8)]

print(f"\n🔱 HEIMDALL Logger")
print(f"📡 Output → {filename}")
print(f"ℹ️  Label : {label}")
print(f"\n👋 WAVE YOUR HAND NOW to mark T=0 sync point")
print(f"   Then hold still and begin scenario.\n")
print(f"   Ctrl+C to stop.\n")

# -------------------------------------------------------------------
# Main loop
# -------------------------------------------------------------------
with open(filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)

    start = time.monotonic()
    frame = 0

    try:
        while True:
            if sensor.data_ready():
                data = sensor.get_data()
                distances = list(data.distance_mm[0][:64])
                elapsed_ms = int((time.monotonic() - start) * 1000)

                writer.writerow([elapsed_ms] + distances)
                f.flush()  # Ensure data is written even if killed externally

                frame += 1
                min_d = min(distances)
                max_d = max(distances)
                print(
                    f"\r✅ Frame {frame:5d} | {elapsed_ms:7d}ms | "
                    f"Min: {min_d:4d}mm  Max: {max_d:4d}mm",
                    end=""
                )

            time.sleep(0.001)

    except KeyboardInterrupt:
        print(f"\n\n🛑 Stopped.")
        print(f"   {frame} frames written → {filename}")
        print(f"   Duration: {int((time.monotonic() - start))}s\n")
