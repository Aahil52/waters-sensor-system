import time
from core.sensors.ads_reader import get_ads, AnalogIn, ADS

class PHSensor:
    def __init__(self, channel: int = 0, temperature: float = 25.0):
        """Initialize the pH sensor on the specified ADS1115 channel (0–3)."""
        try:
            adc_channel = getattr(ADS, f'P{channel}')
        except AttributeError:
            raise ValueError("Invalid channel. Must be 0–3.")

        self.chan = AnalogIn(get_ads(), adc_channel)

    def read(self, samples: int = 10, trim: int = 2) -> float:
        """
        Reads a trimmed average voltage from the pH sensor and converts it to pH.
        - samples: number of voltage samples to collect
        - trim: number of highest and lowest values to discard
        """
        voltages = [self.chan.voltage for _ in range(samples)]
        time.sleep(0.05 * samples)

        # Sort and trim the voltage readings
        voltages.sort()
        trimmed = voltages[trim:-trim] if trim * 2 < samples else voltages
        avg_voltage = sum(trimmed) / len(trimmed)

        # Linear conversion (calibrate this later with real data i.e. pH 3, pH4, pH 7)
        """DOUBLE CHECK LOGIC AGAINST DATA SHEET"""
        ph_value = -5.14 * avg_voltage + 20.4
        return ph_value