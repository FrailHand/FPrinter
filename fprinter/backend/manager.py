import io
import json
import os
import queue
import time
import xml
from enum import Enum, auto

import cairosvg
import pyglet
from PIL import Image

from . import constants
from . import server_unix
from .constants import Event
from .constants import MessageCode
from .drivers import HardwareDrivers
from .svg_slice_lib import parse_svg
from .window import Window


class Manager:
    class State(Enum):
        READY = 'Ready'
        PRINTING = 'Printing'
        ENDING = 'Ending'
        WAITING = 'Waiting'
        EMERGENCY = 'Emergency'

    def __init__(self):
        self.event_queue = queue.Queue()

        self.window = Window(self.fire_event)
        self.drivers = HardwareDrivers(self.fire_event)

        try:
            self.server = server_unix.Server(self.fire_event)

        except Exception as e:
            print('ERROR: when creating socket - {}'.format(e))
            exit(1)

        try:
            self.server.start()
        except Exception as e:
            print('ERROR: when starting server - {}'.format(e))
            exit(1)

        self.state = Manager.State.ENDING
        self.reset_status(purge=True)

        pyglet.clock.schedule_interval(self.update, interval=1 / 60)

    def shutdown(self):
        print('INFO: shutting down printer...')
        self.server.stop()
        self.window.close()
        self.drivers.shutdown()
        print('INFO: display closed')

    def fire_event(self, event):
        self.event_queue.put(event)

    def reset_status(self, purge):
        if purge:
            self.layers = []
            self.name = ''

        self.layer_exposition_time = 0
        self.current_layer = -1
        self.is_paused = False
        self.layer_timestamp = -1
        self.paused_exposition = 0
        self.motor_status = None

        self.save_status()

        if os.path.exists(constants.LAYER_PNG):
            os.remove(constants.LAYER_PNG)

    def save_status(self):
        ready = self.state == Manager.State.READY
        in_progress = self.state == Manager.State.PRINTING or self.state == Manager.State.ENDING
        status = {'ready': ready, 'in_progress': in_progress,
                  'paused': self.is_paused, 'name': self.name,
                  'current_layer': self.current_layer + 1,
                  'max_layer': len(self.layers)}

        with open(constants.PRINTER_STATUS, 'w') as file:
            json.dump(status, file)

        self.drivers.print_LCD(line1=self.state.value)

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
            print('WARNING: tried to upload file while printing')
            return 1

        self.layers = parse_svg(constants.SVG_FILE)

        with open(constants.SVG_NAME, 'r') as file:
            self.name = file.read()

        printable = self.check_printable()

        if not printable:
            print('INFO: svg too big for printing area')
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

                else:
                    print('WARNING: unknown event - {}'.format(event))

        except queue.Empty:
            pass

        if self.state == Manager.State.PRINTING:
            if not self.is_paused:
                if self.motor_status is not None:
                    if self.motor_status.done:
                        self.project_layer()
                        self.save_status()
                        self.motor_status = None

                    elif self.motor_status.aborted:
                        self.emergency_stop()

                elif time.time() - self.layer_timestamp > self.layer_exposition_time:
                    self.window.clear()
                    self.current_layer += 1

                    if self.current_layer >= len(self.layers):
                        if os.path.exists(constants.LAYER_PNG):
                            os.remove(constants.LAYER_PNG)
                        self.state = Manager.State.ENDING

                        print('INFO: print finished')

                    else:
                        dz = float(
                            self.layers[self.current_layer].getchildren()[-1].get(
                                '{http://slic3r.org/namespaces/slic3r}layer-height'))
                        self.layer_exposition_time = dz * constants.EXPOSITION_TIME_PER_MM

                        self.motor_status = self.drivers.move_plate(dz,
                            speed_mode=constants.SpeedMode.SLOW)

        elif self.state == Manager.State.ENDING:
            # TODO move the plate to the top
            self.motor_status = None
            self.state = Manager.State.WAITING
            self.save_status()
            print('INFO: waiting for reset')

        elif self.state == Manager.State.WAITING:
            # TODO catch button reset to move the plate to the ready position
            if self.motor_status is not None:
                if self.motor_status.done:
                    self.motor_status = None
                    self.state = Manager.State.READY
                    print('INFO: printer ready')
                elif self.motor_status.aborted:
                    self.emergency_stop()

    def start(self):
        if len(self.layers) == 0:
            # return error code if the layers are not loaded
            print('WARNING: tried to start printing with no layers loaded')
            return 1

        elif self.state != Manager.State.READY:
            print('WARNING: tried to start printing while not ready')
            return 2

        else:
            self.state = Manager.State.PRINTING
            self.reset_status(purge=False)
            print('INFO: starting to print - {}'.format(self.name))
            return 0

    def pause(self):
        if self.state != Manager.State.PRINTING:
            print('WARNING: tried to pause while not printing')
            return 1

        elif self.is_paused:
            print('WARNING: tried to pause while already paused')
            return 2

        else:
            self.window.clear()
            timestamp = time.time()
            self.is_paused = True
            self.save_status()
            self.paused_exposition = timestamp - self.layer_timestamp

            print('INFO: print paused')
            return 0

    def resume(self):
        if self.state != Manager.State.PRINTING:
            print('WARNING: tried to resume while not printing')
            return 1

        elif not self.is_paused:
            print('WARNING: tried to resume while already running')
            return 2

        else:
            self.is_paused = False
            self.save_status()
            self.project_layer()
            self.layer_timestamp -= self.paused_exposition

            print('INFO: print resumed')
            return 0

    def abort(self):
        if self.state == Manager.State.PRINTING or self.state == Manager.State.READY:
            self.motor_status = None
            self.state = Manager.State.ENDING
            self.window.clear()
        self.reset_status(purge=True)
        print('INFO: aborting print')

    def emergency_stop(self):
        self.motor_status = None
        self.state = Manager.State.EMERGENCY
        self.window.clear()
        self.reset_status(purge=True)
        print('WARNING: emergency stop triggered')
