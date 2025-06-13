from flask import Flask, request, jsonify
import whisper
from transformers import pipeline
import face_recognition
import numpy as np
import cv2
import os
import tempfile
import pytesseract
from PIL import Image

app = Flask(__name__)

# Load models once
whisper_model = whisper.load_model("base")
sentiment_analyzer = pipeline("sentiment-analysis")
audio_emotion_analyzer = pipeline("audio-classification", model="superb/hubert-large-superb-er")

@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio = request.files['audio']
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
        audio.save(temp_audio.name)
        result = whisper_model.transcribe(temp_audio.name)
        os.remove(temp_audio.name)
    return jsonify({'transcription': result['text']})

@app.route('/analyze_text', methods=['POST'])
def analyze_text():
    import openai
    text = request.json['text']
    sentiment = sentiment_analyzer(text)[0]
    # Advanced fraud analysis using GPT
    openai.api_key = os.getenv("OPENAI_API_KEY")
    gpt_prompt = f"""
    You are an expert fraud analyst for supplier onboarding. Analyze the following supplier's answer for signs of fraud, deception, vagueness, overpromising, or risk. If you find any red flags, explain them. Otherwise, explain why the answer seems trustworthy. Return a JSON object with fields: 'fraud_flags' (int), 'red_flags' (list of strings), 'explanation' (string), and 'trust_score' (0-100, lower if risky, higher if trustworthy).

    Supplier answer:
    {text}
    """
    gpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful fraud analyst."},
            {"role": "user", "content": gpt_prompt}
        ],
        max_tokens=300,
        temperature=0.2
    )
    import json
    try:
        gpt_json = json.loads(gpt_response.choices[0].message['content'])
    except Exception:
        gpt_json = {"fraud_flags": 0, "red_flags": [], "explanation": "Could not parse GPT response.", "trust_score": 50}
    return jsonify({'sentiment': sentiment, 'gpt_fraud_analysis': gpt_json})

@app.route('/analyze_audio_emotion', methods=['POST'])
def analyze_audio_emotion():
    audio = request.files['audio']
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
        audio.save(temp_audio.name)
        result = audio_emotion_analyzer(temp_audio.name)
        os.remove(temp_audio.name)
    return jsonify({'emotion': result})

@app.route('/verify_face', methods=['POST'])
def verify_face():
    face_img = request.files['face']
    id_img = request.files['id']
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_face, \
         tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_id:
        face_img.save(temp_face.name)
        id_img.save(temp_id.name)
        face_encodings = face_recognition.face_encodings(face_recognition.load_image_file(temp_face.name))
        id_encodings = face_recognition.face_encodings(face_recognition.load_image_file(temp_id.name))
        os.remove(temp_face.name)
        os.remove(temp_id.name)
        if face_encodings and id_encodings:
            match = face_recognition.compare_faces([id_encodings[0]], face_encodings[0])[0]
            distance = np.linalg.norm(id_encodings[0] - face_encodings[0])
            return jsonify({'match': bool(match), 'distance': float(distance)})
        else:
            return jsonify({'error': 'Face not detected in one or both images.'}), 400

@app.route('/ocr_document', methods=['POST'])
def ocr_document():
    """
    Accepts an uploaded image or PDF, extracts text using pytesseract, and returns the result.
    Only free tools are used (pytesseract + Tesseract OCR engine).
    """
    file = request.files.get('document')
    if not file:
        return jsonify({'error': 'No document uploaded.'}), 400
    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_img:
        file.save(temp_img.name)
        try:
            # Open image for OCR
            img = Image.open(temp_img.name)
            text = pytesseract.image_to_string(img)
        except Exception as e:
            os.remove(temp_img.name)
            return jsonify({'error': f'OCR failed: {str(e)}'}), 500
        os.remove(temp_img.name)
    return jsonify({'extracted_text': text})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
