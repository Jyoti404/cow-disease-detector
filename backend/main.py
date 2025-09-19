import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
import io
import joblib
import os

# --- 1. App and Model Setup ---
app = FastAPI(title="Cow Disease Detection API")

# Configure CORS (Cross-Origin Resource Sharing) to allow the frontend to communicate with this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for simplicity. For production, you might restrict this.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods.
    allow_headers=["*"],  # Allows all headers.
)

# --- 2. Load Models from Local Files ---
# Render will have these files because they are in your GitHub repository.
# This code runs once when the application starts up.
try:
    print("Attempting to load models...")
    image_model = load_model('cow_disease_model.h5')
    symptom_model = joblib.load('symptom_model.joblib')
    print("Models loaded successfully from local files.")
except Exception as e:
    print(f"FATAL: Error loading models: {e}")
    # If the models can't be loaded, the app is not useful. We set them to None.
    image_model = None
    symptom_model = None

# --- 3. Configuration & Constants ---
CLASS_NAMES = ['LUMPY SKIN', 'NORMAL SKIN']
IMAGE_WIDTH, IMAGE_HEIGHT = 224, 224
# Weights for combining the two model predictions.
IMAGE_WEIGHT = 0.60
TEXT_WEIGHT = 0.40


# --- 4. Helper Function for Image Processing ---
def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Takes image bytes, preprocesses them for the model, and returns a numpy array.
    """
    try:
        image = load_img(io.BytesIO(image_bytes), target_size=(IMAGE_WIDTH, IMAGE_HEIGHT))
        image_array = img_to_array(image)
        image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension
        image_array /= 255.0  # Rescale pixel values to [0, 1]
        return image_array
    except Exception as e:
        # This will catch errors from corrupted or invalid image files.
        raise HTTPException(status_code=400, detail=f"Invalid or corrupted image file: {e}")


# --- 5. API Endpoints ---

@app.get("/")
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to the Multi-Modal Cow Disease Detection API, configured for Render."}


@app.post("/predict")
async def predict(
    file: UploadFile = File(..., description="Image file of the cow's skin."),
    symptoms: str = Form(..., description="Text description of the cow's symptoms.")
):
    """
    Main prediction endpoint. Receives an image and symptoms, and returns a fused diagnosis.
    """
    # First, check if the models were loaded correctly on startup.
    if not image_model or not symptom_model:
        raise HTTPException(status_code=503, detail="Models are not available. Check server logs for errors.")

    # --- Step 1: Image Prediction ---
    image_bytes = await file.read()
    processed_image = preprocess_image(image_bytes)
    image_prediction_probs = image_model.predict(processed_image)[0]

    # --- Step 2: Text Prediction ---
    # The model expects a list/array of texts, so we wrap the single symptom string in a list.
    symptom_prediction_probs = symptom_model.predict_proba([symptoms])[0]

    # --- Step 3: Fusion Logic ---
    # Combine the probabilities from both models using the predefined weights.
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


# --- 6. Run the App (for local development) ---
# This part is ignored by Render, which uses the "Start Command" you provide in the dashboard.
# It's useful for running the app on your own computer.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

