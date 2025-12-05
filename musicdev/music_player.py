PLAYLISTS = {
    "happy": "https://www.youtube.com/watch?v=gKgCSFZALkE",
    "sad": "https://www.youtube.com/watch?v=Z3zUcAwOs1A",
    "angry": "https://www.youtube.com/watch?v=iBuTEywEQ6U",
    "neutral": "https://www.youtube.com/watch?v=RUVohRXP8v0"
}

def play_music(mood: str) -> str:
    mood = mood.lower().strip()
    if mood not in PLAYLISTS:
        mood = "neutral"
    return PLAYLISTS[mood]
