"""
eeg.py - Live OpenBCI data via HTTP API
OWNER: Hardware person
Replaces BrainFlow serial connection with HTTP polling of the live worker.
API docs: https://openbci-status-worker.simfish-openbci-live.workers.dev/
"""
import urllib.request
import json
import time

# ── CONFIG ──────────────────────────────────────────────────────────────────
API_BASE = "https://openbci-status-worker.simfish-openbci-live.workers.dev"
LIVE_URL  = f"{API_BASE}/live.json"
TIMEOUT_S = 5
# ────────────────────────────────────────────────────────────────────────────

_last_data   = None
_last_fetch  = 0
_demo_mode   = False
_connected   = False


def connect():
    """Test connection to the live API."""
    global _connected
    try:
        data = _fetch_live()
        if data:
            quality  = data["metrics"].get("quality", "unknown")
            channels = data["metrics"].get("active_channels", [])
            paf      = data["metrics"].get("paf_hz", 0)
            print(f"[EEG] Connected to live API")
            print(f"[EEG] Signal quality: {quality} | Channels: {channels} | Peak alpha: {paf:.2f} Hz")
            _connected = True
    except Exception as e:
        print(f"[EEG] API connection failed: {e}")
        raise


def get_band_powers():
    """
    Fetch latest metrics from live API and return band powers dict.
    Falls back to demo data if API is unreachable.

    Returns dict with keys:
        delta, theta, alpha, beta, gamma     (derived from spectrum)
        alpha_theta_ratio                    (direct from API)
        gamma_delta_ratio                    (direct from API)
        paf_hz                               (peak alpha frequency)
        artifact_flag                        (bool)
        quality                              (str: excellent/good/poor)
    """
    if _demo_mode:
        return _demo_powers()

    try:
        data = _fetch_live()
        return _parse_metrics(data)
    except Exception as e:
        print(f"[EEG] Fetch error: {e} - using demo data")
        return _demo_powers()


def _fetch_live():
    """HTTP GET /live.json with caching (don't hammer the API)."""
    global _last_data, _last_fetch
    now = time.time()
    if now - _last_fetch < 2.0 and _last_data:  # cache for 2s
        return _last_data
    req = urllib.request.Request(LIVE_URL, headers={
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
        _last_data  = json.loads(r.read().decode())
        _last_fetch = now
    return _last_data


def _parse_metrics(data):
    """Extract the fields our classifier needs from the API response."""
    m = data.get("metrics", {})

    # The API gives alpha_theta_ratio and gamma_delta_ratio directly
    alpha_theta = m.get("alpha_theta_ratio", 0.5)
    gamma_delta = m.get("gamma_delta_ratio", 0.01)
    paf_hz      = m.get("paf_hz", 10.0)
    delta_power = m.get("delta_power", 100.0)
    gamma_power = m.get("gamma_power", 5.0)
    artifact    = m.get("artifact_flag", False)
    quality     = m.get("quality", "unknown")

    # Derive individual band values the classifier also uses
    # alpha = alpha_theta_ratio * theta; we estimate from ratio + delta
    theta = delta_power * 0.05          # rough estimate
    alpha = theta * alpha_theta
    beta  = gamma_power * 3.0           # rough estimate
    gamma = gamma_power

    return {
        "delta":             delta_power,
        "theta":             round(theta, 3),
        "alpha":             round(alpha, 3),
        "beta":              round(beta,  3),
        "gamma":             round(gamma, 3),
        "alpha_theta_ratio": round(alpha_theta, 4),
        "gamma_delta_ratio": round(gamma_delta, 6),
        "paf_hz":            round(paf_hz, 2),
        "artifact_flag":     artifact,
        "quality":           quality,
    }


def _demo_powers():
    """Synthetic metrics that cycle through all 3 states for demo."""
    t = time.time()
    import math
    phase = (t % 90) / 90        # 0→1 over 90 seconds
    alpha_theta = 0.15 + abs(math.sin(phase * math.pi)) * 0.6
    gamma_delta = 0.005 + abs(math.cos(phase * math.pi)) * 0.02
    paf_hz      = 8.5  + abs(math.sin(phase * math.pi * 2)) * 3
    delta       = 400.0
    theta       = delta * 0.05
    alpha       = theta * alpha_theta
    beta        = 5.0 + abs(math.cos(phase * math.pi)) * 10
    return {
        "delta": delta, "theta": round(theta, 3),
        "alpha": round(alpha, 3), "beta": round(beta, 3),
        "gamma": 6.0,
        "alpha_theta_ratio": round(alpha_theta, 4),
        "gamma_delta_ratio": round(gamma_delta, 6),
        "paf_hz":            round(paf_hz, 2),
        "artifact_flag":     False,
        "quality":           "demo",
    }


def set_demo_mode(enabled=True):
    global _demo_mode
    _demo_mode = enabled
    print(f"[EEG] Demo mode: {enabled}")


def disconnect():
    global _connected
    _connected = False
    print("[EEG] Disconnected.")
