import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# IMPORT your teammates' functions
# If emotion_detector.py and music_player.py are in same folder, import them.
# emotion_detector must expose `stable_mood(image_path)` and `classify_emotion_from_image`.
# music_player must expose `play_playlist_for_mood(mood)`.
try:
    from emotion_detector import stable_mood
except Exception:
    # fallback: try classify_emotion_from_image if stable_mood not present
    try:
        from emotion_detector import classify_emotion_from_image as _single
        def stable_mood(p): return _single(p)
    except Exception:
        stable_mood = None

try:
    from music_player import play_playlist_for_mood
except Exception:
    play_playlist_for_mood = None

# UI config
APP_TITLE = "Mood Music — Demo"
WINDOW_SIZE = "520x420"
DEFAULT_IMAGE = "captured_face.jpg"  # file person1 creates

root = tk.Tk()
root.title(APP_TITLE)
root.geometry(WINDOW_SIZE)
root.resizable(False, False)

# Widgets
frame_top = tk.Frame(root)
frame_top.pack(pady=10)

img_label = tk.Label(frame_top, text="No image loaded", width=48, height=14, bd=2, relief="sunken")
img_label.pack()

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

status_var = tk.StringVar(value="Status: idle")
status_label = tk.Label(root, textvariable=status_var)
status_label.pack(pady=(0,10))


def show_image(path):
    """Load image and show in img_label (resized to fit)."""
    if not os.path.exists(path):
        img_label.config(text="Image not found")
        return
    try:
        img = Image.open(path)
        img.thumbnail((400, 300))
        tkimg = ImageTk.PhotoImage(img)
        img_label.configure(image=tkimg, text="")
        img_label.image = tkimg
    except Exception as e:
        img_label.config(text=f"Error opening image: {e}")


def choose_file():
    p = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
    )
    if p:
        root.selected_image = p
        show_image(p)
        status_var.set(f"Selected: {os.path.basename(p)}")


def capture_image():
    """
    Call person1's capture script. Two options:
    1) If person1's face_capture.py opens a camera window, run it as a separate process.
    2) If capture is manual, show instructions.
    We'll attempt to call python3 face_capture.py in a thread so UI remains responsive.
    """
    if not os.path.exists("face_capture.py"):
        messagebox.showinfo("Capture", "face_capture.py not found. Ask person1 to run it or drop captured_face.jpg in folder.")
        return

    def run_capture():
        status_var.set("Status: launching capture (press 'c' to capture, 'q' to quit)...")
        # run as subprocess so user can interact with camera window
        import subprocess, sys
        try:
            subprocess.run([sys.executable, "face_capture.py"])
            status_var.set("Status: capture finished. Look for captured_face.jpg")
            if os.path.exists(DEFAULT_IMAGE):
                root.selected_image = DEFAULT_IMAGE
                show_image(DEFAULT_IMAGE)
        except Exception as e:
            status_var.set("Status: capture failed")
            messagebox.showerror("Capture error", str(e))
    threading.Thread(target=run_capture, daemon=True).start()


def detect_and_play():
    """Run emotion detection (calls person2) and play playlist (person3)."""
    img_path = getattr(root, "selected_image", DEFAULT_IMAGE)
    if not os.path.exists(img_path):
        messagebox.showerror("Missing image", f"No image found at {img_path}. Capture or select an image first.")
        return
    if stable_mood is None:
        messagebox.showerror("Missing module", "emotion_detector.stable_mood not available. Check person2's file.")
        return

    def work():
        try:
            status_var.set("Status: detecting mood...")
            # call stable_mood (this may call Gemini, so it's blocking; we run on worker thread)
            mood = stable_mood(img_path)
            status_var.set(f"Status: detected: {mood}")
            messagebox.showinfo("Mood detected", f"Mood: {mood}")
            # play music if function exists
            if play_playlist_for_mood:
                status_var.set("Status: opening playlist...")
                play_playlist_for_mood(mood)
                status_var.set("Status: opened playlist")
            else:
                status_var.set("Status: no music_player found")
        except Exception as e:
            status_var.set("Status: error during detection")
            messagebox.showerror("Detection error", str(e))

    threading.Thread(target=work, daemon=True).start()


# Buttons
btn_frame = tk.Frame(frame_buttons)
btn_frame.pack()

btn_choose = tk.Button(btn_frame, text="Choose Image", width=14, command=choose_file)
btn_capture = tk.Button(btn_frame, text="Capture Image (person1)", width=18, command=capture_image)
btn_detect = tk.Button(btn_frame, text="Detect Mood & Play", width=18, command=detect_and_play)
btn_refresh = tk.Button(btn_frame, text="Refresh Preview", width=14, command=lambda: show_image(getattr(root,"selected_image", DEFAULT_IMAGE)))

btn_choose.grid(row=0, column=0, padx=6, pady=6)
btn_capture.grid(row=0, column=1, padx=6, pady=6)
btn_detect.grid(row=0, column=2, padx=6, pady=6)
btn_refresh.grid(row=1, column=1, padx=6, pady=6)

# Try to load default image at start
if os.path.exists(DEFAULT_IMAGE):
    root.selected_image = DEFAULT_IMAGE
    show_image(DEFAULT_IMAGE)

root.mainloop()
