# Sensor System

This project is a modular, service-based sensor system designed to run as a background process on a Raspberry Pi deployed at a water treatment facility. The system is structured for real-time data acquisition, modular service expansion, and clean deployment.

It consists of:
- A **sensor sampling loop** that reads from the hardware at a fixed 5 minute interval, applies calibration, and writes the current sensor readings to a shared in-memory state.
- A **FastAPI server** that exposes the current sensor readings over the local and Tailscale networks.
- A **calibration workflow** using Jupyter notebook.
- A **modular service structure** allowing easy addition of new services.

---

## 📂 Project Structure

```bash
sensor-system/
├── calibration/              # Calibration notebook, coefficients, and logs
│   ├── calibrate.ipynb
│   ├── coefficients.json
│   └── logs/
├── core/                     # Core service (API, sensor, sampling loop)
│   ├── api.py
│   ├── sampler.py
│   └── state.py
├── deploy.sh                 # Deployment script
├── example/                  # Example service consuming the API
│   └── example.py
├── lib                       # Wrapper library for the API
│   ├── __init__.py
│   └── sensor.py
├── scripts/                  # Sensor test and utility scripts
│   ├── adc_test.py
│   ├── sample_voltage.py
│   └── sensors_test.py
├── services/                 # Systemd service files
│   ├── sensor-system-core.service
│   └── sensor-system-example.service
├── requirements.txt          # Python dependencies
└── README.md
```

## 🤝 Contributing

### Clone the Repository

```bash
$ git clone https://github.com/Aahil52/sensor-system.git
$ cd sensor-system
```

### Create and Activate Virtual Environment

```bash
$ python -m venv .venv
$ source .venv/bin/activate
```

### Install Required Dependencies

```bash
$ pip install -r requirements.txt
```

### Commit and Push Changes

```bash
$ git add .
$ git commit -m "Commit message"
$ git push
```

⚠️ All service development should occur locally on your machine. Do not develop directly on the Raspberry Pi unless necessary. Push changes to GitHub only once a feature is complete. 

## 📡 Services

Each service consists of a directory containing its Python code and a corresponding systemd `.service` file in the `services/` directory. The `.service` file tells systemd to run the corresponding program as a background process.

### Adding a New Service

1. Create a directory for the Python code (e.g. `example/`)
2. Create a corresponding `.service` file in `services/` (e.g. `sensor-system-example.service`)
3. Populate the `.service` file using `sensor-system-example.service` as a reference
    - `ExecStart` in the `.service` file should point to the appropriate Python entry point.

⚠️ All new services should access the sensor data via the provided API. The wrapper library for the API is documented in [`lib/sensor.md`](lib/sensor.md) and is used in [`example/example.py`](example/example.py)

## ⚙️ Deployment

All services are deployed using the `deploy.sh` script.

The script will:
- Clone the project into the `/opt/` directory
- Set up the virtual environment
- Install dependencies
- Copy systemd service files to `/etc/systemd/system`
- Enable and start services.

Run:

```bash
$ ./deploy.sh
```

⚠️ Only run the deployment script on the Raspberry Pi. Make sure the GitHub repository is up to date prior to deployment.

## 🧪 Calibration Workflow
