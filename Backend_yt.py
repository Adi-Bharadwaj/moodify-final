import webbrowser

# ------------------------------------------------------
# 1. ADD YOUR PLAYLIST LINKS HERE
# ------------------------------------------------------
PLAYLISTS = {
    "happy": "https://www.youtube.com/playlist?list=PLKanlGu-b2elpnrOq_5vcZk1OEzBoNt5P",
    "sad": "https://youtube.com/playlist?list=PLGLYO4XhlCiSraorysBMxdmDGg8GbGYDx&si=bF_wElvlXCvF91ri",
    "angry": "https://www.youtube.com/playlist?list=PLxA687tYuMWhPJjhH2r0MAEpd_F4vl5GT",
    "neutral": "https://www.youtube.com/playlist?list=PLA43DqAcT2MFUi_j6ECVC4wcJIyc63FYH",
}

# ------------------------------------------------------
# 2. ASK USER FOR MOOD
# ------------------------------------------------------
print("How are you feeling today?")
print("Options: happy / sad / angry / neutral")

mood = input("Enter your mood: ").strip().lower()

# ------------------------------------------------------
# 3. OPEN PLAYLIST BASED ON MOOD
# ------------------------------------------------------
if mood in PLAYLISTS:
    print(f"🎵 Opening your {mood} playlist...")
    webbrowser.open(PLAYLISTS[mood])
else:
    print("❌ Invalid mood! Please enter: happy, sad, angry, or neutral.")
  
