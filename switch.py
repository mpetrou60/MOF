import RPi.GPIO as GPIO

# Define the GPIO pin for your switch
SWITCH_PIN = 7
GPIO.setmode(GPIO.BOARD)

# Define debounce time in milliseconds
DEBOUNCE_TIME_MS = 200 # 200 milliseconds

# Set the initial state and pull-up resistor for the switch
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialise the switch state and previous state
switch_state = GPIO.input(SWITCH_PIN)
prev_switch_state = switch_state

# define a function to handle switch presses
def switch_callback(channel):
	global switch_sate
	switch_state = GPIO.input(SWITCH_PIN)

try:
	# Main loop
	while True:
		switch_state = GPIO.input(SWITCH_PIN)
		if switch_state == GPIO.HIGH:
			print("The switch: OFF")
		else:
			print("The switch: ON")

except KeyboardInterrupt:
	# Clean up GPIO on exit
	GPIO.cleanup()
