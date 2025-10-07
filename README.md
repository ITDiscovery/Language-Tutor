Language Tutor:
A current solution is a language tutor that drills via using TTS and Whisper to provide a phrase in a language (French currently), 
and then get the user to repeat it back. The script figures out what it thought was said and provide a comparison. The current version
uses a CSV configuration file as a seed for phrases. 

This builds on https://github.com/maudoin/ollama-voice and https://github.com/apeatling/ollama-voice-mac which provides end to end AI responses via audio.

Code built by gemini.google.com.

Installation instructions:

Microphone install first:
You need an SPH0645LM4H or similar I2S Microphone. 
3.3V → 3.3V (Pi pin 1)
GND → GND (Pi pin 6)
SEL → GND (Pi pin 6)
BCLK → GPIO 18 (Pi pin 12)
LRCL → GPIO 19 (Pi pin 35)
DOUT (mic) → GPIO 20 (Pi pin 38) 

In the /boot/firmware/config.txt file add:
dtparam=i2s=on
dtoverlay=googlevoicehat-soundcard

In the /etc/modules file add:
snd-bcm2835
snd-soc-bcm2835

Test via:
arecord -D plughw:2,0 -c1 -r 44100 -f S32_LE -t wav -d 5 test.wav

Playback via:
aplay -D plughw:0,0 test.wav

Change the swap size:
sudo nano /etc/rpi/swap.conf
MaxSizeMiB=2048

sudo apt-get install libportaudio2
pip install sounddevice
sudo apt-get install ffmpeg
pip install -U openai-whisper

sudo apt-get install alsa-utils
