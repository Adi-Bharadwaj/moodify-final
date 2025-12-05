"""
Member 2 – Emotion Detection Module

This file does:
- From image -> mood  (happy / sad / angry / neutral)
- Voting (3 runs) for more stable output
- From text  -> mood  (for textbox in UI)

Dependencies:
    pip install google-genai pillow
"""

import os
import json

from google import genai
from PIL import Image

# --------------------------------------------------
# 1. GEMINI CLIENT SETUP
# --------------------------------------------------

# Put your real key here, inside quotes:
API_KEY = "AIzaSyC_g9NgwnffmexnmFTkBp4I4I1-sbqSaag"   # <-- CHANGE THIS

if not API_KEY or API_KEY == "AIzaSyC_g9NgwnffmexnmFTkBp4I4I1-sbqSaag":
    print("[WARN] API_KEY is not set. Edit emotion_detector.py and put your real key.")

# Create Gemini client
client = genai.Client(api_key=API_KEY)

# Use a model that exists for your account (you saw these in list_models.py)
MODEL_NAME = "models/gemini-2.5-flash"


# --------------------------------------------------
# 2. 1 -> MOOD (single call helper)
# --------------------------------------------------

def _single_emotion_from_image(image_path: str) -> str:
    """
    One call to Gemini for this image.
    Returns one of: happy / sad / angry / neutral
    or 'neutral' if something goes wrong.
    """
    if not os.path.exists(image_path):
        print("[ERROR] Image file not found:", image_path)
        return "neutral"

    try:
        img = Image.open(image_path)
    except Exception as e:
        print("[ERROR] Failed to open image:", e)
        return "neutral"

    prompt = (
        "You are an emotion detector. Look only at the person's facial expression "
        "and classify it as exactly one of: happy, sad, angry, neutral.\n"
        "Respond using this exact JSON format:\n"
        "{\"emotion\": \"happy|sad|angry|neutral\", \"confidence\": 0-100}\n"
        "Do not add any extra text outside the JSON."
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt, img],
        )
    except Exception as e:
        print("[ERROR] Gemini API error (image):", repr(e))
        return "neutral"

    raw_text = (response.text or "").strip()
    print("[DEBUG] Image raw:", raw_text)

    # Try JSON parsing first
    try:
        data = json.loads(raw_text)
        e = str(data.get("emotion", "")).lower()
        conf = float(data.get("confidence", 0.0))
        print("[DEBUG] Image parsed:", e, conf)

        # low confidence -> treat as neutral
        if conf < 50:
            return "neutral"

        if e in ["happy", "sad", "angry", "neutral"]:
            return e

        return "neutral"

    except Exception:
        # Fallback: look for keywords
        low = raw_text.lower()
        if "happy" in low:
            return "happy"
        if "angry" in low or "mad" in low:
            return "angry"
        if "sad" in low:
            return "sad"
        return "neutral"


def classify_emotion_from_image(image_path: str) -> str:
    """
    Public function: one-shot detection from image.
    Other members can use this if they don't want voting.
    """
    return _single_emotion_from_image(image_path)


# --------------------------------------------------
# 3. IMAGE -> MOOD (voting: 3 runs)
# --------------------------------------------------

def stable_mood(image_path: str) -> str:
    """
    Calls _single_emotion_from_image 3 times and returns
    the majority mood. If no majority, returns neutral.
    """
    votes = []
    for _ in range(3):
        result = _single_emotion_from_image(image_path)
        votes.append(result)

    print("[DEBUG] Votes:", votes)

    for label in ["happy", "sad", "angry", "neutral"]:
        if votes.count(label) >= 2:
            return label

    return "neutral"


# --------------------------------------------------
# 4. TEXT -> MOOD (for textbox)
# --------------------------------------------------

def classify_emotion_from_text(feeling_text: str) -> str:
    """
    Takes a sentence like:
        "I'm tired and kind of upset"
    and returns one of: happy, sad, angry, neutral.

    This is what the UI textbox will call.
    """
    if not feeling_text or not feeling_text.strip():
        return "neutral"

    prompt = (
        "You are an emotion detector for text. "
        "Read the following description of how a person feels and classify "
        "their overall emotion as exactly one of: happy, sad, angry, neutral.\n\n"
        f'Text: "{feeling_text}"\n\n'
        "Respond using this exact JSON format:\n"
        "{\"emotion\": \"happy|sad|angry|neutral\", \"confidence\": 0-100}\n"
        "Do not add anything else outside the JSON."
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
    except Exception as e:
        print("[ERROR] Gemini API error (text):", repr(e))
        return "neutral"

    raw_text = (response.text or "").strip()
    print("[DEBUG] Text raw:", raw_text)

    try:
        data = json.loads(raw_text)
        e = str(data.get("emotion", "")).lower()
        conf = float(data.get("confidence", 0.0))
        print("[DEBUG] Text parsed:", e, conf)

        if conf < 50:
            return "neutral"

        if e in ["happy", "sad", "angry", "neutral"]:
            return e

        return "neutral"

    except Exception:
        low = raw_text.lower()
        if "happy" in low:
            return "happy"
        if "angry" in low or "mad" in low:
            return "angry"
        if "sad" in low:
            return "sad"
        return "neutral"


# --------------------------------------------------
# 5. LOCAL TESTING (for you only)
# --------------------------------------------------

if __name__ == "__main__":
    print("1) Test from image")
    print("2) Test from text")
    choice = input("Choose 1 or 2: ").strip()

    if choice == "1":
        path = input("Enter image filename (e.g. captured_face.jpg or test.jpg): ").strip()
        mood = stable_mood(path)
        print("FINAL MOOD (image):", mood)

    elif choice == "2":
        text = input("Type how you feel: ")
        mood = classify_emotion_from_text(text)
        print("FINAL MOOD (text):", mood)

    else:
        print("Invalid choice.")

