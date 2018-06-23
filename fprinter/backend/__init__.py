def main():
    """The main routine."""

    import platform

    fullscreen = True
    if platform.machine() == 'x86_64':
        # this allows to run the code on non-raspberry machines
        # DEVELOPMENT PURPOSE ONLY
        import sys
        import fake_rpi
        from fprinter.tests import fake_rpi_serial
        from fprinter.tests import fake_adafruit_dht

        sys.modules['RPi'] = fake_rpi.RPi
        sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
        sys.modules['smbus'] = fake_rpi.smbus
        sys.modules['serial'] = fake_rpi_serial
        sys.modules['Adafruit_DHT'] = fake_adafruit_dht

        fullscreen = False

    import signal
    import pyglet
    from fprinter.backend.manager import Manager
    from fprinter.backend.constants import Event

    print('\nLaunching the FPrinter backend\n')

    print_manager = Manager(fullscreen=fullscreen)

    def signal_handler(signal_name, frame):
        print('\nINFO: Keyboard interrupt')
        print_manager.fire_event((Event.EXIT,))

    signal.signal(signal.SIGINT, signal_handler)
    pyglet.app.run()

    print('INFO: successfully terminated backend')


if __name__ == '__main__':
    main()
