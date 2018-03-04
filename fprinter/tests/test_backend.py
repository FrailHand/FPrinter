import unittest

import os
import sys

sys.path.append(os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.realpath(__file__)))))

import fprinter.backend.drivers as drivers
import fprinter.backend.constants as constants


class TestHardwareDrivers(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.hardware = drivers.HardwareDrivers(self.handle_event)

    def handle_event(self, event):
        # check the event is well an event
        self.assertIsInstance(event, tuple)
        self.assertIsInstance(event[0], constants.event)


if __name__ == '__main__':
    print('\nRunning unittest on backend\n')
    unittest.main()
