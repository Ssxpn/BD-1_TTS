import os
import shutil
from pydub import AudioSegment

# 🔹 Forcer `pydub` à utiliser `ffmpeg` au lieu de `audioop`
AudioSegment.converter = "C:/ffmpeg/bin/ffmpeg.exe"  # Chemin de ton `ffmpeg.exe`
AudioSegment.ffprobe = "C:/ffmpeg/bin/ffprobe.exe"

# 🔹 Vérifier que `ffmpeg` est bien trouvé
if not os.path.isfile(AudioSegment.converter):
    raise FileNotFoundError("❌ FFmpeg introuvable ! Assure-toi que `ffmpeg.exe` est installé dans `C:/ffmpeg/bin/`")

# 🔹 Forcer pydub à utiliser ffmpeg
AudioSegment.converter = "C:/ffmpeg/bin/ffmpeg.exe"  # Mets le bon chemin vers ffmpeg.exe

# 🔹 Optionnel : Spécifier ffprobe si nécessaire
AudioSegment.ffprobe = "C:/ffmpeg/bin/ffprobe.exe"

# 🔹 Vérification que ffmpeg est bien trouvé
if not os.path.isfile(AudioSegment.converter):
    raise FileNotFoundError("FFmpeg introuvable. Vérifie que ffmpeg.exe est bien installé dans C:/ffmpeg/bin/")

# Forcer l'utilisation de ffmpeg
AudioSegment.converter = "C:/ffmpeg/bin/ffmpeg.exe"

# 📂 Définition des chemins des dossiers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMPRESSED_DIR = os.path.join(BASE_DIR, "sounds", "compressed")
WITHOUT_DUPLICATE_DIR = os.path.join(BASE_DIR, "sounds", "Withoutduplicate")

# 🗑️ Supprimer le dossier Withoutduplicate s'il existe
if os.path.exists(WITHOUT_DUPLICATE_DIR):
    print("🗑️ Suppression de l'ancien dossier 'Withoutduplicate/'...")
    shutil.rmtree(WITHOUT_DUPLICATE_DIR)

# 📂 Créer le dossier Withoutduplicate s'il n'existe pas
os.makedirs(WITHOUT_DUPLICATE_DIR, exist_ok=True)

# 📋 Liste des fichiers de compressed/
audio_files = [f for f in os.listdir(COMPRESSED_DIR) if f.endswith(".wav")]
audio_files.sort()  # Trie les fichiers pour un traitement dans l'ordre

# 📊 Liste des sons déjà ajoutés (avec leur contenu pour comparaison)
unique_sounds = []
file_map = {}  # Dictionnaire pour suivre les fichiers renommés

def is_duplicate(new_audio, existing_audios):
    """Vérifie si un son est déjà présent dans la liste unique."""
    for existing_audio in existing_audios:
        # Vérification simple : même durée et presque même contenu
        if abs(len(new_audio) - len(existing_audio)) < 50:  # Tolérance sur la longueur
            if new_audio.raw_data[:1000] == existing_audio.raw_data[:1000]:  # Compare les 1000 premiers octets
                return True
    return False

# 🏁 Processus de filtrage des doublons
index = 1
for file in audio_files:
    input_path = os.path.join(COMPRESSED_DIR, file)

    # Charger le fichier audio
    audio = AudioSegment.from_wav(input_path)

    # Vérifier si c'est un doublon
    duplicate_index = None
    for i, existing_audio in enumerate(unique_sounds, start=1):
        if is_duplicate(audio, [existing_audio]):
            duplicate_index = i
            break

    if duplicate_index:
        # 🔄 C'est un doublon, on nomme "X.Y.wav"
        new_filename = f"{duplicate_index}.1.wav"
        existing_files = [f for f in os.listdir(WITHOUT_DUPLICATE_DIR) if f.startswith(f"{duplicate_index}.")]

        if existing_files:
            suffixes = [int(f.split(".")[1]) for f in existing_files if f.count(".") == 2]
            max_suffix = max(suffixes) if suffixes else 1  # ✅ Evite l'erreur si la liste est vide
            new_filename = f"{duplicate_index}.{max_suffix + 1}.wav"
        else:
            new_filename = f"{duplicate_index}.1.wav"  # ✅ Première duplication

    else:
        # ✅ C'est un nouveau son, on lui donne un numéro unique
        new_filename = f"{index}.wav"
        unique_sounds.append(audio)  # Ajouter le son à la liste des uniques
        index += 1

    # Copier/Renommer le fichier dans Withoutduplicate/
    output_path = os.path.join(WITHOUT_DUPLICATE_DIR, new_filename)
    shutil.copy(input_path, output_path)
    print(f"🎵 {file} ➝ {new_filename}")

print("🚀 Suppression des doublons terminée, les fichiers sont dans 'Withoutduplicate/'.")