import time
import json
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from collections import deque
import ipywidgets as widgets
from IPython.display import display
import matplotlib.pyplot as plt
import numpy as np

class CalibrationSession:
    def __init__(self, sensor, window_size=10, stabilization_tolerance=0.1, sampling_rate=0.1):
        self.window_size = window_size
        self.stabilization_tolerance = stabilization_tolerance
        self.sampling_rate = sampling_rate
        
        # Sensor type and units
        self.sensor = sensor
        self.units = "pH" if sensor == "pH" else "NTU" if sensor == "Turbidity" else "ppm" if  sensor == "TDS" else "Unknown"
        self.channel = ADS.P0 if sensor == "pH" else ADS.P1 if sensor == "TDS" else ADS.P2 if sensor == "Turbidity" else None

        self.samples = []
        self.standards = []

        # Set up widgets
        self.standard_input = widgets.IntText(
            value=0,
            description="Standard:"
        )
        self.unit_display = widgets.Label(
            value=f"{self.units}",
            style={'description_width': 'auto'}
        )

        self.start_button = widgets.Button(
            description='Start Sampling',
            button_style='',
            layout=widgets.Layout(margin='auto auto auto 20px')
        )
        self.start_button.on_click(self.start_sampling)

        self.mean_display = widgets.Label(value="Mean: N/A")
        self.stdev_display = widgets.Label(value="Standard Deviation: N/A")
        self.status_display = widgets.Label(value="Waiting...")

        # Plot setup
        plt.ion()  # Enable interactive mode
        self.fig, self.ax = plt.subplots(figsize=(7, 5))
        self.scatter = None
        self.fit_line = None
        self.ax.set_xlabel(f"Standard ({self.units})")
        self.ax.set_ylabel("Voltage (V)")
        self.ax.set_title(f"{self.sensor} Calibration")
        self.ax.grid(True)

        # Display layout
        self.hbox = widgets.HBox([self.standard_input, self.unit_display, self.start_button])
        self.vbox = widgets.VBox([self.hbox, self.mean_display, self.stdev_display, self.status_display])
        display(self.vbox)
        #display(self.fig)

        # Initialize the ADS1115 ADC
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        ads.gain = 2 / 3

        self.analog_input = AnalogIn(ads, self.channel)

        
    def sample_until_stable(self):
        sub_samples = deque(maxlen=self.window_size)

        while True:
            voltage = np.random.uniform(1.95, 2.05)  # Replace with actual sensor reading
            sub_samples.append(voltage)

            if len(sub_samples) == self.window_size:
                mean = np.mean(sub_samples)
                stdev = np.std(sub_samples)

                self.mean_display.value = f"Mean: {mean:.4f} V"
                self.stdev_display.value = f"Standard Deviation: {stdev:.6f} V"

                if stdev < self.stabilization_tolerance:
                    self.status_display.value = "✅ Stable"
                    return mean
                else:
                    self.status_display.value = "Stabilizing..."
            else:
                self.status_display.value = f"Collecting... {len(sub_samples)}/{self.window_size}"

            time.sleep(self.sampling_rate)

    def start_sampling(self, button=None):
        mean = self.sample_until_stable()
        self.samples.append(mean)
        self.standards.append(self.standard_input.value)

        self.update_plot()

    def update_plot(self):
        self.ax.cla()
        self.ax.set_xlabel(f"Standard ({self.units})")
        self.ax.set_ylabel("Voltage (V)")
        self.ax.set_title(f"{self.sensor} Calibration")
        self.ax.grid(True)

        # Plot the calibration points
        self.scatter = self.ax.scatter(self.standards, self.samples, color='blue', label='Calibration Points')

        self.ax.legend()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
