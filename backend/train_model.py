import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ReduceLROnPlateau
import matplotlib.pyplot as plt
import numpy as np

# --- 1. Setup and Configuration ---
IMAGE_WIDTH, IMAGE_HEIGHT = 224, 224
BATCH_SIZE = 32
DATA_DIR = 'Lumpy Skin Images Dataset'
NUM_CLASSES = 2
INITIAL_EPOCHS = 15 ### CHANGE: We'll do an initial training phase
FINE_TUNE_EPOCHS = 10 ### CHANGE: And a fine-tuning phase
TOTAL_EPOCHS = INITIAL_EPOCHS + FINE_TUNE_EPOCHS

# --- 2. Data Preprocessing and Augmentation ---
datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=40, ### CHANGE: Increased augmentation range
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split=0.2
)

train_generator = datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMAGE_WIDTH, IMAGE_HEIGHT),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

validation_generator = datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMAGE_WIDTH, IMAGE_HEIGHT),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

# --- 3. Build the Model using Transfer Learning (ResNet50) ---
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(IMAGE_WIDTH, IMAGE_HEIGHT, 3))

# Start by freezing the base model
base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
x = Dropout(0.5)(x)
predictions = Dense(NUM_CLASSES, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)

# --- 4. Compile the Model ---
model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

print("--- Model Summary (Feature Extraction) ---")
model.summary()

# --- 5. Initial Training (Top Layers) ---
print("\n--- Starting Initial Training (frozen base model) ---")
history = model.fit(
    train_generator,
    epochs=INITIAL_EPOCHS,
    validation_data=validation_generator
    ### CHANGE: Removed steps_per_epoch and validation_steps
    ### Keras will now automatically infer the correct number of steps.
)

# --- 6. Prepare for Fine-Tuning ---
### CHANGE: The entire fine-tuning stage is new.
base_model.trainable = True

# We'll unfreeze the top layers of the ResNet model.
# Let's fine-tune from the 143rd layer onwards.
fine_tune_at = 143

# Freeze all the layers before the `fine_tune_at` layer
for layer in base_model.layers[:fine_tune_at]:
    layer.trainable = False

# Re-compile the model with a much lower learning rate for fine-tuning
model.compile(optimizer=Adam(learning_rate=0.00001), loss='categorical_crossentropy', metrics=['accuracy'])

print("\n--- Model Summary (Fine-Tuning) ---")
model.summary()


# --- 7. Fine-Tuning Training ---
print("\n--- Starting Fine-Tuning ---")
history_fine = model.fit(
    train_generator,
    epochs=TOTAL_EPOCHS,
    initial_epoch=history.epoch[-1], # Continue from where we left off
    validation_data=validation_generator
)


# --- 8. Evaluate the Model ---
# Combine history from both training phases
acc = history.history['accuracy'] + history_fine.history['accuracy']
val_acc = history.history['val_accuracy'] + history_fine.history['val_accuracy']
loss = history.history['loss'] + history_fine.history['loss']
val_loss = history.history['val_loss'] + history_fine.history['val_loss']

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(acc, label='Training Accuracy')
plt.plot(val_acc, label='Validation Accuracy')
plt.axvline(INITIAL_EPOCHS -1, color='gray', linestyle='--', label='Start Fine-Tuning') ### Added a line to show where fine-tuning starts
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(loss, label='Training Loss')
plt.plot(val_loss, label='Validation Loss')
plt.axvline(INITIAL_EPOCHS -1, color='gray', linestyle='--', label='Start Fine-Tuning') ### Added a line
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

# Final evaluation
final_loss, final_accuracy = model.evaluate(validation_generator)
print(f"\nFinal Validation Accuracy: {final_accuracy*100:.2f}%")
print(f"Final Validation Loss: {final_loss:.4f}")

if final_accuracy > 0.60:
    print("\nModel achieved >60% accuracy. Saving model.")
    model.save('cow_disease_model.h5')
    print("Model saved as cow_disease_model.h5")
else:
    print("\nModel did not reach 60% accuracy. Consider increasing FINE_TUNE_EPOCHS or adjusting the fine_tune_at layer.")
