import random
import time
import subprocess
import os
import numpy as np
import sounddevice as sd
import whisper
import logging 
import wave

# --- CONFIGURATION ---
MODEL_NAME = "large"  # Use "medium" for French
LANGUAGE = "French"    # Language code for Whisper
VOICE_NAME = "Audrey"  # macOS voice for TTS
SAMPLE_RATE = 44100    # Standard audio sample rate
TEMP_AUDIO_FILE = "user_recording.wav"

FRENCH_PHRASES = [
    "Il fait une de ces chaleurs.",
    "Il fait frisquet.",
    "Il fait un froid polaire.",
    "Il fait doux, hein?",
    "Il fait frais, hein?",
    "Il fait chaud, hein?",
    "Il fait froid, hein?",
    "Il fait un froid de canard.",
    "Il fait bon, hein?",
    "Il va faire froid",
    "Il a fait froid",
    "Il neigeait",
    "il faisait chaud",
]

# --- Helper Function for Comparison ---

def get_highlighted_comparison(expected, actual):
    """
    Compares the expected phrase against the actual transcription,
    highlighting differences using ANSI colors (green for match, red for error).
    """
    # ANSI color codes
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    
    # Simple tokenization and normalization (remove punctuation, lowercase)
    # Note: This simple comparison works well for word-by-word comparison but may
    # misidentify transposition errors (e.g., 'a un' vs 'un a').
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

def speak_phrase(phrase, voice_name, rate=160):
    """Uses the macOS 'say' command to speak the phrase."""
    # Use 'subprocess' to call the system's TTS command for reliability
    try:
        logging.info(f"Speaking: {phrase}")
        
        # -v specifies the voice, --rate specifies words per minute (160 is slow/clear)
        subprocess.run(
            ['say', '-v', voice_name, f'--rate={rate}', phrase],
            check=True
        )
        time.sleep(0.5) # Small pause after speaking
    except subprocess.CalledProcessError as e:
        print(f"Error calling 'say' command: {e}")
        print("Please ensure you are on macOS or adjust the function for your OS.")

def record_audio():
    """
    Records audio using a Push-to-Talk (PTT) mechanism via sounddevice.InputStream.
    Recording starts when the user presses Enter and stops when Enter is pressed again.
    """
    print("-" * 50)
    input("🎤 Press ENTER to START recording your phrase...")
    print("🔴 Recording... Press ENTER again to STOP.")
    print("-" * 50)
    
    audio_data = []
    
    # Callback function to continuously append incoming audio data to the list
    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(f"Audio Status Error: {status}", flush=True)
        audio_data.append(indata.copy())

    # Start a non-blocking stream
    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16', callback=callback):
            # Block the main thread, effectively recording until the user presses Enter
            input() 
            print("🛑 Recording stopped.")
    except Exception as e:
        print(f"Error during audio streaming: {e}")
        return None

    # Process and save audio
    if not audio_data:
        print("❌ No audio recorded.")
        return None
        
    # Concatenate all recorded NumPy arrays into a single array
    recording = np.concatenate(audio_data, axis=0)

    # Save recording to a temporary WAV file using Python's standard 'wave' module
    try:
        with wave.open(TEMP_AUDIO_FILE, 'wb') as wf:
            wf.setnchannels(1)
            # 'int16' dtype is 2 bytes wide
            wf.setsampwidth(2) 
            wf.setframerate(SAMPLE_RATE)
            # Convert NumPy array to raw bytes
            wf.writeframes(recording.tobytes())
        print("✅ Recording saved.")
    except Exception as e:
        print(f"Error saving WAV file with 'wave' module: {e}")
        return None

    return TEMP_AUDIO_FILE

def transcribe_audio(audio_path, model, language):
    """Uses the Whisper model to transcribe the saved audio file."""
    print("🧠 Transcribing audio with Whisper...")
    try:
        result = model.transcribe(audio_path, language=language)
        return result["text"].strip()
    except Exception as e:
        print(f"Error during Whisper transcription: {e}")
        return "ERROR: Could not transcribe."

# --- Main Application Loop ---

def main():
    """The main language practice loop."""
    # NOTE: It's good practice to configure logging here if you want output
    # logging.basicConfig(level=logging.INFO)

    print("--- French Pronunciation Tutor ---")
    print(f"Loading Whisper model: {MODEL_NAME}...")
    try:
        # Load the model once at the start
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
        correct_phrase = random.choice(FRENCH_PHRASES)
        
        print("\n" * 2)
        print("=" * 50)
        print(f"🗣️ Phrase to repeat: '{correct_phrase}'")
        print("=" * 50)
        
        speak_phrase(f"Répétez: {correct_phrase}", VOICE_NAME)
        
        # 2. Record user's attempt using PTT
        audio_file = record_audio() 

        # Handle recording failure
        if not audio_file:
            print("❌ Recording failed or was empty. Skipping transcription.")
            continue

        # 3. Transcribe and compare
        user_transcription = transcribe_audio(audio_file, model, LANGUAGE)
        
        highlighted_transcription = get_highlighted_comparison(correct_phrase, user_transcription)

        print("\n--- RESULTS ---")
        print(f"Phrase Pronounced: '{correct_phrase}'")
        print(f"Whisper Heard:    {highlighted_transcription}") # Print highlighted version
        print("-" * 50)

        # 4. Clean up and prompt next action
        os.remove(TEMP_AUDIO_FILE)
        
        action = input("Press Enter for next phrase, or type 'quit' to exit: ").lower()
        if action == 'quit':
            break

    print("--- Session ended. Au revoir! ---")

if __name__ == "__main__":
    main()