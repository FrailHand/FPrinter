from pyramid.config import Configurator
from . import client_unix

backend_socket = client_unix.Client()


def main(global_config, **settings):
    print('\nLaunching the FPrinter frontend\n')

    print('Connecting to backend...')
    try:
        backend_socket.connect()
    except Exception as e:
        print('ERROR: connecting to backend socket - {}'.format(e))
        exit(1)

    print('Success\n')

    config = Configurator(settings=settings)
    config.add_route('home', '/')
    config.add_route('upload', '/upload')
    config.add_route('buttons', '/button/{type}')
    config.scan('.views')
    config.add_static_view(name='static', path='fprinter.frontend:static')
    return config.make_wsgi_app()
