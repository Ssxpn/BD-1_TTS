import os
import io
import wave
import random
import simpleaudio as sa
from pydub import AudioSegment
from typing import Any
import unicodedata


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

    vowels = "aeiouy"
    consonnes = []
    exceptions = {"je", "tu", "il", "on"}  # Mots de 2 lettres à garder
    
    # Séparer en mots pour exclure ceux de 2 lettres sauf exceptions
    words = message.split()
    
    for word in words:
        if len(word) <= 2 and word not in exceptions:
            continue  # Ignore les mots de 2 lettres sauf exceptions
        
        for i in range(len(word) - 1):  # On traite toutes les lettres sauf la dernière
            char = word[i].lower()
            next_char = word[i + 1].lower()

            if char.isalpha() and char not in vowels and next_char in vowels:
                consonnes.append(char)

    return consonnes

def assign_emotion(message):
    """Détecte l'émotion du message."""
    if "?" in message:
        return "question"
    elif "!" in message:
        return "surprise"
    elif any(word in message.lower() for word in ["oui", "super", "merci"]):
        return "positif"
    elif any(word in message.lower() for word in ["non", "triste", "pas"]):
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

    print(f"\n📝 **Message** : {message}")

    consonnes = decompose_message(message)
    print(f"🔡 **Consonnes extraites** : {consonnes}")

    emotion = assign_emotion(message)
    print(f"🎭 **Émotion détectée** : {emotion}")

    consonnes = enforce_sound_rules(consonnes)
    print(f"✅ **Consonnes après règles** : {consonnes}")

    # 1️⃣ **Préchargement et assemblage des sons**
    final_audio = AudioSegment.silent(duration=0)
    total_duration = 0

    print("\n🎶 **Correspondance des sons** :")
    print("┌────────┬──────────────────────────┬───────────┬──────────────────────────────────────────────┐")
    print("│ Lettre │       Fichier WAV         │ Émotion   │                     Path                    │")
    print("├────────┼──────────────────────────┼───────────┼──────────────────────────────────────────────┤")

    for consonne in consonnes:
        sound_file, sound_emotion = get_sound(consonne, emotion)

        if sound_file:
            audio = AudioSegment.from_wav(sound_file)
            final_audio += audio  # **On assemble les sons**
            total_duration += len(audio) / 1000  # Convertir en secondes
            print(f"│   {consonne}   │ {os.path.basename(sound_file):<24} │ {sound_emotion:<9} │ {sound_file} │")
        else:
            print(f"│   {consonne}   │ ❌ AUCUN SON TROUVÉ         │ {sound_emotion:<9} │ ❌ Aucun fichier trouvé │")

    print("└────────┴──────────────────────────┴───────────┴──────────────────────────────────────────────┘\n")
    print(f"📏 **Durée totale de l'audio généré** : {total_duration:.2f} secondes")

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
    """Génère un son à partir d'un message et le joue immédiatement sans créer de fichier temporaire."""

    # 📝 **Génération du son**
    format, audio_data = generate_tts_audio(message, {"audio_output": "wav"})

    # 🔍 **Vérification**
    print(f"🎧 **Format généré** : {format}")
    print(f"📂 **Taille des données** : {len(audio_data)} octets")

    # 🎵 **Lecture en mémoire sans fichier temporaire**
    try:
        wave_obj = sa.WaveObject.from_wave_read(wave.open(io.BytesIO(audio_data), "rb"))
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Attendre la fin de la lecture
        print(f"✅ Lecture du message terminée !")
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du son : {e}")