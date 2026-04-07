import os
import librosa
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input

def extract_features(dataset):
    X, y = [], []
    for label in ['scream', 'non_scream']:
        folder = os.path.join(dataset, label)
        print(f"🔍 Looking in folder: {folder}")
        for fname in os.listdir(folder):  # ✅ Fixed: now lists files from the correct subfolder
            if not fname.lower().endswith('.wav'):
                continue
            path = os.path.join(folder, fname)
            try:
                audio, sr = librosa.load(path, duration=2.5, sr=16000)
                mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
                mfcc_mean = np.mean(mfcc.T, axis=0)
                X.append(mfcc_mean)
                y.append(1 if label == 'scream' else 0)
            except Exception as e:
                print(f"⚠️ Error loading {fname}: {e}")
    return np.array(X), np.array(y)

print("🔍 Extracting features...")
X, y = extract_features('dataset')

if len(X) < 2:
    print("❌ Not enough data! Please add more .wav files to both 'scream' and 'non_scream' folders.")
    exit()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("🧠 Training model...")
model = Sequential([
    Input(shape=(13,)),
    Dense(32, activation='relu'),
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=25, batch_size=8, validation_data=(X_test, y_test))

print("💾 Saving TFLite model...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
os.makedirs("model", exist_ok=True)
with open("model/scream_model.tflite", "wb") as f:
    f.write(tflite_model)

print("✅ Model saved successfully at model/scream_model.tflite")
