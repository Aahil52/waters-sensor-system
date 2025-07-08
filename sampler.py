import requests
from datetime import datetime, timezone
from time import monotonic, sleep
from dotenv import load_dotenv
import os
import csv
from sensors import Sensors

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
DEVICE_ID = os.getenv("DEVICE_ID")

SAMPLING_INTERVAL = 15  # minutes

start_time = None
next_sample_time = None

sensors = None

def log_sample(sample):
    path = "data/samples.csv"
    fieldnames = ['device_id', 'measured_at', 'uptime', 'turbidity', 'temperature', 'total_dissolved_solids', 'ph']
    file_exists = os.path.isfile(path)

    with open(path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(sample)

def send_sample(sample, max_retries=5, base_backoff=2):
    url = f"{SUPABASE_URL}/functions/v1/insert-sample"
    
    headers = {
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=sample, headers=headers, timeout=10)
            response.raise_for_status()
            print(f"Sample sent at {sample['measured_at']}")
            return
        except Exception as e:
            print(f"Send failed: {e}")
            if attempt == max_retries - 1:
                print("Max retries reached. Giving up.")
                return
            backoff_time = base_backoff * (2 ** attempt)
            print(f"Retrying in {backoff_time} seconds... (Attempt {attempt + 1}/{max_retries})")
            sleep(backoff_time)

def setup():
    global start_time, next_sample_time, sensors
    start_time = monotonic()
    next_sample_time = monotonic()
    sensors = Sensors()
    print("Sampler started.")

def loop():
    global next_sample_time
    
    measured_at = datetime.now(timezone.utc).isoformat()
    uptime = monotonic() - start_time

    turbidity, temperature, total_dissolved_solids, ph = sensors.read_all()
    
    sample = {
        "device_id": DEVICE_ID,
        "measured_at": measured_at,
        "uptime": uptime,
        "turbidity": turbidity,
        "temperature": temperature,
        "total_dissolved_solids": total_dissolved_solids,
        "ph": ph
    }

    # Log the sample to a CSV file
    log_sample(sample)
    
    # Send the sample to Supabase with retries
    send_sample(sample)
    
    # Wait until the next precise interval
    next_sample_time += SAMPLING_INTERVAL * 60  # Convert minutes to seconds
    sleep_time = max(0, next_sample_time - monotonic())
    sleep(sleep_time)

def main():
    try:
        setup()
        while True:
            loop()
    except KeyboardInterrupt:
        print("Sampler interrupted by user.")
    except Exception as e:
        print(f"Uncaught exception in sampler: {e}")
    finally:
        print("Sampler stopped.")

if __name__ == "__main__":
    main()