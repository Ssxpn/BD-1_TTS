import os
import io
import wave
import random
import string
import re
import simpleaudio as sa
from pydub import AudioSegment
from typing import Any
import unicodedata
import threading

# 📂 Définition des dossiers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")
CONSONNES_DIR = os.path.join(SOUNDS_DIR, "consonnes")
EMOTIONS_DIR = os.path.join(SOUNDS_DIR, "emotions")

# 📌 Catégorisation des sons pour règles de répétition
SOUND_TYPES = {
    "sifflement": ["s", "z", "f", "v", "j"],
    "double_sifflement": ["x", "h"],
    "double_beep": ["b", "p", "d", "t", "k", "g", "q"],
    "piano": ["l", "m", "n", "r"],
    "divers": ["w", "y", "c"]
}

# 🧠 Regroupement BSP
BSP_GROUPS = {
    "B": {"b", "p", "d", "t", "k", "g", "q", "c"},
    "S": {"s", "z", "f", "v", "j", "x", "h"},
    "P": {"l", "m", "n", "r"}
}

def process_message_by_phrases(message):
    """Découpe un message en phrases, nettoie les apostrophes/tirets, et attribue une émotion à chaque phrase."""
    # 🔄 Nettoyage initial
    cleaned_message = message.replace("'", " ").replace("-", " ")

    # 🔹 Séparer les phrases tout en gardant les ponctuations
    phrases = re.split(r"([.!?])", cleaned_message)

    structured_text = []
    current_phrase = ""

    for segment in phrases:
        if segment in ".!?":
            if current_phrase.strip():
                full_phrase = (current_phrase + segment).strip()
                structured_text.append((full_phrase, assign_emotion(full_phrase)))
            current_phrase = ""
        else:
            current_phrase += segment

    # Dernière phrase (sans ponctuation éventuelle)
    if current_phrase.strip():
        structured_text.append((current_phrase.strip(), assign_emotion(current_phrase)))

    # Debug
    for phrase, emotion in structured_text:
        print(f"📝 Phrase : {phrase} → 🎭 Émotion détectée : {emotion}")

    return structured_text

def decompose_message(message):
    def _extract_consonnes(message, min_word_len):
        vowels = "aeiou"
        consonnes = []
        exceptions = {}  # {"je", "tu", "il", "on", "yo"}
        force_include = {}  # {"bd-1"}

        words = message.split()

        for word in words:
            cleaned = word.strip(string.punctuation)

            if cleaned in force_include:
                for c in cleaned:
                    if c.isalpha() and c not in vowels:
                        consonnes.append(c)
                consonnes.append(' ')
                continue

            if len(cleaned) <= min_word_len and cleaned not in exceptions:
                continue

            i = 0
            while i < len(cleaned) - 1:
                c1 = cleaned[i]
                c2 = cleaned[i + 1]

                if c2 in vowels and c1.isalpha() and c1 not in vowels:
                    j = i - 1
                    stack = [c1]
                    while j >= 0 and cleaned[j].isalpha() and cleaned[j] not in vowels:
                        stack.insert(0, cleaned[j])
                        j -= 1
                    consonnes.extend(stack)
                    i += 2
                else:
                    i += 1

            consonnes.append(' ')
        return consonnes

    # 🔹 Minuscule + suppression des accents
    message = message.lower()
    message = message.replace("'", " ")
    message = ''.join(
        c for c in unicodedata.normalize('NFD', message)
        if unicodedata.category(c) != 'Mn'
    )

    # 🔹 Première passe (mots de +4 lettres)
    consonnes = _extract_consonnes(message, min_word_len=4)

    # 🔹 Seconde passe si vide (mots de +2 lettres)
    if not [c for c in consonnes if c.strip()]:
        consonnes = _extract_consonnes(message, min_word_len=3)

    return consonnes

def assign_emotion(phrase):
    """Détecte l'émotion d'une phrase."""
    phrase = phrase.strip()
    if "?" in phrase:
        return "question"
    elif any(word in phrase.lower() for word in ["non", "triste", "pas"]):
        return "negatif"
    elif any(word in phrase.lower() for word in ["oui", "super", "merci"]):
        return "positif"
    elif "!" in phrase:
        return "surprise"
    else:
        return "neutre"

def get_random_variant(folder, consonne, used_variants):
    if not os.path.exists(folder):
        return None

    variants = [
        f for f in os.listdir(folder)
        if f.lower().startswith(consonne.lower()) and f.endswith(".wav") and f not in used_variants
    ]

    if variants: #Ne pas répéter le meme son 2 fois
        chosen = random.choice(variants)
        used_variants.add(chosen)
        return os.path.join(folder, chosen)
    return None

def get_sound(consonne, emotion="neutre", used_variants=None):
    if consonne == ' ':
        return None, None

    if used_variants is None:
        used_variants = set()

    emotion_folder = os.path.join(EMOTIONS_DIR, emotion)
    sound_path = get_random_variant(emotion_folder, consonne, used_variants)

    if not sound_path:
        sound_path = get_random_variant(CONSONNES_DIR, consonne, used_variants)
        emotion = "neutre"

    return sound_path, emotion

def map_letters_to_sound_groups(text):
    result = []
    for c in text:
        c_lower = c.lower()
        for group, letters in BSP_GROUPS.items():
            if c_lower in letters:
                result.append(group)
                break
        else:
            result.append(c_lower)
    return result

def get_sound_chunked(message, emotion="neutre", max_chunk=4):
    mapped = map_letters_to_sound_groups(message)
    i = 0
    results = []
    used_variants = set()
    emotion_or = emotion

    while i < len(mapped):
        if mapped[i] == " " or (mapped[i].isalpha() and mapped[i].isupper() is False):
            i += 1
            continue

        # Trouver la fin du mot courant (jusqu'au prochain espace)
        word_end = i
        while word_end < len(mapped) and mapped[word_end] != " ":
            word_end += 1

        chunk_found = False

        for chunk_len in range(min(max_chunk, word_end - i), 0, -1):
            chunk = mapped[i:i + chunk_len]

            # 🔹 Fallback dès le début si chunk_len == 1
            if chunk_len == 1:
                original_char = message[i].lower()
                emotion_folder = os.path.join(EMOTIONS_DIR, emotion_or)
                path = get_random_variant(emotion_folder, original_char, used_variants)
                used_emotion = emotion_or

                if not path:
                    path = get_random_variant(CONSONNES_DIR, original_char, used_variants)
                    used_emotion = "neutre"

                if path:
                    used_variants.add(os.path.basename(path))
                    results.append((path, used_emotion, 1, original_char))
                else:
                    print(f"❌ Aucun son trouvé pour caractère : '{original_char}'")

                i = word_end  # 🔁 Même en fallback, passer au mot suivant
                chunk_found = True
                break

            if not all(c in ["B", "S", "P"] for c in chunk):
                continue

            pattern = " ".join({"B": "Beep", "S": "Sifflement", "P": "Piano"}[c] for c in chunk)
            prefix = "".join(chunk)
            expected_filename = prefix + ".wav"

            folder_path = os.path.join(
                SOUNDS_DIR, "compositions", f"{chunk_len}_caracteres", pattern, emotion
            )

            path = get_random_variant(folder_path, prefix, used_variants)

            if not path and emotion != "neutre":
                folder_path = os.path.join(
                    SOUNDS_DIR, "compositions", f"{chunk_len}_caracteres", pattern, "neutre"
                )
                path = get_random_variant(folder_path, prefix, used_variants)
                if path:
                    emotion = "neutre"

            if path:
                used_variants.add(os.path.basename(path))
                results.append((path, emotion, chunk_len, message[i:i + chunk_len]))
                i = word_end  # 🔁 Une fois le chunk utilisé, on saute le mot entier
                chunk_found = True
                break

        if not chunk_found:
            i = word_end  # 🔁 Sauter au mot suivant même si rien trouvé

    return results

def generate_tts_audio(message: str, options: dict[str, Any]) -> tuple[str, bytes]:
    """Génère un fichier audio à partir du message en assemblant les sons correspondants."""

    emotion = assign_emotion(message)
    consonnes = decompose_message(message)
    print(f"🔡 **Consonnes extraites** : {consonnes}")

    chunks = get_sound_chunked(consonnes, emotion)

    final_audio = AudioSegment.silent(duration=0)
    total_duration = 0

    print("┌────────┬──────────────────────────┬───────────┬──────────────────────────────────────────────┐")
    print("│ Lettre │       Fichier WAV         │ Émotion   │                     Path                    │")
    print("├────────┼──────────────────────────┼───────────┼──────────────────────────────────────────────┤")

    message_letters = list(message)
    msg_index = 0

    for path, emo_used, size, original in chunks:
        if path:
            audio = AudioSegment.from_wav(path)
            final_audio += audio
            total_duration += len(audio) / 1000
            print(f"│   {''.join(original):<10}   │ {os.path.basename(path):<24} │ {emo_used:<9} │ {path} │")
        else:
            print(f"│   {''.join(original):<10}   │ ❌ AUCUN SON TROUVÉ         │ {emo_used:<9} │ ❌ Aucun fichier trouvé │")

    print("└────────┴──────────────────────────┴───────────┴──────────────────────────────────────────────┘\n")

    # Sauvegarde en mémoire
    output_stream = io.BytesIO()
    output_file = wave.open(output_stream, "wb")
    output_file.setnchannels(1)
    output_file.setsampwidth(2)
    output_file.setframerate(44100)
    output_file.writeframes(final_audio.raw_data)
    output_file.close()

    byte_array = output_stream.getvalue()

    if options.get("audio_output") == "wav":
        return ("wav", byte_array)
    return ("raw", byte_array)

def tts_bd1(message: str):
    """Génère et joue un son à partir du message, en adaptant l’émotion à chaque phrase."""

    structured_text = process_message_by_phrases(message)
    final_audio = AudioSegment.silent(duration=0)

    for phrase, emotion in structured_text:

        options = {"audio_output": "wav"}
        format, audio_data = generate_tts_audio(phrase, options)

        temp_stream = io.BytesIO(audio_data)
        phrase_audio = AudioSegment.from_file(temp_stream, format="wav")

        final_audio += phrase_audio
        
    output_path = os.path.join(BASE_DIR, "temp_tts.wav")
    with open(output_path, "wb") as f:
        final_audio.export(f, format="wav")

    with open(output_path, "rb") as f:
        audio_buffer = io.BytesIO(f.read())

    try:
        os.remove(output_path)
        print(f"🗑️ Fichier `{output_path}` supprimé après chargement en mémoire.")
    except Exception as e:
        print(f"❌ Erreur lors de la suppression du fichier `{output_path}` : {e}")

    wave_obj = sa.WaveObject.from_wave_read(wave.open(audio_buffer, "rb"))
    play_obj = wave_obj.play()
    play_obj.wait_done()
