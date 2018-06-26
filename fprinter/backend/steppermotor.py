import queue
# TODO use multiprocessing instead of threading
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

    def __init__(self,
                 step_pin=constants.Pin.MOTOR_STEP,
                 direction_pin=constants.Pin.MOTOR_DIR,
                 end_course_top=constants.Pin.MOTOR_END_COURSE_TOP,
                 end_course_bottom=constants.Pin.MOTOR_END_COURSE_BOTTOM):

        self.step_pin = step_pin
        self.direction_pin = direction_pin
        self.end_course_top = end_course_top
        self.end_course_bottom = end_course_bottom

        self.commands = queue.Queue()
        self.running = False

        self.mutex = threading.Lock()
        self.emergency = False

        self.step_position = 0

        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.direction_pin, GPIO.OUT)
        GPIO.output(self.step_pin, GPIO.LOW)

        GPIO.setup(self.end_course_top, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.end_course_bottom, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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

            direction = GPIO.LOW
            if steps < 0:
                direction = GPIO.HIGH
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

                if GPIO.input(self.end_course_top) == StepMotor.END_COURSE_PRESSED:
                    end_course = True
                    GPIO.output(self.direction_pin, GPIO.HIGH)

                elif GPIO.input(self.end_course_bottom) == StepMotor.END_COURSE_PRESSED:
                    end_course = True
                    GPIO.output(self.direction_pin, GPIO.LOW)

                if end_course:
                    for _ in range(constants.END_COURSE_STEPS):
                        GPIO.output(self.step_pin, GPIO.HIGH)
                        time.sleep(StepMotor.MOTOR_DELAY)
                        GPIO.output(self.step_pin, GPIO.LOW)
                        time.sleep(delay)
                    status.aborted = True
                    break

                GPIO.output(self.step_pin, GPIO.HIGH)
                time.sleep(StepMotor.MOTOR_DELAY)
                GPIO.output(self.step_pin, GPIO.LOW)
                time.sleep(delay)

            else:
                status.done = True

    def stop(self):
        self.running = False
        self.commands.put(None)
        self.thread.join()

    @staticmethod
    def total_delay(steps, delay):
        return 2 * steps * delay
