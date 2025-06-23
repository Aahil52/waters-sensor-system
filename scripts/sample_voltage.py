import sys
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from collections import deque

# Define ANSI escape codes for colored output
class Style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADS object and specify the gain
ads = ADS.ADS1115(i2c)
ads.gain = 2/3

# Define ADS channels
print()
pin = input("Enter the ADS1115 channel to read (0-3, default is 0): ")
pin = pin.strip() if pin else '0'
pin = ADS.P0 if pin == '0' else ADS.P1 if pin == '1' else ADS.P2 if pin == '2' else ADS.P3 if pin == '3' else ADS.P0

A = AnalogIn(ads, pin)

# Prompt user for stabilization parameters
window_size = input("Enter the number of samples for stabilization (default 10): ")
window_size = int(window_size.strip()) if window_size.strip() else 10
window_size = max(1, window_size)  # Ensure at least 1 sample

# Prompt user for stabilization tolerance
stabilization_tolerance = input("Enter the stabilization tolerance (default 0.003): ")
stabilization_tolerance = float(stabilization_tolerance.strip()) if stabilization_tolerance.strip() else 0.003
stabilization_tolerance = max(0.0, stabilization_tolerance)  # Ensure non-negative tolerance

# Initialize lists for standard deviation and average
stdev_list = []
avg_list = []
run_count = 1

print("\n", end='')

def endPrompt():
    str = input("Press Enter to continue reading, type 'reset' to start fresh, 'report' for data, or 'exit' to quit. ")
    return str

# Function to generate a report of the collected data
def generateReport():
    if len(stdev_list) == 0 or len(avg_list) == 0:
        print(f"{Style.RED}No data collected yet.{Style.RESET}\n")
    else:
        final_stdev = sum(stdev_list) / len(stdev_list) if stdev_list else 0
        final_avg = sum(avg_list) / len(avg_list) if avg_list else 0
        print(f"{Style.CYAN}Average Voltage: {final_avg:.4f} V | Std Dev: {final_stdev:.4f} V | Relative Std Dev: {final_stdev / final_avg * 100:.2f}%{Style.RESET}\n")

# Function to clear the collected data
def clearData():
    global run_count
    stdev_list.clear()
    avg_list.clear()
    run_count = 0
    print(f"{Style.MAGENTA}Data cleared. Ready for new readings.{Style.RESET}\n")

# Main loop to collect samples and calculate statistics
while True:
    samples = deque(maxlen=window_size)

    while True:
        voltage = A.voltage
        samples.append(voltage)

        if len(samples) == window_size:
            mean = sum(samples) / window_size
            stdev = (sum((x - mean) ** 2 for x in samples) / window_size) ** 0.5

            color = Style.GREEN if stdev < stabilization_tolerance else Style.RED
            print(" " * 50, end='\r')
            print(f"Run #{run_count} - {color}Average Voltage: {mean:.4f} V | Std Dev: {stdev:.4f} V{Style.RESET}", end='\r')

            if stdev < stabilization_tolerance:
                stdev_list.append(stdev)
                avg_list.append(mean)
                break
        else:
            print(f"Collecting... {len(samples)}/{window_size}", end='\r')

        time.sleep(0.5)  # Sampling interval

    print("\n"*2, end='')  
    for i, sample in enumerate(samples):
        print(f"{Style.YELLOW}Sample {i + 1}/{len(samples)}: {sample:.4f} V{Style.RESET}")
    print("\n", end='')

    # Code from before:
    # response = input("Press Enter to continue reading or type 'exit' to quit: ")
    # print("\n", end='')

    while True:
        response = endPrompt()
        print()
        
        if response.lower() == 'exit':
            sys.exit()
        elif response.lower() == 'reset':
            clearData()
        elif response.lower() == 'report':
            generateReport()
        else:
            run_count += 1
            break