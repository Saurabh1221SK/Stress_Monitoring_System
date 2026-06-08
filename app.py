from flask import Flask, jsonify
from flask_cors import CORS
import numpy as np
import cv2

from tensorflow.keras.models import load_model

app = Flask(__name__)
CORS(app)

model = load_model("model_emosi.h5")

class_labels = [
    'angry',
    'disgusted',
    'fearful',
    'happy',
    'neutral',
    'sad',
    'surprised'
]

stress_map = {
    'happy': 10,
    'neutral': 30,
    'surprised': 45,
    'sad': 70,
    'disgusted': 75,
    'angry': 90,
    'fearful': 95
}

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    'haarcascade_frontalface_default.xml'
)

cap = cv2.VideoCapture(0)

stress_history = []

@app.route("/stress")
def get_stress():

    ret, frame = cap.read()

    if not ret:
        return jsonify({"error": "camera failed"})

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5
    )

    stress = 0
    emotion = "none"

    for (x, y, w, h) in faces:

        face = gray[y:y+h, x:x+w]

        face = cv2.resize(face, (48, 48))

        face = face / 255.0

        face = face.reshape(1, 48, 48, 1)

        prediction = model.predict(face, verbose=0)

        emotion = class_labels[np.argmax(prediction)]

        stress = stress_map[emotion]

        stress_history.append(stress)

        if len(stress_history) > 30:
            stress_history.pop(0)

    avg_stress = (
        sum(stress_history) / len(stress_history)
        if stress_history else 0
    )

    return jsonify({
        "stress": round(avg_stress, 2),
        "emotion": emotion
    })

if __name__ == "__main__":
    app.run(port=5000)