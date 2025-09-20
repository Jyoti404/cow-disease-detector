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

# --- 1. App Setup ---
app = FastAPI(title="Cow Disease Detection API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


IMAGE_MODEL_URL = "https://github.com/gayatriverm/cow-disease-detector/releases/download/v1.0.0/cow_disease_model.h5"
SYMPTOM_MODEL_URL = "https://github.com/gayatriverm/cow-disease-detector/releases/download/v1.0.0/symptom_model.joblib"

IMAGE_MODEL_PATH = "cow_disease_model.h5"
SYMPTOM_MODEL_PATH = "symptom_model.joblib"

# --- 3. Startup Logic with Detailed Logging ---
def download_file_from_url(url, local_path):
    if not os.path.exists(local_path):
        print(f"Downloading {os.path.basename(local_path)}...")
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"Download successful: {local_path}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"!!!!!!!! FATAL: DOWNLOAD FAILED for {local_path}. Error: {e}")
            return False
    else:
        print(f"{os.path.basename(local_path)} already exists.")
        return True

@app.on_event("startup")
def load_models():
    """This function runs once when the server starts."""
    global image_model, symptom_model
    image_model, symptom_model = None, None

    print("--- Server Startup: Loading Models ---")
    # Step 1: Download files
    image_download_ok = download_file_from_url(IMAGE_MODEL_URL, IMAGE_MODEL_PATH)
    symptom_download_ok = download_file_from_url(SYMPTOM_MODEL_URL, SYMPTOM_MODEL_PATH)

    # Step 2: Load Image Model
    if image_download_ok:
        try:
            image_model = load_model(IMAGE_MODEL_PATH)
            print("SUCCESS: Keras image model loaded.")
        except Exception as e:
            print(f"!!!!!!!! FATAL: FAILED TO LOAD H5 MODEL. Error: {e}")
    
    # Step 3: Load Symptom Model
    if symptom_download_ok:
        try:
            symptom_model = joblib.load(SYMPTOM_MODEL_PATH)
            print("SUCCESS: Joblib symptom model loaded.")
        except Exception as e:
            print(f"!!!!!!!! FATAL: FAILED TO LOAD JOBLIB MODEL. Error: {e}")

    if image_model and symptom_model:
        print("--- All models loaded successfully. Server is ready. ---")
    else:
        print("--- One or more models failed to load. Server is NOT ready. ---")

# --- 4. The Rest of the App (No changes needed here) ---
CLASS_NAMES = ['LUMPY SKIN', 'NORMAL SKIN']
IMAGE_WIDTH, IMAGE_HEIGHT = 224, 224
IMAGE_WEIGHT, TEXT_WEIGHT = 0.60, 0.40

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    try:
        image = load_img(io.BytesIO(image_bytes), target_size=(IMAGE_WIDTH, IMAGE_HEIGHT))
        image_array = img_to_array(image)
        image_array = np.expand_dims(image_array, axis=0)
        image_array /= 255.0
        return image_array
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Cow Disease Detection API."}

@app.post("/predict")
async def predict(file: UploadFile = File(...), symptoms: str = Form(...)):
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
        "fused_confidence": f"{fused_confidence:.2f}",
    }

