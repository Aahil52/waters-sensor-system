from CQRobot_ADS1115 import ADS1115, ADS1115_REG_CONFIG_PGA_6_144V

class ADSReader:
    def __init__(self, address=0x48, gain=ADS1115_REG_CONFIG_PGA_6_144V):
        self.adc = ADS1115()
        self.adc.setAddr_ADS1115(address)
        self.adc.setGain(gain)

    def read_voltage(self, channel: int) -> float:
        """Reads the voltage from the given channel in volts"""
        raw_millivolts = self.adc.readVoltage(channel)['r']
        return raw_millivolts / 1000.0
