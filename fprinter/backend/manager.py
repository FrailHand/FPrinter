import time

import cairosvg
import io
import json
import logging
import os
import pyglet
import queue
import xml
from PIL import Image
from enum import Enum

from fprinter.backend import constants
from fprinter.backend import server_unix
from fprinter.backend.constants import Event
from fprinter.backend.constants import MessageCode
from fprinter.backend.drivers import HardwareDrivers
from fprinter.backend.svg_slice_lib import parse_svg
from fprinter.backend.window import Window


class Manager:
    class State(Enum):
        READY = 'Ready'
        PRINTING = 'Printing'
        ENDING = 'Ending'
        WAITING = 'Waiting'
        EMERGENCY = 'Emergency'

    def __init__(self, fullscreen=True):
        self.layers = None
        self.piece_height = None
        self.name = None
        self.printed_height = None
        self.layer_exposition_time = None
        self.current_layer = None
        self.is_paused = None
        self.layer_timestamp = None
        self.paused_exposition = None
        self.state = None
        self.shutdown_timestamp = 0
        self.system_halt = False

        self.event_queue = queue.Queue()

        self.window = Window(self.fire_event, fullscreen=fullscreen)

        try:
            self.drivers = HardwareDrivers(self.fire_event)
        except Exception as e:
            logging.error('when launching drivers - {}'.format(e))
            self.shutdown(cleanup=False)
            exit(1)

        try:
            self.server = server_unix.Server(self.fire_event)

        except Exception as e:
            logging.error('when creating socket - {}'.format(e))
            self.window.close()
            self.drivers.shutdown()
            exit(1)

        try:
            self.server.start()
        except Exception as e:
            logging.error('when starting server - {}'.format(e))
            self.shutdown(cleanup=False)
            exit(1)

        self.motor_status = None
        self.reset_status(purge=True)
        self.set_state(Manager.State.ENDING)

        pyglet.clock.schedule_interval(self.update, interval=1 / 60)

    def shutdown(self, cleanup=True):
        logging.info('shutting down printer...')
        self.drivers.print_LCD('SHUTDOWN', '...')
        self.server.stop(cleanup)
        self.window.close()
        self.drivers.shutdown()
        logging.info('display closed')

    def fire_event(self, event):
        self.event_queue.put(event)

    def reset_status(self, purge):
        if purge:
            self.layers = []
            self.piece_height = -1
            self.name = ''

        self.printed_height = 0
        self.layer_exposition_time = 0
        self.current_layer = -1
        self.is_paused = False
        self.layer_timestamp = -1
        self.paused_exposition = 0

        if os.path.exists(constants.LAYER_PNG):
            os.remove(constants.LAYER_PNG)

    def save_status(self):
        ready = self.state == Manager.State.READY or self.state == Manager.State.PRINTING
        in_progress = self.state == Manager.State.PRINTING or self.state == Manager.State.ENDING
        status = {'ready': ready, 'in_progress': in_progress,
                  'paused': self.is_paused, 'name': self.name,
                  'current_layer': self.current_layer + 1,
                  'max_layer': len(self.layers), 'ETA': self.eta}

        with open(constants.PRINTER_STATUS, 'w') as file:
            json.dump(status, file)

        if self.state == Manager.State.PRINTING:
            if self.is_paused:
                self.drivers.print_LCD(line1='Paused')
            self.drivers.print_LCD(line2=self.eta)
        else:
            self.drivers.print_LCD(line1=self.state.value)

    def set_state(self, status):
        if status != Manager.State.PRINTING:
            self.drivers.projector_auto_sleep()

        if status == Manager.State.ENDING:
            self.motor_status = self.drivers.move_plate(constants.PRINTER_HEIGHT * 2,
                                                        speed_mode=constants.SpeedMode.FAST)
        elif status == Manager.State.PRINTING:
            self.reset_status(purge=False)

        self.state = status
        self.save_status()

    @property
    def remaining_time(self):
        remaining_height = self.piece_height - self.printed_height
        remaining_time = remaining_height * constants.EXPOSITION_TIME_PER_MM
        # TODO compute motor time
        # remaining_time += self.drivers.motor.delay(remaining_height)
        return remaining_time

    @property
    def eta(self):
        if self.current_layer < 0:
            return ''
        remaining = round(self.remaining_time)
        minutes = remaining // 60
        seconds = remaining % 60
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            eta = '{}h {}min'.format(hours, minutes)
        else:
            eta = '{}min {}s'.format(minutes, seconds)
        return eta

    def check_printable(self):
        layer = self.layers[0]

        stream = io.BytesIO()
        cairosvg.surface.PNGSurface.convert(
            bytestring=xml.etree.ElementTree.tostring(layer),
            write_to=stream, dpi=96, scale=1)
        image = pyglet.image.load('', file=stream)
        stream.close()

        if image.height > self.window.height or image.width > self.window.width:
            return False

        else:
            return True

    def load_svg(self):
        if self.state != Manager.State.READY and self.state != Manager.State.WAITING:
            logging.warning('tried to upload file while printing')
            return 1

        self.layers, self.piece_height = parse_svg(constants.SVG_FILE)

        with open(constants.SVG_NAME, 'r') as file:
            self.name = file.read()

        printable = self.check_printable()

        if not printable:
            logging.info('svg too big for printing area')
            self.reset_status(purge=True)

        self.save_status()

        return 0 if printable else 1

    def project_layer(self):
        layer = self.layers[self.current_layer]

        stream = io.BytesIO()
        cairosvg.surface.PNGSurface.convert(
            bytestring=xml.etree.ElementTree.tostring(layer),
            write_to=stream, dpi=constants.PROJECTOR_DPI, scale=1)
        image = pyglet.image.load('', file=stream)
        stream.close()

        self.window.clear()
        image.blit(x=(self.window.width - image.width) // 2,
                   y=(self.window.height - image.height) // 2)
        self.layer_timestamp = time.time()

        temp_file = constants.LAYER_PNG + '~'

        buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        b_image = buffer.image_data.get_image_data()
        pil_image = Image.frombytes(b_image.format, (b_image.width, b_image.height),
                                    b_image.get_data(b_image.format, b_image.pitch))
        pil_image = pil_image.transpose(Image.FLIP_TOP_BOTTOM)
        pil_image = pil_image.convert('RGB')
        pil_image.save(temp_file, 'PNG')

        os.rename(temp_file, constants.LAYER_PNG)

    def confirm_if_zero(self, value):
        if value == 0:
            self.server.send(MessageCode.CONFIRM)
        else:
            self.server.send(MessageCode.REFUSE)

    def update(self, dt):
        try:
            while True:
                event = self.event_queue.get(block=False)
                if event[0] == Event.EXIT:
                    self.shutdown()
                    return

                elif event[0] == Event.FILE_UPLOADED:
                    self.confirm_if_zero(self.load_svg())

                elif event[0] == Event.START_UI:
                    self.confirm_if_zero(self.start())

                elif event[0] == Event.PAUSE_UI:
                    self.confirm_if_zero(self.pause())

                elif event[0] == Event.RESUME_UI:
                    self.confirm_if_zero(self.resume())

                elif event[0] == Event.ABORT_UI:
                    self.abort()
                    self.server.send(MessageCode.CONFIRM)

                elif event[0] == Event.PROJECTOR_ERROR:
                    self.emergency_stop(message='projector')

                elif event[0] == Event.EMERGENCY_BTN:
                    self.emergency_stop(message='button')

                elif event[0] == Event.TEMPERATURE_ERROR:
                    self.emergency_stop(message='temp err {}'.format(event[1]))

                elif event[0] == Event.OVERHEAT:
                    self.emergency_stop(message='overheat {}'.format(event[1]))

                elif event[0] == Event.RESET_BTN:
                    if self.state == Manager.State.WAITING:
                        # move the plate to the bottom, then up to the printing area
                        self.drivers.move_plate(-constants.PRINTER_HEIGHT * 2,
                                                speed_mode=constants.SpeedMode.FAST)
                        self.motor_status = self.drivers.move_plate(constants.PRINTING_AREA_HEIGHT,
                                                                    speed_mode=constants.SpeedMode.MEDIUM)

                elif event[0] == Event.SHUTDOWN_BTN:
                    timestamp = time.time()
                    if timestamp - self.shutdown_timestamp < constants.SHUTDOWN_DELAY:
                        self.system_halt = True
                        self.shutdown()
                    else:
                        self.abort()
                        self.shutdown_timestamp = timestamp

                else:
                    logging.warning('unknown event - {}'.format(event))

        except queue.Empty:
            pass

        if self.state == Manager.State.PRINTING:
            if self.drivers.ready_projector():
                if not self.is_paused:
                    if self.motor_status is not None:
                        if self.motor_status.done:
                            self.project_layer()
                            self.save_status()
                            self.motor_status = None

                        elif self.motor_status.aborted:
                            self.emergency_stop(message='motor')

                    elif time.time() - self.layer_timestamp > self.layer_exposition_time:
                        self.window.clear()
                        self.printed_height += float(
                            self.layers[self.current_layer].getchildren()[-1].get(
                                '{http://slic3r.org/namespaces/slic3r}layer-height'))
                        self.current_layer += 1

                        if self.current_layer >= len(self.layers):
                            if os.path.exists(constants.LAYER_PNG):
                                os.remove(constants.LAYER_PNG)

                            self.set_state(Manager.State.ENDING)
                            logging.info('print finished')

                        else:
                            dz = float(
                                self.layers[self.current_layer].getchildren()[-1].get(
                                    '{http://slic3r.org/namespaces/slic3r}layer-height'))
                            self.layer_exposition_time = dz * constants.EXPOSITION_TIME_PER_MM

                            self.motor_status = self.drivers.move_plate(dz,
                                                                        speed_mode=constants.SpeedMode.SLOW)

        elif self.state == Manager.State.ENDING:
            if self.motor_status is not None:
                if self.motor_status.done:
                    logging.error('ending step - '
                                  'moving printer to top gave "done" instead of "aborted"')
                    self.emergency_stop(message='motor')
                elif self.motor_status.aborted:
                    self.motor_status = None

            else:
                self.set_state(Manager.State.WAITING)
                logging.info('waiting for reset')

        elif self.state == Manager.State.WAITING:
            if self.motor_status is not None:
                if self.motor_status.done:
                    self.motor_status = None
                    self.set_state(Manager.State.READY)
                    logging.info('printer ready')
                elif self.motor_status.aborted:
                    self.emergency_stop(message='motor')

        self.drivers.update()

    def start(self):
        if len(self.layers) == 0:
            # return error code if the layers are not loaded
            logging.warning('tried to start printing with no layers loaded')
            return 1

        elif self.state != Manager.State.READY:
            logging.warning('tried to start printing while not ready')
            return 2

        else:
            self.set_state(Manager.State.PRINTING)
            logging.info('starting to print - {}'.format(self.name))
            return 0

    def pause(self):
        if self.state != Manager.State.PRINTING:
            logging.warning('tried to pause while not printing')
            return 1

        elif self.is_paused:
            logging.warning('tried to pause while already paused')
            return 2

        else:
            self.window.clear()
            timestamp = time.time()
            self.is_paused = True
            self.save_status()
            self.paused_exposition = timestamp - self.layer_timestamp

            logging.info('print paused')
            return 0

    def resume(self):
        if self.state != Manager.State.PRINTING:
            logging.warning('tried to resume while not printing')
            return 1

        elif not self.is_paused:
            logging.warning('tried to resume while already running')
            return 2

        else:
            self.is_paused = False
            self.save_status()
            self.project_layer()
            self.layer_timestamp -= self.paused_exposition

            logging.info('print resumed')
            return 0

    def abort(self):
        self.reset_status(purge=True)
        if self.state == Manager.State.PRINTING or self.state == Manager.State.READY:
            self.set_state(Manager.State.ENDING)
            self.window.clear()
            logging.info('aborting print')

    def emergency_stop(self, message='', hardware=False):
        if hardware:
            self.drivers.security.disable()
            logging.warning('relays disabled')

        self.drivers.motor_emergency(True)
        self.window.clear()
        self.motor_status = None
        self.reset_status(purge=True)
        self.set_state(Manager.State.EMERGENCY)
        self.drivers.print_LCD(line2=message)
        # TODO how do we leave emergency state?
        logging.warning('emergency stop triggered - {}'.format(message))
