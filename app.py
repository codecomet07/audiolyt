from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import tensorflow as tf
import os
import requests
from utils.feature_extractor import extract_features
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)
CORS(app)

# Download model from GitHub if not present
MODEL_URL = "https://github.com/codecomet07/latest.github.io/audio_classification_model.h5"
MODEL_PATH = "audio_classification_model.h5"

if not os.path.exists(MODEL_PATH):
    print("Downloading model...")
    response = requests.get(MODEL_URL)
    with open(MODEL_PATH, "wb") as f:
        f.write(response.content)

# Load the model
model = tf.keras.models.load_model(MODEL_PATH)

# Label encoder
label_encoder = LabelEncoder()
label_encoder.classes_ = np.array(['autotuned', 'deepfake', 'real'])

@app.route('/predict', methods=['POST'])
def predict():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400

    file = request.files['audio']
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    features = extract_features(file_path)
    if features is not None:
        features = features.reshape(1, -1)
        prediction = model.predict(features)
        class_index = np.argmax(prediction)
        result = label_encoder.inverse_transform([class_index])[0]
        return jsonify({'prediction': result})

    return jsonify({'error': 'Could not process the audio'}), 500

@app.route('/echo', methods=['POST'])
def echo_string():
    # Check if the request has JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    # Get the string from the JSON data
    data = request.get_json()
    
    # Check if 'input_string' is in the JSON
    if 'input_string' not in data:
        return jsonify({"error": "No 'input_string' provided"}), 400
    
    # Return the input string
    return jsonify({"result": data['input_string']})


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=10000)
