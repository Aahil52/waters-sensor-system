import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADS object and specify the gain
ads = ADS.ADS1115(i2c)
ads.gain = 2/3
A0 = AnalogIn(ads, ADS.P0)
A1 = AnalogIn(ads, ADS.P1)
A2 = AnalogIn(ads, ADS.P2)

# Continuously print the values
while True:
    print(f"A0 Voltage: {A0.voltage:.2f} V")
    print(f"A1 Voltage: {A1.voltage:.2f} V")
    print(f"A2 Voltage: {A2.voltage:.2f} V")
    print("-----------------------------")
    time.sleep(1)