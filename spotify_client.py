import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
    )
)

def get_track_data(track_id):
    track = sp.track(track_id)
    features = sp.audio_features([track_id])[0]

    return {
        "track_id": track_id,
        "title": track["name"],
        "artist": track["artists"][0]["name"],
        "album": track["album"]["name"],
        "release_year": track["album"]["release_date"][:4],
        "popularity": track["popularity"],
        "features": features
    }

def interpret_features(f):
    mood = []
    tempo_desc = ""
    harmony_desc = ""

    if f["tempo"] < 90:
        tempo_desc = "slow and relaxed"
    elif f["tempo"] < 120:
        tempo_desc = "moderate and steady"
    else:
        tempo_desc = "fast and energetic"

    if f["valence"] < 0.4:
        mood.append("emotionally dark")
    elif f["valence"] > 0.6:
        mood.append("uplifting and positive")

    if f["energy"] > 0.7:
        mood.append("high-energy")
    else:
        mood.append("soft and calm")

    if f["mode"] == 0:
        harmony_desc = "uses a minor key, giving it a melancholic tone"
    else:
        harmony_desc = "uses a major key, giving it a bright feel"

    return {
        "tempo_description": tempo_desc,
        "mood": ", ".join(mood),
        "harmony_description": harmony_desc
    }
