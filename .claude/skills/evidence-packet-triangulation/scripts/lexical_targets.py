"""Lexical-blind probe helper (optional extension; see SKILL.md).

Renders high-resolution wideband spectrogram panels for a few short
targets so an analyst can attempt structure -> phoneme-family -> lexeme
hypotheses BEFORE any transcript. Stays inside the Stage A blind: no
ASR, no transcript, no frames. Panel titles bake in stable IDs (T1..Tn),
exact times, and the blindness tag, so write-up and artifact cannot
drift apart.

Wideband settings (short analysis window, tiny hop) trade harmonic
resolution for time resolution: formant trajectories, stop gaps,
frication, and syllable boundaries become visible.

Usage:
    python lexical_targets.py audio.wav <label> start1 end1 [start2 end2 ...]
Times in seconds. Output: <label>_lexical_targets.png
"""
import sys
import numpy as np
import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SR = 22050


def main():
    if len(sys.argv) < 5 or (len(sys.argv) - 3) % 2:
        sys.exit(__doc__)
    path, label = sys.argv[1], sys.argv[2]
    ts = [float(x) for x in sys.argv[3:]]
    wins = list(zip(ts[::2], ts[1::2]))
    y, sr = librosa.load(path, sr=SR, mono=True)
    fig, axes = plt.subplots(len(wins), 1, figsize=(16, 4.2 * len(wins)))
    if len(wins) == 1:
        axes = [axes]
    for k, ((a, b), ax) in enumerate(zip(wins, axes), 1):
        seg = y[int(a * sr):int(b * sr)]
        # ~11.6 ms window -> wideband; hop 32 -> ~1.5 ms time grid
        D = librosa.amplitude_to_db(
            np.abs(librosa.stft(seg, n_fft=256, hop_length=32)), ref=np.max)
        ax.imshow(D, origin="lower", aspect="auto", cmap="gray_r",
                  extent=[a, b, 0, sr / 2], vmin=-60, vmax=0)
        ax.set_ylim(0, 6000)
        ax.set_title(f"T{k}  isolated lexical target {a:.2f}-{b:.2f}s "
                     f"— blind: no ASR / no transcript")
        ax.set_ylabel("Hz")
        ax.set_xlabel("time (s)")
    fig.tight_layout()
    out = f"{label}_lexical_targets.png"
    fig.savefig(out, dpi=110)
    print("wrote", out)


main()
