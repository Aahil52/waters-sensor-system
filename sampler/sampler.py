import asyncio
import aiohttp
from datetime import datetime, timezone
from time import monotonic
from dotenv import load_dotenv
import os
import csv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
DEVICE_ID = os.getenv("DEVICE_ID")

SAMPLING_INTERVAL = 15 * 60  # seconds

async def send_sample(session, sample, max_retries=5, base_backoff=2):
    url = f"{SUPABASE_URL}/functions/v1/insert-sample"

    headers = {
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }

    retries = 0

    while retries < max_retries:
        try:
            async with session.post(url, json=sample, headers=headers, timeout=10) as response:
                response.raise_for_status()
                print(f"Sample sent at {sample['measured_at']}")
                return
        except Exception as e:
            print(f"Send failed: {e}")
            retries += 1
            if retries >= max_retries:
                print("Max retries reached. Giving up.")
                return
            # Exponential backoff: 2, 4, 8, 16, 32 seconds
            backoff_time = base_backoff * (2 ** (retries - 1))
            print(f"Retrying in {backoff_time} seconds... (Attempt {retries}/{max_retries})")
            await asyncio.sleep(backoff_time)

def log_sample(sample):
    path = "samples.csv"
    fieldnames = ['device_id', 'measured_at', 'uptime', 'turbidity', 'temperature', 'total_dissolved_solids', 'ph']
    file_exists = os.path.isfile(path)

    with open(path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()
        
        writer.writerow(sample)

async def sampler_loop():
    start_time = monotonic()
    
    async with aiohttp.ClientSession() as session:
        next_sample_time = monotonic()

        while True:
            measured_at = datetime.now(timezone.utc).isoformat()
            uptime = monotonic() - start_time

            # Read sensor values
            turbidity, temperature, total_dissolved_solids, ph = None, None, None, None

            sample = {
                "device_id": DEVICE_ID,
                "measured_at": measured_at,
                "uptime": uptime,
                "turbidity": turbidity,
                "temperature": temperature,
                "total_dissolved_solids": total_dissolved_solids,
                "ph": ph
            }

            # Send the sample to Supabase asynchronously
            asyncio.create_task(send_sample(session, sample))

            # Log the sample to a CSV file synchronously
            log_sample(sample)

            # Wait until the next precise interval
            next_sample_time += SAMPLING_INTERVAL
            await asyncio.sleep(max(0, next_sample_time - monotonic()))

async def main():
    print("Sampler started.")
    try:
        await sampler_loop()
    except Exception as e:
        print(f"Uncaught exception in sampler: {e}")
    finally:
        print("Sampler stopped.")

if __name__ == "__main__":
    asyncio.run(main())
