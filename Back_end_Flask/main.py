import librosa
import numpy as np
from flask_cors import CORS
from keras.models import load_model
import pickle
from flask import Flask, request, jsonify
from google.cloud import storage
import soundfile as sf
from subprocess import PIPE, run
from io import BytesIO
   	
def get_top_5_predictions(audio_blob, sample_rate=16000, duration=1, top_db=20):
    model = load_model("./best_model_other_92.h5")

    with open("./class_label_other.pkl", "rb") as f:
        class_labels = pickle.load(f)

    #signal, original_sample_rate = sf.read(audio_blob)
    signal, _ = librosa.load(audio_blob)
  
    signal, _ = librosa.effects.trim(signal, top_db=top_db)

    max_length = sample_rate * duration

    # Pad or truncate the signal
    if len(signal) < max_length:
        signal = np.pad(signal, (0, max_length - len(signal)))
    elif len(signal) > max_length:
        signal = signal[:max_length]


    mfcc = librosa.feature.mfcc(y=signal, sr=sample_rate, n_mfcc=13)
    mfcc = librosa.util.fix_length(mfcc, size=63, axis=1)
    mfcc = mfcc[np.newaxis, ..., np.newaxis]


    predictions = model.predict(mfcc)
    top_5_indices = predictions[0].argsort()[-5:][::-1]
    top_5_probabilities = predictions[0][top_5_indices]


    top_5_predictions = [(class_labels[i], prob) for i, prob in zip(top_5_indices, top_5_probabilities)]

    return top_5_predictions

app = Flask(__name__)
CORS(app)  # This line enables CORS for all routes and origins
@app.route('/predict', methods=['POST'])
def predict_audio():

    if 'file' not in request.files:
        return jsonify({'error': 'No audio file found'}), 400

    audio_file = request.files['file']
    audio_blob = audio_file.read()

    def convert_webm_to_wav(webm_blob):
        process = run(['ffmpeg', '-y', '-i', 'pipe:', '-f', 'wav', '-'], input=webm_blob, stdout=PIPE, stderr=PIPE)
        return process.stdout

    #path = "common_voice_fr_21899099.mp3"
    output_bytes = convert_webm_to_wav(audio_blob)
    output_buffer = BytesIO(output_bytes)


    top_5_predictions = get_top_5_predictions(output_buffer)


    predictions_list = [{'label': label, 'probability': float(prob)} for label, prob in top_5_predictions]

    return jsonify({'predictions': predictions_list})

if __name__ == "__main__":
    app.run(debug=False, port=5000, host='0.0.0.0')
