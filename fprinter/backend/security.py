import RPi.GPIO as GPIO


class Security:
    RELAY_ON = GPIO.HIGH
    RELAY_OFF = GPIO.LOW

    def __init__(self, relay_pins):
        self.relay_pins = relay_pins

        for pin in self.relay_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, Security.RELAY_OFF)

    def disable(self):
        for pin in self.relay_pins:
            GPIO.output(pin, Security.RELAY_OFF)

    def enable(self):
        for pin in self.relay_pins:
            GPIO.output(pin, Security.RELAY_ON)
