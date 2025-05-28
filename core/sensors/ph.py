import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class PHSensor():
    def __init__(self, channel: int = 0):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(i2c)
        self.ads.gain = 1  # Gain of 1 for 0-4.096V range

        if channel == 0:
            self.chan = AnalogIn(self.ads, ADS.P0)
        elif channel == 1:
            self.chan = AnalogIn(self.ads, ADS.P1)
        elif channel == 2:
            self.chan = AnalogIn(self.ads, ADS.P2)
        elif channel == 3:
            self.chan = AnalogIn(self.ads, ADS.P3)
        else:
            raise ValueError("Invalid channel number. Must be 0–3.")

    def read(self) -> float:
        """Returns averaged voltage from pH sensor input"""
        buf = []
        for _ in range(10):  # Take 10 samples
            buf.append(self.chan.voltage)
            time.sleep(0.05)
        buf.sort()
        trimmed = buf[2:-2]  # Drop highest/lowest 2
        avg_voltage = sum(trimmed) / len(trimmed)

        # You can customize this mapping later based on calibration data.
        # Placeholder: linear mapping assuming 0V = pH 0, 5V = pH 14
        ph_value = (avg_voltage / 5.0) * 14.0
        return round(ph_value, 2)
