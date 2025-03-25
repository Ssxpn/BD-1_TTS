# BD-1 Voice Assistant Project

Welcome to the **BD-1 Voice Assistant Project**! 🎧🤖

This repository aims to build a custom **Text-to-Speech (TTS) system** that mimics the vocal style of **BD-1**, the adorable droid from *Star Wars Jedi: Fallen Order*. The TTS reacts to user input using pre-recorded BD-1 sounds that are matched to emotion and sentence structure.

![BD-1 Sound Project](https://th.bing.com/th/id/OIP.Shcaq2sc_Ovxg0BefIrLsAHaLO?rs=1&pid=ImgDetMain)

> **Work in Progress:** The TTS core is functional. Emotion detection and assistant logic are under improvement.

---

## 🎯 Project Goal

To build a **TTS system in BD-1's style**, capable of:
- Responding to user prompts using a combination of **BD-1 sounds**.
- Matching **emotion** (e.g. happy, sad, surprised) to the content of the phrase.
- **Mimicking language structure** while remaining robotic and cute.


---

## 🛠️ Current To-Do List

Here's what's left:

- Improve **emotion detection** from text input. (see `assign_emotion()` function)
- Test different styles and expressions with **more BD-1 phrases**.

---

## 🧩 Project Architecture

### 🔉 Sound System (Folder: `/sounds`)
Find more info in the Readme.md in the sounds folder.

### 🧪 Dev vs. Prod Environments

- **`text_to_speech_v0.py`** → Dev version (lots of `print()` for debugging and understanding chunk logic).
- **`text_to_speech_vX.py` (latest)** → Production-ready version, callable from other scripts without flooding logs.

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
