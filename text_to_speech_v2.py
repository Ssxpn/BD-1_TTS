import os
import io
import wave
import random
import re
import simpleaudio as sa
from pydub import AudioSegment
from typing import Any
import unicodedata
import pygame
import time


# 📂 Définition des dossiers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")
CONSONNES_DIR = os.path.join(SOUNDS_DIR, "consonnes")
EMOTIONS_DIR = os.path.join(SOUNDS_DIR, "emotions")

# 📌 **Catégorisation des sons**
SOUND_TYPES = {
    "sifflement": ["s", "z", "f", "v", "j"],
    "double_sifflement": ["x", "h"],
    "double_beep": ["b", "p", "d", "t", "k", "g", "q"],
    "piano": ["l", "m", "n", "r"],
    "divers": ["w", "y", "c"]
}

def get_random_variant(folder, consonne):
    """Cherche une variante aléatoire du son (ex: "z.wav", "z1.wav", "z2.wav"...) dans un dossier donné."""
    if not os.path.exists(folder):
        return None

    variants = [f for f in os.listdir(folder) if f.lower().startswith(consonne.lower()) and f.endswith(".wav")]

    if variants:
        return os.path.join(folder, random.choice(variants))
    return None

def process_message_by_phrases(message):
    """Divise le message en phrases et assigne une émotion distincte à chaque partie."""
    
    # 🔹 Séparer les phrases tout en gardant les séparateurs
    phrases = re.split(r"([.!?])", message)

    structured_text = []
    current_phrase = ""

    for segment in phrases:
        if segment in ".!?":  
            # 🏷️ Fin d'une phrase -> Déterminer son émotion
            if current_phrase.strip():  # ⬅️ Vérifie qu'on ne traite pas une phrase vide
                current_phrase += segment
                structured_text.append((current_phrase.strip(), assign_emotion(current_phrase)))
            current_phrase = ""  # Reset de la phrase en cours
        else:
            current_phrase += segment

    # ⬇️ Vérifier s'il reste une phrase en dehors des séparateurs (éviter les phrases vides)
    if current_phrase.strip():
        structured_text.append((current_phrase.strip(), assign_emotion(current_phrase)))

    # 🔹 Vérification du résultat
    for phrase, emotion in structured_text:
        print(f"📝 Phrase : {phrase} → 🎭 Émotion détectée : {emotion}")

    return structured_text

def get_sound(consonne, emotion="neutre"):
    """Cherche un son correspondant à une consonne et une émotion. Fallback vers `consonnes/` si nécessaire."""

    # 1️⃣ Essayer d'abord dans `emotions/{emotion}/`
    emotion_folder = os.path.join(EMOTIONS_DIR, emotion)
    sound_path = get_random_variant(emotion_folder, consonne)

    # 2️⃣ Si pas trouvé, fallback dans `consonnes/` (neutre)
    if not sound_path:
        sound_path = get_random_variant(CONSONNES_DIR, consonne)
        emotion = "neutre"  # Met à jour l'affichage pour indiquer un fallback

    # 3️⃣ Si toujours pas trouvé, afficher un message
    if not sound_path:
        print(f"❌ Aucun fichier trouvé pour `{consonne}` dans `{emotion}` et `consonnes/`.")

    return sound_path, emotion

def decompose_message(message):
    """Ne garde que les consonnes qui sont suivies d'une voyelle et supprime les accents."""

    # 🔹 **Mettre le message en minuscule dès le début**
    message = message.lower()
    
    # 🔹 **Supprimer les accents tout en conservant les lettres**
    message = ''.join(
        c if unicodedata.category(c) != 'Mn' else ''  # Supprime l'accent mais garde la lettre
        for c in unicodedata.normalize('NFD', message)
    )

    vowels = "aeiou"
    consonnes = []
    exceptions = {"je", "tu", "il", "on", "yo"}  # Mots de 2 lettres à garder
    
    # Séparer en mots pour exclure ceux de 2 lettres sauf exceptions
    words = message.split()
    
    for word in words:
        word = word.lower()
        if len(word) <= 2 and word not in exceptions:
            continue  # Ignore les mots de 2 lettres sauf exceptions
        
        for i in range(len(word) - 1):  # On traite toutes les lettres sauf la dernière
            char = word[i].lower()
            next_char = word[i + 1].lower()

            if char.isalpha() and char not in vowels and next_char in vowels:
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

def enforce_sound_rules(consonnes):
    """Évite deux sons du même type consécutifs."""
    for i in range(len(consonnes) - 1):
        c1, c2 = consonnes[i], consonnes[i + 1]
        type1 = next((t for t, lst in SOUND_TYPES.items() if c1 in lst), "divers")
        type2 = next((t for t, lst in SOUND_TYPES.items() if c2 in lst), "divers")

        if type1 == type2 and type1 in ["sifflement", "double_sifflement", "double_beep", "piano"]:
            consonnes[i + 1] = random.choice(SOUND_TYPES["divers"])

    return consonnes

def generate_tts_audio(message: str, options: dict[str, Any]) -> tuple[str, bytes]:
    """Génère un fichier audio à partir du message en assemblant les sons correspondants."""

    #print(f"\n📝 **Message** : {message}")

    consonnes = decompose_message(message)
    print(f"🔡 **Consonnes extraites** : {consonnes}")

    emotion = assign_emotion(message)
    #print(f"🎭 **Émotion détectée** : {emotion}")

    consonnes = enforce_sound_rules(consonnes)
    #print(f"✅ **Consonnes après règles** : {consonnes}")

    # 1️⃣ **Préchargement et assemblage des sons**
    final_audio = AudioSegment.silent(duration=0)
    total_duration = 0

    #print("\n🎶 **Correspondance des sons** :")
    #print("┌────────┬──────────────────────────┬───────────┬──────────────────────────────────────────────┐")
    #print("│ Lettre │       Fichier WAV         │ Émotion   │                     Path                    │")
    #print("├────────┼──────────────────────────┼───────────┼──────────────────────────────────────────────┤")

    for consonne in consonnes:
        sound_file, sound_emotion = get_sound(consonne, emotion)

        if sound_file:
            audio = AudioSegment.from_wav(sound_file)
            final_audio += audio  # **On assemble les sons**
            total_duration += len(audio) / 1000  # Convertir en secondes
            #print(f"│   {consonne}   │ {os.path.basename(sound_file):<24} │ {sound_emotion:<9} │ {sound_file} │")
        else:
            print(f"│   {consonne}   │ ❌ AUCUN SON TROUVÉ         │ {sound_emotion:<9} │ ❌ Aucun fichier trouvé │")

    #print("└────────┴──────────────────────────┴───────────┴──────────────────────────────────────────────┘\n")
    #print(f"📏 **Durée totale de l'audio généré** : {total_duration:.2f} secondes")

    # 2️⃣ **Sauvegarde en mémoire**
    output_stream = io.BytesIO()
    output_file = wave.open(output_stream, "wb")
    output_file.setnchannels(1)  # Mono
    output_file.setsampwidth(2)  # 16 bits
    output_file.setframerate(44100)  # 44.1 kHz
    output_file.writeframes(final_audio.raw_data)
    output_file.close()

    byte_array = output_stream.getvalue()

    # 3️⃣ **Retour du format audio**
    if options.get("audio_output") == "wav":
        return ("wav", byte_array)
    return ("raw", byte_array)

def tts_bd1(message: str):
    """Génère et joue un son à partir du message, en adaptant l’émotion à chaque phrase."""

    structured_text = process_message_by_phrases(message)
    final_audio = AudioSegment.silent(duration=0)

    for phrase, emotion in structured_text:
        #print(f"📝 **Phrase analysée** : {phrase} → 🎭 **Émotion détectée** : {emotion}")

        options = {"audio_output": "wav"}
        format, audio_data = generate_tts_audio(phrase, options)

        temp_stream = io.BytesIO(audio_data)
        phrase_audio = AudioSegment.from_file(temp_stream, format="wav")

        final_audio += phrase_audio
        
    output_path = os.path.join(BASE_DIR, "temp_tts.wav")
    with open(output_path, "wb") as f:
        final_audio.export(f, format="wav")

    #print(f"✅ Fichier `{output_path}` généré et prêt à être lu.")
    audio_file = os.path.join(BASE_DIR, "temp_tts.wav")
    # Initialiser pygame mixer
    pygame.mixer.init()
    
    # Charger et jouer le fichier audio
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    
    # Attendre que la lecture soit terminée
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.quit() 
    # Supprimer le fichier audio après lecture
    os.remove(audio_file)