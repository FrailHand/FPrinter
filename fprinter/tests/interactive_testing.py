import os
import sys
import unittest

sys.path.append(os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.realpath(__file__)))))

import fprinter.backend.drivers as drivers
import fprinter.backend.constants as constants


def interactive_check(test, message):
    """Ask the user for a confirmation check by pressing enter if OK or ^C if not"""
    answer = input('\nConfirm ([y]/n) that:\n\t{}\t'.format(message))
    print()

    test.assertIn(answer, ['Y', 'y', ''])


class TestHardwareDrivers(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        self.hardware = drivers.HardwareDrivers(self.handle_event)

    def tearDown(self):
        self.hardware.shutdown()

    def handle_event(self, event):
        # check the event is well an event
        print('Event received: ', event)
        self.assertIsInstance(event, tuple)
        self.assertIsInstance(event[0], constants.Event)

    def test_lcd(self):
        self.hardware.print_LCD("line1", "line2")
        interactive_check(self, "line 1 and line 2 on the LCD ?")

    def test_serial(self):
        a = False
        while not a:
            a = self.hardware.ready_projector()

        interactive_check(self, "projector turns on ?")


if __name__ == '__main__':
    print('\nRunning interactive unittest on backend\n')
    unittest.main()
