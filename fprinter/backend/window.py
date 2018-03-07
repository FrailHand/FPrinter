import queue

import pyglet
from pyglet.gl import *

import io
import cairosvg
import xml

from . import constants

class Window(pyglet.window.Window):

    def __init__(self):
        super().__init__(caption='FPrinter', resizable=False, fullscreen=True)

        self.set_mouse_visible(False)

        pyglet.clock.schedule_interval(self.update, interval=1 / 60)

        self.event_queue = queue.Queue()

        from fprinter.backend.svg_slice_lib import parse_svg
        layers = parse_svg('/idiap/temp/fmarelli/tmp/fprinter/fprinter/tests/print.svg')
        layer = layers[-1]

        stream = io.BytesIO()
        cairosvg.surface.PNGSurface.convert(bytestring=xml.etree.ElementTree.tostring(layer),
                                   write_to=stream, dpi=96, scale=1)
        image = pyglet.image.load('', file=stream)
        stream.close()
        
        self.test = pyglet.sprite.Sprite(image, x=self.width//2, y=self.height//2)


    def fire_event(self, event):
        self.event_queue.put(event)


    def update(self, dt):


        try:
            while True:
                event = self.event_queue.get(block=False)

        except queue.Empty:
            pass



    def on_draw(self):
        self.clear()
        self.test.draw()



