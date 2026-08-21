# Changelog

- **v1.2** — Lexical-blind probe extension (three-level scoring:
  acoustic structure → phoneme family → lexeme; declared genre priors;
  stable target IDs via `scripts/lexical_targets.py`). CPPS added to
  the per-bin table as the primary connected-speech voice-quality
  measure; jitter/shimmer demoted to supporting. Amplitude gate
  relabeled non-silent (it is not VAD). Question-contour test scoped
  to tag/polar questions. "One-take certification" replaced with cut
  screening. Blind statement made procedural ("ran no ASR, accessed
  no transcript, made no deliberate use of lexical content"). Visual
  rules rephrased as evidence-weights with named alternatives. Pitch
  histogram demoted from speaker counter to speaker screen.
- **v1.1.1** — Bug fixes, empirically verified: pitch overlay plotted
  in Hz (was mel-valued, rendering at the floor); leading/trailing
  silences added to the pause ledger; end-of-file flush for unvoiced
  events; outlined pitch trace for legibility; dynamic frame-label
  boxes for videos past 10 minutes.
- **v1.1** — Stage 0 priors declaration added to the iron rule; burst
  triage by expected disagreement; ASR hallucination and
  punctuation-as-annotation cautions in Stage B; speaker-relative
  final-slope stats; living miss scorecard and cross-architecture
  replication extensions.
- **v1** — Initial method: blind acoustics → transcript verification →
  visuals → junction synthesis, under a sequential-unmasking iron
  rule; evidence packets, not classifiers.
