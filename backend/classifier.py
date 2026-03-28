"""
classifier.py - Mental state classifier using live OpenBCI API metrics
OWNER: Anyone
Uses pre-computed API ratios (much more reliable than raw band power).
"""

# ── THRESHOLDS ───────────────────────────────────────────────────────────────
# Tune these after watching a few minutes of the person's live data
PAF_FOCUSED_MIN      = 10.0   # Hz - peak alpha freq above this = alert/focused
ALPHA_THETA_CALM_MIN = 0.25   # above this = calm (alpha dominant over theta)
ALPHA_THETA_MED_MIN  = 0.40   # above this = meditative
GAMMA_DELTA_FOCUS    = 0.012  # above this = high cognitive engagement
# ─────────────────────────────────────────────────────────────────────────────


def classify_state(bands: dict) -> str:
    """
    Classify mental state from API metrics dict.

    Priority order: artifact check -> meditative -> focused -> calm -> neutral
    """
    if not bands:
        return "neutral"

    # If hardware artifact detected, hold current state
    if bands.get("artifact_flag", False):
        print("[Classifier] Artifact detected - skipping this window")
        return "neutral"

    quality = bands.get("quality", "unknown")
    if quality == "poor":
        print("[Classifier] Poor signal quality - skipping")
        return "neutral"

    alpha_theta = bands.get("alpha_theta_ratio", 0.0)
    gamma_delta = bands.get("gamma_delta_ratio", 0.0)
    paf_hz      = bands.get("paf_hz",            10.0)

    # Meditative: high alpha/theta ratio + low peak alpha freq (slow brain)
    if alpha_theta >= ALPHA_THETA_MED_MIN and paf_hz < 9.5:
        return "meditative"

    # Focused: fast peak alpha + high gamma/delta engagement
    if paf_hz >= PAF_FOCUSED_MIN and gamma_delta >= GAMMA_DELTA_FOCUS:
        return "focused"

    # Calm: good alpha/theta ratio without the focus markers
    if alpha_theta >= ALPHA_THETA_CALM_MIN:
        return "calm"

    return "neutral"


def get_state_description(state: str) -> dict:
    """Return display metadata for each state."""
    meta = {
        "focused": {
            "emoji": "TARGET", "color": "#4A90D9",
            "description": "High PAF + gamma/delta - sharp focus mode"
        },
        "calm": {
            "emoji": "WAVE", "color": "#50C878",
            "description": "Alpha dominant - relaxed awareness"
        },
        "meditative": {
            "emoji": "ZEN", "color": "#9B59B6",
            "description": "Theta rising + slow alpha - deep calm"
        },
        "neutral": {
            "emoji": "BOLT", "color": "#F39C12",
            "description": "Balanced / transitioning"
        },
    }
    return meta.get(state, meta["neutral"])
