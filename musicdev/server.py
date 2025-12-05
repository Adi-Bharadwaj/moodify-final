# server.py
import os
from flask import Flask, request, jsonify
from camera_mood_gemini import stable_mood_gemini, classify_emotion_from_text_gemini
from music_player import play_music
import uuid

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
        if "image" not in request.files:
            return jsonify({"error": "no_image"}), 400

        image_file = request.files["image"]
        os.makedirs("temp_images", exist_ok=True)
        filename = f"img_{uuid.uuid4().hex}.png"
        image_path = os.path.join("temp_images", filename)
        image_file.save(image_path)

        mood = stable_mood_gemini(image_path)
        playlist_msg = play_music(mood)

        return jsonify({"mood": mood, "playlist": playlist_msg})
    except Exception as e:
        # Always return JSON on error so frontend won't crash parsing HTML.
        print("ERROR /analyze-image:", e)
        return jsonify({"error": "server_error", "details": str(e)}), 500


# ---------------------
# TEXT → EMOTION
# ---------------------
@app.route("/analyze-text", methods=["POST"])
def analyze_text():
    try:
        data = request.get_json(force=True)
        user_text = data.get("user_text", "").strip()
        if not user_text:
            return jsonify({"error": "empty_text"}), 400

        mood = classify_emotion_from_text_gemini(user_text)
        playlist_msg = play_music(mood)
        return jsonify({"mood": mood, "playlist": playlist_msg})
    except Exception as e:
        print("ERROR /analyze-text:", e)
        return jsonify({"error": "server_error", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
