import sys, time, os
sys.path.insert(0, '/home/impact-alert/heimdall/driver/vl53l8cx/library')
from vl53l8cx_ctypes import VL53L8CX, RESOLUTION_8X8

# Shading characters — dim to bright
SHADES = " ░▒▓█"

def mm_to_shade(mm):
    if mm <= 0 or mm > 4000:
        return "?"
    # 0-500mm = bright, 3500-4000mm = dim
    idx = int((1 - min(mm, 3500) / 3500) * (len(SHADES) - 1))
    return SHADES[idx]

sensor = VL53L8CX()
sensor.set_resolution(RESOLUTION_8X8)
sensor.start_ranging()

print("🔱 HEIMDALL — Live 8x8 Depth Stream (Ctrl+C to stop)\n")

try:
    while True:
        while not sensor.data_ready():
            time.sleep(0.005)

        data = sensor.get_data()
        distances = data.distance_mm[0]  # 64 values, 8x8

        os.system('clear')
        print("🔱 HEIMDALL — Live 8x8 Depth Stream (Ctrl+C to stop)\n")
        print("  Close ◄────────────────────────────► Far\n")

        for row in range(8):
            row_vals = distances[row * 8:(row + 1) * 8]
            shade_row = "  ".join(mm_to_shade(v) * 2 for v in row_vals)
            mm_row = "  ".join(f"{v:4d}" for v in row_vals)
            print(f"  {shade_row}   │  {mm_row}")

        print(f"\n  Min: {min(v for v in distances if v > 0):4d}mm   Max: {max(distances):4d}mm")

except KeyboardInterrupt:
    sensor.stop_ranging()
    print("\nStream stopped.")
