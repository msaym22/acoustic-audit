# Acoustic-Audit — Real-Time Quran Recitation Verifier

**Status: Under active development**

A real-time phonetic error detection system for Quranic recitation.
Built for Huffaz who practise alone and have no way to catch their own mistakes
mid-recitation.

## How It Works

Audio streams from the device microphone over a **full-duplex WebSocket** connection
to a Python server. The server runs the audio through **Wav2Vec 2.0** to produce a
phoneme sequence, then computes **Levenshtein Distance** against the ground-truth ayah.
If the edit distance exceeds the threshold, an error event is sent back to the client
and the UI highlights the mismatch in under 200ms.

Microphone → Int16 PCM → WebSocket → NumPy normalisation
→ Wav2Vec 2.0 → phoneme sequence → Levenshtein comparison
→ JSON error payload → Flutter UI highlight

Key design choice: processing streams in small chunks rather than waiting for sentence
completion. This gives sub-second feedback — necessary for recitation, where errors
happen at the syllable level.

## Stack

- **Client:** Flutter (Dart), WebSocketChannel
- **Server:** Python, FastAPI
- **ML:** PyTorch, Wav2Vec 2.0, NumPy
- **Algorithm:** Levenshtein Distance

## Current Progress

- WebSocket pipeline: complete
- Audio normalisation and Wav2Vec inference: complete
- Levenshtein grading logic: complete
- Noise cancellation preprocessing: in progress
