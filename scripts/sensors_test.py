import time
from core.sensors import PHSensor, TdsSensor, TurbiditySensor, TempSensor

def read_all_sensors():
    # Instantiate and read temperature for analog sensor calibration
    temp_sensor = TempSensor()
    temp = temp_sensor.read()
    
    # Instantiate sensors (choose appropriate ADS1115 channels)
    ph_sensor = PHSensor(channel=0)
    turb_sensor = TurbiditySensor(channel=1)
    tds_sensor = TdsSensor(channel=2)

    # Read analog sensor values
    ph = ph_sensor.read()
    tds = tds_sensor.read()
    turbidity = turb_sensor.read()

    # Output results
    print(f"pH: {ph:.2f}")
    print(f"TDS: {tds:.2f} ppm")
    print(f"Turbidity: {turbidity:.2f} NTU")
    print(f"Temperature: {temp[0]:.2f} °C")
    print("-----------------------------")

# Continuously print values
while True:
    try:
        read_all_sensors()
    except Exception as e:
        print("Error:", e)
    time.sleep(1)  # Adjust sleep time as needed