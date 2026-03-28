"""
eeg.py - BrainFlow connection and band power extraction
OWNER: Hardware person
"""
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations

# ── CONFIG ──────────────────────────────────────────────────────────────────
BOARD_ID = BoardIds.CYTON_BOARD   # swap to GANGLION_BOARD if using Ganglion
SERIAL_PORT = "COM3"              # Windows: check Device Manager for correct port
WINDOW_SECONDS = 4                # seconds of EEG data per analysis window
# ────────────────────────────────────────────────────────────────────────────

board = None
sampling_rate = None
eeg_channels = None


def connect():
    """Initialise and start streaming from the OpenBCI board."""
    global board, sampling_rate, eeg_channels
    BoardShim.enable_dev_board_logger()
    params = BrainFlowInputParams()
    params.serial_port = SERIAL_PORT
    board = BoardShim(BOARD_ID, params)
    board.prepare_session()
    board.start_stream()
    sampling_rate = BoardShim.get_sampling_rate(BOARD_ID)
    eeg_channels = BoardShim.get_eeg_channels(BOARD_ID)
    print(f"[EEG] Connected — {sampling_rate} Hz, channels: {eeg_channels}")


def get_band_powers():
    """
    Grab a window of raw EEG, apply filters, return band powers.
    Returns dict: {delta, theta, alpha, beta, gamma}
    Returns None if board not connected (falls back to demo mode).
    """
    if board is None:
        return _demo_powers()

    n_samples = sampling_rate * WINDOW_SECONDS
    data = board.get_current_board_data(n_samples)

    for ch in eeg_channels:
        # Detrend
        DataFilter.detrend(data[ch], DetrendOperations.CONSTANT.value)
        # Remove 60 Hz power-line noise (US) — change to 50 if in Europe
        DataFilter.perform_bandstop(data[ch], sampling_rate, 58.0, 62.0, 4,
                                    FilterTypes.BUTTERWORTH.value, 0)
        # Bandpass to EEG range
        DataFilter.perform_bandpass(data[ch], sampling_rate, 1.0, 50.0, 4,
                                    FilterTypes.BUTTERWORTH.value, 0)

    bands, _ = DataFilter.get_avg_band_powers(data, eeg_channels, sampling_rate, True)
    delta, theta, alpha, beta, gamma = bands

    return {"delta": delta, "theta": theta, "alpha": alpha,
            "beta": beta, "gamma": gamma}


def _demo_powers():
    """Synthetic band powers for demo/testing without hardware."""
    import random, time
    t = time.time()
    # Slowly oscillate between calm and focused states
    alpha = 1.5 + abs(np.sin(t / 30)) * 2
    beta  = 1.0 + abs(np.cos(t / 20)) * 2
    theta = 0.8 + abs(np.sin(t / 60)) * 0.5
    return {"delta": 0.5, "theta": theta, "alpha": alpha,
            "beta": beta, "gamma": 0.3}


def disconnect():
    if board and board.is_prepared():
        board.stop_stream()
        board.release_session()
        print("[EEG] Disconnected.")
