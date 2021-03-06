import RPi.GPIO as GPIO
import logging

from fprinter.backend import constants
from fprinter.backend.buttons import Buttons
from fprinter.backend.lcd import LCD
from fprinter.backend.security import Security
from fprinter.backend.steppermotor import StepMotor
from fprinter.backend.temperature import Temperature


class HardwareDrivers:

    def __init__(self, event_listener):
        """
        Setup the hardware drivers

        :param event_listener: (function) event listener for hardware events
        """

        GPIO.setmode(GPIO.BCM)

        self.fire_event = event_listener

        self.security = Security(constants.Pin.RELAYS)
        self.security.enable()

        self.lcd = LCD()
        self.motor = StepMotor()
        # self.serial_projector = SerialProjector(self.fire_event)
        self.buttons = Buttons(self.fire_event)
        self.temperature_sensors = (
            Temperature(self.fire_event, constants.Pin.TEMPERATURE_1),
            Temperature(self.fire_event, constants.Pin.TEMPERATURE_2),
        )

        logging.info('hardware drivers initialized')

    def shutdown(self):
        """
        Shutdown the hardware drivers and stop the threads

        :return:
        """
        self.motor.stop()
        # self.serial_projector.shutdown()
        self.security.disable()

        GPIO.cleanup()
        logging.info('hardware drivers successfully cleaned')

    def update(self):
        # self.serial_projector.update()
        for sensor in self.temperature_sensors:
            sensor.update()

    def move_plate(self, dz, speed_mode=constants.SpeedMode.SLOW):
        """
        Move the printing plate upwards or downwards

        :param dz: (float) vertical displacement in mm
        :param speed_mode: (float) step delay in s
        :return status: (Status) command status
        """

        step = self.length_to_motor_steps(dz)
        return self.motor.move(step, speed_mode)

    def length_to_motor_steps(self, dz):
        # TODO dz -> steps convesion
        return round(dz * 20)

    def compute_motor_time(self, dz, speed_mode=constants.SpeedMode.SLOW):
        steps = abs(self.length_to_motor_steps(dz))
        return self.motor.total_delay(steps, speed_mode)

    def motor_emergency(self, emergency):
        self.motor.set_emergency_state(emergency)

    def print_LCD(self, line1=None, line2=None):
        """
        Print message on LCD screen
        Only refresh used lines

        :param line1: (str) message for first line
        :param line2: (str) message for second line
        :return: None
        """
        self.lcd.write(line1, line2)
        logging.warning('LCD disabled, debug mode')

    def ready_projector(self):
        return True
        # return self.serial_projector.ready()

    def projector_auto_sleep(self):
        pass
        # self.serial_projector.enable_auto_sleep()
