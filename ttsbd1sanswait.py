import random
import os
import wave
import simpleaudio as sa

# Dossier principal des sons
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_PATH = os.path.join(BASE_DIR, "sounds", "compressed")

# Dossiers pour chaque type de son
SOUND_DIRECTORIES = {
    "affirmation": os.path.join(SOUND_PATH, "01_Happy_Thrilled"),
    "negation": os.path.join(SOUND_PATH, "04_Sadness_Deception"),
    "question": os.path.join(SOUND_PATH, "03_Surprise_Questionning"),
    "surprise": os.path.join(SOUND_PATH, "03_Surprise_Questionning"),
    "neutral": os.path.join(SOUND_PATH, "10_Neutral"),
}

# Charger tous les fichiers WAV une seule fois au démarrage
SOUND_FILES = {category: [] for category in SOUND_DIRECTORIES}

for category, folder in SOUND_DIRECTORIES.items():
    if os.path.exists(folder):
        SOUND_FILES[category] = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".wav")]

def get_random_sound(category):
    """Retourne un fichier audio aléatoire pour la catégorie donnée, ou un son neutre."""
    files = SOUND_FILES.get(category, [])
    return random.choice(files) if files else random.choice(SOUND_FILES["neutral"])

def load_wav_file(sound_file):
    """Charge un fichier WAV en mémoire et retourne les données audio."""
    with wave.open(sound_file, "rb") as wav_file:
        return (
            wav_file.readframes(wav_file.getnframes()), 
            wav_file.getnchannels(), 
            wav_file.getsampwidth(), 
            wav_file.getframerate()
        )

# Liste pour stocker les objets `play_obj` et éviter qu'ils ne soient supprimés trop tôt
active_sounds = []

def play_bd1_sound(audio_data, num_channels, bytes_per_sample, sample_rate):
    """Joue un fichier WAV préchargé sans latence et empêche la suppression prématurée."""
    play_obj = sa.play_buffer(audio_data, num_channels, bytes_per_sample, sample_rate)
    active_sounds.append(play_obj)  # Stocke l'objet pour empêcher sa suppression immédiate
    print(" Lecture en cours...")

def get_sound_category(text):
    """Détecte la catégorie du son en fonction du texte reçu."""
    SOUND_MAP = {
        "oui": "affirmation",
        "non": "negation",
        "?": "question",
        "merci": "affirmation",
        "quoi": "question",
        "super": "affirmation",
    }

    for word, category in SOUND_MAP.items():
        if word in text.lower():
            return category

    return "neutral"

# Test avec une phrase
user_input = "Oui, c'est parfait !"
category = get_sound_category(user_input)
sound_file = get_random_sound(category)

if sound_file:
    sound_data = load_wav_file(sound_file)
    play_bd1_sound(*sound_data)
else:
    print(" Aucun son disponible pour cette catégorie.")

# Attente passive pour éviter que le programme ne se ferme trop vite
input("Appuyez sur Entrée pour quitter après lecture du son...")