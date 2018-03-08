import signal


def main():
    '''The main routine.'''

    import pyglet
    from fprinter.backend.window import Window

    print('\nLaunching the FPrinter backend\n')

    window = Window()

    def signal_handler(signal, frame):
        print('\n\nKeyboard interrupt\n')
        window.on_close()

    signal.signal(signal.SIGINT, signal_handler)

    pyglet.app.run()


if __name__ == '__main__':
    main()
