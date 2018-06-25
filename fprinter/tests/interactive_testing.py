import os
import sys
import unittest

import platform

if platform.machine() == 'x86_64':
    # this allows to run the code on non-raspberry machines
    # DEVELOPMENT PURPOSE ONLY
    import sys
    import fake_rpi
    from fprinter.tests import fake_rpi_serial
    from fprinter.tests import fake_adafruit_dht

    sys.modules['RPi'] = fake_rpi.RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
    sys.modules['smbus'] = fake_rpi.smbus
    sys.modules['serial'] = fake_rpi_serial
    sys.modules['Adafruit_DHT'] = fake_adafruit_dht

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

    def test_relay(self):
        self.hardware.security.disable()
        interactive_check(self, "relays are disconnected ?")
        self.hardware.security.enable()
        interactive_check(self, "relays are connected ?")

    def test_serial(self):
        a = False
        while not a:
            a = self.hardware.ready_projector()

        interactive_check(self, "projector turns on ?")

    def test_motor(self):
        self.hardware.move_plate(10)
        interactive_check(self, "plate moves up 10mm ?")
        self.hardware.move_plate(-10)
        interactive_check(self, "plate moves down 10mm ?")


if __name__ == '__main__':
    print('\nRunning interactive unittest on backend\n')
    unittest.main()
