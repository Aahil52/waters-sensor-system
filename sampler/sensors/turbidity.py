import time
from sampler.sensors.ads_reader import get_ads, AnalogIn, ADS

class TurbiditySensor:
    def __init__(self, channel: int = 0):
        """Initialize the turbidity sensor on the specified ADS1115 channel (0–3)."""
        try:
            adc_channel = getattr(ADS, f'P{channel}')
        except AttributeError:
            raise ValueError("Invalid channel. Must be 0–3.")

        self.chan = AnalogIn(get_ads(), adc_channel)

    def read(self) -> float:
        """
        Reads the turbidity sensor voltage and converts it to an estimated NTU value.
        Placeholder formula: (voltage / 5V) * 1000 NTU
        """
        voltage = self.chan.voltage
        ntu = (voltage / 5.0) * 1000.0  # Adjust this based on calibration
        return round(ntu, 2)