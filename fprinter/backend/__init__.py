def main():
    """The main routine."""

    import platform
    import logging


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

        logging.basicConfig(format='%(levelname)s:%(module)s.%(funcName)s:%(message)s',
                            level=logging.DEBUG)
        logging.warning('using fake RPi interfaces')

    else:
        logging.basicConfig(filename='/tmp/fprinter_backend.log',
                            format='%(levelname)s:%(module)s.%(funcName)s:%(message)s',
                            level=logging.DEBUG)

    import signal
    import pyglet
    from fprinter.backend.manager import Manager
    from fprinter.backend.constants import Event
    from subprocess import call

    logging.info('launching the FPrinter backend')

    print_manager = Manager(fullscreen=fullscreen)

    def signal_handler(signal_name, frame):
        logging.info('keyboard interrupt')
        print_manager.fire_event((Event.EXIT,))

    signal.signal(signal.SIGINT, signal_handler)
    pyglet.app.run()

    logging.info('successfully terminated backend')

    if print_manager.system_halt:
        logging.info('shutting down system')
        call('sudo halt', shell=True)


if __name__ == '__main__':
    main()
