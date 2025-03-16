import os

# 📌 Trouver le fichier utils.py dans le venv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYDUB_UTILS_PATH = os.path.join(BASE_DIR, "venv", "Lib", "site-packages", "pydub", "utils.py")

# 🛠️ Vérifier si le fichier utils.py existe
if os.path.exists(PYDUB_UTILS_PATH):
    print(f"🔍 Modification de : {PYDUB_UTILS_PATH}")

    with open(PYDUB_UTILS_PATH, "r", encoding="utf-8") as file:
        content = file.read()

    # 🛠️ Correction des importations (supprime audioop et pyaudioop)
    content = content.replace(
        "try:\n    import audioop\nexcept ImportError:\n    import pyaudioop as audioop",
        "audioop = None  # Suppression de audioop car incompatible avec Python 3.13"
    )

    # 🛠️ Correction des expressions régulières (ajout du r'' pour éviter le warning)
    content = content.replace(
        "re.match('([su]([0-9]{1,2})p?) \\(([0-9]{1,2}) bit\\)$', token)",
        "re.match(r'([su]([0-9]{1,2})p?) \\(([0-9]{1,2}) bit\\)$', token)"
    )

    content = content.replace(
        "re.match('([su]([0-9]{1,2})p?)( \\(default\\))?$', token)",
        "re.match(r'([su]([0-9]{1,2})p?)( \\(default\\))?$', token)"
    )

    content = content.replace(
        "re.match('(flt)p?( \\(default\\))?$', token)",
        "re.match(r'(flt)p?( \\(default\\))?$', token)"
    )

    content = content.replace(
        "re.match('(dbl)p?( \\(default\\))?$', token)",
        "re.match(r'(dbl)p?( \\(default\\))?$', token)"
    )

    # 📝 Réécrire le fichier modifié
    with open(PYDUB_UTILS_PATH, "w", encoding="utf-8") as file:
        file.write(content)

    print("✅ Modification de `pydub/utils.py` terminée !")
else:
    print("❌ Erreur : Le fichier `pydub/utils.py` n'a pas été trouvé dans le venv.")