from pyglet.gl import *

from fprinter.backend.constants import Event
from fprinter.backend import FULLSCREEN


class Window(pyglet.window.Window):

    def __init__(self, event_listener):
        super().__init__(caption='FPrinter', resizable=False, fullscreen=FULLSCREEN)

        self.set_mouse_visible(False)
        self.fire_event = event_listener

    def on_close(self):
        self.fire_event((Event.EXIT,))
