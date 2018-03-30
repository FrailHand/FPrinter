import queue
import threading
import time

import RPi.GPIO as GPIO

from . import constants


class Status():
    def __init__(self):
        self.condition = threading.Condition()
        self.processing = False
        self.done = False
        self.aborted = False

    def ended(self):
        return self.done or self.aborted

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


class StepMotor():
    STEP_SEQUENCE = ((1, 0, 1, 0), (0, 1, 1, 0), (0, 1, 0, 1), (1, 0, 0, 1))

    def __init__(self):

        self.commands = queue.Queue()
        self.running = False

        self.step_position = 0

        GPIO.setup(constants.Pin.MOTOR_ENABLE, GPIO.OUT)
        GPIO.setup(constants.Pin.MOTOR_A_1, GPIO.OUT)
        GPIO.setup(constants.Pin.MOTOR_A_2, GPIO.OUT)
        GPIO.setup(constants.Pin.MOTOR_B_1, GPIO.OUT)
        GPIO.setup(constants.Pin.MOTOR_B_2, GPIO.OUT)

        GPIO.output(constants.Pin.MOTOR_ENABLE, 1)

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def move(self, step, delay):

        status = Status()
        self.commands.put((step, delay, status))
        return status

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
                # TODO check end course sensor
                # -> status.aborted = True
                # break

                self.step_position = (self.step_position + direction) % 4
                self.set_step(*StepMotor.STEP_SEQUENCE[self.step_position])
                time.sleep(delay)

            # TODO print warning if steps == 0 ?

            command[1].done = True

    def set_step(self, w1, w2, w3, w4):
        GPIO.output(constants.Pin.MOTOR_A_1, w1)
        GPIO.output(constants.Pin.MOTOR_A_2, w2)
        GPIO.output(constants.Pin.MOTOR_B_1, w3)
        GPIO.output(constants.Pin.MOTOR_B_2, w4)

    def stop(self):
        self.running = False
        self.commands.put(None)
        self.thread.join()
