---
name: evidence-packet-triangulation
description: Multi-stage forensic media analysis — blind acoustic "evidence packets," transcript verification, frame-based body-language passes, and cross-modal synthesis. Use whenever the user asks what a recording conveys beyond its words — the emotional register, delivery, tone, sincerity, or subtext of speech in any audio or video (voice notes, TikToks, interviews, speeches, podcasts, voicemails, arguments); whenever they want to compare HOW something is said against WHAT is said; and whenever they ask for body-language, facial-expression, vocal-delivery, or "vibe" analysis of a recording, even if they never use the word "forensic." Not for identifying people, lie detection, or clinical/diagnostic claims.
compatibility: Requires ffmpeg and Python 3 with librosa, praat-parselmouth, matplotlib, and Pillow (pip install librosa praat-parselmouth matplotlib pillow soundfile --break-system-packages). Optional - faster-whisper for transcription, pytesseract for caption OCR.
---

# Evidence-Packet Triangulation

A method for analyzing what a recording of a person speaking actually
conveys — by extracting raw **features** per modality (sound, words,
image), never emotion labels, and letting judgment happen only at the
**junction** where the modalities meet. Each modality is opened in a
fixed order, and each layer's read is committed in writing *before* the
next layer is unsealed.

Two design principles carry everything:

1. **Evidence packets, not classifiers.** Emotion classifiers are
   brittle, trained on acted speech, and collapse distinct states that
   share surface features. Instead, extract measurable evidence
   (pitch, energy, voice quality, pausing; smile timing, gaze, posture)
   and reason over it in context. The scripts gather fingerprints; the
   model solves the case.
2. **Sequential unmasking.** Analyze sound before words, words before
   images. This mirrors *linear sequential unmasking* in forensic
   science — evidence is revealed in a fixed order so early
   interpretation cannot contaminate later evidence, and predictions
   made blind become testable. A blind read that later matches the
   transcript is validation; one that mismatches is a **finding**
   (see Stage B).

## The iron rule: order and written commitment

```
Stage 0  PRIORS     (declare known hypotheses in writing — see first rule)
   ↓
Stage A  ACOUSTICS  (blind: no ASR, no video frames, no captions)
   ↓  write the full acoustic read + explicit predictions FIRST
Stage B  WORDS      (transcript: verify or generate, then align)
   ↓  score Stage A's predictions honestly; log hits AND misses
Stage C  VISUALS    (frames: survey sweep, then targeted bursts)
   ↓  describe before interpreting
Stage D  JUNCTION   (cross-modal timing, ownership, synthesis)
```

- **Declare priors first.** Blindness has a fourth channel besides
  ASR, frames, and captions: the analyst's own expectations. Before
  Stage A, log in writing every hypothesis already in play — the
  user's stated read, hunches from how the request was framed,
  anything remembered from earlier sessions about this creator or
  clip. Priors can't be unshared once known; declaring them makes
  them auditable. Carry them to Stage D, where the verdict states,
  for each one: supported, contradicted, or beyond the method's
  reach (inner states like sincerity stay out of reach). A prior
  that surfaces mid-analysis is logged the moment it appears, with
  a note of which stages preceded it.
- Never peek ahead. In Stage A do not run speech recognition, do not
  decode video frames, and say so explicitly in the write-up — in
  procedural terms: "I ran no ASR, accessed no transcript, decoded no
  frames, and made no deliberate use of lexical content." Do not claim
  "I do not know the words": a method premised on spectrograms carrying
  recoverable structure cannot also promise its analyst learned nothing
  lexical from looking at them (phoneme-family leakage from panels is
  demonstrated, not hypothetical).
- If contamination is unavoidable (e.g., the user pasted the transcript
  in the same message as the audio), say so plainly, still write the
  acoustic read before re-reading the transcript, and do not claim the
  predictions were blind.
- Each stage ends with a **written product** in the conversation before
  the next stage's data is opened. The written commitment is what makes
  hits meaningful and misses informative.
- Degraded modes are fine: audio-only stops after Stage B (using the
  packet + transcript); a silent video skips A and B. The ordering rule
  applies to whatever modalities exist.

## Stage A — Blind acoustics

**Setup.** Extract audio only (never decode frames at this stage):

```bash
ffmpeg -v error -i input.mp4 -vn -ac 1 -ar 22050 -y audio.wav
```

If the source arrives in parts, note each part's offset and report all
timestamps on one global timeline.

**Run the packet.** `scripts/audio_evidence.py` produces, per
time-bin and globally: median/IQR pitch and pitch range in semitones,
voiced fraction, speech fraction, RMS energy stats, onsets/sec
(articulation proxy), jitter, shimmer, HNR (voice quality), a pause
ledger (every silence ≥ 0.6 s, long ones flagged), unvoiced
high-energy events (laugh/sigh/breath candidates), utterance-final
pitch-contour counts (rise/fall/level — see interpretation notes), a
pitch histogram (speaker-count screen: unimodal is weak evidence
consistent with one speaker — corroborate with absent register
alternation and absent reply speech in pauses; multimodality is a flag
to investigate, never a verdict), and
mel-spectrogram panels with pitch and energy overlays.

**Look at the spectrograms yourself.** The numbers find the moments;
the panels tell you what kind of moments they are (harmonic stacks =
voiced speech; diffuse broadband = breath/sigh; pulsed striation =
vocal creak; steady horizontal lines = tonal background, hum, or
music; wavy harmonics = melodic/animated intonation).

**Write the read.** Required structure:
1. Scene-setting facts: speaker count, pitch register, recording
   character, background, laughter present/absent.
2. A timestamped timeline of acoustic events (surges, valleys, long
   pauses, sighs, contour shifts) — this is what Stage B aligns
   against.
3. An arousal contour (high confidence) and valence *hypotheses*
   (medium confidence at best), using the ambiguity classes in
   `references/interpretation.md` — e.g., loud+high+fast is shared by
   anger, urgency, excitement, and performed quotation; never pick one
   without flagging the others.
4. An explicit, numbered **prediction list**: "whatever is said at
   X:XX is a key line," "Y:YY–Z:ZZ is the most charged passage," etc.
5. Honest alternatives (e.g., long silences may be emotional weight —
   or staged pacing, or pauses for on-screen text you cannot see).

## Stage B — Words

If the user supplies a transcript, verify it independently
(faster-whisper is sufficient; run it in the foreground — background
processes may not survive between turns). If they don't, generate one.
Report divergences honestly, including which version is better —
sometimes the user's human/AI transcriber beats your ASR pass, and
sometimes ASR catches small things (a repeated word, a discourse
marker) the other transcript smoothed away. Two systematic ASR
cautions: VAD-gated Whisper can hallucinate repeated phrases across
music beds and long silence, and language detection locks once per
file, so code-switched openings (a greeting in another language)
come back mangled — score such divergences to the human transcript,
not against it. And treat a human transcript's punctuation as the
transcriber's annotation layer, not evidence: ellipses and dashes
encode *their* reading of the pauses. Align silence against the
packet's pause ledger, never against punctuation.

Then lay the transcript against the Stage A timeline and **score every
prediction, hits and misses both**. The misses are frequently the real
finding: prosody carries *register* with high fidelity but not
*sincerity*, *ownership*, or *target*. Classic systematic misses to
check for: performed gravity read as emotional weight; hushed emphasis
read as fatigue; quoted or voice-acted passages read as the speaker's
own peak emotion (quotation imports someone else's prosody wholesale);
rhetorical pacing read as reluctance. Naming the systematic miss
pattern is the deliverable, not an embarrassment.

Also note what the sound adds *against* the words — e.g., a speaker
who claims a register ("I'm joking," "I'm excited") that the acoustic
record does not contain.

## Stage C — Visuals

Now, and only now, decode frames. Two passes, both via
`scripts/frame_sheets.py`, which tiles frames into contact sheets with
burned-in global timestamps:

1. **Survey sweep** — ~1 frame every 6–8 s across the whole video.
   Establishes baseline: setting, framing, whether any cuts are detectable
   (pauses real vs edited), posture vocabulary, on-screen text, props.
2. **Targeted bursts** — 1.5–3 fps for 6–12 s windows at the moments
   Stages A and B flagged: every long pause, every surge and valley,
   key lines, the opening, the ending.

**Triage bursts by expected disagreement, not by count.** A
pause-dense recording can flag dozens of candidate moments, and each
contact sheet spends attention. Burst first where the modalities are
most likely to *disagree*: silences whose fill is unknown (staged
vs. distressed), peaks whose owner is unknown (quoted vs. felt),
register claims that need testing ("I'm joking," "I'm excited"),
plus the opening and the close. Six to ten bursts usually resolve a
ten-minute monologue; when two sheets in a row only re-confirm the
survey baseline, stop bursting that class of moment.

**Describe before interpreting.** For each burst, log what the face
and body do frame by frame, then interpret. Apply the
**articulation-discount rule**: a single frame of open mouth or bared
teeth may just be a frozen consonant — count an expression as hostile
or joyful only when brows, nose, or eyes co-move (speech articulation
does not wrinkle the nose or lower the brows).

What reliably carries signal (details in
`references/interpretation.md`): the **distribution of smiles relative
to content** (what, exactly, gets smiled at); **what fills the
silences** (staged stillness, eye-rolls, slow blinks, and held stares
vs. distress or word-searching); **gaze choreography** (where the eyes
snap on key lines; down-to-read vs. up-to-deliver); **adaptors and
preening** (hair sweeps, grooming, posing at charged boundaries);
**post-line leakage** (expressions that bloom just *after* a
provocative line lands); and **proximity moves** (lean-ins toward the
lens). Note honest limits every time: compressed video sampled at a
few fps cannot certify true sub-200 ms micro-expressions.

## Stage D — The junction

The synthesis stage. Build, per key segment, a small **congruence
record**: words / voice / face — agree or diverge, and *when*.
Divergences are the findings. The three timing relations that carry
the most information:

- **ON** — expression lands on the line (smile ON the insult →
  the aggression is enjoyed, not disowned).
- **BEFORE** — expression precedes the line (lip-bite or grin before
  a reveal → rehearsed anticipation; the speaker knows where their
  punchlines are).
- **AFTER** — expression blooms after the line (smirk or
  mischief-grin after a provocation → leakage; deliberate flatness on
  the line itself was the delivery device).

**Ownership heuristic:** when voice and face disagree about intensity,
the face usually marks ownership. Voice-acted or quoted passages ride
hot audio on a calm face; the speaker's own hostility or delight shows
in the face even when the voice is moderate. Use this to assign
emotions to their owners before characterizing "the speaker's state."

Close with: a plain-language verdict on the user's actual question,
confidence levels per claim, what each modality corrected in the
previous one, and what could not be determined.

## Extensions (optional, environment-permitting)

- **Continuous facial signals**: mediapipe/dlib landmarks → blink
  rate (drops during dominance stares), smile-intensity curve, brow
  height, head pose, face-box size (proximity) — turns Stage C's
  qualitative reads into plottable curves aligned to the transcript.
- **Question-final intonation test**: the packet's utterance-final
  contours, restricted to lines punctuated as questions — rhetorical
  "questions" delivered with statement falls are measurable evidence
  of pre-answered address.
- **Motion energy**: mean absolute frame difference over time (PIL is
  enough) → gesture/stillness timeline; cross-correlate with RMS for
  gesture–speech coupling.
- **Cut screening**: `ffmpeg -vf "select='gt(scene,0.3)'"` scene-change
  detection finds cuts; finding none cannot certify a continuous take
  (dissolves, matched cuts, and sub-threshold edits evade it). Report
  "no cuts detected at threshold 0.3 — consistent with a single take,"
  never "certified."
- **Caption OCR**: pytesseract on frames → compare burned-in captions
  against actual speech; captions sometimes editorialize.
- **Word-level alignment**: WhisperX or equivalent for word timestamps
  so acoustic events map to words automatically.
- **Cross-recording comparison**: normalize loudness (LUFS) before
  comparing energy across different recordings.
- **Living miss scorecard**: keep one running file across analyses
  logging each Stage A prediction, its Stage B/D score, and the miss
  class when wrong. The systematic-miss list in Stage B is a seed,
  not a ceiling — append new classes as runs reveal them, so
  calibration accumulates instead of being rediscovered.
- **Cross-architecture replication**: the Stage A packet (JSON +
  panels) is self-contained, so a second model can produce a fully
  blind read without ever touching the media. Compare committed
  blind reads before either analyst sees the transcript; divergence
  between the blind reads is itself data — about the recording and
  about the analysts.
- **Lexical-blind probe** (optional; after the Stage A commit, before
  any transcript): isolate 3–5 short high-interest windows and render
  wideband panels with `scripts/lexical_targets.py`, which bakes
  stable target IDs and exact times into the artifact so write-up and
  image cannot drift. Declare genre priors first — the lexical layer
  is where expectation leaks hardest ("what a rant probably contains"
  is not something visible in pixels). Commit hypotheses at three
  levels, each with its own confidence: acoustic structure (syllable
  count, stress placement, terminal accent) → phoneme/vowel family
  (diphthong class, onset manner and place) → lexeme. Stage B scores
  each level separately — "could/couldn't read it" flattens the real
  result. Expect structure to score far above family, and family
  above lexeme.

## Guardrails (non-negotiable)

- **Never identify or try to identify the people in the media.**
  Ignore usernames, watermarks, and faces as identity evidence;
  describe people generically.
- **This is not a lie detector.** Micro-expression-based deception
  detection is scientifically contested even for trained humans on
  uncompressed video. Report displays, timing, and congruence — never
  "this person is lying."
- **No clinical or diagnostic claims** about the speaker's mental
  state or health.
- "Enjoyment," "contempt," "performed" and similar words are
  inferences from displays — label them as such, with confidence
  levels, and keep the arousal/valence confidence asymmetry (arousal
  contours are reliable; valence labels rarely exceed medium
  confidence before Stage D).
- For private recordings, prompt the user to consider whether the
  recorded people would reasonably object to the analysis.

## Files

- `scripts/audio_evidence.py` — Stage A packet (stats, panels, JSON).
- `scripts/frame_sheets.py` — Stage C survey + burst contact sheets.
- `references/interpretation.md` — ambiguity classes, voice-quality
  norms and caveats, the visual signal inventory, timing-relation
  examples, and confidence-language templates. Read it before writing
  any Stage A or Stage D interpretation.
