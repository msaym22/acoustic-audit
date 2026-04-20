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
