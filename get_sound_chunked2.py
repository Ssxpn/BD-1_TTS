def get_sound_chunked(message, emotion="neutre", max_chunk=4):
    mapped = map_letters_to_sound_groups(message)
    i = 0
    results = []
    used_variants = set()
    emotion_or=emotion

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
                print(f"🔸 Aucun chunk valide, fallback avec get_sound() sur '{original_char}'")
                emotion_folder = os.path.join(EMOTIONS_DIR, emotion_or)
                path = get_random_variant(emotion_folder, original_char, used_variants)
                used_emotion = emotion_or

                if not path:
                    path = get_random_variant(CONSONNES_DIR, original_char, used_variants)
                    used_emotion = "neutre"

                if path:
                    print(f"✅ Fichier trouvé (1 lettre) : {path}")
                    used_variants.add(os.path.basename(path))
                    results.append((path, used_emotion, 1, original_char))
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
                SOUNDS_DIR, "compositions", f"{chunk_len}_caracteres", pattern, emotion
            )

            print(f"\n🔍 Chunk : {''.join(chunk)} → Dossier : {folder_path}")
            print(f"🔎 Fichier attendu : {expected_filename}")

            path = get_random_variant(folder_path, prefix, used_variants)

            if not path and emotion != "neutre":
                print(f"⚠️ Rien trouvé pour {emotion}, on tente 'neutre'.")
                folder_path = os.path.join(
                    SOUNDS_DIR, "compositions", f"{chunk_len}_caracteres", pattern, "neutre"
                )
                print(f"📁 Dossier fallback : {folder_path}")
                print(f"🔎 Fichier attendu : {expected_filename}")
                path = get_random_variant(folder_path, prefix, used_variants)
                if path:
                    emotion = "neutre"

            if path:
                print(f"✅ Fichier trouvé : {path}")
                used_variants.add(os.path.basename(path))
                results.append((path, emotion, chunk_len, message[i:i+chunk_len]))
                i += chunk_len
                break
        else:
            print(f"❌ Aucun son trouvé pour : {mapped[i]}")
            i += 1

    return results