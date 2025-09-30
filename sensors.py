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
        :return: Dict with voltage, rsd, success_rate, attempts, and success flag
        """
        analog_input = AnalogIn(self.ads, channel)
        last_attempt_data = None

        for attempt in range(num_attempts):
            # Collect samples
            samples = []
            for _ in range(num_samples):
                try:
                    samples.append(analog_input.voltage)
                except Exception:
                    pass  # Silently skip failed readings
                sleep(sampling_interval)

            # Calculate metrics for this attempt
            success_rate = len(samples) / num_samples
            mean = np.mean(samples) if samples else 0.0
            rsd = self._calculate_rsd(samples, mean) if len(samples) > 1 else float('inf')

            attempt_data = {
                'voltage': mean if samples else None,
                'rsd': rsd,
                'success_rate': success_rate,
                'attempts': attempt + 1,
                'success': False
            }

            # Check if this attempt meets quality criteria
            if success_rate >= 0.8 and rsd <= rsd_tolerance:
                attempt_data['success'] = True
                print(f"Successfully read channel {channel}. Mean: {mean:.4f} V, RSD: {rsd * 100:.2f}%, Success Rate: {success_rate:.2f}")
                return attempt_data

            # Store failed attempt data
            last_attempt_data = attempt_data
            if success_rate < 0.8:
                print(f"Warning: Low success rate ({success_rate:.2f}) for channel {channel}. Retrying...")
            else:
                print(f"Warning: High RSD ({rsd * 100:.2f}%) for channel {channel}. Retrying...")

        # All attempts failed - return the last attempt's data
        print(f"Error: Failed to read from channel {channel} after {num_attempts} attempts.")
        if last_attempt_data:
            last_attempt_data['attempts'] = num_attempts
            return last_attempt_data

        # Fallback if no samples were ever collected
        return {
            'voltage': None,
            'rsd': None,
            'success_rate': 0.0,
            'attempts': num_attempts,
            'success': False
        }

    def _calculate_rsd(self, samples, mean):
        """Calculate relative standard deviation, handling edge cases."""
        if len(samples) <= 1 or abs(mean) < 1e-6:
            return float('inf')
        stdev = np.std(samples, ddof=1)
        return stdev / mean

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
        :return: Tuple of (turbidity_value, diagnostic_data) or (None, diagnostic_data)
        """
        adc_data = self.read_adc_average(self.TURBIDITY_CHANNEL)
        if adc_data['voltage'] is None or not adc_data['success']:
            return None, adc_data
        turbidity_coeffs = self.coeffs['turbidity']['coeffs']
        turbidity_value = np.polyval(turbidity_coeffs, adc_data['voltage'])
        return turbidity_value, adc_data

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
        :return: Tuple of (total_dissolved_solids_value, diagnostic_data) or (None, diagnostic_data)
        """
        adc_data = self.read_adc_average(self.TOTAL_DISSOLVED_SOLIDS_CHANNEL)
        if adc_data['voltage'] is None or not adc_data['success']:
            return None, adc_data
        total_dissolved_solids_coeffs = self.coeffs['total_dissolved_solids']['coeffs']
        total_dissolved_solids_value = np.polyval(total_dissolved_solids_coeffs, adc_data['voltage'])
        return total_dissolved_solids_value, adc_data

    def read_ph(self):
        """
        Read the pH sensor value.
        This method reads the ADC value from the pH sensor channel and applies
        the calibration coefficients to convert it to a pH value.
        :return: Tuple of (ph_value, diagnostic_data) or (None, diagnostic_data)
        """
        adc_data = self.read_adc_average(self.PH_CHANNEL)
        if adc_data['voltage'] is None or not adc_data['success']:
            return None, adc_data
        ph_coeffs = self.coeffs['ph']['coeffs']
        ph_value = np.polyval(ph_coeffs, adc_data['voltage'])
        return ph_value, adc_data

    def read_all(self):
        """
        Read all sensors and return their values and diagnostic data.
        :return: Dict with sensor values and diagnostic data
        """
        turbidity, turbidity_diag = self.read_turbidity()
        temperature = self.read_temperature()
        total_dissolved_solids, total_dissolved_solids_diag = self.read_total_dissolved_solids()
        ph, ph_diag = self.read_ph()

        return {
            'turbidity': turbidity,
            'temperature': temperature,
            'total_dissolved_solids': total_dissolved_solids,
            'ph': ph,
            'turbidity_voltage': turbidity_diag['voltage'],
            'turbidity_rsd': turbidity_diag['rsd'],
            'turbidity_success_rate': turbidity_diag['success_rate'],
            'turbidity_attempts': turbidity_diag['attempts'],
            'total_dissolved_solids_voltage': total_dissolved_solids_diag['voltage'],
            'total_dissolved_solids_rsd': total_dissolved_solids_diag['rsd'],
            'total_dissolved_solids_success_rate': total_dissolved_solids_diag['success_rate'],
            'total_dissolved_solids_attempts': total_dissolved_solids_diag['attempts'],
            'ph_voltage': ph_diag['voltage'],
            'ph_rsd': ph_diag['rsd'],
            'ph_success_rate': ph_diag['success_rate'],
            'ph_attempts': ph_diag['attempts']
        }
