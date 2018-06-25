import RPi.GPIO as GPIO

from fprinter.backend import constants


class Buttons:
    DEBOUNCE_DELAY = 200

    def __init__(self, event_handler,
                 reset_pin=constants.Pin.BUTTON_RESET,
                 emergency_pin=constants.Pin.BUTTON_EMERGENCY,
                 shutdown_pin=constants.Pin.BUTTON_SHUTDOWN):
        self.fire_event = event_handler

        GPIO.setup(reset_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(emergency_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(shutdown_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(reset_pin, GPIO.FALLING, callback=self.reset_pressed, bouncetime=Buttons.DEBOUNCE_DELAY)
        GPIO.add_event_detect(emergency_pin, GPIO.FALLING, callback=self.emergency_pressed,
                              bouncetime=Buttons.DEBOUNCE_DELAY)
        GPIO.add_event_detect(shutdown_pin, GPIO.FALLING, callback=self.shutdown_pressed,
                              bouncetime=Buttons.DEBOUNCE_DELAY)

    def reset_pressed(self, channel):
        self.fire_event((constants.Event.RESET_BTN,))

    def emergency_pressed(self, channel):
        self.fire_event((constants.Event.EMERGENCY_BTN,))

    def shutdown_pressed(self, channel):
        self.fire_event((constants.Event.SHUTDOWN_BTN,))
