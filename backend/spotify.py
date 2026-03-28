"""
spotify.py - Spotify playback control via Spotipy
OWNER: Software person
"""
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG ──────────────────────────────────────────────────────────────────
# Add your playlist URIs in .env or directly here for hackathon speed
PLAYLISTS = {
    "focused":    os.getenv("PLAYLIST_FOCUSED",    "spotify:playlist:37i9dQZF1DX0XUsuxWHRQd"),
    "calm":       os.getenv("PLAYLIST_CALM",       "spotify:playlist:37i9dQZF1DWZqd5JICZI0u"),
    "meditative": os.getenv("PLAYLIST_MEDITATIVE", "spotify:playlist:37i9dQZF1DX3Ogo9pFvBkY"),
    "neutral":    os.getenv("PLAYLIST_FOCUSED",    "spotify:playlist:37i9dQZF1DX0XUsuxWHRQd"),
}
# ────────────────────────────────────────────────────────────────────────────

sp = None
current_playlist = None


def connect():
    """Authenticate with Spotify — opens browser first time."""
    global sp
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8080"),
        scope="user-modify-playback-state user-read-playback-state"
    ))
    user = sp.current_user()
    print(f"[Spotify] Connected as: {user['display_name']}")


def switch_music(state: str):
    """Switch to the playlist for the given state (only if state changed)."""
    global current_playlist
    uri = PLAYLISTS.get(state)
    if not uri or uri == current_playlist:
        return

    try:
        devices = sp.devices()
        if not devices["devices"]:
            print("[Spotify] No active device found — open Spotify on any device.")
            return
        device_id = devices["devices"][0]["id"]
        sp.start_playback(device_id=device_id, context_uri=uri)
        current_playlist = uri
        print(f"[Spotify] Switched to {state} playlist")
    except Exception as e:
        print(f"[Spotify] Playback error: {e}")


def get_now_playing() -> dict:
    """Return currently playing track info for the dashboard."""
    try:
        track = sp.current_playback()
        if track and track.get("item"):
            item = track["item"]
            return {
                "track":  item["name"],
                "artist": item["artists"][0]["name"],
                "album":  item["album"]["name"],
            }
    except Exception:
        pass
    return {"track": "—", "artist": "—", "album": "—"}
