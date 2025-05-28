import time
import RPi.GPIO as GPIO

class TurbiditySensor():
    def __init__(self, pin: int = None):
        """
        Initialize the turbidity sensor.

        Args:
            pin (int): The BCM GPIO pin number used for digital signal input.
                       You MUST assign the correct pin number when wiring is finalized.
        """
        if pin is None:
            raise ValueError("You must specify a GPIO pin for the turbidity sensor.")

        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    @property
    def name(self) -> str:
        return "turbidity"

    def read(self) -> float:
        """
        Reads the sensor state. Returns:
            - 1.0 if sensor is blocked (high turbidity)
            - 0.0 if sensor is clear (low turbidity)
        """
        state = GPIO.input(self.pin)
        if state == GPIO.LOW:
            # Sensor blocked — higher turbidity
            return 1.0
        else:
            # Sensor clear — lower turbidity
            return 0.0
