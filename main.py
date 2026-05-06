import threading
import time
import subprocess
import board, digitalio, busio
import os
import logging

logging.basicConfig(filename="/home/maria/mof/mof.log", level=logging.INFO, format="%(asctime)s - %(message)s")
logging.info("Assistant service starting...")

# --- kill leftover systems ---
os.system("sudo fuser -k /dev/snd/*")
   
# restart pulseaudio
subprocess.run(["pulseaudio", "-k"], stderr=subprocess.DEVNULL)
subprocess.run(["pulseaudio", "--start"], stderr=subprocess.DEVNULL)

# --- import your modules ---
import eyes
import spotify

# Define GPIO pin of your switch
switch = digitalio.DigitalInOut(board.D4)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

## Define LEDS
led_chat_active = digitalio.DigitalInOut(board.D16)
led_chat_active.direction = digitalio.Direction.OUTPUT

led_you_talk = digitalio.DigitalInOut(board.D20)
led_you_talk.direction = digitalio.Direction.OUTPUT

led_bot_talk = digitalio.DigitalInOut(board.D21)
led_bot_talk.direction = digitalio.Direction.OUTPUT

led_bot_talk.value = False
led_you_talk.value = False
led_chat_active.value = False

# Debounce parameters
DEBOUNCE_DELAY = 0.25 # seconds
last_state = switch.value
last_change_time = time.monotonic()

# Flag for chat mode
chat_running = False

def run_eyes():
    """Continuously show eye animation."""
    try:
        eyes.run()
    except Exception as e:
        logging.warning(f"Eyes display not available: {e}")

def monitor_switch():
    """Monitors the switch and launches chat.py when ON."""
    global chat_running
    global last_change_time
    global last_state
    logging.info("Monitor switch...")
    while True:
        current_state = switch.value
        now = time.monotonic()

        if current_state != last_state:
            # switch changed; record time
            last_change_time = now
            last_state = current_state

        # Only act if stable for debounce delay
        if (now-last_change_time) >= DEBOUNCE_DELAY:
            if not current_state and not chat_running:
                logging.info("Switch ON")
                chat_running = True
                threading.Thread(target=start_chat, daemon=True).start()
            #elif current_state and chat_running:
             #   print("Switch OFF → Stopping Chat")
              #  stop_chat()
               # chat_running = False
        time.sleep(0.5)

chat_process = None

def start_chat():
    global chat_process
    # Start chat.py as a separate process
    logging.info("Starting Chat")
    chat_process = subprocess.Popen(["python3", "/home/maria/mof/chat.py"])

def stop_chat():
    global chat_process
    if chat_process:
        chat_process.terminate()
        chat_process = None

def handle_spotify_command(command):
    """You can call this from chat.py (via IPC or shared state)."""
    if "play" in command.lower():
        spotify.play_song(command)

def main():
    # Start eyes animation in background
    threading.Thread(target=run_eyes, daemon=True).start()

    # Start switch monitor
    monitor_switch()

if __name__ == "__main__":
    main()
