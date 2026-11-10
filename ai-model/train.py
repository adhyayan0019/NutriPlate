from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import json

# Data Augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,
    zoom_range=0.2,
    horizontal_flip=True,
    shear_range=0.2
)

val_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

# Load dataset
train = train_datagen.flow_from_directory(
    '../khana',
    target_size=(224,224),
    batch_size=16,
    class_mode='categorical',
    subset='training'
)

val = val_datagen.flow_from_directory(
    '../khana',
    target_size=(224,224),
    batch_size=16,
    class_mode='categorical',
    subset='validation'
)

#  Load MobileNetV2 (Pretrained)
base_model = MobileNetV2(
    input_shape=(224,224,3),
    include_top=False,
    weights='imagenet'
)

#  Freeze most layers
for layer in base_model.layers[:-50]:
    layer.trainable = False

# Fine-tune last 50 layers
for layer in base_model.layers[-50:]:
    layer.trainable = True

# Build model
model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.BatchNormalization(),   
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(train.num_classes, activation='softmax')
])

# Compile model
model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Callbacks 
early_stop = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

checkpoint = ModelCheckpoint(
    "best_model.h5",
    monitor='val_accuracy',
    save_best_only=True,
    verbose=1
)

# Train model (20 epochs)
history = model.fit(
    train,
    validation_data=val,
    epochs=20,
    callbacks=[early_stop, checkpoint]
)

# Save final model
model.save("final_model.h5")

# Save class labels
with open("class_indices.json", "w") as f:
    json.dump(train.class_indices, f)

print("✅ Training Complete with 20 Epochs + Optimized Setup")