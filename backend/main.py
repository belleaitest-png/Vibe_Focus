"""
main.py - Entry point. Wires EEG -> Classifier -> Spotify + Server
OWNER: Belle
Run: python main.py
     python main.py --demo     (no hardware, simulated EEG)
"""
import sys, time, threading, argparse

import eeg
import classifier
import spotify
import server

POLL_INTERVAL = 10   # seconds between EEG reads


def main(demo_mode=False):
    print("=" * 50)
    print("  VIBE FOCUS - EEG Adaptive Music")
    print("=" * 50)

    # 1. Start Flask server in background thread
    t = threading.Thread(target=server.run_server, daemon=True)
    t.start()
    print("[Main] Dashboard server running at http://127.0.0.1:5000")

    # 2. Connect to Spotify
    spotify.connect()

    # 3. Connect to EEG (or run in demo mode)
    if demo_mode:
        print("[Main] Running in DEMO MODE - no hardware needed")
    else:
        try:
            eeg.connect()
        except Exception as e:
            print(f"[Main] EEG connection failed: {e}")
            print("[Main] Falling back to DEMO MODE")

    # 4. Main loop
    current_state = None
    print(f"\n[Main] Starting loop (every {POLL_INTERVAL}s) - Ctrl+C to stop\n")

    try:
        while True:
            bands = eeg.get_band_powers()
            state = classifier.classify_state(bands)
            meta  = classifier.get_state_description(state)
            track = spotify.get_now_playing()

            # Update server state (broadcasts via WebSocket)
            server.update_shared_state(state, bands, track)

            # Only switch music on state change
            if state != current_state:
                print(f"  State -> {state.upper():12s} | {meta['description']}")
                spotify.switch_music(state)
                current_state = state
            else:
                print(f"  Holding {state:12s} | a={bands['alpha']:.2f}  b={bands['beta']:.2f}  t={bands['theta']:.2f}")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\n[Main] Shutting down...")
        eeg.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Run without hardware")
    args = parser.parse_args()
    main(demo_mode=args.demo)
