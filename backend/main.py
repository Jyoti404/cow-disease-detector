import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
import io
import joblib

# --- 1. App and Model Setup ---
app = FastAPI(title="Cow Disease Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load Models ---
try:
    # Load the CNN model for image prediction
    image_model = load_model('cow_disease_model.h5')
    print("Image model loaded successfully.")
    # Load the scikit-learn pipeline for text prediction
    symptom_model = joblib.load('symptom_model.joblib')
    print("Symptom model loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}")
    image_model = None
    symptom_model = None

# --- Configuration ---
CLASS_NAMES = ['LUMPY SKIN', 'NORMAL SKIN']
IMAGE_WIDTH, IMAGE_HEIGHT = 224, 224
# Define weights for fusion. We trust the visual evidence from the image slightly more.
IMAGE_WEIGHT = 0.60
TEXT_WEIGHT = 0.40


# --- 2. Helper Function for Image Preprocessing ---
def preprocess_image(image_bytes):
    """
    Preprocesses the uploaded image to the format the model expects.
    """
    try:
        # Load the image from bytes into a PIL object
        image = load_img(io.BytesIO(image_bytes), target_size=(IMAGE_WIDTH, IMAGE_HEIGHT))
        # Convert the PIL image to a NumPy array
        image_array = img_to_array(image)
        # Add a batch dimension (e.g., from (224, 224, 3) to (1, 224, 224, 3))
        image_array = np.expand_dims(image_array, axis=0)
        # Rescale the pixel values to the [0, 1] range, as done during training
        image_array /= 255.0
        return image_array
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid or corrupted image file: {e}")


# --- 3. API Endpoints ---
@app.get("/")
def read_root():
    """
    Root endpoint to welcome users and confirm the API is running.
    """
    return {"message": "Welcome to the Multi-Modal Cow Disease Detection API."}

@app.post("/predict")
async def predict(
    file: UploadFile = File(..., description="Image file of the cow's skin."),
    symptoms: str = Form(..., description="Text description of the cow's symptoms.")
):
    """
    Receives an image and text symptoms, fuses the predictions, and returns the result.
    """
    if not image_model or not symptom_model:
        raise HTTPException(status_code=503, detail="One or more models are not loaded or available.")

    # === Image Prediction ===
    try:
        image_bytes = await file.read()
        processed_image = preprocess_image(image_bytes)
        # Get probabilities for each class from the image model
        image_prediction_probs = image_model.predict(processed_image)[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the image: {e}")


    # === Text Prediction ===
    try:
        # The symptom model expects a list of strings for prediction
        # predict_proba gives probabilities for each class: [P(class_0), P(class_1)]
        symptom_prediction_probs = symptom_model.predict_proba([symptoms])[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the symptoms: {e}")


    # === Fusion Logic ===
    # Combine the predictions using a weighted average.
    # The class order [LUMPY SKIN, NORMAL SKIN] must be consistent for both models.
    fused_probs = (image_prediction_probs * IMAGE_WEIGHT) + (symptom_prediction_probs * TEXT_WEIGHT)

    fused_prediction_index = np.argmax(fused_probs)
    fused_prediction_name = CLASS_NAMES[fused_prediction_index]
    fused_confidence = float(fused_probs[fused_prediction_index])

    # Return a detailed response
    return {
        "filename": file.filename,
        "image_prediction": CLASS_NAMES[np.argmax(image_prediction_probs)],
        "image_confidence": f"{np.max(image_prediction_probs):.2f}",
        "symptom_prediction": CLASS_NAMES[np.argmax(symptom_prediction_probs)],
        "symptom_confidence": f"{np.max(symptom_prediction_probs):.2f}",
        "fused_prediction": fused_prediction_name,
        "fused_confidence": f"{fused_confidence:.2f}"
    }

# --- 4. Run the App ---
# This block allows you to run the server directly with `python main.py`
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

