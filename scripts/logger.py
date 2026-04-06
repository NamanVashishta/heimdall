#!/usr/bin/env python3
"""
HEIMDALL — Data Logger
Records live 8x8 depth frames from VL53L8CX to a timestamped CSV.

Usage:
    ~/venv/bin/python3 scripts/logger.py [label]

CSV columns:
    timestamp   — real wall-clock time HH:MM:SS.mmm  (matches Timestamp Camera video)
    z0_0..z7_7  — 64 depth zones in mm, row-major order

Sync method:
    Record iPhone video with 'Timestamp Camera' app.
    Wave hand in front of sensor for 2s at start of each scenario.
    In video: see wave + clock time. In CSV: find the distance spike at that time.
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

# CSV header
header = ["timestamp"] + [f"z{r}_{c}" for r in range(8) for c in range(8)]

print(f"\n🔱 HEIMDALL Logger")
print(f"📡 Output  → {filename}")
print(f"🏷️  Label   → {label}")
print(f"🕐 Started → {datetime.datetime.now().strftime('%H:%M:%S')}")
print(f"\n👋 Wave hand in front of sensor to mark each scenario start")
print(f"   Ctrl+C to stop.\n")

# -------------------------------------------------------------------
# Main loop
# -------------------------------------------------------------------
with open(filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)

    frame = 0

    try:
        while True:
            if sensor.data_ready():
                data = sensor.get_data()
                distances = list(data.distance_mm[0][:64])
                now = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]

                writer.writerow([now] + distances)
                f.flush()

                frame += 1
                min_d = min(distances)
                max_d = max(distances)
                print(
                    f"\r✅ Frame {frame:5d} | {now} | "
                    f"Min: {min_d:4d}mm  Max: {max_d:4d}mm",
                    end=""
                )

            time.sleep(0.001)

    except KeyboardInterrupt:
        stop_time = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"\n\n🛑 Stopped at {stop_time}")
        print(f"   {frame} frames written → {filename}\n")
