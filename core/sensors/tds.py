import time
from core.sensors.ads_reader import get_ads, AnalogIn, ADS

class TdsSensor:
    def __init__(self, channel: int = 0, temperature: float = 25.0):
        """Initialize the TDS sensor on the specified ADS1115 channel (0–3)."""
        try:
            adc_channel = getattr(ADS, f'P{channel}')
        except AttributeError:
            raise ValueError("Invalid channel. Must be 0–3.")

        self.chan = AnalogIn(get_ads(), adc_channel)
        self.temperature = temperature

    def read(self) -> float:
        voltages = [self.chan.voltage for _ in range(30)]
        time.sleep(0.05 * len(voltages))

        voltages.sort()
        trimmed = voltages[2:-2]
        avg_voltage = sum(trimmed) / len(trimmed)

        # Temperature compensation
        compensation_coeff = 1.0 + 0.02 * (self.temperature - 25.0)
        compensated_voltage = avg_voltage / compensation_coeff

        # NEED TO BETTER CALCULATE THIS
        tds = (compensated_voltage / 5.0) * 1000.0 * 0.5
        """
        ~0 ppm @ ~0.0V (distilled water)
        ~300 ppm @ ~1.5V (tap water)
        ~500+ ppm @ ~2.3V (hard water) 
        """

        return round(tds, 2)
    
    def set_temperature(self, temperature: float):
        """Set the temperature for TDS compensation."""
        if not (0 <= temperature <= 100):
            raise ValueError("Temperature must be between 0 and 100 degrees Celsius.")
        self.temperature = temperature
    
    def get_temperature(self) -> float:
        """Get the current temperature setting for TDS compensation."""
        return self.temperature