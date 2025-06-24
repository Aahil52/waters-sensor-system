from lib import sensor
from time import sleep

while True:
    try:
        sensor_data = sensor.read()
        if sensor_data["sensor_ready"]:
            print(f"[{sensor_data['last_update']}] Turbidity: {sensor_data['turbidity']}, "
                f"Temperature: {sensor_data['temperature']}, "
                f"TDS: {sensor_data['total_dissolved_solids']}, "
                f"pH: {sensor_data['pH']}")
        else:
            print("Sensor not ready. Retrying...")
    except Exception as e:
        print(f"Error reading sensor data: {e}")

    # Logs every 10 seconds as a visible example
    # In reality, the sensor only samples every 5 minutes
    sleep(10)