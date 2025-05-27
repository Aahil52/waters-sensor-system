import os
import glob
import time
from .base import BaseSensor

class TemperatureSensor(BaseSensor):
    def __init__(self):
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        base_dir = '/sys/bus/w1/devices/'
        device_folders = glob.glob(base_dir + '28*')
        if not device_folders:
            raise RuntimeError("No temperature sensors found on OneWire bus.")
        self.device_file = device_folders[0] + '/w1_slave'

    @property
    def name(self) -> str:
        return "temperature"

    def _read_raw(self) -> list[str]:
        with open(self.device_file, 'r') as f:
            return f.readlines()

    def read(self) -> float:
        lines = self._read_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self._read_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
        raise RuntimeError("Failed to read temperature data.")
