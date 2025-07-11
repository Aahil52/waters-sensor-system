#!/usr/bin/env python3
"""
predict_do.py

Reads current sensor data via the sensor API and predicts dissolved oxygen (DO) 
using a pre-trained GradientBoosting model with TDS.
"""

import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import joblib
from datetime import datetime

from lib import sensor

def preprocess_sensor_data(sensor_data: dict) -> np.ndarray:
    """
    Convert raw sensor data dictionary to feature array for model prediction.
    Model expects: [DateOrdinal, Temp, pH, Turbidity, TDS]
    
    No scaling needed since GradientBoosting was trained without scaling.
    """
    date_ordinal = pd.Timestamp(sensor_data["last_update"]).toordinal()
    temperature = sensor_data["temperature"]
    ph = sensor_data["pH"]
    turbidity = sensor_data["turbidity"]
    tds = sensor_data["total_dissolved_solids"]

    features = [date_ordinal, temperature, ph, turbidity, tds]
    X = np.array([features])  # Shape: (1, 5)
    
    return X

def predict_do() -> float:
    """
    Load GradientBoosting_withTDS model and predict DO from current sensor reading.
    """
    script_dir = pathlib.Path(__file__).parent
    model_path = script_dir / "GradientBoosting_withTDS_model.joblib"

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    # Load model (no scaler needed)
    model = joblib.load(model_path)
    sensor_data = sensor.read(local=True)

    if not sensor_data.get("sensor_ready", False):
        raise RuntimeError("Sensor not ready - cannot make prediction")

    # Ensure all required fields are present and not None
    for field in ["temperature", "pH", "turbidity", "total_dissolved_solids"]:
        if sensor_data.get(field) is None:
            raise ValueError(f"Required sensor field '{field}' is None")

    # Preprocess sensor data (no scaling applied)
    X = preprocess_sensor_data(sensor_data)
    
    # Make prediction
    do_prediction = model.predict(X)[0]
    return float(do_prediction)

def main():
    try:
        predicted_do = predict_do()
        print(f"[{datetime.utcnow().isoformat()}] Predicted DO (with TDS): {predicted_do:.2f} mg/L")
    except Exception as e:
        print(f"[{datetime.utcnow().isoformat()}] Error: {str(e)}")

if __name__ == "__main__":
    main()
