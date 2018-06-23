import queue
import threading
import time

import RPi.GPIO as GPIO

from fprinter.backend import constants


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
    MOTOR_DELAY = 0.005
    END_COURSE_PRESSED = GPIO.HIGH

    def __init__(self, step_pin=constants.Pin.MOTOR_STEP, direction_pin=constants.Pin.MOTOR_DIR,
                 end_course_pins=constants.Pin.MOTOR_END_COURSE):

        self.step_pin = step_pin
        self.direction_pin = direction_pin
        self.end_course_sensors = end_course_pins

        self.commands = queue.Queue()
        self.running = False

        self.mutex = threading.Lock()
        self.emergency = False

        self.step_position = 0

        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.direction_pin, GPIO.OUT)
        GPIO.output(self.step_pin, GPIO.LOW)

        for pin in self.end_course_sensors:
            GPIO.setup(pin, GPIO.IN)

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

            direction = GPIO.HIGH
            if steps < 0:
                direction = GPIO.LOW
                steps = -steps

            GPIO.output(self.direction_pin, direction)
            time.sleep(StepMotor.MOTOR_DELAY)

            for step in range(steps):
                with self.mutex:
                    if self.emergency:
                        status.aborted = True
                        break
                if not self.running:
                    status.aborted = True
                    break

                end_course = False
                for pin in self.end_course_sensors:
                    if GPIO.input(pin) == StepMotor.END_COURSE_PRESSED:
                        end_course=True
                        break
                if end_course:
                    status.aborted = True
                    break

                GPIO.output(self.step_pin, GPIO.HIGH)
                time.sleep(StepMotor.MOTOR_DELAY)
                GPIO.output(self.step_pin, GPIO.LOW)
                time.sleep(delay)

            # TODO print warning if steps == 0 ?
            else:
                status.done = True

    def stop(self):
        self.running = False
        self.commands.put(None)
        self.thread.join()
