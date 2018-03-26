import queue

import pyglet

from .constants import Event
from .constants import MessageCode
from .window import Window
from .printer import Printer
from . import server_unix


class Manager():
    def __init__(self):
        self.event_queue = queue.Queue()

        self.window = Window(self.fire_event)
        self.printer = Printer(self.fire_event, window=self.window)

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

    def shutdown(self):
        print('INFO: shutting down printer...')
        self.server.stop()
        self.window.close()
        self.printer.shutdown()
        print('INFO: display closed')

    def fire_event(self, event):
        self.event_queue.put(event)

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
                    self.confirm_if_zero(self.printer.load_svg())

                elif event[0] == Event.START_UI:
                    self.confirm_if_zero(self.printer.start())

                elif event[0] == Event.PAUSE_UI:
                    self.confirm_if_zero(self.printer.pause())

                elif event[0] == Event.RESUME_UI:
                    self.confirm_if_zero(self.printer.resume())

                elif event[0] == Event.ABORT_UI:
                    self.printer.abort()
                    self.server.send(MessageCode.CONFIRM)

                else:
                    print('WARNING: unknown event - {}'.format(event))

        except queue.Empty:
            pass

        self.printer.update()
