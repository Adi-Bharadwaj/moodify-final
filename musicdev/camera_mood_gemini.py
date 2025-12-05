# camera_mood_gemini.py
import os
import random
from PIL import Image

GEMINI_API_KEY = os.getenv("AIzaSyC25hfSzRZ4baYv5ExzEs8cwY57OczpmiQ")

# Try to import/configure the Google generative AI library if key present
genai = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print("Warning: google.generativeai import/config failed:", e)
        genai = None

# Candidate vision-capable models to try (may vary by account/region)
_MODEL_CANDIDATES = [
    "gemini-1.5-pro-vision",
    "gemini-1.5-pro-001",
    "gemini-1.5-flash-001",
    "gemini-1.0-pro-vision"
]

LABELS = ["happy", "sad", "angry", "neutral", "excited", "stressed"]


def _choose_model():
    """Return a GenerativeModel instance for the first working candidate, or None."""
    if not genai:
        return None
    for name in _MODEL_CANDIDATES:
        try:
            model = genai.GenerativeModel(name)
            # quick smoke call not made here to avoid extra requests; assume instantiation ok
            return model
        except Exception:
            continue
    return None


def _text_fallback(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["happy", "great", "joy", "excited", "awesome"]):
        return "happy"
    if any(w in t for w in ["sad", "down", "unhappy", "depressed", "lonely"]):
        return "sad"
    if any(w in t for w in ["angry", "mad", "furious", "annoyed"]):
        return "angry"
    if any(w in t for w in ["stress", "stressed", "anxious", "nervous"]):
        return "stressed"
    return "neutral"


def _image_fallback(image_path: str) -> str:
    """Very simple brightness-based fallback heuristic."""
    try:
        img = Image.open(image_path).convert("L").resize((10, 10))
        avg = sum(img.getdata()) / 100.0
        if avg > 140:
            return random.choice(["happy", "neutral"])
        elif avg > 100:
            return random.choice(["neutral", "happy", "sad"])
        else:
            return random.choice(["sad", "angry", "neutral"])
    except Exception:
        return random.choice(LABELS)


# -----------------------------
# PUBLIC: classify image using Gemini if possible, else fallback
# -----------------------------
def classify_emotion_from_image_gemini(image_path: str) -> str:
    model = _choose_model()
    if not model:
        return _image_fallback(image_path)

    # read raw bytes
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    prompt = (
        "Analyze the facial expression in the image and respond with EXACTLY one word: "
        "happy, sad, angry, neutral, excited, or stressed. Respond only with the word."
    )

    try:
        # pass prompt + image bytes in the format genai expects
        response = model.generate_content([prompt, {"mime_type": "image/png", "data": image_bytes}])
        text = (response.text or "").strip().lower()
        for lab in LABELS:
            if lab in text:
                return lab
    except Exception as e:
        print("Gemini image call failed:", e)

    return _image_fallback(image_path)


def stable_mood_gemini(image_path: str, votes: int = 3) -> str:
    results = [classify_emotion_from_image_gemini(image_path) for _ in range(votes)]
    # majority
    for label in LABELS:
        if results.count(label) >= (votes // 2) + 1:
            return label
    # tie-break
    return max(set(results), key=results.count)


# -----------------------------
# PUBLIC: classify text using Gemini if possible, else fallback
# -----------------------------
def classify_emotion_from_text_gemini(text: str) -> str:
    if not genai:
        return _text_fallback(text)

    model = _choose_model()
    if not model:
        return _text_fallback(text)

    prompt = f"Classify the emotion of this text as one word (happy, sad, angry, neutral, excited, stressed). Text: {text}"
    try:
        resp = model.generate_content(prompt)
        out = (resp.text or "").strip().lower()
        for lab in LABELS:
            if lab == out or lab in out:
                return lab
    except Exception as e:
        print("Gemini text call failed:", e)

    return _text_fallback(text)
