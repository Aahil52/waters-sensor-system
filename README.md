# Sensor System

This project is a lightweight, single-service sensor system designed to run on a Raspberry Pi for real-time water quality monitoring at a treatment facility. 

It features:
- A sensor sampling loop that reads hardware data at a fixed 15 minute interval.
- Calibration applied to sensor readings.
- Storage of sensor data in a remote PostgreSQL database hosted on Supabase.

---

## 📂 Project Structure

```bash
sensor-system/
├── calibration/
├── data/                           # Directory containing local sample logs
├── deploy.sh                       # Script that deploys the sampler as a systemd service
├── docs/
├── README.md
├── requirements.txt                
├── sampler.py                      # Program that samples every 15 minutes and sends to the database and logs locally
├── scripts/                        
├── sensors.py                      # Class that handles direct hardware sensor interface
└── sensor-system-sampler.service   # Systemd service configuration for the sampler
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

## ⚙️ Deployment

All services are deployed using the `deploy.sh` script.

The script will:
- Clone the project into the `/opt/` directory
- Set up the virtual environment
- Install dependencies
- Copy systemd sampler service file to `/etc/systemd/system`
- Enable and start sampler service.

Run:

```bash
$ ./deploy.sh
```

⚠️ Only run the deployment script on the Raspberry Pi. Make sure the GitHub repository is up to date prior to deployment.
