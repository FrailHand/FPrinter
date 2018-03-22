from pyglet.gl import *
from .constants import Event

class Window(pyglet.window.Window):

    def __init__(self, fire_event):
        super().__init__(caption='FPrinter', resizable=False, fullscreen=False)

        self.set_mouse_visible(False)
        self.fire_event = fire_event

    def on_close(self):
        self.fire_event(Event.WINDOW_CLOSE)
