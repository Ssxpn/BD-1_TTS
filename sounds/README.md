### 🔉 Sound System

All sounds have been classified into **three main sound families** to match BD-1’s vocal patterns:

- **Beep** → short and punchy electronic beeps  
- **Sifflement** *(French for “whistle”)* → airy, high-pitched hisses or slides  
- **Piano** → melodic or multitonal beeps (resembling musical tones)

---

To achieve this, we first **removed all vowels** and kept only **consonants**, which were then mapped to one of the three families based on how they sound phonetically in speech:

| Family         | Letters                      |
|----------------|------------------------------|
| **Beep (B)**     | b, p, d, t, k, g, q, c         |
| **Sifflement (S)** | s, z, f, v, j, x, h           |
| **Piano (P)**      | l, m, n, r                    |

---

Each sound file in the library was then **manually reviewed** 🎧.  
Some clips clearly express **emotional nuances** — like distorted metal crashes, rising tones, or sad descending beeps — which allowed us to associate not only a **letter group** (e.g. `BSP`) but also a fitting **emotion** (e.g. `happy`, `sad`, `angry`).

> ✅ This means that for any combination of letter patterns and emotional tone, we can pick from multiple matching sound files at runtime — adding variety and personality to BD-1’s responses.

### Folder Architecture
- **`consonnes/`**: Individual letter sounds.
- **`emotions/{emotion}/`**: Emotion-based folders for single-letter sounds.
- **`compositions/{length} caractères/{type}/emotion/`**: Multi-letter sound chunks (e.g. `BPS` for Beep-Piano-Sifflement).
- All sound file selection is **contextual**, based on **emotion** and **letter groups**.