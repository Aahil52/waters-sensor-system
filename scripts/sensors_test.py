import time
from core.sensors.ph import PHSensor
from core.sensors.tds import TdsSensor
from core.sensors.turbidity import TurbiditySensor

def read_all_sensors():
    # Instantiate sensors (choose appropriate ADS1115 channels)
    ph_sensor = PHSensor(channel=0)
    tds_sensor = TdsSensor(channel=1, temperature=25.0)
    turb_sensor = TurbiditySensor(channel=2)

    # Read values
    ph = ph_sensor.read()
    tds = tds_sensor.read()
    turbidity = turb_sensor.read()

    # Output results
    print(f"pH: {ph}")
    print(f"TDS: {tds} ppm")
    print(f"Turbidity: {turbidity} NTU")

while True:
    try:
        read_all_sensors()
    except Exception as e:
        print("Error:", e)
    time.sleep(1)  # Adjust sleep time as needed