"""Stage A: blind acoustic evidence packet.

Usage:  python3 audio_evidence.py audio.wav [label] [offset_seconds]

Produces per-bin and global prosody/voice-quality stats (JSON + table on
stdout), a pause ledger, unvoiced high-energy events, utterance-final
pitch contours (with final-slope distribution stats for
speaker-relative reading), and 2-minute mel-spectrogram panels with pitch (white)
and RMS energy (red) overlays: <label>_fig*.png.

No emotion labels are produced anywhere. Interpretation happens in the
conversation, by the model, in context.  Blindness rule: run this
BEFORE any ASR and BEFORE decoding any video frames.
"""
import sys, json, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import librosa, librosa.display
import parselmouth
from parselmouth.praat import call

SR, N_FFT, HOP, BIN_S = 22050, 1024, 256, 15.0
TOP_DB = 32  # silence floor (dB below recording peak) for the pause/
             # speech split — floor-relative, so pause counts are
             # within-recording evidence only

def mmss(t):
    return f"{int(max(t,0)//60)}:{int(max(t,0)%60):02d}"

def st_range(a):
    if len(a) < 10:
        return float("nan")
    return float(12*np.log2(np.percentile(a, 95)/np.percentile(a, 5)))

def analyze(path, label="a", offset=0.0):
    y, sr = librosa.load(path, sr=SR, mono=True)
    dur = len(y)/sr
    snd = parselmouth.Sound(y.astype(np.float64), sampling_frequency=sr)

    pitch = snd.to_pitch(time_step=0.01, pitch_floor=50, pitch_ceiling=500)
    f0 = pitch.selected_array["frequency"]; f0[f0 == 0] = np.nan
    t_f0 = pitch.xs()

    rms = librosa.feature.rms(y=y, frame_length=N_FFT, hop_length=HOP)[0]
    t_rms = librosa.times_like(rms, sr=sr, hop_length=HOP)
    rms_db = librosa.amplitude_to_db(rms, ref=np.max(rms))

    S_db = librosa.power_to_db(librosa.feature.melspectrogram(
        y=y, sr=sr, n_fft=N_FFT, hop_length=HOP, n_mels=128, fmax=8000,
        power=2.0), ref=np.max)

    # non-silence segmentation (amplitude gate, NOT voice-activity
    # detection) and pause ledger
    iv = librosa.effects.split(y, top_db=TOP_DB, frame_length=N_FFT,
                               hop_length=HOP) / sr
    pauses = [(iv[i-1][1], iv[i][0]-iv[i-1][1])
              for i in range(1, len(iv)) if iv[i][0]-iv[i-1][1] >= 0.6]
    if len(iv) and iv[0][0] >= 0.6:                      # leading silence
        pauses.insert(0, (0.0, float(iv[0][0])))
    if len(iv) and len(y)/sr - iv[-1][1] >= 0.6:         # trailing silence
        pauses.append((float(iv[-1][1]), len(y)/sr - float(iv[-1][1])))

    onsets = librosa.onset.onset_detect(y=y, sr=sr, hop_length=HOP,
                                        units="time", backtrack=False)
    speech_time = float(sum(e-s for s, e in iv)) or 1e-9

    # unvoiced high-energy events (laugh/sigh/breath candidates)
    voiced_flag = (~np.isnan(f0)).astype(float)
    voiced_on_rms = np.interp(t_rms, t_f0, voiced_flag) > 0.5
    cand = (rms_db > -22) & ~voiced_on_rms
    events, run = [], None
    for i, c in enumerate(cand):
        if c and run is None:
            run = i
        elif not c and run is not None:
            if t_rms[i-1]-t_rms[run] >= 0.25:
                events.append((t_rms[run], t_rms[i-1]-t_rms[run]))
            run = None
    if run is not None and t_rms[-1]-t_rms[run] >= 0.25:  # flush at EOF
        events.append((t_rms[run], t_rms[-1]-t_rms[run]))

    # utterance-final contours: slope of last 0.35 s of voiced pitch
    finals = {"rise": 0, "fall": 0, "level": 0}
    ledger, slopes = [], []
    for s, e in iv:
        m = (t_f0 >= e-0.35) & (t_f0 <= e) & ~np.isnan(f0)
        if m.sum() >= 5:
            st = 12*np.log2(f0[m]/f0[m][0])
            slope = float(np.polyfit(t_f0[m]-t_f0[m][0], st, 1)[0])
            kind = "rise" if slope > 8 else "fall" if slope < -8 else "level"
            finals[kind] += 1
            slopes.append(slope)
            ledger.append([mmss(offset+e), round(slope, 1), kind])

    # HNR (voice quality)
    try:
        harm = call(snd, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
        hnr = round(call(harm, "Get mean", 0, 0), 1)
    except Exception:
        hnr = None

    v = f0[~np.isnan(f0)]
    glob = {
        "label": label, "duration_s": round(dur, 1),
        "voiced_fraction": round(float(np.mean(~np.isnan(f0))), 3),
        "pitch_hz": {"median": round(float(np.median(v)), 1),
                     "iqr": [round(float(np.percentile(v, 25)), 1),
                             round(float(np.percentile(v, 75)), 1)],
                     "range_semitones": round(st_range(v), 1)},
        "pitch_hist_50_500": np.histogram(v, bins=30, range=(50, 500))[0].tolist(),
        "hnr_db_mean": hnr,
        "articulation_onsets_per_nonsilent_s": round(len(onsets)/speech_time, 2),
        "overall_onsets_per_s": round(len(onsets)/dur, 2),
        "n_pauses>=0.6s": len(pauses),
        "long_pauses>=1.2s": [[mmss(offset+t), round(g, 2)]
                              for t, g in pauses if g >= 1.2],
        "unvoiced_high_energy_events": [[mmss(offset+t), round(d, 2)]
                                        for t, d in events][:40],
        "utterance_final_contours": finals,
        "final_slope_stats_st_per_s": ({
            "median": round(float(np.median(slopes)), 1),
            "iqr": [round(float(np.percentile(slopes, 25)), 1),
                    round(float(np.percentile(slopes, 75)), 1)],
            "p10_p90": [round(float(np.percentile(slopes, 10)), 1),
                        round(float(np.percentile(slopes, 90)), 1)],
        } if slopes else None),
        "final_contour_ledger": ledger[:80],
    }
    print(json.dumps(glob, indent=1))

    # per-bin table
    print("t | voi nsl | f0med iqr stR | rmsMed rmsMax | ons/s | cpps | jit% shim%")
    for b in range(int(np.ceil(dur/BIN_S))):
        a0, a1 = b*BIN_S, min((b+1)*BIN_S, dur)
        fv = f0[(t_f0 >= a0) & (t_f0 < a1)]; fvv = fv[~np.isnan(fv)]
        rb = rms_db[(t_rms >= a0) & (t_rms < a1)]
        sp = sum(max(0, min(e, a1)-max(s, a0)) for s, e in iv)/(a1-a0)
        jit = shim = cpps = float("nan")
        try:
            sb = snd.extract_part(from_time=a0, to_time=a1)
        except Exception:
            sb = None
        if sb is not None:
            try:
                pp = call(sb, "To PointProcess (periodic, cc)", 50, 500)
                jit = call(pp, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
                shim = call([sb, pp], "Get shimmer (local)",
                            0, 0, 0.0001, 0.02, 1.3, 1.6)
            except Exception:
                pass
            try:
                pcg = call(sb, "To PowerCepstrogram", 60, 0.002, 5000, 50)
                cpps = call(pcg, "Get CPPS", False, 0.02, 0.0005, 60, 330,
                            0.05, "Parabolic", 0.001, 0.05, "Straight",
                            "Robust")
            except Exception:
                pass
        row = [f"{mmss(offset+a0)}-{mmss(offset+a1)}",
               round(float(np.mean(~np.isnan(fv))), 2) if len(fv) else 0,
               round(sp, 2),
               round(float(np.median(fvv)), 0) if len(fvv) > 5 else None,
               round(float(np.percentile(fvv, 75)-np.percentile(fvv, 25)), 0)
               if len(fvv) > 5 else None,
               round(st_range(fvv), 1) if len(fvv) > 10 else None,
               round(float(np.median(rb)), 1) if len(rb) else None,
               round(float(np.max(rb)), 1) if len(rb) else None,
               round(len(onsets[(onsets >= a0) & (onsets < a1)])/(a1-a0), 1),
               round(float(cpps), 1) if cpps == cpps else None,
               round(jit*100, 2) if jit == jit else None,
               round(shim*100, 2) if shim == shim else None]
        print(" | ".join(str(x) for x in row))

    # 2-minute panels, 2 rows of 60 s, pitch + energy overlays
    for fi in range(int(np.ceil(dur/120))):
        fig, axes = plt.subplots(2, 1, figsize=(16, 8))
        for ri in range(2):
            a0, a1 = fi*120 + ri*60, min(fi*120 + (ri+1)*60, dur)
            ax = axes[ri]
            if a0 >= dur:
                ax.axis("off"); continue
            i0, i1 = int(a0*sr/HOP), int(a1*sr/HOP)
            librosa.display.specshow(
                S_db[:, i0:i1], x_axis="time", y_axis="mel", sr=sr,
                hop_length=HOP, fmax=8000, cmap="turbo", ax=ax,
                x_coords=np.linspace(offset+a0, offset+a1, i1-i0))
            m = (t_f0 >= a0) & (t_f0 < a1)
            ax.plot(offset+t_f0[m], f0[m], color="black", lw=3.0)
            ax.plot(offset+t_f0[m], f0[m], color="white", lw=1.5)
            ax2 = ax.twinx()
            mr = (t_rms >= a0) & (t_rms < a1)
            ax2.plot(offset+t_rms[mr], rms_db[mr], color="red", ls="--",
                     lw=1.0, alpha=0.85)
            ax2.set_ylim(-60, 2)
            ax.set_title(f"{label}  {mmss(offset+a0)}-{mmss(offset+a1)}"
                         "  (white=pitch, red=energy)")
        plt.tight_layout()
        fig.savefig(f"{label}_fig{fi}.png", dpi=110)
        plt.close(fig)

if __name__ == "__main__":
    analyze(sys.argv[1],
            sys.argv[2] if len(sys.argv) > 2 else "a",
            float(sys.argv[3]) if len(sys.argv) > 3 else 0.0)
