import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
import io
import joblib
import os
import requests

# --- 1. App and Model Setup ---
app = FastAPI(title="Cow Disease Detection API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Download Models if Not Already Present ---
# Replace these with your actual GitHub release "raw" URLs
MODEL_URL_H5 = "https://github.com/gayatriverm/cow-disease-detector/releases/download/v1.0.0/cow_disease_model.h5"
MODEL_URL_JOBLIB = "https://github.com/gayatriverm/cow-disease-detector/releases/download/v1.0.0/symptom_model.joblib"

def download_file(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename} from {url} ...")
        resp = requests.get(url)
        if resp.status_code == 200:
            with open(filename, "wb") as f:
                f.write(resp.content)
            print(f"{filename} downloaded successfully.")
        else:
            raise RuntimeError(f"Failed to download {filename} from {url} (status {resp.status_code})")

try:
    # Download files once on startup
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
CLASS_NAMES = ['LUMPY SKIN', 'NORMAL SKIN']
IMAGE_WIDTH, IMAGE_HEIGHT = 224, 224
IMAGE_WEIGHT = 0.60
TEXT_WEIGHT = 0.40
