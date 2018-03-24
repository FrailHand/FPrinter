import signal
import pyglet
from .manager import Manager
from .constants import Event


def main():
    """The main routine."""

    print('\nLaunching the FPrinter backend\n')

    manager = Manager()

    def signal_handler(signal, frame):
        print('\nINFO: Keyboard interrupt')
        manager.fire_event((Event.EXIT,))

    signal.signal(signal.SIGINT, signal_handler)
    pyglet.app.run()

    print('INFO: successfully terminated backend')


if __name__ == '__main__':
    main()
