import csv, datetime, time, os
from vl53l8cx_ctypes import VL53L8CX, RESOLUTION_8X8

sensor = VL53L8CX()
sensor.set_resolution(RESOLUTION_8X8)
sensor.start_ranging()

os.makedirs(os.path.expanduser("~/heimdall/data"), exist_ok=True)
fname = os.path.expanduser(f"~/heimdall/data/log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

print(f"Logging to {fname} — Ctrl+C to stop")

with open(fname, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["time"] + [f"z{r}_{c}" for r in range(8) for c in range(8)])
    n = 0
    try:
        while True:
            if sensor.data_ready():
                d = list(sensor.get_data().distance_mm[0][:64])
                w.writerow([datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]] + d)
                f.flush()
                n += 1
                print(f"\rFrames: {n}", end="")
            time.sleep(0.001)
    except KeyboardInterrupt:
        print(f"\nDone. {n} frames saved to {fname}")
