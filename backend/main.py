import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
# We are back to using the full Keras model loader
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
import io
import joblib
import os
import requests

# --- 1. App Setup ---
app = FastAPI(title="Cow Disease Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Model Downloading and Loading Logic ---

# ==============================================================================
# IMPORTANT: PASTE YOUR GITHUB RELEASE URLS HERE!
# Use the URL for your original .h5 model, NOT the .tflite one.
# ==============================================================================
IMAGE_MODEL_URL = "PASTE_THE_URL_FOR_cow_disease_model.h5_HERE"
SYMPTOM_MODEL_URL = "PASTE_THE_URL_FOR_symptom_model.joblib_HERE"
# ==============================================================================

IMAGE_MODEL_PATH = "cow_disease_model.h5"
SYMPTOM_MODEL_PATH = "symptom_model.joblib"

def download_file_from_url(url, local_path):
    if not os.path.exists(local_path):
        print(f"Downloading {os.path.basename(local_path)} from {url}...")
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"Download complete: {local_path}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"FATAL: Error downloading {local_path}: {e}")
    else:
        print(f"{os.path.basename(local_path)} already exists.")

print("Server starting up. Checking for models...")
# Initialize models to None
image_model = None
symptom_model = None
try:
    download_file_from_url(IMAGE_MODEL_URL, IMAGE_MODEL_PATH)
    download_file_from_url(SYMPTOM_MODEL_URL, SYMPTOM_MODEL_PATH)
    # Load the Keras and Joblib models
    image_model = load_model(IMAGE_MODEL_PATH)
    symptom_model = joblib.load(SYMPTOM_MODEL_PATH)
    print("Keras and symptom models loaded successfully.")
except Exception as e:
    print(f"FATAL: Could not download or load models: {e}")

# --- 3. Configuration & Constants ---
CLASS_NAMES = ['LUMPY SKIN', 'NORMAL SKIN']
IMAGE_WIDTH, IMAGE_HEIGHT = 224, 224
IMAGE_WEIGHT = 0.60
TEXT_WEIGHT = 0.40

# --- 4. Helper Functions ---
def preprocess_image(image_bytes: bytes) -> np.ndarray:
    try:
        image = load_img(io.BytesIO(image_bytes), target_size=(IMAGE_WIDTH, IMAGE_HEIGHT))
        image_array = img_to_array(image)
        image_array = np.expand_dims(image_array, axis=0)
        image_array /= 255.0
        return image_array
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {e}")

# --- 5. API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Cow Disease Detection API."}

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    symptoms: str = Form(...)
):
    if not image_model or not symptom_model:
        raise HTTPException(status_code=503, detail="Models are not available. Check server logs.")

    image_bytes = await file.read()
    processed_image = preprocess_image(image_bytes)
    image_prediction_probs = image_model.predict(processed_image)[0]

    symptom_prediction_probs = symptom_model.predict_proba([symptoms])[0]

    fused_probs = (image_prediction_probs * IMAGE_WEIGHT) + (symptom_prediction_probs * TEXT_WEIGHT)
    
    fused_prediction_index = np.argmax(fused_probs)
    fused_prediction_name = CLASS_NAMES[fused_prediction_index]
    fused_confidence = float(fused_probs[fused_prediction_index])

    return {
        "filename": file.filename,
        "image_prediction": CLASS_NAMES[np.argmax(image_prediction_probs)],
        "image_confidence": f"{np.max(image_prediction_probs):.2f}",
        "symptom_prediction": CLASS_NAMES[np.argmax(symptom_prediction_probs)],
        "symptom_confidence": f"{np.max(symptom_prediction_probs):.2f}",
        "fused_prediction": fused_prediction_name,
        "fused_confidence": f"{fused_confidence:.2f}"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

