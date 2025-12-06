# server.py
import os
import uuid
from flask import Flask, request, jsonify

# Imports from updated camera_mood_gemini.py (using v1 Gemini models)
from camera_mood_gemini import stable_mood_gemini, classify_emotion_from_text_gemini
from music_player import play_music

app = Flask(__name__, static_folder="web_ui", static_url_path="")

# Serve UI
@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    return app.send_static_file(filename)

# ---------------------
# IMAGE → EMOTION
# ---------------------
@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    try:
        print("Entering /analyze-image")

        if "image" not in request.files:
            return jsonify({"error": "no_image"}), 400

        image_file = request.files["image"]

        # temp folder
        os.makedirs("temp_images", exist_ok=True)
        filename = f"img_{uuid.uuid4().hex}.png"
        image_path = os.path.join("temp_images", filename)
        image_file.save(image_path)

        print("Saved image:", image_path)

        # Emotion detection (Gemini v1 models handled inside stable_mood_gemini)
        mood = stable_mood_gemini(image_path)
        print("Detected image mood:", mood)

        # Music selection
        playlist_msg = play_music(mood)
        print("after playmusic",playlist_msg)

        return jsonify({"mood": mood, "playlist": playlist_msg})

    except Exception as e:
        print("ERROR /analyze-image:", str(e))
        return jsonify({"error": "server_error", "details": str(e)}), 500


# ---------------------
# TEXT → EMOTION
# ---------------------
@app.route("/analyze-text", methods=["POST"])
def analyze_text():
    try:
        print("Entering /analyze-text")

        data = request.get_json(force=True)
        user_text = data.get("user_text", "").strip()

        if not user_text:
            return jsonify({"error": "empty_text"}), 400

        # Text emotion detection (Gemini v1 models handled inside classify_emotion_from_text_gemini)
        mood = classify_emotion_from_text_gemini(user_text)
        print("Detected text mood:", mood)

        playlist_msg = play_music(mood)

        return jsonify({"mood": mood, "playlist": playlist_msg})

    except Exception as e:
        print("ERROR /analyze-text:", str(e))
        return jsonify({"error": "server_error", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
