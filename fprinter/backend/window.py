import queue

import pyglet
from pyglet.gl import *

from . import server_unix
from .printer import Printer
from .constants import message_code


class Window(pyglet.window.Window):

    def __init__(self):
        super().__init__(caption='FPrinter', resizable=False, fullscreen=False)

        self.set_mouse_visible(False)

        self.event_queue = queue.Queue()
        self.printer = Printer(self)

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

        pyglet.clock.schedule_interval(self.update, interval=1 / 60)

    def fire_event(self, event):
        self.event_queue.put(event)

    def update(self, dt):

        try:
            while True:
                event = self.event_queue.get(block=False)
                if event == event.FILE_LOADED:
                    self.printer.load_svg()
                    print('INFO: layers successfully loaded')

                elif event == event.START_PRINTING:
                    ok = self.printer.start()
                    if ok == 0:
                        self.server.send(message_code.CONFIRM)
                    else:
                        self.server.send(message_code.REFUSE)

                elif event == event.PAUSE:
                    ok = self.printer.pause()
                    if ok == 0:
                        self.server.send(message_code.CONFIRM)
                    else:
                        self.server.send(message_code.REFUSE)

                elif event == event.RESUME:
                    ok = self.printer.resume()
                    if ok == 0:
                        self.server.send(message_code.CONFIRM)
                    else:
                        self.server.send(message_code.REFUSE)

                elif event == event.ABORT:
                    self.printer.abort()
                    self.server.send(message_code.CONFIRM)

                else:
                    print('WARNING: unknown event - {}'.format(event))

        except queue.Empty:
            pass

        self.printer.update()

    def on_close(self):
        super().on_close()
        print('INFO: Display closed')
        self.server.stop()
