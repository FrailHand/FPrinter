from . import constants
from .svg_slice_lib import parse_svg
import json


class Printer():
    def __init__(self):
        self.reset()

    def reset(self):
        self.layers = []
        self.name = ''
        self.printing_in_progress = False
        self.is_paused = False
        self.current_layer = -1

        self.save_status()

    def save_status(self):
        status = {'in_progress': self.printing_in_progress, 'paused': self.is_paused,
                  'name': self.name, 'current_layer': self.current_layer + 1,
                  'max_layer': len(self.layers)}

        with open(constants.PRINTER_STATUS, 'w') as file:
            json.dump(status, file)

    def load_svg(self):
        self.layers = parse_svg(constants.SVG_FILE)
        with open(constants.SVG_NAME, 'r') as file:
            self.name = file.read()
        self.save_status()

    def start(self):
        if len(self.layers) is 0:
            # return error code if the layers are not loaded
            print('WARNING: tried to start printing with no layers loaded')
            return 1

        elif self.printing_in_progress:
            print('WARNING: tried to start printing while already running')
            return 2

        else:
            print('INFO: starting to print - {}'.format(self.name))
            self.printing_in_progress = True
            self.is_paused = False
            self.current_layer = -1

            self.save_status()

            # TODO start the printing process

            return 0

    def pause(self):
        if not self.printing_in_progress:
            print('WARNING: tried to pause while not printing')
            return 1

        elif self.is_paused:
            print('WARNING: tried to pause while already paused')
            return 2

        else:
            self.is_paused = True
            print('INFO: print paused')
            self.save_status()
            # TODO pause the print
            return 0

    def resume(self):
        if not self.printing_in_progress:
            print('WARNING: tried to resume while not printing')
            return 1

        elif not self.is_paused:
            print('WARNING: tried to resume while already running')
            return 2

        else:
            self.is_paused = False
            print('INFO: print resumed')
            self.save_status()
            # TODO resume the print
            return 0

    def abort(self):
        self.reset()

        self.save_status()

        # TODO abort printing
        print('INFO: aborting print')
