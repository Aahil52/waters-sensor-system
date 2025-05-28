# core/sensors/ads_reader.py

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# This class allows sensor classes to import from this module directly

# Shared I2C and ADS1115 instance
i2c = busio.I2C(board.SCL, board.SDA)
_ads = ADS.ADS1115(i2c)
_ads.gain = 1  # 1 = ±4.096V

def get_ads():
    """Returns shared ADS1115 instance"""
    return _ads

# Expose ADC symbols for cleaner imports in sensor classes
__all__ = ["get_ads", "AnalogIn", "ADS"]
