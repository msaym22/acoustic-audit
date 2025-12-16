# 🎙️ Acoustic-Audit: Real-Time Verification Engine

![Status](https://img.shields.io/badge/Status-Prototype-orange.svg) ![Stack](https://img.shields.io/badge/Stack-Python_|_WebSockets-blue.svg) ![Model](https://img.shields.io/badge/Model-Wav2Vec_2.0-green.svg) ![Performance](https://img.shields.io/badge/Latency-<200ms-brightgreen.svg)

## ⚡ Technical Overview
A high-performance audio processing pipeline designed to detect **phonetic anomalies** in real-time speech streams.
Unlike standard Speech-to-Text (STT) APIs which process whole sentences, this system streams raw audio packets via **WebSockets**, enabling **sub-second feedback loops** for error correction.

> **Use Case:** Originally designed for recitation verification, this architecture is applicable to **Voice Biometrics**, **Trading Floor Surveillance**, and **Automated Command Verification** in FinTech.

---

## 🏗️ System Architecture

### 1. The "Ears" (Client-Side Stream)
* **Protocol:** Full-Duplex WebSockets (Low Latency).
* **Data Format:** Captures raw `Int16` PCM audio streams directly from the hardware microphone.
* **Optimization:** Audio is chunked into small packets to prevent network bottlenecks, ensuring real-time transmission.

### 2. The "Translator" (Data Normalization)
* **Ingestion:** Python server receives raw integer arrays (e.g., `[102, 500, -200...]`).
* **Vectorization:** Uses **NumPy** to convert `Int16` buffers into floating-point tensors (`-1.0` to `1.0`) required for Neural Network inference.
    ```python
    # High-performance normalization logic
    chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
    ```

### 3. The "Brain" (Neural Inference)
* **Model:** **Wav2Vec 2.0** (Facebook AI).
* **Process:** The model analyzes the waveform shape to output a probability matrix of phonemes for every timestamp (e.g., *t=0.5s: 90% probability of 'B'*).
* **Decoding:** Stitches probability peaks to reconstruct the phonetic sequence (e.g., `B-I-S-M-I-L-L-A-H`).

### 4. The "Grader" (Algorithmic Logic)
* **Algorithm:** **Levenshtein Distance** (Edit Distance).
* **Logic:** Calculates the mathematical "distance" between the *Predicted Speech* and the *Ground Truth*.
* **Thresholding:**
    * If `Distance > 3`: Triggers Error Event.
    * If `Distance == 0`: Validates Input.
    * *Example:* `BISMALLAH` vs `BISMILLAH` = Distance 1 (Vowel Mismatch).

### 5. The "Feedback" (Latency Loop)
* **Response:** Server pushes a lightweight JSON payload back to the client.
* **UI Update:** Flutter client parses the JSON index (e.g., `{"index": 5, "error": "mismatch"}`) and repaints the UI text in **Red** within milliseconds.

---

## 🛠️ Tech Stack
* **Client:** Flutter (Dart), WebSocketChannel.
* **Server:** Python, FastAPI/Flask (for socket handling).
* **AI/ML:** PyTorch, Wav2Vec 2.0, NumPy.
* **Algorithms:** Levenshtein (Fuzzy Matching).

---

## 🚧 Current Development Status
![Status](https://img.shields.io/badge/Status-Under_Active_R&D-orange)

This project is currently in the **R&D Phase**.
* **Optimized:** WebSocket handshake latency reduced for 3G/4G networks.
* **In Progress:** Integrating noise-cancellation preprocessing for high-noise environments.

---

### 👤 Author
**Muhammad Saim**
*Systems Engineer & AI Researcher | FAST NUCES*
