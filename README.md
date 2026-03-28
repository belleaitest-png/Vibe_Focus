# 🎵 Vibe Focus — EEG-Adaptive Music

> OpenBCI brainwave data → real-time mental state detection → Spotify playlist switching

Built at Resolution Hackathon 2025.

---

## How It Works

```
OpenBCI Hardware → BrainFlow (Python) → Band Power Extraction
    → State Classifier (alpha/beta ratio)
    → Spotify API (playlist switch)
    → Flask + WebSocket → Live Dashboard
```

**States detected:** 🎯 Focused · 🌊 Calm · 🧘 Meditative · ⚡ Neutral

---

## Quick Start

### 1. Clone & install
```bash
git clone https://github.com/belleaitest-png/Vibe_Focus.git
cd Vibe_Focus/backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Set up credentials
```bash
cp .env.example .env
# Edit .env with your Spotify credentials + playlist URIs
```
Get Spotify credentials at: https://developer.spotify.com/dashboard

### 3. Run
```bash
# With OpenBCI hardware:
python main.py

# Demo mode (no hardware needed):
python main.py --demo
```

### 4. Open dashboard
Open `frontend/index.html` in your browser.

---

## File Ownership
| File | Owner | Purpose |
|------|-------|---------|
| `backend/eeg.py` | Hardware person | BrainFlow + band power |
| `backend/classifier.py` | Anyone | State classification logic |
| `backend/spotify.py` | Software person | Spotify API control |
| `backend/server.py` | Software person | Flask + WebSocket API |
| `backend/main.py` | Belle | Entry point, wires everything |
| `frontend/index.html` | Anyone | Live dashboard UI |

---

## Tuning
Edit thresholds in `classifier.py` to calibrate for the specific user.
Run a 2-min baseline calibration session before demo for best results.
