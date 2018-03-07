def main():
    '''The main routine.'''

    import pyglet
    from fprinter.backend.window import Window

    print('\nLaunching the FPrinter backend\n')

    Window()
    pyglet.app.run()


if __name__ == '__main__':
    main()
