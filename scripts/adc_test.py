import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADS object and specify the gain
ads = ADS.ADS1115(i2c)
ads.gain = 1 
turbidity = AnalogIn(ads, ADS.P0)
ph = AnalogIn(ads, ADS.P1)
tds = AnalogIn(ads, ADS.P2)

# Continuously print the values
while True:
    print(f"Turbidity Voltage: {turbidity.voltage:.2f} V")
    print(f"pH Voltage: {ph.voltage:.2f} V")
    print(f"TDS Voltage: {tds.voltage:.2f} V")
    print("-----------------------------")
    time.sleep(1)