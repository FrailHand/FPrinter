import queue
import threading
import time

import RPi.GPIO as GPIO

from . import constants


class Status:
    def __init__(self):
        self.condition = threading.Condition()
        self.processing = False
        self.done = False
        self.aborted = False

    def __getattribute__(self, item):
        if item == 'condition':
            return super().__getattribute__(item)
        else:
            with self.condition:
                return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key == 'condition':
            super().__setattr__(key, value)
        else:
            with self.condition:
                super().__setattr__(key, value)
                self.condition.notify_all()


class StepMotor:
    STEP_SEQUENCE = ((1, 0, 1, 0), (0, 1, 1, 0), (0, 1, 0, 1), (1, 0, 0, 1))

    def __init__(self, motor_pins=(constants.Pin.MOTOR_A_1,
                                   constants.Pin.MOTOR_A_2,
                                   constants.Pin.MOTOR_B_1,
                                   constants.Pin.MOTOR_B_2), enable_pin=constants.Pin.MOTOR_ENABLE):

        if len(motor_pins) != 4:
            print('ERROR: bad number of motor pins - got {}, expected 4'.format(len(motor_pins)))
        self.motor_pins = motor_pins
        self.enable_pin = enable_pin

        self.commands = queue.Queue()
        self.running = False

        self.mutex = threading.Lock()
        self.emergency = False

        self.step_position = 0

        GPIO.setup(self.enable_pin, GPIO.OUT)
        GPIO.setup(self.motor_pins[0], GPIO.OUT)
        GPIO.setup(self.motor_pins[1], GPIO.OUT)
        GPIO.setup(self.motor_pins[2], GPIO.OUT)
        GPIO.setup(self.motor_pins[3], GPIO.OUT)

        GPIO.output(self.enable_pin, 1)
        self.set_step(*StepMotor.STEP_SEQUENCE[self.step_position])

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def move(self, step, delay):

        status = Status()

        with self.mutex:
            emergency = self.emergency

        if not emergency:
            self.commands.put((step, delay, status))
        else:
            status.aborted = True

        return status

    def set_emergency_state(self, emergency):
        with self.mutex:
            self.emergency = emergency

    def run(self):

        self.running = True

        while self.running:

            command = self.commands.get()

            if command is None:
                break

            steps, delay, status = command
            status.processing = True

            direction = 1
            if steps < 0:
                direction = -1
                steps = -steps

            for step in range(steps):
                with self.mutex:
                    if self.emergency:
                        status.aborted = True
                        break
                if not self.running:
                    status.aborted = True
                    break
                # TODO check end course sensor
                # -> status.aborted = True
                # break

                self.step_position = (self.step_position + direction) % 4
                self.set_step(*StepMotor.STEP_SEQUENCE[self.step_position])
                time.sleep(delay)

            # TODO print warning if steps == 0 ?
            else:
                status.done = True

    def set_step(self, w1, w2, w3, w4):
        GPIO.output(self.motor_pins[0], w1)
        GPIO.output(self.motor_pins[1], w2)
        GPIO.output(self.motor_pins[2], w3)
        GPIO.output(self.motor_pins[3], w4)

    def stop(self):
        self.running = False
        self.commands.put(None)
        self.thread.join()
