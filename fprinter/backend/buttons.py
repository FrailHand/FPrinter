import RPi.GPIO as GPIO

from . import constants


class Buttons:
    DEBOUNCE_DELAY = 200

    def __init__(self, event_handler, reset_pin=constants.Pin.BUTTON_RESET,
                 emergency_pin=constants.Pin.BUTTON_EMERGENCY):
        self.fire_event = event_handler

        # TODO pull up or down?
        GPIO.setup(reset_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(emergency_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # TODO rising or falling?
        GPIO.add_event_detect(reset_pin, GPIO.RISING, callback=self.reset_pressed, bouncetime=Buttons.DEBOUNCE_DELAY)
        GPIO.add_event_detect(emergency_pin, GPIO.RISING, callback=self.emergency_pressed,
                              bouncetime=Buttons.DEBOUNCE_DELAY)

    def reset_pressed(self, channel):
        self.fire_event((constants.Event.RESET_BTN,))

    def emergency_pressed(self, channel):
        self.fire_event((constants.Event.EMERGENCY_BTN,))
