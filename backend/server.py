"""
server.py - Flask REST + WebSocket server
OWNER: Software person
Exposes /state and /bands endpoints + pushes live updates via SocketIO
"""
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import threading, time

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Shared state — written by main.py loop, read by API endpoints
shared_state = {
    "state":  "neutral",
    "bands":  {"delta": 0, "theta": 0, "alpha": 0, "beta": 0, "gamma": 0},
    "track":  {"track": "—", "artist": "—", "album": "—"},
    "history": [],          # last 60 state snapshots for sparkline
}


# ── REST endpoints ────────────────────────────────────────────────────────────

@app.route("/state")
def get_state():
    return jsonify({
        "state":  shared_state["state"],
        "bands":  shared_state["bands"],
        "track":  shared_state["track"],
    })


@app.route("/history")
def get_history():
    return jsonify(shared_state["history"][-60:])


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ── WebSocket broadcast ───────────────────────────────────────────────────────

def broadcast_state():
    """Called from main loop whenever state updates."""
    socketio.emit("state_update", {
        "state": shared_state["state"],
        "bands": shared_state["bands"],
        "track": shared_state["track"],
    })


def update_shared_state(state, bands, track):
    shared_state["state"] = state
    shared_state["bands"] = bands
    shared_state["track"] = track
    shared_state["history"].append({"state": state, "bands": bands,
                                    "time": time.time()})
    broadcast_state()


def run_server():
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    run_server()
