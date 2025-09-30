import os
import csv
import time
import numpy as np
from datetime import datetime

import board, busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

def ask(prompt, cast=int, default=None, valid=lambda x: True):
    """Generic input prompt with default fallback and validation."""
    raw = input(prompt)
    try:
        value = cast(raw)
        if valid(value):
            return value
    except ValueError:
        pass
    return default

# --- Hardware setup ---
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 2/3          # ±6.144 V FSR (inputs must stay within 0..VDD)
ads.data_rate = 128     # target 128 SPS
PERIOD = 1.0 / ads.data_rate

# --- CSV setup ---
csv_name = input("Enter CSV file name (e.g. results.csv): ").strip()
if not csv_name.endswith(".csv"):
    csv_name += ".csv"
out_dir = "data/test-logs"
os.makedirs(out_dir, exist_ok=True)
csv_path = os.path.join(out_dir, csv_name)

new_file = not os.path.exists(csv_path)

print(f"\nLogging to: {csv_path}")
print(f"gain={ads.gain:.2f}, data_rate={ads.data_rate}\n")

with open(csv_path, "a", newline="") as f:
    writer = csv.writer(f)
    if new_file:
        writer.writerow(["Timestamp", "Gain", "Data_Rate", "Reference_V", "Channel", "N", "Mean_V", "Stdev_V"])

    try:
        while True:
            reference = ask("Enter sample reference voltage (Enter to quit): ", str, "")
            if reference == "":
                print("Quitting.")
                break

            ch = ask("Enter input channel (P0/P1/P2; default P0): ",
                     str, "P0", lambda s: s.upper() in {"P0", "P1", "P2"}).upper()
            n = ask("Enter number of samples to average (default 1000): ",
                    int, 1000, lambda x: x > 0)

            A = AnalogIn(ads, getattr(ADS, ch))

            # Collect n samples paced at 128 SPS
            samples = np.empty(n, dtype=float)
            next_tick = time.perf_counter()
            for i in range(n):
                while True:
                    now = time.perf_counter()
                    dt = next_tick - now
                    if dt <= 0:
                        break
                    if dt > 0.002:
                        time.sleep(dt - 0.001)
                    # else spin
                samples[i] = A.voltage
                next_tick += PERIOD

            mean_v = np.mean(samples)
            stdev_v = np.std(samples, ddof=1)

            print(f"→ {reference} on {ch}: mean = {mean_v:.6f} V (N={n}), stdev = {stdev_v:.6f} V")

            writer.writerow([
                datetime.now().isoformat(), ads.gain, ads.data_rate,
                reference, ch, n,
                f"{mean_v:.9f}", f"{stdev_v:.9f}"
            ])
            f.flush()
            os.fsync(f.fileno())

    except KeyboardInterrupt:
        print("\nInterrupted. File saved.")
