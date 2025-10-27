from gpiozero import DigitalOutputDevice
from time import sleep

# --- GPIO setup ---
# Adjust these pins to match your wiring
EN = DigitalOutputDevice(18)     # Single GPIO controlling both EN pins
IN1 = DigitalOutputDevice(23)    # Motor 1 direction
IN2 = DigitalOutputDevice(24)    # Motor 2 direction

# --- Function to move motors ---
def forward(duration=2):
    EN.on()        # Enable both motors
    IN1.on()       # Motor 1 forward
    IN2.on()       # Motor 2 forward
    sleep(duration)
    EN.off()       # Stop motors

def backward(duration=2):
    EN.on()
    IN1.off()      # Motor 1 backward
    IN2.off()      # Motor 2 backward
    sleep(duration)
    EN.off()

# --- Test sequence ---
if __name__ == "__main__":
    while True:
        print("Moving forward")
        forward(3)
        sleep(1)
        print("Moving backward")
        backward(3)
        sleep(1)
