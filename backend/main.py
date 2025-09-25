import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
import io
import joblib
import os

# --- 1. App Setup ---
app = FastAPI(title="Cow Disease Detection API (Local)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- 2. Model Loading for Local Environment ---
# This version loads models directly from your local 'backend' folder.
# Ensure your model files are in the same directory as this script.
IMAGE_MODEL_PATH = "cow_disease_model.h5"
SYMPTOM_MODEL_PATH = "symptom_model.joblib"

image_model = None
symptom_model = None

print("--- Local Server Startup: Loading Models ---")
# Load Image Model
if os.path.exists(IMAGE_MODEL_PATH):
    try:
        image_model = load_model(IMAGE_MODEL_PATH)
        print("SUCCESS: Keras image model loaded from local file.")
    except Exception as e:
        print(f"!!!!!!!! FATAL: FAILED TO LOAD H5 MODEL. Error: {e}")
else:
    print(f"!!!!!!!! FATAL: Image model file not found at '{IMAGE_MODEL_PATH}'")

# Load Symptom Model
if os.path.exists(SYMPTOM_MODEL_PATH):
    try:
        symptom_model = joblib.load(SYMPTOM_MODEL_PATH)
        print("SUCCESS: Joblib symptom model loaded from local file.")
    except Exception as e:
        print(f"!!!!!!!! FATAL: FAILED TO LOAD JOBLIB MODEL. Error: {e}")
else:
    print(f"!!!!!!!! FATAL: Symptom model file not found at '{SYMPTOM_MODEL_PATH}'")

if image_model and symptom_model:
    print("--- All models loaded successfully. Server is ready. ---")
else:
    print("--- One or more models failed to load. Server will report errors. ---")


# --- 3. The Rest of the App (No changes needed here) ---
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
    return {"message": "Welcome to the Cow Disease Detection API (Local Version)."}

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

# --- 4. Running the Server Locally ---
# This block allows you to run the server directly with `python main.py`
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

