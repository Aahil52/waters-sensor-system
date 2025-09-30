import numpy as np
from random import randint
from time import sleep
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import json
import os
import glob

class Sensors:
    def __init__(self):
        with open('data/calibration.json', 'r') as f:
            self.coeffs = json.load(f)

        i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(i2c)
        self.ads.gain = 2/3

        self.TURBIDITY_CHANNEL = ADS.P1
        self.TOTAL_DISSOLVED_SOLIDS_CHANNEL = ADS.P2
        self.PH_CHANNEL = ADS.P0

        # Mount the temperature probe
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        base_dir = '/sys/bus/w1/devices/'
        # Get all the filenames begin with 28 in the path base_dir.
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'

    def read_adc_average(self, channel, num_samples=200, sampling_interval=0.01, rsd_tolerance=0.01, num_attempts=3):
        """
        Read the ADC channel and return the average voltage with stability checks.
        :param channel: The ADS channel to read from (ADS.P0, ADS.P1, etc.)
        :param num_samples: Number of samples to take for averaging
        :param sampling_interval: Time interval between samples in seconds
        :param rsd_tolerance: Relative standard deviation tolerance for stability
        :param num_attempts: Number of attempts to read the channel if stability checks fail
        :return: Average voltage if successful, None if failed after all attempts
        """
        analog_input = AnalogIn(self.ads, channel)

        for _ in range(num_attempts):
            samples = []
            for _ in range(num_samples):
                try:
                    sample = analog_input.voltage
                    samples.append(sample)
                except Exception as e:
                    pass
                sleep(sampling_interval)

            success_rate = len(samples) / num_samples
            if success_rate < 0.8:
                print(f"Warning: Low success rate ({success_rate:.2f}) for channel {channel}. Retrying...")
                continue

            mean = np.mean(samples)
            stdev = np.std(samples, ddof=1)
            rsd = stdev / mean if abs(mean) > 1e-6 else float('inf')

            if rsd > rsd_tolerance:
                print(f"Warning: High RSD ({rsd * 100:.2f}%) for channel {channel}. Retrying...")
                continue

            print(f"Successfully read channel {channel}. Mean: {mean:.4f} V, RSD: {rsd * 100:.2f}%, Success Rate: {success_rate:.2f}")
            return mean
        print(f"Error: Failed to read from channel {channel} after {num_attempts} attempts. Discarding reading.")
        return None

    def read_temperature_raw(self, num_attempts=3):
        for _ in range(num_attempts):
            with open(self.device_file, 'r') as f:
                lines = f.readlines()
            if lines[0].strip()[-3:] == 'YES':
                print("Successfully read temperature sensor.")
                return lines
            print("Warning: Temperature read failed, retrying...")
            sleep(0.2)
        print(f"Error: Temperature read failed after {num_attempts} attempts. Discarding reading.")
        return None

    def read_turbidity(self):
        """
        Read the turbidity sensor value.
        This method reads the ADC value from the turbidity sensor channel and applies
        the calibration coefficients to convert it to a turbidity value.
        :return: Calculated turbidity value or None if reading failed
        """
        value = self.read_adc_average(self.TURBIDITY_CHANNEL)
        if value is None:
            return None
        turbidity_coeffs = self.coeffs['turbidity']['coeffs']
        return np.polyval(turbidity_coeffs, value)

    def read_temperature(self):
        """
        Read the temperature sensor value.
        This method reads the temperature from the 1-Wire temperature sensor.
        :return: Temperature in Celsius or None if reading failed
        """
        lines = self.read_temperature_raw()

        if lines is None:
            return None

        # Find the index of 't=' in a string.
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            # Read the temperature .
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c

    def read_total_dissolved_solids(self):
        """
        Read the total dissolved solids sensor value.
        This method reads the ADC value from the total dissolved solids sensor channel and applies
        the calibration coefficients to convert it to a total dissolved solids value.
        :return: Calculated total dissolved solids value or None if reading failed
        """
        value = self.read_adc_average(self.TOTAL_DISSOLVED_SOLIDS_CHANNEL)
        if value is None:
            return None
        total_dissolved_solids_coeffs = self.coeffs['total_dissolved_solids']['coeffs']
        return np.polyval(total_dissolved_solids_coeffs, value)

    def read_ph(self):
        """
        Read the pH sensor value.
        This method reads the ADC value from the pH sensor channel and applies
        the calibration coefficients to convert it to a pH value.
        :return: Calculated pH value or None if reading failed
        """
        value = self.read_adc_average(self.PH_CHANNEL)
        if value is None:
            return None
        ph_coeffs = self.coeffs['ph']['coeffs']
        return np.polyval(ph_coeffs, value)

    def read_all(self):
        """
        Read all sensors and return their values in a tuple ordered as:
        (turbidity, temperature, total dissolved solids, pH)
        """
        return self.read_turbidity(), self.read_temperature(), self.read_total_dissolved_solids(), self.read_ph()
