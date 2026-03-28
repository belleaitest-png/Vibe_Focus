import eeg
import classifier

print("Fetching live OpenBCI data...")
bands = eeg.get_band_powers()
if bands:
    print(f"Quality:          {bands['quality']}")
    print(f"Artifact flag:    {bands['artifact_flag']}")
    print(f"Peak alpha (PAF): {bands['paf_hz']} Hz")
    print(f"Alpha/theta:      {bands['alpha_theta_ratio']}")
    print(f"Gamma/delta:      {bands['gamma_delta_ratio']}")
    print(f"Alpha:            {bands['alpha']:.3f}")
    print(f"Beta:             {bands['beta']:.3f}")
    print()
    state = classifier.classify_state(bands)
    meta  = classifier.get_state_description(state)
    print(f"Detected state: {state.upper()} - {meta['description']}")
