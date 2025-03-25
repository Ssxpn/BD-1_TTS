import os
import io
import wave
import random
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
    "B": {"b", "p", "d", "t", "k", "g", "q"},
    "S": {"s", "z", "f", "v", "j", "x", "h"},
    "P": {"l", "m", "n", "r"}
}

# def decompose_message(message):
#     """Ne garde que les consonnes suivies d'une voyelle et insère un espace entre chaque mot traité. Supprime les accents."""
#     message = message.lower()
#     message = ''.join(
#         c for c in unicodedata.normalize('NFD', message)
#         if unicodedata.category(c) != 'Mn'
#     )
#     vowels = "aeiouy"
#     consonnes = []
#     exceptions = {"je", "tu", "il", "on", "yo"}
#     words = message.split()

#     for word in words:
#         if len(word) <= 2 and word not in exceptions:
#             continue
#         for i in range(len(word) - 1):
#             char = word[i]
#             next_char = word[i + 1]
#             if char.isalpha() and char not in vowels and next_char in vowels:
#                 consonnes.append(char)
#         consonnes.append(' ')

#     return consonnes

def decompose_message(message):
    """
    Ne garde que les consonnes et les espaces d'un message,
    et retourne le tout sous forme de liste.

    Ex: "Salut BD-1" → ['s', 'l', 't', ' ', 'b', 'd']
    """
    message = message.lower()

    vowels = "aeiouy"
    consonnes = []

    for char in message:
        if char == ' ':
            consonnes.append(' ')
        elif char.isalpha() and char not in vowels:
            consonnes.append(char)

    return consonnes

def assign_emotion(phrase):
    """Détecte l'émotion d'une phrase."""
    phrase = phrase.strip()
    if "?" in phrase:
        return "question"
    elif "!" in phrase:
        return "surprise"
    elif any(word in phrase.lower() for word in ["oui", "super", "merci"]):
        return "positif"
    elif any(word in phrase.lower() for word in ["non", "triste", "pas"]):
        return "negatif"
    else:
        return "neutre"


def get_random_variant(folder, consonne):
    if not os.path.exists(folder):
        print(f"⛔ Dossier introuvable : {folder}")
        return None

    variants = [
        f for f in os.listdir(folder)
        if f.lower().startswith(consonne.lower()) and f.endswith(".wav")
    ]

    print(f"🔍 Fichiers présents dans {folder} : {variants}")

    if variants:
        return os.path.join(folder, random.choice(variants))
    return None

def get_sound(consonne, emotion="neutre"):
    if consonne == ' ':
        return None, None

    emotion_folder = os.path.join(EMOTIONS_DIR, emotion)
    sound_path = get_random_variant(emotion_folder, consonne)

    if not sound_path:
        sound_path = get_random_variant(CONSONNES_DIR, consonne)
        emotion = "neutre"

    if not sound_path:
        print(f"❌ Aucun fichier trouvé pour `{consonne}` dans `{emotion}` et `consonnes/`.")

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

    print(f"\n🔤 Lettres conservées : {list(message)}")
    print(f"🧩 Mappage BSP : {mapped}\n")

    while i < len(mapped):
        if mapped[i] == " " or (mapped[i].isalpha() and mapped[i].isupper() is False):
            i += 1
            continue

        for chunk_len in range(min(max_chunk, len(mapped) - i), 0, -1):
            chunk = mapped[i:i+chunk_len]

            if chunk_len == 1:
                original_char = message[i].lower()
                print(f"🔸 Chunk trop court ({chunk}), on utilise get_sound() avec '{original_char}'")
                path, emo_used = get_sound(original_char, emotion)
                if path:
                    print(f"✅ Fichier trouvé (1 lettre) : {path}")
                    results.append((path, emo_used, 1, original_char))
                    i += 1
                    break
                else:
                    print(f"❌ Aucun son trouvé pour caractère : '{original_char}'")
                    i += 1
                    break

            if not all(c in ["B", "S", "P"] for c in chunk):
                continue

            pattern = " ".join({"B": "Beep", "S": "Sifflement", "P": "Piano"}[c] for c in chunk)
            prefix = "".join(chunk)
            expected_filename = prefix + ".wav"

            folder_path = os.path.join(
                SOUNDS_DIR, "compositions", f"{chunk_len} caractères", pattern, emotion
            )

            print(f"\n🔍 Chunk : {''.join(chunk)} → Dossier : {folder_path}")
            print(f"🔎 Fichier attendu : {expected_filename}")

            path = get_random_variant(folder_path, prefix)

            if not path and emotion != "neutre":
                print(f"⚠️ Rien trouvé pour {emotion}, on tente 'neutre'.")
                folder_path = os.path.join(
                    SOUNDS_DIR, "compositions", f"{chunk_len} caractères", pattern, "neutre"
                )
                print(f"📁 Dossier fallback : {folder_path}")
                print(f"🔎 Fichier attendu : {expected_filename}")
                path = get_random_variant(folder_path, prefix)
                if path:
                    emotion = "neutre"

            if path:
                print(f"✅ Fichier trouvé : {path}")
                results.append((path, emotion, chunk_len, message[i:i+chunk_len]))
                i += chunk_len
                break
        else:
            print(f"❌ Aucun son trouvé pour : {mapped[i]}")
            i += 1

    return results

def generate_tts_audio(message: str, options: dict[str, Any]) -> tuple[str, bytes]:
    """Génère un fichier audio à partir du message en assemblant les sons correspondants."""
    print(f"\n📝 **Message** : {message}")

    emotion = assign_emotion(message)
    print(f"🎭 **Émotion détectée** : {emotion}")

    consonnes = decompose_message(message)
    print(f"🔡 **Consonnes extraites** : {consonnes}")

    chunks = get_sound_chunked(consonnes, emotion)

    final_audio = AudioSegment.silent(duration=0)
    total_duration = 0

    print("\n🎶 **Correspondance des sons** :")
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
    print(f"📏 **Durée totale de l'audio généré** : {total_duration:.2f} secondes")

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

    final_audio = AudioSegment.silent(duration=0)

    # 🔹 On peut ajouter plus tard une séparation en phrases
    options = {"audio_output": "wav"}
    format, audio_data = generate_tts_audio(message, options)

    temp_stream = io.BytesIO(audio_data)
    audio_segment = AudioSegment.from_file(temp_stream, format="wav")
    final_audio += audio_segment

    output_path = os.path.join(BASE_DIR, "temp_tts.wav")
    with open(output_path, "wb") as f:
        final_audio.export(f, format="wav")

    print(f"✅ Fichier `{output_path}` généré et prêt à être lu.")

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