import random
import time
import subprocess
import os
import numpy as np
import sounddevice as sd
import whisper
import logging
import wave
import csv
import warnings
import sys
import select
# NEW: Import the Piper voice modules
from piper import PiperVoice

# --- CONFIGURATION ---
MODEL_NAME = "small"
LANGUAGE = "French"     # Language code for Whisper
SAMPLE_RATE = 44100     # Standard audio sample rate
PIPER_MODEL_SAMPLE_RATE = 22050 # NEW: Correct rate for UPMC French model
TEMP_AUDIO_FILE = "/tmp/tutor_user_recording.wav"
TUTOR_CONTENT_FILE = "tutor_content.csv"

# --- PIPER TTS CONFIGURATION ---
# Absolute paths to the downloaded UPMC voice model files
PIPER_MODEL_PATH = "/home/pi/.local/share/piper-tts/piper-voices/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx"
PIPER_CONFIG_PATH = "/home/pi/.local/share/piper-tts/piper-voices/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx.json"
JESSICA_ID = 0 # Female voice
PIERRE_ID = 1  # Male voice

# VVVV CHANGE SPEAKER HERE VVVV
# Set this to JESSICA_ID (0) or PIERRE_ID (1) to select the voice gender.
PIPER_SPEAKER_ID = JESSICA_ID
# ^^^^ CHANGE SPEAKER HERE ^^^^

# Global variables to hold content and the Piper voice object
TUTOR_CONTENT = []
PIPER_VOICE = None

# --- ANSI Color Codes for Output ---
BLUE = '\033[94m'
RED = '\033[91m'
WHITE = '\033[97m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
ENDC = '\033[0m'

# --- Content Loading Function ---
def load_tutor_content(file_path):
    """
    Reads the tutor content from a CSV file and returns it as a list of dictionaries.
    Keys are derived from the CSV header (text, source, translation, notes).
    """
    content_list = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            # csv.DictReader maps the headers to the dictionary keys
            reader = csv.DictReader(file)
            for row in reader:
                content_list.append(row)
        print(f"✅ Loaded {len(content_list)} phrases from {file_path}")
        return content_list
    except FileNotFoundError:
        print(f"FATAL: Content file not found: {file_path}")
        return []
    except Exception as e:
        print(f"FATAL: Error loading content from CSV: {e}")
        return []


# --- Helper Function for Comparison ---

def get_highlighted_comparison(expected, actual):
    """
    Compares the expected phrase against the actual transcription,
    highlighting differences using ANSI colors (green for match, red for error).
    """

    # Simple tokenization and normalization (remove punctuation, lowercase)
    expected_words = expected.lower().replace("'", " ").replace(",", "").replace("?", "").split()
    actual_words = actual.lower().replace("'", " ").replace(",", "").replace("?", "").split()
    
    highlighted_actual = []
    
    # Use the shorter length for direct comparison
    min_len = min(len(expected_words), len(actual_words))
    
    for i in range(min_len):
        e_word = expected_words[i]
        a_word = actual_words[i]
        
        if e_word == a_word:
            # Word matches, use green
            highlighted_actual.append(f"{GREEN}{a_word}{ENDC}")
        else:
            # Word does not match expected word at this position, use red
            highlighted_actual.append(f"{RED}{a_word}{ENDC}")
            
    # Handle extra words in the actual transcription (mark as error)
    if len(actual_words) > min_len:
        for i in range(min_len, len(actual_words)):
            extra_word = actual_words[i]
            highlighted_actual.append(f"{RED}{extra_word}{ENDC}")

    # Reconstruct the string
    return " ".join(highlighted_actual)


# --- TTS & Audio Recording Functions ---
def play_audio_file(file_path):
    """Uses the Linux 'aplay' command to play a local audio file."""
    try:
        logging.info(f"Playing audio file: {file_path}")
        subprocess.run(['aplay', file_path], check=True) 
        time.sleep(0.5)
    except subprocess.CalledProcessError as e:
        print(f"Error calling 'aplay' command. File not played: {file_path}. Error: {e}")
        print("Ensure the audio file exists and is accessible, and 'alsa-utils' is installed.")

# --- TTS & Audio Recording Functions ---
def play_audio_file(file_path):
    """Uses the Linux 'aplay' command to play a local audio file."""
    try:
        logging.info(f"Playing audio file: {file_path}")
        subprocess.run(['aplay', file_path], check=True) 
        time.sleep(0.5)
    except subprocess.CalledProcessError as e:
        print(f"Error calling 'aplay' command. File not played: {file_path}. Error: {e}")
        print("Ensure the audio file exists and is accessible, and 'alsa-utils' is installed.")

# --- TTS & Audio Recording Functions ---
def play_audio_file(file_path):
    """Uses the Linux 'aplay' command to play a local audio file."""
    try:
        logging.info(f"Playing audio file: {file_path}")
        subprocess.run(['aplay', file_path], check=True) 
        time.sleep(0.5)
    except subprocess.CalledProcessError as e:
        print(f"Error calling 'aplay' command. File not played: {file_path}. Error: {e}")
        print("Ensure the audio file exists and is accessible, and 'alsa-utils' is installed.")

def speak_text(text, output_filename="/tmp/tutor_speak.wav"):
    """
    Uses the global PiperVoice model to speak the text in the selected speaker's voice.
    """
    global PIPER_VOICE

    if PIPER_VOICE is None:
        print("FATAL: Piper voice model is not loaded.")
        return

    try:
        logging.info(f"Generating audio for: {text}")

        # 1. SPEAKER LOGIC for 1.3.0: Set the speaker ID on the voice object before synthesis.
        PIPER_VOICE.speaker_id = PIPER_SPEAKER_ID 
        
        # 2. Use PiperVoice to synthesize the audio bytes (FIXED: Join and Extract from AudioChunk)
        audio_generator = PIPER_VOICE.synthesize(text)
        
        # Join all audio chunks, extracting the raw bytes using the definitive property (.audio_int16_bytes)
        audio_bytes = b"".join(chunk.audio_int16_bytes for chunk in audio_generator) 

        # 3. Determine the Sample Rate (Fallbacks remain necessary)
        try:
            sample_rate = PIPER_VOICE.config.audio.sample_rate
        except AttributeError:
            sample_rate = 22050 
        
        # 4. Write the raw audio bytes to a proper WAV file
        with wave.open(output_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2) # 16-bit audio (2 bytes)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_bytes)
        
        # 5. Use aplay to play the generated WAV file
        # FIX: Open os.devnull and pass it to subprocess to silence the "Playing WAVE..." output.
        with open(os.devnull, 'w') as devnull:
            subprocess.run(
                ['aplay', output_filename],
                check=True,
                stdout=devnull, 
                stderr=devnull
            )
        time.sleep(0.5)

    except Exception as e:
        print(f"Error generating audio with Piper: {e}")

    finally:
        # Clean up the temporary file
        if os.path.exists(output_filename):
            os.remove(output_filename)

def present_phrase(source): # Removed 'voice_name' argument
    """
    Presents the content. If 'source' is a file path, it plays the file.
    Otherwise, it uses TTS (Piper) to speak the content.
    """
    # 1. Speak the instruction (Répétez)
    speak_text("Répétez")
    
    # 2. Present the source content
    if isinstance(source, str) and os.path.exists(source):
        play_audio_file(source)
    elif isinstance(source, str):
        speak_text(source)
    else:
        print(f"Error: Unknown content source type or file not found: {source}")

def record_audio(blue_color, red_color, filename=TEMP_AUDIO_FILE):
    """
    Records audio from the default microphone and saves it as a WAV file.
    Uses push-to-talk style recording (Press ENTER to start, ENTER to stop).
    Returns a tuple (filename, duration) or None on failure.
    """

    global SAMPLE_RATE 

    # Define a generous maximum recording duration
    max_duration = 10  
    
    # Wait for the user to press ENTER to start
    # FIX: Using the passed color arguments
    input(f"{blue_color}Press ENTER to START recording your phrase...{ENDC}")
    print(f"{red_color}Recording... Press ENTER again to STOP.{ENDC}")

    # Start a non-blocking stream for continuous recording until interrupted
    stream = sd.InputStream(samplerate=SAMPLE_RATE, 
                            channels=1, # CRITICAL FIX: Set to 1 channel (mono)
                            dtype='int16')
    stream.start()
    
    # Store audio data in a list
    audio_data = []
    start_time = time.time()

    # Wait for the user to press ENTER again or reach max duration
    try:
        # Use select to wait for input on stdin without blocking the loop entirely
        while not select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []) and (time.time() - start_time) < max_duration:
             # Read data in small blocks
            try:
                data, overflowed = stream.read(1024)
                audio_data.append(data.copy())
            except sd.PortAudioError as e:
                 # Handle common recording errors gracefully
                print(f"Error during audio streaming: {e}")
                stream.close()
                return None
        
        # Stop the stream when ENTER is pressed or max duration reached
        stream.stop()

    except Exception as e:
        print(f"Error during audio streaming: {e}")
        return None

    finally:
        if stream.active:
            stream.stop()
        if stream.stopped == False:
            stream.close()

    print("--------------------------------------------------")

    # If no audio data was recorded (user hit enter too fast or error)
    if not audio_data:
        return None

    # Concatenate the audio blocks into a single NumPy array
    recording = np.concatenate(audio_data, axis=0)

    # Calculate duration
    audio_duration = recording.shape[0] / SAMPLE_RATE

    # Save the NumPy array to a WAV file
    try:
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1) # Must match the recording channel count
            wf.setsampwidth(2) # 16-bit audio (2 bytes)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(recording.tobytes())
        
        print(f"✅ Recording saved to {filename} ({audio_duration:.2f} seconds)")
        return filename, audio_duration # RETURNS FILENAME AND DURATION
    
    except Exception as e:
        print(f"Error saving audio file: {e}")
        return None

def transcribe_audio(audio_file, model, language, prompt_text, audio_duration): 
    """
    Transcribes the given audio file using the Whisper model, measures RTF, and 
    uses an initial prompt for improved accuracy.
    
    Returns: A tuple (transcribed_text, transcribe_time, rtf)
    """
    
    # We use logging.info here to keep the main console clean
    logging.info(f"Starting transcription for {audio_file}")

    print("Transcribing audio with Whisper...Please Wait!")

    start_time = time.time()
    
    # Transcribe the audio
    # The 'initial_prompt' guides the model toward the expected phrase, boosting accuracy.
    result = model.transcribe(
        audio_file, 
        language=language,
        initial_prompt=prompt_text
    )
    
    end_time = time.time()
    
    # Calculate transcription time and RTF
    transcribe_time = end_time - start_time
    
    # Check to prevent division by zero in case of an extremely short audio file
    if audio_duration > 0:
        rtf = transcribe_time / audio_duration
    else:
        rtf = float('inf') # Set RTF to infinity if duration is zero

    # Print the speed metrics (STAYS HERE as the variables are in scope)
    print(f"⏱️ Transcription Time: {transcribe_time:.2f} seconds (RTF: {rtf:.2f})")
    
    # NEW RETURN: Return the text AND the calculated speed metrics
    return result["text"], transcribe_time, rtf

def main():
    """The main language practice loop."""
    global TUTOR_CONTENT
    global PIPER_VOICE # Declare global for assignment

    warnings.filterwarnings("ignore", category=UserWarning)

    print("--- French Pronunciation & Listening Tutor ---")

# --- Main Application Loop ---
def main():
    """The main language practice loop."""
    global TUTOR_CONTENT
    global PIPER_VOICE 
    
    # Define colors here (or ensure they are defined globally)
    BLUE = '\033[94m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m' 

    # Suppress warnings that come from the Whisper library during transcription
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)

    print("--- French Pronunciation & Listening Tutor ---")
    
    # --- LOAD PIPER VOICE ---
    try:
        print("Loading Piper Voice Model...")
        PIPER_VOICE = PiperVoice.load(
            PIPER_MODEL_PATH, 
            PIPER_CONFIG_PATH
        )
        
        speaker_name = "Jessica" if PIPER_SPEAKER_ID == JESSICA_ID else "Pierre"
        print(f"✅ Piper Model loaded successfully with speaker: {speaker_name}")
    except Exception as e:
        print(f"FATAL: Could not load Piper voice model. Error: {e}")
        print("Ensure your MODEL_PATH and CONFIG_PATH variables are correct.")
        return

    # --- LOAD CONTENT ---
    TUTOR_CONTENT = load_tutor_content(TUTOR_CONTENT_FILE)
    if not TUTOR_CONTENT:
        print("\nFATAL: Could not load tutor content. Exiting.")
        return
        
    print(f"Loading Whisper model: {MODEL_NAME}...")
    try:
        model = whisper.load_model(MODEL_NAME)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"FATAL: Could not load Whisper model. Error: {e}")
        print("Ensure 'pip install whisper' was successful.")
        return

    input("Press Enter to start the first practice session...")
    
    # Main game loop
    while True:
        # 1. Select and announce the phrase
        phrase_data = random.choice(TUTOR_CONTENT)
        
        correct_phrase = phrase_data['text']
        notes = phrase_data['notes']
        translation = phrase_data['translation']

        # --- PHRASE ANNOUNCEMENT OUTPUT (Themed) ---
        print("\n" * 2)
        print("=" * 50)
        print(f"{BLUE}Phrase to Repeat:{ENDC} '{correct_phrase}'")
        print(f"{RED}What you Hear:{ENDC} {notes}")
        print(f"{WHITE}What it Means:{ENDC} {translation}")
        print("=" * 50)
        
        # Present the phrase (TTS)
        speak_text(correct_phrase) 
        
        # 2. Record user's attempt using PTT
        result_tuple = record_audio(BLUE, RED) 

        # Handle recording failure
        if result_tuple is None:
            print(f"{WHITE}❌ Recording failed or was empty. Skipping transcription.{ENDC}") 
            continue

        # UNPACK FILENAME AND DURATION
        audio_file, audio_duration = result_tuple 

        # 3. Transcribe and compare
        # FIX: UNPACK ALL THREE RETURN VALUES (text, time, rtf)
        user_transcription, transcribe_time, rtf = transcribe_audio(audio_file, model, LANGUAGE, correct_phrase, audio_duration)
        
        
        # --- CLEANED UP RESULTS OUTPUT ---
        
        # 3a. Simple normalization for robust comparison
        import re
        target_normalized = re.sub(r'[^\w\s]', '', correct_phrase).lower().strip()
        user_normalized = re.sub(r'[^\w\s]', '', user_transcription).lower().strip()
        
        if user_normalized == target_normalized:
            accuracy_color = GREEN
            feedback = "PERFECT! (Match)"
        else:
            accuracy_color = YELLOW
            feedback = "MISMATCH: Check your pronunciation."

        # 3b. Print the results block
        print("\n" + "=" * 50)
        
        # Print speed metrics (Variables are now defined due to the unpacking above)
        print(f"{WHITE}⏱️ Transcription Time: {transcribe_time:.2f} seconds (RTF: {rtf:.2f}){ENDC}")
        print("-" * 50)
        
        print(f"{WHITE}WHISPER HEARD:{ENDC} {accuracy_color}{user_transcription}{ENDC}") 
        print(f"{accuracy_color}{feedback}{ENDC}")
        print("=" * 50 + "\n")
        # ---------------------------------

        # 4. Clean up and prompt next action
        import os
        if os.path.exists(TEMP_AUDIO_FILE):
             os.remove(TEMP_AUDIO_FILE)
        
        action = input(f"{WHITE}Press ENTER for next phrase / type 'q' to quit:{ENDC} ").lower()
        if action == 'q' or action == 'quit':
            break

    print("--- Session ended. Au revoir! ---")

if __name__ == "__main__":
    import random
    main()
