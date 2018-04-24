from __future__ import division
from __future__ import print_function

import serial
import time
from fake_rpi.Base import Base

EIGHTBITS = serial.EIGHTBITS
PARITY_NONE = serial.PARITY_NONE
STOPBITS_ONE = serial.STOPBITS_ONE


class Serial(Base):
    """
    A dummy interface to test with when not hooked up to real hardware.
    """
    cd = False
    cts = True
    dsr = False
    in_waiting = True
    out_waiting = False
    ri = False
    port = None
    baudrate = 0
    timeout = 0
    status = False  # open or closed
    name = 'name'

    def __init__(self, port, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE,
                 stopbits=STOPBITS_ONE):
        # super(Base, self).__init__(self.__class__)
        Base.__init__(self, self.__class__)
        self.port = port

    def open(self):
        if not self.port:
            raise Exception('set Serial::port before opening')
        self.status = True

    def isOpen(self):
        return self.status

    def setRTS(self, a):
        pass

    def read(self, size=1):
        time.sleep(2)
        pass

    def write(self, data: bytearray):
        print('fake_rpi_serial.Serial.write - {}'.format(data.hex()))
        return len(data)

    def close(self):
        self.status = False

    def flush(self):
        pass

    def flushInput(self):
        pass

    def flushOutput(self):
        pass

    def set_output_flow_control(self, enable=True):
        pass

    def set_input_flow_control(self, enable=True):
        pass

    def cancel_read(self):
        pass

    def cancel_write(self):
        pass

    def get_settings(self):
        return {'port': self.port}
