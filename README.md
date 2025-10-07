# Language Tutor 🚀

A current solution is a language tutor that drills via using **Text-to-Speech (TTS)** and **Whisper (STT)** to provide a phrase in a language (French currently), and then get the user to repeat it back. The script figures out what it thought was said and provides a comparison. The current version uses a **CSV configuration file** as a seed for phrases.

This project builds on [https://github.com/maudoin/ollama-voice](https://github.com/maudoin/ollama-voice) and [https://github.com/apeatling/ollama-voice-mac](https://github.com/apeatling/ollama-voice-mac), which provides end-to-end AI responses via audio.

Code built by gemini.google.com.

---

## Prerequisites

Ensure you have the following installed on your system:

* **Python 3.x** (We recommend Python 3.9 or newer).
* **Git** (for cloning the repository).
* **A Microphone** (digital I2S mic required for Raspberry Pi).

---

## 🛠️ Installation & Setup

This guide covers setup for both **macOS/Linux** and **Raspberry Pi OS (Debian)**.

### 1. Clone the Repository

Open your terminal and clone the project:

```bash
git clone [https://github.com/ITDiscovery/Language-Tutor.git](https://github.com/ITDiscovery/Language-Tutor.git)
cd Language-Tutor
```

2. 🎤 Hardware Setup (Raspberry Pi Audio)

This project requires a digital I2S microphone for reliable audio input on the Raspberry Pi.

I2S Microphone Installation

You need an SPH0645LM4H or similar I2S Microphone. Connect the microphone to your Raspberry Pi's GPIO pins as follows:

Mic Pin	RPi Pin	RPi GPIO	Function
3.3V	Pin 1	3.3V	Power
GND	Pin 6	GND	Ground
SEL	Pin 6	GND	Select (Set to Low/Ground for 1-channel mode)
BCLK	Pin 12	GPIO 18	Bit Clock
LRCL	Pin 35	GPIO 19	Left/Right Clock
DOUT (mic)	Pin 38	GPIO 20	Data Out

💻 System Dependencies

RaspberryPi OS (Critical for audio libraries (ALSA) and compiling Python packages like PyAudio. We also include python3-venv to ensure venv is available).

```bash
sudo apt update
sudo apt install -y alsa-utils portaudio19-dev espeak-ng libespeak-ng1 python3-venv
```

macOS / Linux (General)	
No special system dependencies are usually required. Proceed to Step 3.	portaudio dependencies may be required if PyAudio installation fails (e.g., brew install portaudio on Mac or sudo apt install libasound-dev on Debian/Ubuntu).

3. Create and Activate the Virtual Environment
Create a Python virtual environment named .venv to isolate the project's dependencies, then activate it.

Create venv	python3 -m venv .venv	
This creates a .venv directory in your project folder.
Activate venv	source .venv/bin/activate	Your command prompt should now show (.venv) at the beginning.

4. Install Project Dependencies
With the virtual environment active (look for (.venv) in your prompt), install the required packages.
```bash
pip install -r requirements.txt
```

5. Run the Project
You can now run the application's main script.

Bash
# Ensure you are still inside the active virtual environment: (.venv)
python your_main_script_name.py

6. Deactivate the Virtual Environment
When you're finished working on the project, exit the environment:

```Bash
deactivate
```

Usage
Add usage instructions here, including code snippets or commands.
