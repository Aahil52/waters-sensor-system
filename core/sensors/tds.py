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

    # Reads a trimmed average voltage from the TDS sensor and converts it to TDS in ppm.
    def read(self) -> float:
        voltages = [self.chan.voltage for _ in range(30)]
        time.sleep(0.05 * len(voltages))

        voltages.sort()
        trimmed = voltages[2:-2]
        avg_voltage = sum(trimmed) / len(trimmed)

        # Temperature compensation
        # Assuming a linear compensation model for simplicity
        # Dive deeper into this with other models if needed
        compensation_coeff = 1.0 + 0.02 * (self.temperature - 25.0)
        compensated_voltage = avg_voltage / compensation_coeff

        # NEED TO BETTER CALCULATE THIS, COMPARE AGAINST KNOWN TDS VALUES
        # TDS ranges from 0 to 1000+ ppm, so we scale the voltage accordingly
        tds = (compensated_voltage / 5.0) * 1000.0 * 0.5
        """
        TDS conversion based on drinking water standards:
        - 0-300 ppm: Low TDS (distilled water, rainwater)
        - 300-500 ppm: Medium TDS (tap water, groundwater)
        - 500+ ppm: High TDS (hard water, brackish water)
        """

        return round(tds, 2)
    
    # Setters and Getters for temperature compensation
    def set_temperature(self, temperature: float):
        """Set the temperature for TDS compensation."""
        if not (0 <= temperature <= 55):
            raise ValueError("Temperature must be between 0 and 55 degrees Celsius.")
        self.temperature = temperature
    
    def get_temperature(self) -> float:
        """Get the current temperature setting for TDS compensation."""
        return self.temperature