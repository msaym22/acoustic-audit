# Acoustic-Audit — Real-Time Quran Recitation Verifier

**Status: Under development**

A real-time phonetic error detection system for Quranic recitation. Built for Huffaz who practise alone and have no feedback mechanism to catch their own mistakes mid-recitation. Audio is streamed from a mobile device to a Python server, analysed using Wav2Vec 2.0, and errors are surfaced in the Flutter UI in under 200ms.

---

## The Problem

When reciting from memory, a Hafiz often doesn't register their own errors in the moment — they move past them automatically. Without a listener, these mistakes go uncorrected and compound over time. Acoustic-Audit acts as that listener, flagging vowel-level errors (short vowels: Zabar, Zer, Pesh) in real time.

---

## How It Works

```
Microphone → Int16 PCM → WebSocket → NumPy normalisation
→ Wav2Vec 2.0 → phoneme sequence → Levenshtein comparison
→ JSON error payload → Flutter UI highlight
```

Audio is captured as raw 16-bit PCM at 16kHz and streamed over a full-duplex WebSocket to the Python server. The server processes audio in 2-second sliding windows with a 0.5-second overlap to maintain continuity across chunk boundaries.

Each chunk goes through:
1. **Wav2Vec 2.0 inference** — produces an uppercase phoneme string (e.g., `B I S M I`)
2. **Position detection** — on first recitation, Levenshtein ratio is used to find where in the Quran database the user has started (accepts ≥75% match)
3. **Strict vowel comparison** — once positioned, `Levenshtein.editops()` identifies substitution errors specifically on vowel characters (A, I, U), ignoring consonant approximations
4. **Error payload** — a JSON message is sent back with the error index and a description (e.g., `"Vowel Mistake: Expected A"`)

The client receives this and highlights the corresponding character in the Quran display in red with a yellow background.

---

## Repository Structure

```
acoustic-audit/
├── server/
│   ├── server.py            # FastAPI WebSocket server, Wav2Vec inference, Levenshtein grading
│   ├── setup_database.py    # One-time script: downloads Quran from API, converts to phoneme DB
│   └── quran_full.json      # Pre-built phoneme database (114 surahs, 6236 ayahs)
└── app/
    ├── lib/
    │   └── main.dart        # Flutter app: mic capture, WebSocket client, Quran display UI
    ├── pubspec.yaml         # Flutter dependencies
    └── android/ ios/ ...    # Platform build files
```

---

## Stack

| Layer | Technology |
|---|---|
| Mobile client | Flutter (Dart) |
| Audio capture | `sound_stream` |
| Transport | WebSocket (`web_socket_channel`) |
| Server framework | FastAPI + Uvicorn |
| ML model | `facebook/wav2vec2-base-960h` via HuggingFace Transformers |
| Tensor ops | PyTorch, NumPy |
| Error detection | `python-Levenshtein` |
| Quran data source | [Al-Quran Cloud API](https://alquran.cloud) — Uthmani script |

---

## Key Files

### `server/setup_database.py`

A one-time setup script that must be run before starting the server. It:

- Fetches the full Quran from the Al-Quran Cloud API (Uthmani script, vowelised)
- Verifies integrity by checking for exactly **6236 ayahs**
- Converts each Arabic character to a phoneme token using a hand-crafted `ARABIC_TO_PHONEME` map designed for Pakistani accent compatibility (e.g., ث → `S`, ذ → `Z`, ع → `A`)
- Handles **Shadda** (ّ) by doubling the preceding phoneme
- Saves the result as `quran_full.json`

Run this once before starting the server:
```bash
cd server
python setup_database.py
```

### `server/server.py`

The FastAPI WebSocket server. On startup it:
- Loads `facebook/wav2vec2-base-960h` from HuggingFace
- Loads and cleans `quran_full.json` — applies a **Sun Letter rule** that removes the silent `L` from `AL` before sun letters (R, S, D, Z, N, T), so `AL-Rahman` becomes `AR-Rahman` as the model hears it
- Builds a flat `QURAN_DB` string and a `SURAH_INDEX` for position lookup

Per WebSocket session:
- Buffers incoming PCM chunks
- Runs inference every 2 seconds
- Scans the first 50,000 characters of the database to find where the user is reciting (session detection phase)
- Once locked on, uses `editops` to flag vowel substitutions only

Start the server:
```bash
cd server
uvicorn server:app --host 0.0.0.0 --port 8000
```

### `app/lib/main.dart`

The Flutter client. Key behaviour:

- Requests microphone permission on connect
- Opens a WebSocket to the server IP entered by the user (configurable field in the UI — important for real-device testing)
- Streams raw audio bytes via `RecorderStream`
- Receives JSON messages from the server: `info`, `status`, or `mistake`
- On `mistake`: appends the error character index to `_mistakeIndices` and rebuilds the `RichText` Quran display, colouring that character red with a yellow highlight
- Optionally plays a `beep.mp3` asset on error (if the server sends `action: beep`)

The Quran text is rendered right-to-left using the `quran` package, displayed in the Amiri font at 28sp.

---

## Setup & Running Locally

### Prerequisites

- Python 3.9+
- Flutter SDK 3.x
- A device and PC on the same local network

### Server

```bash
cd server
pip install fastapi uvicorn torch transformers numpy python-Levenshtein requests
python setup_database.py   # builds quran_full.json — only needed once
python server.py
```

The first run will download the Wav2Vec 2.0 model (~360MB) from HuggingFace.

### Flutter App

1. Find your PC's local IP address (e.g., `192.168.1.5`)
2. Enter it in the IP field in the app
3. Run:

```bash
cd app
flutter pub get
flutter run
```

> **Android emulator:** use `10.0.2.2` instead of your PC's IP.  
> **Real device:** use your PC's LAN IP and ensure both are on the same network.

---

## Current Progress

| Feature | Status |
|---|---|
| WebSocket audio pipeline | ✅ Complete |
| PCM normalisation and Wav2Vec inference | ✅ Complete |
| Levenshtein grading and vowel error detection | ✅ Complete |
| Quran phoneme database (114 surahs) | ✅ Complete |
| Sun Letter correction in phoneme pipeline | ✅ Complete |
| Pakistani accent phoneme mapping | ✅ Complete |
| Real-time UI highlighting | ✅ Complete |
| Noise cancellation preprocessing | 🔄 In progress |
| Surah selection UI | 🔄 Planned |
| Session summary / error report | 🔄 Planned |

---

## Known Limitations

- **English-trained ASR:** Wav2Vec 2.0 (`wav2vec2-base-960h`) is trained on English speech. It approximates Arabic phonemes but is not a dedicated Arabic/Quranic ASR model. A model fine-tuned on Quranic recitation would substantially improve accuracy.
- **Search window:** Position detection currently scans only the first 50,000 characters of the database. Users starting mid-Quran will not be detected until this is extended.
- **Dialect:** The phoneme map is tuned for Pakistani/South Asian pronunciation. Gulf or Egyptian pronunciation patterns may produce more false positives.
- **Single flat text:** The database is stored as one concatenated string. This makes cross-surah boundary detection possible but complicates surah-specific navigation.

---

## Background

Built by Muhammad Saim. The motivation is personal: as a Hafiz, self-correction during solo recitation is genuinely difficult. This project is an attempt to build the feedback mechanism that is otherwise only available when reciting to a teacher.

The phonetic pipeline, particularly the vowel-level strictness and the Pakistani accent mappings, was designed from direct observation of how errors actually occur in practice: not wrong consonants, but wrong short vowels (Zabar/Zer/Pesh mix-ups) that change meaning.
