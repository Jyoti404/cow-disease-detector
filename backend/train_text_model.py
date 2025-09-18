import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

# --- 1. Create a Synthetic Dataset ---
# In a real-world scenario, you would collect this data from veterinarians or farm records.
# We map to 0 (LUMPY SKIN) and 1 (NORMAL/OTHER) to align with our image model's classes.
data = {
    'symptoms': [
        "large skin nodules, fever, loss of appetite, watery eyes",
        "firm raised nodules on skin, reduced milk yield, swollen limbs",
        "high fever, scabby skin lesions, reluctance to move, nasal discharge",
        "visible lumps on hide and neck, animal is lethargic and not eating",
        "multiple hard nodules across the body, animal has a fever",
        "no visible skin issues, eating well, normal energy levels",
        "animal seems healthy, good appetite, no fever or nodules",
        "minor scrape on leg, otherwise healthy and active",
        "coughing but no skin lesions, eating normally",
        "limping slightly, but skin is clear and appetite is strong"
    ],
    'disease': [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]  # 0: Lumpy Skin, 1: Normal/Other
}
df = pd.DataFrame(data)

# --- 2. Define the Model Pipeline ---
# We'll create a pipeline that first converts text to numerical vectors (TF-IDF)
# and then feeds them into a Logistic Regression classifier.
text_model_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english')),
    ('clf', LogisticRegression(solver='liblinear', random_state=42))
])

# --- 3. Train the Model ---
print("Training the text-based symptom model...")
X = df['symptoms']
y = df['disease']
text_model_pipeline.fit(X, y)
print("Training complete.")

# --- 4. Save the Model and Vectorizer ---
# We save the entire pipeline, which includes both the vectorizer and the classifier.
joblib.dump(text_model_pipeline, 'symptom_model.joblib')

print("\nSymptom model saved as 'symptom_model.joblib'")
print("This model is now ready to be used by the FastAPI backend.")

# --- 5. Test the saved model (optional) ---
print("\n--- Testing the loaded model ---")
loaded_model = joblib.load('symptom_model.joblib')
test_symptoms = [
    "animal has fever and many skin nodules", # Should predict Lumpy Skin
    "cow is healthy and eating"              # Should predict Normal
]

# The model's predict_proba method gives us confidence scores for each class.
# The order is [P(Lumpy Skin), P(Normal)]
predictions = loaded_model.predict_proba(test_symptoms)
for symptom, pred in zip(test_symptoms, predictions):
    print(f"Symptom: '{symptom}'")
    print(f"  -> Prediction (Probabilities): [Lumpy Skin: {pred[0]:.2f}, Normal: {pred[1]:.2f}]")

