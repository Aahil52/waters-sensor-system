from .ads_reader import ADSReader
import time

class TdsSensor():
    def __init__(self, channel: int = 1, temp_c: float = 25.0):
        self.ads = ADSReader()
        self.channel = channel
        self.temperature = temp_c

    def read(self) -> float:
        # Read 30 samples and use median
        samples = [self.ads.read_voltage(self.channel) for _ in range(30)]
        samples.sort()
        trimmed = samples[2:-2]
        avg_voltage = sum(trimmed) / len(trimmed)

        # Temperature compensation
        compensation_coeff = 1.0 + 0.02 * (self.temperature - 25.0)
        compensated_voltage = avg_voltage / compensation_coeff

        # Convert to TDS (example formula)
        tds = (133.42 * compensated_voltage**3
              - 255.86 * compensated_voltage**2
              + 857.39 * compensated_voltage) * 0.5
        return round(tds, 2)
