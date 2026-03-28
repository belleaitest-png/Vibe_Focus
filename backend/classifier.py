"""
classifier.py - Brainwave state classifier
OWNER: Belle / anyone
Rule-based v1 — replace body of classify_state() with ML model later.
"""

# Thresholds — tune these during calibration with the actual user
ALPHA_BETA_FOCUS_RATIO = 0.8    # below this → likely focused (beta dominant)
ALPHA_BETA_CALM_RATIO  = 1.2    # above this → likely calm  (alpha dominant)
THETA_MEDITATIVE_MIN   = 1.4    # theta spike → meditative / drowsy


def classify_state(bands: dict) -> str:
    """
    Classify mental state from band power dict.

    Args:
        bands: {"delta": float, "theta": float, "alpha": float,
                "beta": float, "gamma": float}

    Returns:
        One of: "focused" | "calm" | "meditative" | "neutral"
    """
    if bands is None:
        return "neutral"

    alpha = bands.get("alpha", 1.0)
    beta  = bands.get("beta",  1.0)
    theta = bands.get("theta", 1.0)

    ratio = alpha / (beta + 1e-6)   # avoid division by zero

    if theta > THETA_MEDITATIVE_MIN and ratio > ALPHA_BETA_CALM_RATIO:
        return "meditative"
    elif ratio >= ALPHA_BETA_CALM_RATIO:
        return "calm"
    elif ratio <= ALPHA_BETA_FOCUS_RATIO:
        return "focused"
    else:
        return "neutral"


def get_state_description(state: str) -> dict:
    """Return UI metadata for each state."""
    meta = {
        "focused":    {"emoji": "🎯", "color": "#4A90D9", "bpm_target": "80-100",
                       "description": "High beta — sharp focus mode"},
        "calm":       {"emoji": "🌊", "color": "#50C878", "bpm_target": "60-75",
                       "description": "Alpha dominant — relaxed awareness"},
        "meditative": {"emoji": "🧘", "color": "#9B59B6", "bpm_target": "40-60",
                       "description": "Theta rising — deep calm"},
        "neutral":    {"emoji": "⚡", "color": "#F39C12", "bpm_target": "70-85",
                       "description": "Balanced state"},
    }
    return meta.get(state, meta["neutral"])
