from . import constants
from .svg_slice_lib import parse_svg


class Printer():
    def __init__(self):
        self.layers = None
        self.name = ''
        self.printing_in_progress = False

    def load_svg(self):
        self.layers = parse_svg(constants.SVG_FILE)
        with open(constants.SVG_NAME, 'r') as file:
            self.name = file.read()

    def start(self):
        if self.layers is None:
            # return error code if the layers are not loaded
            print('WARNING: tried to start printing with no layers loaded')
            return 1

        elif self.printing_in_progress:
            print('WARNING: tried to start printing while already running')
            return 2

        else:
            print('INFO: starting to print - {}'.format(self.name))
            self.printing_in_progress = True

            # TODO start the printing process

            return 0

    def abort(self):
        self.printing_in_progress = False
        # TODO abort printing
        print('INFO: aborting print')
