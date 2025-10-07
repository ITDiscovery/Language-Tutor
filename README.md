
# Language Tutor

A current solution is a language tutor that drills via using **Text-to-Speech (TTS)** and **Whisper (STT)** to provide a phrase in a language (French currently), and then get the user to repeat it back. The script figures out what it thought was said and provides a comparison. The current version uses a **CSV configuration file** as a seed for phrases.

This project builds on [https://github.com/maudoin/ollama-voice](https://github.com/maudoin/ollama-voice) and [https://github.com/apeatling/ollama-voice-mac](https://github.com/apeatling/ollama-voice-mac), which provides end-to-end AI responses via audio.

Code built by gemini.google.com.

---

## 🎤 Hardware Setup (Raspberry Pi Audio)

This project requires a digital I2S microphone for reliable audio input on the Raspberry Pi.

### I2S Microphone Installation

You need an **SPH0645LM4H** or similar I2S Microphone. Connect the microphone to your Raspberry Pi's GPIO pins as follows:

| Mic Pin | RPi Pin | RPi GPIO | Function |
| :--- | :--- | :--- | :--- |
| **3.3V** | Pin 1 | 3.3V | Power |
| **GND** | Pin 6 | GND | Ground |
| **SEL** | Pin 6 | GND | Select (Set to Low/Ground for 1-channel mode) |
| **BCLK** | Pin 12 | GPIO 18 | Bit Clock |
| **LRCL** | Pin 35 | GPIO 19 | Left/Right Clock |
| **DOUT (mic)**| Pin 38 | GPIO 20 | Data Out |

---

## 🛠️ Installation Instructions

These instructions are specifically tailored for **Raspberry Pi OS (Debian)** and ensure all dependencies for Piper (TTS) and Whisper (STT) are correctly installed.

### 1. System Dependencies (ALSA & Audio Libraries)

Install the necessary low-level audio libraries. This is critical for preventing audio recording errors and enabling Python packages to compile correctly.

```bash
# Update package list and install necessary dependencies
sudo apt update
sudo apt install -y alsa-utils portaudio19-dev espeak-ng libespeak-ng1
