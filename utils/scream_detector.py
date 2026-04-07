import numpy as np
import librosa
import tensorflow as tf

class ScreamDetector:
    def __init__(self, model_path='model/scream_model.tflite'):
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def predict(self, audio_path):
        try:
            audio, sr = librosa.load(audio_path, sr=16000, duration=2.5)
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            mfcc_mean = np.mean(mfcc.T, axis=0).reshape(1, 13).astype(np.float32)

            self.interpreter.set_tensor(self.input_details[0]['index'], mfcc_mean)
            self.interpreter.invoke()
            output = self.interpreter.get_tensor(self.output_details[0]['index'])
            return int(output[0][0] > 0.5)
        except Exception as e:
            print(f"❌ Error: {e}")
            return -1
