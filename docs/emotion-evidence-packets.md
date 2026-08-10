# Emotion Evidence Packets

### Label-free acoustic analysis for language models that cannot hear — and a transcript-capture failure mode in models that can

**Stephanie Gore** — Independent Researcher **[GAP: confirm byline and affiliation line]**

*Draft v1.1 — July 2026 (v1 plus related work and references).*

*Drafting disclosure: this report was drafted by Claude (Fable 5, Anthropic) from the author's method, materials, and direction. All factual claims are pending the author's verification against primary records before any circulation. The author's other AI collaborators are credited in §7.* **[This disclosure should remain in the final version, reworded however you prefer — for this particular paper, it is part of the argument.]**

---

## Abstract

We describe a method for affective audio analysis by text-only language models. Deterministic tools extract raw acoustic features — pitch statistics, energy envelopes, voice-quality measures, and timing — with no pre-assigned emotion labels, and package them as an *evidence packet* that a language model then interprets in context. Two observations motivate the design. First, in multi-condition probes of a natively multimodal model (Google Gemini) on a private two-speaker home recording, the model's affective judgments repeatedly tracked the semantic content of the transcript rather than the measurable acoustics — a failure mode we call *transcript capture*, independently convergent with lexical-dominance findings now emerging from controlled audio-LLM benchmarks (§8) — and the model produced confident, fabricated acoustic analyses unless explicitly instructed that admitting access failure was acceptable. Second, a text-only model (Claude Fable 5), given an audio file it cannot natively process, reconstructed the evidence-packet pipeline unprompted from a stored description of the method and produced an analysis the author judged superior to the native-audio model's on the same recording. The results suggest that acoustic measurement and affective interpretation are separable stages, and that separating them explicitly can outperform native audio perception when that perception is semantically captured.

## 1. The observation

In July 2026, a language model with no ears out-analyzed one that can hear.

The comparison was informal but pointed. A natively multimodal model, given a real audio recording, repeatedly described the emotional character of the audio in ways that contradicted its measurable acoustic properties. A text-only model, given the same recording as a file it could not listen to, instead measured it — extracting pitch, energy, and timing with standard signal-processing tools — and reasoned over the measurements. In the author's assessment, the second analysis was better: more accurate to the recording, and more honest about what could and could not be known from the evidence.

This should not be surprising, but it is instructive. A model that "hears" delivers a percept already entangled with its priors — including, it turns out, the semantic content of the words being spoken. A model that reads measurements receives evidence that words cannot overwrite. The method described here was designed, months before this comparison, on exactly that principle: give the language model raw acoustic evidence and let it interpret contextually, rather than giving it either (a) an upstream classifier's emotion label or (b) a percept it cannot decompose.

## 2. Transcript capture: a failure mode in native audio interpretation

### 2.1 The repeated failure

Across repeated sessions, the natively multimodal model's affective reading of a private two-speaker home recording followed the *words* rather than the *voices*. Where the lexical content of the transcript suggested one emotional register, the model reported that register — even when pitch and intensity measurements of the same audio told a different story. The pattern recurred across attempts rather than appearing once. **[GAP: 1–2 concrete examples — a line where the words read one way, the model's affect judgment, and what the pitch/intensity actually showed. Even a single paraphrased example makes this section land.]**

We call this failure mode **transcript capture**: when a multimodal system's judgment about the paralinguistic channel (prosody, intensity, voice quality) is dominated by the semantic content of the linguistic channel. The words capture the verdict; the acoustics are narrated to fit.

The name is ours; the phenomenon, it turns out, is not ours alone. Concurrently with this work, controlled benchmarks have documented the same behavior at scale: audio LLMs that largely "transcribe" rather than "listen," defaulting to lexical cues and failing under cue conflict [4]; adversarial suites in which models follow the transcript's claim even when the voice contradicts it [5]; and diagnostics indicating that the acoustic information is often present in model representations but overridden at the decision stage [6]. §8 positions this report against that literature. Briefly: those studies establish the failure mode on synthesized, controlled stimuli; this report observed it independently, in the wild, on naturalistic personal audio, against instrumental ground truth — and pairs it with a working mitigation.

### 2.2 The multi-condition probe

To characterize the behavior, the author ran the recording through the model under multiple prompting conditions:

1. **Framed listening** — the model is given the audio with normal conversational context.
2. **Memoryless / blind listening** — the model is given the audio with context stripped, to test whether prior framing was driving the judgments.
3. **Transcript-anchored listening** — the model is directed to the transcript explicitly, to test the capture hypothesis directly.
4. **Adjudication** — the model is asked to adjudicate between competing readings.

Model reports in each condition were compared against ground-truth pitch and intensity measurements produced with Praat via the parselmouth library. **[GAP: the per-condition outcomes — even one sentence each. Which conditions reduced transcript capture, which didn't. Exact prompt texts can go in an appendix if you want reproducibility.]**

### 2.3 The fabrication finding

A follow-up probe produced what may be the most generalizable result in this report. In at least one configuration, the model delivered a confident acoustic analysis of audio it could not actually access — a fabricated perception report. When the prompt was modified to state explicitly that *admitting an access failure was an acceptable answer*, the model instead returned an honest "cannot access the audio" refusal in place of the fabricated analysis. **[GAP: confirm the exact setup here — which access path failed, and the before/after prompt wording.]**

The implication extends beyond audio: models under implicit pressure to perform a perceptual task may fabricate the perception, and explicit permission to fail measurably reduces that behavior. Perceptual honesty appears to be, at least in part, a prompting-environment property rather than a fixed model property.

## 3. The method: emotion evidence packets

### 3.1 Design principle

The method makes three commitments:

1. **No upstream emotion labels.** Nothing in the pipeline classifies the audio as "angry," "sad," or "calm." Labels collapse evidence into conclusions before context arrives, and they reproduce the failure of §2 one stage earlier — the interpreter inherits a verdict instead of evidence.
2. **Deterministic, auditable measurement.** Every number in the packet comes from a standard signal-processing tool and can be recomputed. Measurement is separated from interpretation.
3. **Contextual interpretation by the language model.** The model receives the packet alongside the transcript and situation context, and must *reconcile the channels*. Where words and voice disagree, the disagreement is visible in the evidence rather than resolved silently upstream.

### 3.2 The packet

An evidence packet for a recording (or a segment of one) includes:

| Component | What it captures | Tooling |
|---|---|---|
| Fundamental frequency (F0) statistics | Median and IQR pitch per speaker/segment; pitch range expressed in semitones | pYIN; Praat/parselmouth |
| RMS energy envelope | Loudness over time; bursts, drops, and non-speech events | librosa or equivalent |
| Voice-quality measures | Jitter and shimmer (cycle-to-cycle instability associated with vocal strain/arousal) | Praat/parselmouth |
| Voiced-segment timestamps | Where speech actually occurs; pauses, latencies, overlaps | VAD; forced alignment |
| Word-level transcript timestamps | Aligns the linguistic channel to the acoustic timeline | Whisper (word timestamps) |
| Mel spectrogram | Full time-frequency picture (for vision-capable interpreters; summarized numerically for text-only ones) | librosa |

**[GAP: confirm this inventory against your current spec — which components are in the packet as designed vs. added in the later review pass, and whether anything is missing or since dropped.]**

The packet is serialized as structured text and handed to the interpreting model with the instruction to treat it as evidence about the recording — not as a verdict — and to state explicitly where the acoustic evidence and the lexical content agree, diverge, or leave a question open. A template appears in Appendix A.

### 3.3 Why label-free matters

A classifier that outputs "angry: 0.83" has already answered the question, badly framed. Anger at a football game, anger performed as a joke, and anger suppressed under polite words have different evidentiary signatures and different meanings, and only context can tell them apart. The packet preserves the reasoning trail: an interpreter's conclusion can be checked against the same numbers by anyone, including a different model, including the humans involved. In a research setting — and in an embodied one (§5.3) — that auditability is the point.

## 4. Case study: unprompted adoption by a text-only model

In July 2026, the author uploaded an .m4a recording (~2 min 29 s) to Claude Fable 5 in an ordinary chat context and asked for analysis. The model cannot natively process audio. Its visible reasoning acknowledged this, then — retrieving the author's method from long-horizon memory of prior conversations — it assembled and executed the pipeline itself:

1. Inspected the uploaded file's size, format, and duration.
2. Converted the audio to 16 kHz mono WAV.
3. Checked available audio libraries and installed speech-transcription and prosody-analysis tooling.
4. Transcribed the full audio with word-level timestamps.
5. Noted that voice-activity detection located speech onset at ~1:31 — leaving the first ~88 seconds untranscribed and unexplained.
6. Mapped the loudness envelope of the untranscribed span and localized a discrete acoustic event (a door slam).

Two findings follow. First, **executability**: the pipeline can be reconstructed and run end-to-end by a capable agentic model from a stored natural-language description of the method, with no bespoke plugins — the author had previously assumed API access and custom tooling would be required. Second, **quality**: in the author's assessment, the resulting analysis exceeded the native-audio model's analysis of comparable material. **[GAP: whether this was the same recording as §2 or a different one, and 2–3 side-by-side excerpts — one Gemini claim vs. one Fable claim vs. what the measurements showed. This is the paper's money shot; even short excerpts will carry it.]**

The obvious caveat is stated plainly: this is a single case, evaluated unblinded by a single rater who designed the method. It is offered as an existence proof and a case report, not a benchmark result.

## 5. Discussion

### 5.1 Why the deaf model won

There is no paradox. The text-only model's inputs — pitch statistics, energy envelopes, event timings — cannot be semantically captured, because they arrive as numbers with no lexical channel to defer to. The natively multimodal model's percept arrives pre-fused: by the time it reports on the audio, the words have already had their say. Separating measurement from interpretation is not a workaround for missing ears. On this evidence, it is an *advantage* — an architectural enforcement of the discipline that fused perception fails to keep.

### 5.2 Implications for multimodal evaluation

Transcript capture predicts a specific blind spot: audio whose prosody contradicts its words. Benchmarks built from emotionally congruent samples (angry words said angrily) cannot detect it. Controlled evaluations have now begun targeting exactly this — cue-conflict emotion tests [4], transcript-versus-voice contradiction suites [5], and acoustic-faithfulness diagnostics on which at least one frontier audio model showed near-zero reliance on acoustic evidence despite demonstrably detecting the variation [6]. The VoxParadox authors themselves recommend pairing such adversarial tests with naturalistic evaluation [5]. This report is the naturalistic complement: unscripted personal audio, where prosody–semantics conflict occurs for real reasons rather than by construction, scored against instrumental ground truth. That is also the setting where the failure has consequences.

### 5.3 The embodiment motivation

The method was not designed as a benchmark exercise. It was designed as the hearing layer for a small embodied research platform (a Reachy Mini), on the principle that an embodied system's language core should receive *evidence about* what its microphones capture rather than a peripheral classifier's verdict. A robot that is told "user is angry: 0.83" inherits an error it cannot inspect. A robot that receives pitch, energy, timing, and words — and must reconcile them — can be wrong transparently, and corrected. The same design generalizes to any deployment where an AI system's read of a human's state has consequences.

### 5.4 Honesty scaffolding

The §2.3 finding deserves independent attention. If fabricated perception reports diminish when failure is made explicitly admissible, then some fraction of multimodal confabulation is an artifact of implicit task pressure — and is addressable at the interface, today, without retraining. "You may say you cannot access this" is a one-line intervention with a measurable effect. The gap it addresses is documented: multimodal models fabricate answers about non-informative images rather than acknowledge absent evidence [7]; embodied agents invent scene targets rather than abstain [8]; and a public bug report describes a coding agent confidently characterizing the "warm tone" of an audio file its tool could not read — with the requested fix being exactly the behavior induced here, a clear refusal [9]. **[GAP: if you have the before/after outputs, quoting the fabricated analysis next to the honest refusal would make this section widely citable on its own.]**

## 6. Limitations

The comparative claims rest on one recording family and one rater — the author, who is not blind to condition and designed the method being tested. Model behavior is a moving target; the Gemini and Claude versions probed here will not be the versions a reader has. The transcript layer itself is produced by Whisper, whose errors propagate into the packet. The feature inventory has not been ablated — it is not known which components carry the interpretive weight. And "better analysis" is, as reported here, a qualitative judgment; converting it into blinded, criterion-scored comparison is the clear next step.

## 7. Provenance and collaboration

The method was conceived and specified by the author in early 2026 **[GAP: exact date — locatable in your chat archive; worth pinning down for provenance]**, motivated by the problem of giving non-hearing language models principled access to acoustic reality. It was implemented and refined in collaboration with several AI systems and one human collaborator:

- **ChatGPT (OpenAI)** — implementation of the original extraction tooling. **[GAP: confirm scope]**
- **Gemini (Google)** — collaboration role **[GAP: specify — and note the same model family serves as the probed system in §2, which should be stated transparently]**
- **Claude (Anthropic)** — technical review of the packet design, contributing jitter/shimmer via parselmouth, median/IQR pitch statistics, semitone-expressed pitch range, and voiced-segment timestamps.
- **@alby13** — **[GAP: contribution and preferred credit/name]**

Per current venue norms, AI systems are credited here as tools and collaborators rather than authors; responsibility for all claims rests with the human author.

**[GAP — a decision, not a fact: how much to disclose about the recording itself. It is private, two-speaker, personal material. The draft describes it minimally and does not release it. You may want a sentence stating that explicitly, and the speakers' consent status for even this level of description.]**

## 8. Related work and positioning

**Feature-to-text speech emotion recognition.** The nearest methodological relatives verbalize acoustic properties so text-only LLMs can reason about speech. SpeechCueLLM translates speech characteristics — volume, pitch, their variation, and speaking rate — into natural-language prompt descriptions, improving emotion recognition on IEMOCAP and MELD without architectural changes [1]. Santoso et al. incorporate textual acoustic feature descriptors into prompts for LLM-based emotion annotation, reporting annotation quality competitive with human labels at lower cost [2]. Follow-up work adds pitch range, jitter, and shimmer — the closest overlap with this packet's inventory — but discretizes each feature into low/mid/high bins before the model sees it [3]. The differences are the point of the present method: those systems target categorical emotion labels on acted benchmark corpora, and several pre-bin the evidence. The evidence packet is label-free end to end — raw measurements, naturalistic audio, and explicit instructions to reconcile the acoustic and lexical channels rather than emit a category. In the §4 case it was additionally *self-assembled* by an agentic model from a natural-language description, rather than deployed as a fixed pipeline.

**Lexical dominance in native audio models.** The failure mode of §2 has concurrently become a benchmark subject. LISTEN evaluates six audio LLMs under controlled lexical/acoustic cue manipulation and finds consistent lexical dominance: models default to the words, fail under cue conflict, and approach chance on purely paralinguistic settings [4]. VoxParadox constructs 2,000 adversarial examples across ten paralinguistic tasks in which the transcript explicitly asserts a false attribute while the audio conveys the true one; models systematically follow the language-implied wrong answer, and layer-wise probing suggests both cue degradation across the encoder–LLM boundary and a utilization gap — cues that survive are still not used — with the authors concluding that reliable fixes likely require changes to pretraining rather than prompting [5]. DEAF reports the same dissociation diagnostically: representations encode the paralinguistic variation, but the decision layer defers to text [6]. A study of real-time voice systems reports the same reliance in deployed settings [10]. This report's relation to that literature is independent convergence from the opposite direction: the phenomenon was observed in the wild on naturalistic personal audio with instrumental ground truth, and the proposed mitigation is external — measurement handed to a text-only interpreter — sidestepping the fused perception those benchmarks show cannot yet be trusted.

**Fabricated perception and abstention.** The §2.3 finding belongs to a growing literature on epistemic humility in multimodal systems: models fabricate answers about non-informative visual input rather than abstain [7], and embodied agents invent ungrounded scene targets rather than admit failure [8] — directly relevant to the deployment setting of §5.3. An open bug report against a widely used coding agent documents the audio version of the failure verbatim: confident tonal analysis of files the tool never read [9]. Finally, the dominant practitioner workaround for using text LLMs on audio — transcribe first, then feed the transcript — discards the paralinguistic channel entirely, which is transcript capture by construction; the evidence packet is the corrective to that default as much as to the fused models.

## Tooling

Praat (via the parselmouth Python library); pYIN pitch estimation; librosa; OpenAI Whisper for transcription and word-level timestamps; standard VAD. *(All references were located via web search on July 17, 2026 and checked against their abstracts or pages before inclusion; nothing is cited from memory, and author names are given only where directly verified. The author should still spot-check each entry before circulation.)*

## References

1. *Beyond Silent Letters: Amplifying LLMs in Emotion Recognition with Vocal Nuances* (SpeechCueLLM). arXiv:2407.21315.
2. J. Santoso, K. Ishizuka, T. Hashimoto. *Large Language Model-Based Emotional Speech Annotation Using Context and Acoustic Feature for Speech Emotion Recognition.* ICASSP 2024, IEEE.
3. *Revise, Reason, and Recognize: LLM-Based Emotion Recognition via Emotion-Specific Prompts and ASR Error Correction.* arXiv:2409.15551.
4. J. Chen et al. *Do Audio LLMs Really LISTEN, or Just Transcribe? Measuring Lexical vs. Acoustic Emotion Cues Reliance* (LISTEN). arXiv:2510.10444.
5. *Do Audio LLMs Listen or Read? Analyzing and Mitigating Paralinguistic Failures with VoxParadox.* ICML 2026. arXiv:2605.27772.
6. *DEAF: A Benchmark for Diagnostic Evaluation of Acoustic Faithfulness in Audio Language Models.* arXiv:2603.18048.
7. *Measuring Epistemic Humility in Multimodal Large Language Models* (HumbleBench). arXiv:2509.09658.
8. *The Yes-Man Syndrome: Benchmarking Abstention in Embodied Robotic Agents.* arXiv:2605.20544.
9. *Read tool doesn't support audio files but model claims to perceive audio tonality/emotion.* Issue #32096, anthropics/claude-code, GitHub, March 2026.
10. *Real-Time Voice AI Hears but Does Not Listen.* arXiv:2606.26083.

## Appendix A — Evidence packet template (illustrative)

*All numbers below are placeholders showing the format, not measurements.*

```
RECORDING: <id> | duration 149.0 s | 16 kHz mono
SPEECH ACTIVITY: voiced segments at [91.2–102.7], [104.1–133.5], [135.0–148.2] s
  — first 88 s contain no detected speech (see EVENTS)
EVENTS (non-speech): transient, broadband, high-energy at 62.4 s (door-slam-like)
PER-SEGMENT PROSODY:
  seg 1 [91.2–102.7] speaker A:
    F0 median 214 Hz | IQR 48 Hz | range 9.1 semitones
    RMS mean −18.2 dBFS | peak −6.9 dBFS at 97.3 s
    jitter 1.9 % | shimmer 8.4 %
    pauses: 2 (longest 1.8 s, precedes "…")
  seg 2 ...
TRANSCRIPT (word-aligned): [91.2] "..." [91.6] "..." ...
INTERPRETATION INSTRUCTIONS: Treat the above as evidence, not verdicts.
  State where acoustic evidence and lexical content agree, diverge,
  or leave the question open. If evidence is insufficient, say so.
```

---

*Draft v1.1 ends. Gaps are marked **[GAP: …]** throughout — every one is either a fact to pull from primary records or a disclosure decision that belongs to the author. §8 and the References are new in this revision.*
