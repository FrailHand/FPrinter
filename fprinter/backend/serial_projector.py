import logging
import threading

import serial
import time

from fprinter.backend import constants


# TODO check the behavior of this bunch of code
# certainly in a thread, with events to the main loop
class Command:
    def __init__(self, command, response_code, action=None):
        self.command = bytearray.fromhex(command)
        self.response_code = bytearray.fromhex(response_code)
        self.action = action

    def send(self, serial_port: serial.Serial):
        serial_port.write(self.command)
        response = serial_port.read(Commands.RESPONSE_SIZE)
        print('expect response: {}'.format(self.response_code.hex()))
        print('serial response: {}'.format(response))
        # TODO read the response here! check the status code
        return self.action


class Commands:
    # TODO should we put a timeout and read as many bytes as possible?
    RESPONSE_SIZE = 8
    POWER_ON = Command('02 00 00 00 00 02', '22 00', constants.ProjectorStatus.ON)
    POWER_OFF = Command('02 01 00 00 00 03', '22 01', constants.ProjectorStatus.OFF)


class SerialProjector:

    AUTO_SLEEP_DELAY = 10

    def __init__(self, event_handler, port='/dev/tty0'):
        self.serial = serial.Serial(port=port,
                                    baudrate=9600,
                                    bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    )

        self.fire_event = event_handler

        self.sleep_time_origin = -1
        self.auto_sleep = False

        self.mutex = threading.Lock()
        self._status = constants.ProjectorStatus.OFF

        self.command = None
        self.condition = threading.Condition()

        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    @property
    def status(self):
        with self.mutex:
            return self._status

    @status.setter
    def status(self, value):
        with self.mutex:
            self._status = value

    def run(self):
        while self.running:
            with self.condition:
                if self.command is None:
                    self.condition.wait()

                if self.command is None:
                    continue

                action = self.command.send(self.serial)
                self.command = None
                if action is not None:
                    self.status = action
                if action == constants.ProjectorStatus.ERROR:
                    self.fire_event((constants.Event.PROJECTOR_ERROR,))

    def send_command(self, command):
        if self.condition.acquire(blocking=False):
            self.status = constants.ProjectorStatus.WAITING
            self.command = command
            self.condition.notify()
            self.condition.release()
        else:
            raise Exception('SerialProjector: cannot send serial commands when status is WAITING')

    def enable_auto_sleep(self, enable=True):
        if enable:
            self.auto_sleep = True
            self.sleep_time_origin = time.time()
        else:
            self.auto_sleep = False

    def ready(self):
        if self.status == constants.ProjectorStatus.ON:
            return True

        if self.status == constants.ProjectorStatus.OFF:
            self.enable_auto_sleep(False)
            self.send_command(Commands.POWER_ON)

        return False

    def update(self):
        if self.auto_sleep and self.status == constants.ProjectorStatus.ON:
            if time.time() - self.sleep_time_origin > SerialProjector.AUTO_SLEEP_DELAY:
                logging.info('projector goes to sleep')
                self.send_command(Commands.POWER_OFF)

    def shutdown(self):
        with self.condition:
            if self.status != constants.ProjectorStatus.OFF:
                self.status = constants.ProjectorStatus.WAITING
                self.command = Commands.POWER_OFF

            self.running = False
            self.condition.notify()

        self.thread.join()
        self.serial.close()
