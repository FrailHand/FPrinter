import queue

import pyglet
from pyglet.gl import *

from . import constants

class Window(pyglet.window.Window):

    def __init__(self):
        super().__init__(caption='FPrinter', resizable=False, fullscreen=True)

        self.set_mouse_visible(False)

        pyglet.clock.schedule_interval(self.update, interval=1 / 60)

        self.event_queue = queue.Queue()


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


