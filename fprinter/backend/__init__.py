import signal
import pyglet
from .printer import Printer
from .constants import Event


def main():
    '''The main routine.'''

    print('\nLaunching the FPrinter backend\n')

    printer = Printer()

    def signal_handler(signal, frame):
        print('\nINFO: Keyboard interrupt')
        printer.fire_event((Event.EXIT,))

    signal.signal(signal.SIGINT, signal_handler)
    pyglet.app.run()

    print('INFO: successfully terminated backend')


if __name__ == '__main__':
    main()
