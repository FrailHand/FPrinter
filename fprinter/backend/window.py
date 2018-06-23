from pyglet.gl import *

from fprinter.backend.constants import Event


class Window(pyglet.window.Window):

    def __init__(self, event_listener, fullscreen=True):
        super().__init__(caption='FPrinter', resizable=False, fullscreen=fullscreen)

        self.set_mouse_visible(False)
        self.fire_event = event_listener

    def on_close(self):
        self.fire_event((Event.EXIT,))
