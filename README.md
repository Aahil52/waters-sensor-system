# Sensor System

This program is designed to run as a background process (daemon) on our Raspberry Pi sensor system while it is deployed at the water treatment facility. It consists of an sensor loop and a FastAPI sever that communicate via a shared in-memory state. 

The sensor loop handles low-level sensor interface, samples at a fixed interval, and applies necessary callibration and correction. It stores the current sensor values in the shared state. The FastAPI server exposes the current sensor values from the shared state over the local network for use by downstream consumers.

## Contributing

### Clone the repo
```bash
$ git clone https://github.com/Aahil52/sensor-system.git
```

### Create and activate virtual environment
```bash
$ python -m venv .venv
$ source .venv/bin/activate
```

### Install required dependencies
```bash
$ pip install -r requirements.txt
```

### Make sure to update `requirements.txt` if you add dependencies
```bash
$ pip freeze > requirements.txt
```