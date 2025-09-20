import tensorflow as tf

# Load your trained Keras model
model = tf.keras.models.load_model('cow_disease_model.h5')

# Create a TFLite converter object
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Apply optimizations (optional but recommended)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Convert the model
tflite_model = converter.convert()

# Save the TFLite model to a file
with open('cow_disease_model.tflite', 'wb') as f:
    f.write(tflite_model)

print("Successfully converted cow_disease_model.h5 to cow_disease_model.tflite")
