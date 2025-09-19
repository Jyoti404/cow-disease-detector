import os
import io
import requests
import joblib
import numpy as np
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img

# --- 1. App Setup ---
app = FastAPI(title="Cow Disease Detection API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Model Download & Loading ---
# Replace these with your actual GitHub release URLs
MODEL_URL_H5 = "https://github.com/gayatriverm/cow-disease-detector/releases/download/v1.0.0/cow_disease_model.h5"
MODEL_URL_JOBLIB = "https://github.com/gayatriverm/cow-disease-detector/releases/download/v1.0.0/symptom_model.joblib"

def download_file(url: str, filename: str):
    """Download file from URL if not already present locally."""
    if not os.path.exists(filename):
        print(f"Downloading {filename} from {url} ...")
        resp = requests.get(url)
        if resp.status_code == 200:
            with open(filename, "wb") as f:
                f.write(resp.content)
            print(f"{filename} downloaded successfully.")
        else:
            raise RuntimeError(
                f"Failed to download {filename} (status {resp.status_code})"
            )

# Try loading models
try:
    download_file(MODEL_URL_H5, "cow_disease_model.h5")
    download_file(MODEL_URL_JOBLIB, "symptom_model.joblib")

    print("Attempting to load models...")
    image_model = load_model("cow_disease_model.h5")
    symptom_model = joblib.load("symptom_model.joblib")
    print("Models loaded successfully.")
except Exception as e:
    print(f"FATAL: Error loading models: {e}")
    image_model = None
    symptom_model = None

# --- 3. Config & Constants ---
CLASS_NAMES = ["LUMPY SKIN", "NORMAL SKIN"]
IMAGE_WIDTH, IMAGE_HEIGHT = 224, 224
IMAGE_WEIGHT = 0.60
TEXT_WEIGHT = 0.40

# --- 4. Root Endpoint ---
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Cow Disease Detection API is running"}

# --- 5. Entry Point for Render ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render provides PORT env var
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
