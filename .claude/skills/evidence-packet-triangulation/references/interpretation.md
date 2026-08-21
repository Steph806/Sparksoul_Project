# Interpretation Reference

Read this before writing any Stage A read or Stage D synthesis.

## Acoustic ambiguity classes

The arousal contour (how activated) is reliable. Valence (what kind of
feeling) is not — every acoustic profile is shared by several distinct
states. Always name the class, then hypothesize within it.

| Profile | Shared by |
|---|---|
| loud + high + fast | anger, indignation, urgency, excitement, performed outrage, quoted/voice-acted characters |
| soft + low + slow | grief, fatigue, resignation, solemnity, hushed emphasis ("lean in, this matters"), savoring relish, intimacy |
| halting, long pauses | distress, word-searching, cognitive load, staged patience/condescension, dramatic pacing, pauses for on-screen content the audio cannot see |
| pitch spikes/wide arcs | emphasis, animation, mock-melodic teacherese, distress wobble (needs visual layer to separate) |
| unvoiced broadband bursts | sigh, exhale, sniff, laugh, plosive/handling noise (check spectrogram shape and context) |

Absences are evidence too: nine minutes with zero laughter argues
against a genuinely light register no matter what the speaker claims.

Quotation warning: a speaker performing someone else's words imports
that person's prosody wholesale. The loudest passage of a recording
may belong to a quoted character, not the speaker. Flag any passage
that could be read-aloud, quoted, or voice-acted material.

## Voice-quality numbers (with caveats)

Jitter/shimmer/HNR norms come from sustained vowels in clinical
settings; conversational speech reads "worse" on all of them, and
phone-mic recordings worse still. Use them **comparatively within the
recording**, not against clinical thresholds: a stretch where shimmer
runs 2–3 points above the recording's own baseline is a real
instability signal (strain, emotional load, or pressed/rough
phonation); an absolute value alone is not. Prefer CPPS (smoothed
cepstral peak prominence, in the packet's per-bin table) as the primary
voice-quality measure for connected speech — far more robust than
perturbation measures outside sustained vowels; lower CPPS reads
breathier/rougher, and like everything here it is read comparatively
against the recording's own baseline, with jitter/shimmer demoted to
supporting evidence. HNR falls with
breathiness and roughness. Creak/vocal fry shows up as pitch-histogram
mass at 50–80 Hz plus pulsed striation on the spectrogram; it is a
register choice in many speakers, not distress.

Pause detection is floor-relative: the ledger's silence threshold
sits a fixed depth below the recording's own peak, so pause counts
and boundaries move with background level and mic distance. Pause
structure is within-recording evidence; never compare raw pause
counts across recordings without loudness-normalizing first.

Utterance-final contours: scope the test to tag and polar questions
("okay?", "right?", yes/no forms) — wh-questions end in falls natively
in most English varieties, so a falling "who did this?" is
unremarkable, while statement-like falls on tag/polar questions are
evidence of rhetorical (pre-answered) address; genuine
information-seeking tag/polar questions carry rises far more often. Count, don't cherry-pick. The ±8 st/s rise/fall
thresholds are perceptually anchored but not speaker-calibrated:
wide-arc animated speakers inflate raw rise counts. Read contour
counts — especially the question-final subset — against the
recording's own final-slope distribution (reported in the packet as
final_slope_stats_st_per_s), not against absolute totals.

## Visual signal inventory

What earns weight, and what each observation does and does not
license:

- **Smile distribution vs. content.** Chart what gets smiled at. Smiles
  concentrated on aggressive/gotcha content raise the plausibility that
  the aggression is enjoyed — live alternatives include social masking,
  nervousness, politeness-to-camera, performance, and irony, so require
  ≥2 co-occurring signals before "enjoyed" becomes the working
  hypothesis, and treat it as inference about display, never certainty
  about inner state. Smiles also do not establish the "just joking" frame — that frame
  needs shared-play cues (self-deprecation, laughter offered to the
  audience, ironic markers).
- **Silence behavior.** Distress silences avert and close; staged
  silences display: held direct stares, slow luxurious blinks,
  eye-rolls, posing, grooming. These are typical patterns, not laws — a
  practiced performer can display through genuine distress and a shy
  speaker can avert during comfortable staging; treat the pattern as
  strong but defeasible evidence.
- **Gaze choreography.** Down-to-read vs. up-to-deliver; gaze snapping
  to the lens precisely on key lines is evidence the speaker knows where
  the punchlines are (rehearsal/intent); reading placement, habit, and
  off-screen prompts are the live alternatives.
- **Adaptors and preening.** Hair sweeps, grooming, and posing at
  charged moments read as performed unbotheredness/self-display.
  Distinguish from stress adaptors (face-touching with gaze aversion,
  self-clasping), which co-occur with closed postures.
- **Post-line leakage.** Expressions blooming just after a provocative
  line (smirk, suppressed grin, "tee-hee" scrunch) while the line
  itself was delivered flat: the flatness was the delivery device;
  the leakage is the affect.
- **Proximity and posture.** Lean-ins toward the lens on attack lines
  are aggression displays; chin-up, down-the-nose angles are dominance
  framing; recline/languid postures perform ease.
- **Anger/disgust configurations.** Brow-lowering, lid-tightening,
  nose-wrinkle, teeth bared beyond articulation. These weigh
  toward genuine heat far more than voice volume does — though a capable
  performer can produce them deliberately, so they license "heat
  displayed and owned," not "felt beyond doubt."

**Articulation-discount rule:** single frames freeze speech into
pseudo-expressions. An open mouth or visible teeth alone is a
consonant until brows, nose, or eye aperture co-move — articulation
does not wrinkle the nose or lower the brows.

**Micro-expression honesty:** at a few fps on compressed video,
sub-200 ms micro-expressions are not reliably observable, and
micro-expression-based deception detection is contested science even
under lab conditions. Report display behavior and timing; never
"detect lies."

## The junction: timing relations and ownership

- **ON**: expression lands on the line → the content is owned/enjoyed
  as spoken.
- **BEFORE**: anticipatory display (lip-bite, forming grin, deliberate
  slowdown) → rehearsed reveal; the speaker is landing a planned
  moment.
- **AFTER**: leakage following a flat delivery → the underplaying was
  itself the performance.

**Ownership heuristic:** when modalities disagree about intensity, the
face usually marks ownership — a heuristic, strongest during read-aloud
quotation, capped at medium confidence (deliberate underacting and
camera awareness are live alternatives). Quoted/performed material: hot voice, cool face.
The speaker's own affect: it reaches the face (heat, delight,
disgust) even when the voice is moderate. Assign every strong emotion
to an owner before characterizing "the speaker's state."

**Congruence record per key segment:** words / voice / face → agree or
diverge, with the timing relation. The divergences are the findings.
A recording where all three agree throughout is also a finding —
report it plainly rather than hunting for subtext.

## Confidence language

- High: arousal contour, pause structure, detected cuts (absence of
  detected cuts is only "consistent with a single take"), laughter
  presence/absence, gaze/smile timing visible on frames, and speaker
  count when histogram shape, register alternation, and pause-reply
  evidence converge.
- Medium: valence hypotheses after triangulation; "performed,"
  "staged," "relished" when supported by ≥2 independent signals.
- Low/never: sincerity of inner belief, deception, diagnosis,
  identity. Say what the evidence shows and where it stops.

Standard phrasings: "the acoustic architecture of X"; "consistent with
X or Y — the visual layer will separate them"; "this is an inference
from displays, not mind-reading"; "high confidence on the contour,
medium on the label."
