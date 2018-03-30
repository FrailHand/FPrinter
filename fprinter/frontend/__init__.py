from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory

from . import client_unix
from . import unique_access_provider

backend_socket = client_unix.Client()
access_provider = unique_access_provider.Unique()


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

    # use cookies for session information
    session_factory = SignedCookieSessionFactory('fy3JUe.4')
    config.set_session_factory(session_factory)

    # use jinja for templating
    config.include('pyramid_jinja2')

    config.add_route('home', '/')
    config.add_route('upload', '/upload')
    config.add_route('status', '/status')
    config.add_route('layer', '/layer.png')
    config.add_route('ping', '/ping')
    config.add_route('buttons', '/button/{type}')
    config.scan('.views')
    config.add_static_view(name='static', path='fprinter.frontend:static')
    return config.make_wsgi_app()
