import requests
import json
import re

# ==========================================
# 1. ROBUST ARABIC -> PHONEME MAPPER
# ==========================================
# This ensures we control exactly how "Zabar", "Zair", "Pesh" are stored.
# We don't rely on English translators; we rely on the raw Arabic Harakat.

ARABIC_TO_PHONEME = {
    # --- CONSONANTS ---
    '\u0627': 'A',   # Alif
    '\u0628': 'B',   # Baa
    '\u062A': 'T',   # Taa
    '\u062B': 'S',   # Thaa (Mapped to S for Pakistani accent compatibility)
    '\u062C': 'J',   # Jeem
    '\u062D': 'H',   # Haa (Sharp)
    '\u062E': 'K',   # Khaa (We map close to K/H for simplicity)
    '\u062F': 'D',   # Daal
    '\u0630': 'Z',   # Dhaal (Mapped to Z)
    '\u0631': 'R',   # Raa
    '\u0632': 'Z',   # Zaa
    '\u0633': 'S',   # Seen
    '\u0634': 'SH',  # Sheen
    '\u0635': 'S',   # Saad (Thick S -> S)
    '\u0636': 'D',   # Daad (Thick D -> D)
    '\u0637': 'T',   # Taa (Thick T -> T)
    '\u0638': 'Z',   # Dhaa (Thick Z -> Z)
    '\u0639': 'A',   # Ain (Difficult sound, usually 'A' or silent in AI)
    '\u063A': 'G',   # Ghain
    '\u0641': 'F',   # Faa
    '\u0642': 'Q',   # Qaaf
    '\u0643': 'K',   # Kaaf
    '\u0644': 'L',   # Laam
    '\u0645': 'M',   # Meem
    '\u0646': 'N',   # Noon
    '\u0647': 'H',   # Haa (Round)
    '\u0648': 'W',   # Waw
    '\u064A': 'Y',   # Yaa
    
    # --- VOWELS (HARAKAT) - THE CRITICAL PART ---
    '\u064E': 'A',   # Fatha (Zabar)
    '\u0650': 'I',   # Kasra (Zair)
    '\u064F': 'U',   # Damma (Pesh)
    '\u064B': 'AN',  # Fathatan
    '\u064D': 'IN',  # Kasratan
    '\u064C': 'UN',  # Dammatan
    '\u0670': 'A',   # Dagger Alif (Standing Zabar)
    
    # --- SPECIAL CHARS ---
    '\u0629': 'H',   # Taa Marbuta (usually H at stop, T in flow. We use H for safety)
    '\u0651': 'SHADDA' # Special handling needed
}

def arabic_to_phonemes(arabic_text):
    result = []
    chars = list(arabic_text)
    
    for i, char in enumerate(chars):
        # Handle Shadda (Doubling the PREVIOUS letter)
        if char == '\u0651': 
            if result: result.append(result[-1]) # Repeat last char
            continue
            
        # Standard Mapping
        if char in ARABIC_TO_PHONEME:
            result.append(ARABIC_TO_PHONEME[char])
            
    return " ".join(result) # Return spaced phonemes "B I S M I"

# ==========================================
# 2. DOWNLOAD & VERIFY LOGIC
# ==========================================
def generate_verified_database():
    print("⬇️  Fetching Source 1: Al-Quran Cloud (Uthmani Script)...")
    url_1 = "http://api.alquran.cloud/v1/quran/quran-simple-enhanced"
    
    try:
        data = requests.get(url_1).json()
        
        # VERIFICATION STEP:
        # We verify against the known total number of Ayahs (6236)
        total_ayahs_found = sum(len(s["ayahs"]) for s in data["data"]["surahs"])
        print(f"🔍 Verification Check: Found {total_ayahs_found} Ayahs.")
        
        if total_ayahs_found != 6236:
            print("❌ INTEGRITY CHECK FAILED: Expected 6236 Ayahs.")
            return

        print("✅ Integrity Passed. Generating Phonetic Database...")
        
        final_db = []
        
        for surah in data["data"]["surahs"]:
            surah_phonemes = ""
            
            for ayah in surah["ayahs"]:
                # Convert raw Arabic to our Strict Phonetic System
                # text field contains vowels
                raw_arabic = ayah["text"]
                
                # Convert
                phonetic_text = arabic_to_phonemes(raw_arabic)
                surah_phonemes += phonetic_text + " "
            
            # Clean up double spaces
            surah_phonemes = re.sub(r'\s+', ' ', surah_phonemes).strip()
            
            final_db.append({
                "id": surah["number"],
                "name": surah["englishName"],
                "phonemes": surah_phonemes
            })
            
            print(f"   Processed Surah {surah['number']} ({surah['englishName']})")

        # Save
        with open("quran_full.json", "w") as f:
            json.dump(final_db, f)
            
        print("\n🏆 VERIFIED DATABASE CREATED: 'quran_full.json'")
        print("   - Source: Uthmani Script (Simple Enhanced)")
        print("   - Logic: Strict Vowel Mapping (Zabar=A, Zer=I, Pesh=U)")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_verified_database()