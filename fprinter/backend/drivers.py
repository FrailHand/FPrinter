from . import constants
from .constants import Event


class HardwareDrivers():

    def __init__(self, event_listener):
        """
        Setup the hardware drivers

        :param fire_event: (function) event listener for hardware events
        """

        self.fire_event = event_listener

        print('Hardware setup')

    def update(self):
        """Update the hardware"""
        print('Hardware updated')

    def move_plate(self, dz, speed=1000):
        """
        Move the printing plate upwards or downwards

        :param dz: (float) vertical displacement in µm
        :param speed: (float) speed  in µm/s
        :return: None
        """
        print('Plate moved vertically of {} µm with speed {} µm/s'.format(dz, speed))

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
