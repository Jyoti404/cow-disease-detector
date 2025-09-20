import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
# We now import the TFLite Interpreter instead of the full Keras library
import tflite_runtime.interpreter as tflite
from PIL import Image # Pillow is used for more direct image processing
import numpy as np
import io
import joblib
import os
import requests

# --- 1. App Setup ---
app = FastAPI(title="Cow Disease Detection API (TFLite Version)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Model Downloading and Loading Logic ---

IMAGE_MODEL_URL = "https://github.com/gayatriverm/cow-disease-detector/releases/download/v1.0.0/cow_disease_model.tflite"
SYMPTOM_MODEL_URL = "https://github.com/gayatriverm/cow-disease-detector/releases/download/v1.0.0/symptom_model.joblib"


IMAGE_MODEL_PATH = "cow_disease_model.tflite"
SYMPTOM_MODEL_PATH = "symptom_model.joblib"

def download_file_from_url(url, local_path):
    """
    Downloads a file from a URL to a local path if it doesn't already exist.
    """
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
            # If download fails, the app cannot start, so we raise an error.
            raise RuntimeError(f"FATAL: Error downloading {local_path}: {e}")
    else:
        print(f"{os.path.basename(local_path)} already exists. Skipping download.")

# --- Download models when the application starts up ---
print("Server starting up. Checking for models...")
try:
    download_file_from_url(IMAGE_MODEL_URL, IMAGE_MODEL_PATH)
    download_file_from_url(SYMPTOM_MODEL_URL, SYMPTOM_MODEL_PATH)
except RuntimeError as e:
    print(e)
    # Set models to None if download fails so the app can start and report errors.
    image_model = None
    symptom_model = None

# --- Load the downloaded models ---
if os.path.exists(IMAGE_MODEL_PATH) and os.path.exists(SYMPTOM_MODEL_PATH):
    try:
        # Load TFLite model and allocate tensors.
        image_model = tflite.Interpreter(model_path=IMAGE_MODEL_PATH)
        image_model.allocate_tensors()
        # Get input and output tensor details for later use.
        image_input_details = image_model.get_input_details()
        image_output_details = image_model.get_output_details()
        
        # Load the scikit-learn model
        symptom_model = joblib.load(SYMPTOM_MODEL_PATH)
        print("TFLite and symptom models loaded successfully.")
    except Exception as e:
        print(f"FATAL: Error loading models after download: {e}")
        image_model = None
        symptom_model = None
else:
    print("FATAL: One or more model files are missing. Cannot load models.")
    image_model = None
    symptom_model = None


# --- 3. Configuration & Constants ---
CLASS_NAMES = ['LUMPY SKIN', 'NORMAL SKIN']
IMAGE_WIDTH, IMAGE_HEIGHT = 224, 224
IMAGE_WEIGHT = 0.60
TEXT_WEIGHT = 0.40

# --- 4. Helper Functions for Prediction ---
def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Takes image bytes, preprocesses them for the TFLite model, and returns a numpy array.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT))
        image_array = np.array(image, dtype=np.float32)
        image_array = np.expand_dims(image_array, axis=0)
        image_array /= 255.0 # Normalize to [0, 1]
        return image_array
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid or corrupted image file: {e}")

def predict_with_tflite(interpreter, image_data):
    """
    Performs inference using the loaded TFLite interpreter.
    """
    # Set the value of the input tensor.
    interpreter.set_tensor(image_input_details[0]['index'], image_data)
    # Run the inference.
    interpreter.invoke()
    # Get the result.
    output_data = interpreter.get_tensor(image_output_details[0]['index'])
    return output_data[0] # Return the probability array


# --- 5. API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Cow Disease Detection API (TFLite Version)."}

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    symptoms: str = Form(...)
):
    if not image_model or not symptom_model:
        raise HTTPException(status_code=503, detail="Models are not available. Check server logs for errors.")

    # --- Step 1: Image Prediction with TFLite ---
    image_bytes = await file.read()
    processed_image = preprocess_image(image_bytes)
    image_prediction_probs = predict_with_tflite(image_model, processed_image)

    # --- Step 2: Text Prediction ---
    symptom_prediction_probs = symptom_model.predict_proba([symptoms])[0]

    # --- Step 3: Fusion Logic ---
    fused_probs = (image_prediction_probs * IMAGE_WEIGHT) + (symptom_prediction_probs * TEXT_WEIGHT)
    
    fused_prediction_index = np.argmax(fused_probs)
    fused_prediction_name = CLASS_NAMES[fused_prediction_index]
    fused_confidence = float(fused_probs[fused_prediction_index])

    # --- Step 4: Return the detailed response ---
    return {
        "filename": file.filename,
        "image_prediction": CLASS_NAMES[np.argmax(image_prediction_probs)],
        "image_confidence": f"{np.max(image_prediction_probs):.2f}",
        "symptom_prediction": CLASS_NAMES[np.argmax(symptom_prediction_probs)],
        "symptom_confidence": f"{np.max(symptom_prediction_probs):.2f}",
        "fused_prediction": fused_prediction_name,
        "fused_confidence": f"{fused_confidence:.2f}"
    }

# This part is for local development and is ignored by Render.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

