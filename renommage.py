import os
import librosa

# 📂 Définition du dossier contenant les fichiers audio
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMPRESSED_DIR = os.path.join(BASE_DIR, "sounds", "compressed")

# 🛠️ Fonction pour obtenir la durée d'un fichier audio
def get_audio_duration(file_path):
    try:
        y, sr = librosa.load(file_path, sr=None)
        return round(librosa.get_duration(y=y, sr=sr), 2)  # Arrondi à 2 décimales
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de {file_path}: {e}")
        return None  # Retourne None si une erreur survient

# 🔄 Parcours des fichiers dans le dossier `compressed/`
renamed_files = []
compressed_files = [f for f in os.listdir(COMPRESSED_DIR) if f.endswith(".wav")]

for file in compressed_files:
    file_path = os.path.join(COMPRESSED_DIR, file)

    # Récupérer la durée du fichier
    duration = get_audio_duration(file_path)

    if duration is not None:
        # 🏷️ Créer le nouveau nom du fichier
        new_name = f"{duration}s - {file}"
        new_path = os.path.join(COMPRESSED_DIR, new_name)

        # ⚠️ Vérifier si le fichier a déjà été renommé
        if os.path.exists(new_path):
            print(f"⚠️ Fichier déjà renommé : {new_name}")
            continue

        # 🔄 Renommer le fichier
        os.rename(file_path, new_path)
        renamed_files.append((file, new_name))
        print(f"✅ {file} ➝ {new_name}")

# 📋 Afficher un résumé des fichiers renommés
if renamed_files:
    print(f"\n✅ {len(renamed_files)} fichiers renommés :")
    for old_name, new_name in renamed_files:
        print(f" - {old_name} ➝ {new_name}")
else:
    print("✅ Aucun fichier à renommer, tout est OK !")

print("🚀 Renommage terminé.")