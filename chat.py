import subprocess
import tempfile
import openai
import os, re
import sys
import time
import pyttsx3
import spotify
import board, digitalio, busio
import logging

logging.basicConfig(filename="/home/maria/mof/mof.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# --- Find correct mic ---
def get_mic_hw_id(name_hint="USB"):
    result = subprocess.run(["arecord", "-l"], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if name_hint.lower() in line.lower():
            m = re.search(r"card (\d+): (.*?), device (\d+):", line)
            if m:
                card, device = m.group(1), m.group(3)
                return f"hw:{card},{device}"
    return None

mic_hw = get_mic_hw_id() or "hw:3,0"
logging.info(f"Using microphone: {mic_hw}")

# --- Audio settings ---
INPUT_DEVICE = mic_hw   # USB mic
OUTPUT_DEVICE = "hw:0,0"  # Headphones / speaker
SAMPLE_RATE = 44100
CHANNELS = 1
RECORD_SECONDS = 5

SYSTEM_ROLE = "You are a helpful voice assistant on the slightly sarcastic side, kind of like Jarvis from Iron Man."
CHATGPT_MODEL = "gpt-3.5-turbo"
WHISPER_MODEL = "whisper-1"

openai.api_key = os.environ.get("OPENAI_API_KEY")
if openai.api_key is None:
    logging.info("Set OPENAI_API_KEY in environment")
    sys.exit(1)

def record_audio(seconds=RECORD_SECONDS):
    """Record audio from the USB mic using arecord and save to a temp WAV file"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wave:
        wav_path = tmp_wave.name

    cmd = [
        "arecord",
        "-D", INPUT_DEVICE,
        "-f", "S16_LE",
        "-c", str(CHANNELS),
        "-r", str(SAMPLE_RATE),
        wav_path,
        "-d", str(seconds)
    ]

    subprocess.run(cmd, check=True)
    return wav_path

def transcribe(wav_file):
    """Send WAV file to OpenAI Whisper for transcription"""
    with open(wav_file, "rb") as f:
        result = openai.audio.transcriptions.create(model=WHISPER_MODEL,file=f)
    return result.text.strip()


def sendchat(prompt):
    """Send user prompt to OpenAI Chat API"""
    response = openai.chat.completions.create(
        model=CHATGPT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_ROLE},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content

# Initialize TTS engine once
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Adjust speed
voices = tts_engine.getProperty('voices')
if voices:
    tts_engine.setProperty('voice', voices[0].id)

def speak_text(text):
    """Speak the given text via pyttsx3"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_file = tmp.name

    # use espeak to create a wav
    cmd_espeak = ["espeak", "-w", wav_file, text]
    subprocess.run(cmd_espeak, check=True)

    # use espeak to create a wav
    cmd_play = ["aplay", "-D", "hw:0,0", wav_file]
    subprocess.run(cmd_play, check=True)

    os.unlink(wav_file)

def main():
    
    led_chat_active = digitalio.DigitalInOut(board.D16)
    led_chat_active.direction = digitalio.Direction.OUTPUT

    led_you_talk = digitalio.DigitalInOut(board.D20)
    led_you_talk.direction = digitalio.Direction.OUTPUT

    led_bot_talk = digitalio.DigitalInOut(board.D21)
    led_bot_talk.direction = digitalio.Direction.OUTPUT

    led_bot_talk.value = True
    led_you_talk.value = False
    led_chat_active.value = True
    speak_text("Hello!")
    logging.info("Hello!")

    while True:
        try:
            led_you_talk.value = True
            led_bot_talk.value = False
            #logging.info("\nListening…")            
            wav_file = record_audio()

            #logging.info("\nTranscribing…")
            led_you_talk.value = False
            led_bot_talk.value = True
            text = transcribe(wav_file)
            os.unlink(wav_file)
            logging.info("You said:", {text})

            if "stand for" in text:
                speak_text("MOF stands for Maria's only friend. Honestly it's a bit sad. You should work on your people skills.")
            elif "play music" in text:
                speak_text("Just connecting to spotify")
                spotify.play_song()
            else:
                #logging.info("ChatGPT is thinking…")
                chat_resp = sendchat(text)
                logging.info("ChatGPT:", {chat_resp})

                # Speak the response
                speak_text(chat_resp)

            # clean up temporary file
            if wav_file and os.path.exists(wav_file):
                os.remove(wav_file)

        #except KeyboardInterrupt:
            #logging.info("\nExiting.")
            #break
        except Exception as e:
            logging.errror(f"Error in main loop {e}:", exc_info=True)


if __name__ == "__main__":
    main()
