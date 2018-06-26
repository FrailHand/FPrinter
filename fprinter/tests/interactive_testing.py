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
        self.hardware.print_LCD("first", "second")
        interactive_check(self, "'first' and 'second' are printed the LCD")
        self.hardware.print_LCD("third")
        interactive_check(self, "'third' and 'second' are printed the LCD")

    def test_relay(self):
        self.hardware.security.disable()
        interactive_check(self, "relays are disconnected")
        self.hardware.security.enable()
        interactive_check(self, "relays are connected")

    # def test_serial(self):
    #     a = False
    #     while not a:
    #         a = self.hardware.ready_projector()
    #
    #     interactive_check(self, "projector turns on")

    def test_buttons(self):
        interactive_check(self, "when you press buttons, events are printed")

    def test_motor(self):
        self.hardware.move_plate(100, constants.SpeedMode.FAST)
        interactive_check(self, "plate moves up 100mm")
        self.hardware.move_plate(-100, constants.SpeedMode.FAST)
        interactive_check(self, "plate moves down 100mm")

    def test_temperature(self):
        temp = self.hardware.temperature_sensors[0].update()
        interactive_check(self, "temperature is {}°C (sensor 1)".format(temp))
        temp = self.hardware.temperature_sensors[1].update()
        interactive_check(self, "temperature is {}°C (sensor 2)".format(temp))


if __name__ == '__main__':
    print('\nRunning interactive unittest on backend\n')
    unittest.main()
