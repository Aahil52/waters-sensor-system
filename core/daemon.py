from core.state import update_state
from time import sleep, monotonic, time

SAMPLING_INTERVAL = 5  # minutes

start_time = None

def setup():
    global start_time
    start_time = monotonic()

    # Initialize sensors and other hardware here

def loop():
    uptime = monotonic() - start_time
    last_update = time()

    # Read sensor data and apply corrections here

    # Make sure to handle exceptions and errors in sensor reading
    # Set sensor_ready to False if there's an error
    # Could also add a message field to the schema if needed

    # Construct the sensor data dictionary
    sensor_data = {
        "sensor_ready": True,
        "last_update": last_update,
        "uptime": uptime,
        "turbidity": 0.0,
        "temperature": 0.0,
        "total_dissolved_solids": 0.0,
        "pH": 0.0
    }

    update_state(sensor_data)

    sleep(SAMPLING_INTERVAL * 60)  # Convert minutes to seconds

def cleanup():
    # Cleanup code for sensors and other hardware
    pass

def start_daemon():
    try:
        setup()
        while True:
            loop()
    except Exception as e:
        print(f"Error in daemon: {e}")
    finally:
        cleanup()