# BD-1 Voice Assistant Project

Welcome to the **BD-1 Voice Assistant Project**! 🎧🤖

This repository aims to build a custom **Text-to-Speech (TTS) system** that mimics the vocal style of **BD-1**, the adorable droid from *Star Wars Jedi: Fallen Order*. The TTS reacts to user input using pre-recorded BD-1 sounds that are matched to emotion and sentence structure.

![BD-1 Sound Project](https://th.bing.com/th/id/OIP.Shcaq2sc_Ovxg0BefIrLsAHaLO?rs=1&pid=ImgDetMain)

> **Work in Progress:** The TTS core is functional. Emotion detection and assistant logic are under improvement.

---

## Project Goal

To build a **TTS system in BD-1's style**, capable of:
- Responding to user prompts using a combination of **BD-1 sounds**.
- Matching **emotion** (e.g. happy, sad, surprised) to the content of the phrase.
- **Mimicking language structure** while remaining robotic and cute.


---

## Current To-Do List

Here's what's left:

- Improve **emotion detection** from text input. (see `assign_emotion()` function)
- Test different styles and expressions with **more BD-1 phrases**.
- Find a way to make BD-1's sentence shorter and keeping a "grammatical" sens

---

## 📂 Folder Structure

```bash
BD-1-Conversationnal-AI/
├── text_to_speech_v0.py       # Core logic for BD-1 voice synthesis
├── text_to_speech_vX.py       # (latest)** → Production-ready version, callable from other scripts without flooding logs.
├── test.py                    # Main script to test BD-1 voice playback
├── sounds/                    # Find more info in the Readme.md in the sounds folder.
│   ├── consonnes/             # Raw consonant sounds (neutral)
│   ├── emotions/              # Same sounds, sorted by emotion (happy, sad, etc.)
│   └── compositions/          # Multi-letter chunks classified by sound families and emotion
└── temp_tts.wav               # Temporary output file
```

## Functional Breakdown (text_to_speech_vX.py)

### tts_bd1(message: str)
  Main entry point to play a complete BD-1 response.

  - Splits full message into emotional phrases
  - Calls generate_tts_audio() per phrase
  - Assembles and plays final audio

### process_message_by_phrases(message: str)
  Splits the text into short sentences using ., !, ? and detects emotion per phrase.

  - Returns a list of (phrase, emotion).
  - assign_emotion(phrase: str)

  Rules-based emotion classifier:
  |            Keyword         | Emotion                      |
  |----------------------------|------------------------------|
  |      **?**                 | Question                     |
  |      **!**                 | Surprise                     |
  | **Keywords like non**      | negatif                      |
  | **Keywords like oui**      | positif                      |
  | **Keywords like triste**   | triste (sad)                 |
  |        **Else**            | neutre (neutral)             |


# REPRENDRE ICI

decompose_message(message: str)

Extracts consonants by syllable:

Removes vowels and accents

Only keeps consonants followed by vowels

Groups leading consonants (e.g. dr, gn, mp)

Discards words of length ≤ 4 unless exception

Returns a cleaned list of consonants.

map_letters_to_sound_groups(text: list[str])

Converts consonants to families:

B = Beep

S = Sifflement

P = Piano

get_sound_chunked(consonnes, emotion)

Core of audio matching logic.

Tries longest chunks (4 → 3 → 2 → 1)

Uses folders like:

sounds/compositions/3 caracteres/Beep Piano Sifflement/positif

Fallback:

Same chunk in neutre

Then letter-level fallback with get_sound()

Ensures no .wav is used twice

Returns list of (path, emotion, chunk_length, original_chars)

get_sound(consonne, emotion)

Fallback sound lookup:

Tries in sounds/emotions/{emotion}/

If not found, tries sounds/consonnes/

generate_tts_audio(message: str, options)

Assembles final audio from selected chunks:

Uses AudioSegment.from_wav

Displays full table of sound matches

Returns in-memory WAV file

🎤 What Happens Step-by-Step

Suppose the message is:

"Je peux parler librement ! Non pas content ! Triste."

1. tts_bd1() calls process_message_by_phrases()

Breaks into:

Phrase 1: "Je peux parler librement !" → surprise

Phrase 2: "Non pas content !" → surprise

Phrase 3: "Triste." → negatif

2. For each phrase:

generate_tts_audio() is called

3. decompose_message() extracts consonants

Keeps only relevant syllables (e.g., pr, tr, pl)

4. get_sound_chunked() looks for sound files

Tries biggest matching chunk (4 to 1)

Fallback if needed

Prevents sound reuse

5. Files are combined

With pydub.AudioSegment, then played with simpleaudio

---

## License

This project is **community-driven** and intended for **non-commercial and fan-based use only**.  
Please verify individual file licenses before using them.

---

## Thanks

Special thanks to:  
- **[vigonotion/tts.astromech](https://github.com/vigonotion/tts.astromech)** for inspiring this project!  
- **[BD-1 Sound Database Spreadsheet](https://docs.google.com/spreadsheets/d/1isG7yhRa6qXGd1NMjFjuTrLWa93BwfY8t4Y0y8e7ufs/edit?pli=1&gid=541004497#gid=541004497)** for helping navigate the game’s audio files.  

---

**Thank you for your help! May the Force be with you.** 

## Join the Mission

To contribute:
1. **Fork this repo**
2. Tweak or add functionality
3. Submit a **pull request**

Let’s bring BD-1 to life – together! 💬🔊✨
