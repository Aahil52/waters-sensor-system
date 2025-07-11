import time
import json
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from collections import deque
import numpy as np
import csv
from datetime import datetime
import json
import plotext as plt

class Style:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    UP = '\033[F'
    CLEAR = '\033[K'
    SEPARATOR = '-' * 120

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

def sample_until_stable(analog_input, window_size=200, sampling_rate=0.01, stabilization_tolerance=0.003):
    """Sample the sensor until the standard deviation stabilizes below a threshold."""
    sub_samples = deque(maxlen=window_size)

    while True:
        voltage = analog_input.voltage
        sub_samples.append(voltage)

        if len(sub_samples) == window_size:
            mean = np.mean(sub_samples)
            stdev = np.std(sub_samples)

            print(f"Mean: {mean:.4f} V | Std Dev: {stdev:.6f} V", end='\r')
            print(Style.CLEAR, end='')

            if stdev < stabilization_tolerance:
                return mean
        else:
            print(f"Collecting... {len(sub_samples)}/{window_size}", end='\r')
            print(Style.CLEAR, end='')

        time.sleep(sampling_rate)

def initialize_adc(channel_index):
    """Initialize the ADS1115 on the selected channel."""
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    ads.gain = 2 / 3
    return AnalogIn(ads, getattr(ADS, f'P{channel_index}'))

def collect_samples(analog_input, num_standards, num_samples, sensor):
    """Collect samples for calibration based on user-defined standards."""
    samples = {}

    for i in range(num_standards):
        standard = ask(
            f"Enter standard {i + 1}/{num_standards} for {sensor['name'].lower()} (default 0.0 {sensor['unit']}): ",
            cast=float,
            default=0.0,
            valid=lambda x: x >= 0.0
        )

        samples[standard] = []

        for j in range(num_samples):
            print(f"Samples for {standard} {sensor['unit']}: [{', '.join(f'{s:.4f}' for s in samples[standard])}]")
            print(Style.SEPARATOR)

            input(f"Press enter when ready to collect sample {j + 1}/{num_samples} for {standard} {sensor['unit']}.")
            print(Style.UP + Style.CLEAR, end='')

            sample = sample_until_stable(analog_input, 
                                         window_size=200, 
                                         sampling_rate=0.01, 
                                         stabilization_tolerance=0.03)
            samples[standard].append(sample)

            print(Style.CLEAR + Style.UP + Style.CLEAR + Style.UP + Style.CLEAR, end='')

        print(f"Samples for {standard} {sensor['unit']}: [{', '.join(f'{s:.4f}' for s in samples[standard])}]")
        print(Style.SEPARATOR)

    # Ready for saving, fitting, or exporting later
    return samples

def samples_to_arrays(samples):
    """Format samples for plotting or further processing."""
    x = []
    y = []
    for standard, voltages in samples.items():
        for v in voltages:
            x.append(v)
            y.append(standard)
    return np.array(x), np.array(y)

def fit(x, y, degree):
    coeffs = np.polyfit(x, y, deg=degree)
    p = np.poly1d(coeffs)

    y_pred = p(x)
    residuals = y - y_pred

    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y - np.mean(y))**2)

    r_squared = 1 - (ss_res / ss_tot)
    mse = np.mean(residuals**2)

    return coeffs, r_squared, mse

def plot_fit(x, y, coeffs, sensor):
    p = np.poly1d(coeffs)

    # Create smoother curve for fit
    x_fit = np.linspace(min(x), max(x), 100)
    y_fit = p(x_fit)

    plt.clear_figure()
    plt.plot(x_fit, y_fit, marker="*", color="green")
    plt.scatter(x, y, marker="star", color="red")

    plt.title(f"{sensor['name']} Calibration Curve")
    plt.xlabel("Voltage (V)")
    plt.ylabel(f"{sensor['name']} ({sensor['unit']})")
    plt.plot_size(100, 20)
    plt.show()

def log_samples(samples, sensor):
    sensor_name = sensor['name'].lower().replace(' ', '_')
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"data/calibration-logs/{sensor_name}_calibration_{timestamp}.csv"

    with open(filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([sensor['unit'], "voltage"])

        for standard, voltages in samples.items():
            for v in voltages:
                writer.writerow([standard, f"{v:.6f}"])

    print(f"Calibration samples for {sensor['name']} logged at: `{filename}`")

    return filename

def apply_calibration(coeffs, degree, log, sensor):
    sensor_name = sensor['name'].lower().replace(' ', '_')
        
    calibration = {}

    try:
        with open('data/calibration.json', 'r') as f:
            calibration = json.load(f)
    except Exception:
        calibration = {}

    with open('data/calibration.json', 'w') as f:
        calibration[sensor_name] = {
            "coeffs": coeffs.tolist(),
            "degree": degree,
            "log": log
        }
        json.dump(calibration, f, indent=4)
        

    print(f"Calibration coefficients for {sensor['name']} saved to calibration.json.")

def main():
    print("Welcome to the Sensor Calibration Tool!\n")
    sensors = ["Turbidity", "Total Dissolved Solids", "pH"]
    units = ["NTU", "ppm", "pH"]

    print(Style.SEPARATOR)
    print("Available sensors:")
    for i, sensor in enumerate(sensors):
        print(f"{i}. {sensor}")
    print(Style.SEPARATOR)

    sensor_index = ask(
        f"Select a sensor to calibrate (0-{len(sensors) - 1}, default 0): ",
        cast=int,
        default=0,
        valid=lambda x: 0 <= x < len(sensors)
    )

    channel_index = ask("Select the ADS channel (0-3, default 0): ", int, 0, lambda x: 0 <= x <= 3)
    num_standards = ask("Enter the number of standards to collect (default 3): ", int, 3, lambda x: x > 0)
    num_samples = ask("Enter the number of samples to collect for each standard (default 10): ", int, 10, lambda x: x > 0)

    sensor = {"name": sensors[sensor_index], "unit": units[sensor_index]}

    print(Style.SEPARATOR)
    print(f"Proceeding with {sensor['name'].lower()} calibration on ADC channel {channel_index} using {num_standards} standards with {num_samples} samples each.")
    print(Style.SEPARATOR)

    analog_input = initialize_adc(channel_index)

    samples = collect_samples(analog_input, num_standards, num_samples, sensor)

    degree = ask("Enter the degree of polynomial for fitting (default 1): ", int, 1, lambda x: x >= 0)
    
    x, y = samples_to_arrays(samples)

    try:
        coeffs, r_squared, mse = fit(x, y, degree)
    except Exception as e:
        print(f"Error during fitting: {e}")
        print("Exiting...")
        return

    print(Style.SEPARATOR)
    print(f"Calibration results for {sensor['name']}:")
    print(np.poly1d(coeffs))
    print(f"R-squared: {r_squared:.4f}")
    print(f"Mean Squared Error: {mse:.4f}")
    print(Style.SEPARATOR)
    plot_fit(x, y, coeffs, sensor)
    print(Style.SEPARATOR)

    option = ask("Would you like to apply the calibration and log the samples, only log the samples, or exit? (a/l/e, default 'a'): ",
                 cast=str, default='a', valid=lambda x: x in ['a', 'l', 'e'])
    print(Style.SEPARATOR)
    
    log = ""

    # Log the samples to a csv
    if(option in ['a', 'l']):
        log = log_samples(samples, sensor)

    # Write the coefficients to `coefficients.json`
    if(option in ['a']):
        apply_calibration(coeffs, degree, log, sensor)
        print(Style.SEPARATOR)

    print("\nProgram complete. Exiting...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Exiting...")
