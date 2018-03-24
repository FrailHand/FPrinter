from . import constants
from .constants import Event
from .steppermotor import StepMotor


class HardwareDrivers():

    def __init__(self, event_listener):
        """
        Setup the hardware drivers

        :param fire_event: (function) event listener for hardware events
        """

        GPIO.setmode(GPIO.BCM)

        self.fire_event = event_listener

        self.motor = StepMotor()

        print('INFO: hardware drivers initialized')

    def shutdown(self):
        """
        Shutdown the hardware drivers and stop the threads

        :return:
        """
        self.motor.stop()
        print('INFO: hardware drivers successfully cleaned')

    def update(self):
        """Update the hardware"""
        print('Hardware updated')

    def move_plate(self, dz, speed_mode=constants.SpeedMode.SLOW):
        """
        Move the printing plate upwards or downwards

        :param dz: (float) vertical displacement in µm
        :param speed_mode: (float) step delay in s
        :return status: (Status) command status
        """

        # TODO dz -> steps convesion
        # speed profile

        step = round(dz)
        

        return self.motor.move(step, speed_mode)

    def print_LCD(self, line1=None, line2=None):
        """
        Print message on LCD screen
        Only refresh used lines

        :param line1: (str) message for first line
        :param line2: (str) message for second line
        :return: None
        """

        print('Printing on LCD')
        if line1 is not None:
            print('Line 1: {}'.format(line1))
        if line2 is not None:
            print('Line2: {}'.format(line2))
