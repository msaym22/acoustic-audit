import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import numpy as np
import torch
import json
import re
import Levenshtein
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

app = FastAPI()

print("\n--- 🧠 INITIALIZING QURAN AI BRAIN ---")

# 1. LOAD AI MODEL
print("1. Loading Neural Network...")
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
print("   - Model Loaded.")

# 2. LOAD & CLEAN QURAN DATABASE
print("2. Loading Quran Database...")
QURAN_DB = ""
SURAH_INDEX = []

def clean_phonemes_for_ai(text):
    """
    Fixes the 'Sun Letter' issue in the JSON file.
    If 'L' is followed by a Sun Letter (R, S, D, Z, N, T), we remove the 'L'.
    This ensures 'Al-Rahman' becomes 'Ar-Rahman' matching what the AI hears.
    """
    # Remove Silent L before Sun Letters (R, S, D, Z, N, T, SH)
    # The file writes "A L R R", this regex turns it into "A R R"
    text = re.sub(r'A L ([RSDZNT])', r'A \1', text) 
    return text

try:
    with open("quran_full.json", "r") as f:
        data = json.load(f)
        for surah in data:
            # Clean the text before storing
            clean_text = clean_phonemes_for_ai(surah["phonemes"])
            
            start_pos = len(QURAN_DB)
            QURAN_DB += clean_text + " "
            
            SURAH_INDEX.append({
                "id": surah["id"],
                "name": surah["name"],
                "start": start_pos,
                "end": len(QURAN_DB)
            })
            
    print(f"   - Loaded {len(SURAH_INDEX)} Surahs.")
    print(f"   - Database ready for Pakistani Accent validation.")
    
except FileNotFoundError:
    print("❌ CRITICAL: 'quran_full.json' not found. Upload the file to the 'server' folder.")
    QURAN_DB = "B I S M I A L L A H" # Fallback

# 3. WEBSOCKET LOGIC
@app.websocket("/ws/recite")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    buffer = np.array([], dtype=np.float32)
    session_active = False
    current_idx = 0

    try:
        await websocket.receive_text() # Swallow config message

        while True:
            data = await websocket.receive_bytes()
            chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
            buffer = np.concatenate((buffer, chunk))

            # Process every 2 seconds
            if len(buffer) > 32000:
                # Predict
                input_values = processor(buffer, sampling_rate=16000, return_tensors="pt").input_values
                with torch.no_grad():
                    logits = model(input_values).logits
                predicted_ids = torch.argmax(logits, dim=-1)
                transcription = processor.batch_decode(predicted_ids)[0].upper()
                
                # Logic: Find where user is reciting
                if not session_active:
                    # Scan database for match
                    # We accept 80% accuracy to find the starting point
                    found = False
                    # Optimization: Scan in chunks of 1000 chars to save CPU
                    search_window = 50000 
                    # In real app, we would search whole DB. For demo, we search first 50k chars.
                    
                    for i in range(0, search_window, 10): 
                        db_slice = QURAN_DB[i : i+len(transcription)]
                        ratio = Levenshtein.ratio(transcription, db_slice)
                        if ratio > 0.75:
                            session_active = True
                            current_idx = i + len(transcription)
                            await websocket.send_json({"type": "info", "message": "Detected! Reciting..."})
                            found = True
                            break
                    
                    if not found:
                         await websocket.send_json({"type": "info", "message": "Listening..."})

                else:
                    # STRICT VOWEL CHECKING
                    expected = QURAN_DB[current_idx : current_idx + len(transcription)]
                    
                    # We use 'editops' to find specific substitution errors (Wrong Vowels)
                    ops = Levenshtein.editops(transcription, expected)
                    mistakes = []
                    
                    for op in ops:
                        if op[0] == 'replace':
                            idx_in_transcription = op[1]
                            idx_in_expected = op[2]
                            
                            wrong_char = transcription[idx_in_transcription]
                            correct_char = expected[idx_in_expected]
                            
                            # FLAG ONLY VOWEL ERRORS (A, I, U)
                            if correct_char in ['A', 'I', 'U'] and wrong_char in ['A', 'I', 'U']:
                                mistakes.append(correct_char)

                    if mistakes:
                        await websocket.send_json({
                            "type": "mistake",
                            "action": "highlight",
                            "index": current_idx, 
                            "details": f"Vowel Mistake: Expected {mistakes[0]}"
                        })
                    else:
                        await websocket.send_json({"type": "status", "msg": "Correct"})
                        current_idx += len(transcription)

                # Overlap buffer
                buffer = buffer[-8000:] # Keep last 0.5s

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)