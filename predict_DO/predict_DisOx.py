import os
from datetime import datetime
import numpy as np
import pandas as pd
import joblib
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DEVICE_ID = int(os.getenv("DEVICE_ID")) 

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def preprocess_sensor_data(sample):
    """
    Convert Supabase sample row into model-ready NumPy array.
    Expects: [DateOrdinal, Temperature, pH, Turbidity, TDS]
    """
    date_ordinal = pd.Timestamp(sample["measured_at"]).toordinal()
    temperature = sample["temperature"]
    ph = sample["ph"]
    turbidity = sample["turbidity"]
    tds = sample["total_dissolved_solids"]

    features = [date_ordinal, temperature, ph, turbidity, tds]
    return np.array([features])  # Shape: (1, 5)

def predict_do() -> float:
    """
    Fetch latest sensor data from Supabase and predict DO using Gradient Boosting model.
    """
    # Query latest sample
    response = supabase.table("samples")\
        .select("*")\
        .eq("device_id", DEVICE_ID)\
        .order("measured_at", desc=True)\
        .limit(1)\
        .execute()

    samples = response.data
    if not samples:
        raise ValueError(f"No samples found for device_id = {DEVICE_ID}")

    sample = samples[0]

    # Preprocess
    X = preprocess_sensor_data(sample)

    # Load model
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "GradientBoosting_withTDS_model.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at path: {model_path}")
    
    model = joblib.load(model_path)

    # Predict DO
    predicted_do = model.predict(X)[0]
    return float(predicted_do)

if __name__ == "__main__":
    try:
        result = predict_do()
        print(f"[{datetime.utcnow().isoformat()}] Predicted DO (with TDS): {result:.2f} mg/L")
    except Exception as e:
        print(f"[{datetime.utcnow().isoformat()}] Error: {str(e)}")