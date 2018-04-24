import RPi.GPIO as GPIO

from . import constants
from .lcd import LCD
from .steppermotor import StepMotor
from . import serial_projector


class HardwareDrivers:

    def __init__(self, event_listener):
        """
        Setup the hardware drivers

        :param event_listener: (function) event listener for hardware events
        """

        GPIO.setmode(GPIO.BCM)

        self.fire_event = event_listener

        self.lcd = LCD()

        self.motor = StepMotor()

        self.serial_projector = serial_projector.SerialProjector(self.fire_event)

        print('INFO: hardware drivers initialized')

    def shutdown(self):
        """
        Shutdown the hardware drivers and stop the threads

        :return:
        """
        self.motor.stop()
        self.serial_projector.shutdown()

        GPIO.cleanup()
        print('INFO: hardware drivers successfully cleaned')

    def update(self):
        self.serial_projector.update()

    def move_plate(self, dz, speed_mode=constants.SpeedMode.SLOW):
        """
        Move the printing plate upwards or downwards

        :param dz: (float) vertical displacement in µm
        :param speed_mode: (float) step delay in s
        :return status: (Status) command status
        """

        # TODO dz -> steps convesion
        # speed profile

        step = round(dz * 20)

        return self.motor.move(step, speed_mode)

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

    def ready_projector(self):
        if self.serial_projector.status == constants.ProjectorStatus.ON:
            return True

        if self.serial_projector.status == constants.ProjectorStatus.OFF:
            self.serial_projector.enable_auto_sleep(False)
            self.serial_projector.send_command(serial_projector.Commands.POWER_ON)

        return False

    def projector_auto_sleep(self):
        self.serial_projector.enable_auto_sleep()
