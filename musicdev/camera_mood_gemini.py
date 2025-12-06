import os
import random
from PIL import Image
import json
from google import genai
import cv2

# -----------------------------------------------------
# GEMINI API KEY SETUP
# -----------------------------------------------------
GEMINI_API_KEY = "AIzaSyBdaWWfn7UzdjrPZt2Krn52i6lVzXthxVk"
# Create Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Use a model that exists for your account (you saw these in list_models.py)
MODEL_NAME = "models/gemini-2.5-flash"

# Official Gemini v1 models
_MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-2.0-flash-lite-preview"
]

LABELS = ["happy", "sad", "angry", "neutral", "excited", "stressed"]


# -----------------------------------------------------
# FACE EXTRACTION
# -----------------------------------------------------
def extract_face(image_path: str) -> str:
    try:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        img = cv2.imread(image_path)
        if img is None:
            return image_path

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return image_path

        x, y, w, h = faces[0]
        face_crop = img[y:y + h, x:x + w]
        cropped_path = image_path.replace(".png", "_crop.png")
        cv2.imwrite(cropped_path, face_crop)
        return cropped_path

    except Exception:
        return image_path


# -----------------------------------------------------
# CHOOSE BEST AVAILABLE MODEL
# -----------------------------------------------------
def _choose_model():
    for model_name in _MODEL_CANDIDATES:
        try:
            return genai.GenerativeModel(model_name)
        except Exception:
            continue
    return None


# -----------------------------------------------------
# FALLBACKS
# -----------------------------------------------------
def _text_fallback(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["happy", "great", "joy", "excited", "awesome"]):
        return "happy"
    if any(w in t for w in ["sad", "down", "unhappy", "lonely"]):
        return "sad"
    if any(w in t for w in ["angry", "mad", "furious"]):
        return "angry"
    if any(w in t for w in ["stress", "stressed", "anxious"]):
        return "stressed"
    return "neutral"


def _image_fallback(image_path: str) -> str:
    try:
        img = Image.open(image_path).convert("L").resize((10, 10))
        avg = sum(img.getdata()) / 100
        if avg > 140:
            return random.choice(["happy", "neutral"])
        elif avg > 100:
            return random.choice(["neutral", "happy", "sad"])
        else:
            return random.choice(["sad", "angry", "neutral"])
    except:
        return random.choice(LABELS)


# -----------------------------------------------------
# IMAGE → EMOTION
# -----------------------------------------------------
def classify_emotion_from_image_gemini(image_path: str) -> str:
    processed_path = extract_face(image_path)

    #model = _choose_model()
    #if not model:
     #   return _image_fallback(processed_path)

    #with open(processed_path, "rb") as f:
        #img_bytes = f.read()
    try:
        img = Image.open(processed_path)
    except Exception as e:
        print("[ERROR] Failed to open image:", e)
        return "neutral"

    prompt = (
        "Analyze the facial expression and respond with ONLY one word: "
        "happy, sad, angry, neutral, excited, stressed."
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt, img],
        )
        print("response: ",response)
        text = (response.text or "").strip().lower()
        print("text: ",text)
        for label in LABELS:
            if label in text:
                return label

    except Exception as e:
        print("Gemini image call failed:", e)

    return _image_fallback(processed_path)


# -----------------------------------------------------
# STABLE VOTING (reduces noise)
# -----------------------------------------------------
def stable_mood_gemini(image_path: str, votes: int = 3) -> str:
    results = [classify_emotion_from_image_gemini(image_path) for _ in range(votes)]
    for label in LABELS:
        if results.count(label) >= (votes // 2) + 1:
            return label
    return max(set(results), key=results.count)


# -----------------------------------------------------
# TEXT → EMOTION
# -----------------------------------------------------
def classify_emotion_from_text_gemini(text: str) -> str:
    model=MODEL_NAME
    if not model:
        return _text_fallback(text)

    
    prompt = (
        "Classify the emotional tone of this message in ONE word: "
        "happy, sad, angry, neutral, excited, stressed."
          )  
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt, text],
        )
        print("response: ",response)
        text = (response.text or "").strip().lower()
        print("text: ",text)
        for lab in LABELS:
            if lab == out or lab in out:
                 return lab
    except Exception:
        pass

    return _text_fallback(text)
