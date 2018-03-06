from pyramid.config import Configurator                                         
                                                                                
                                                                                
def main(global_config, **settings):
    print('\nLaunching the FPrinter frontend\n')
    config = Configurator(settings=settings)
    config.add_route('home', '/')
    config.add_route('upload', '/upload')
    config.scan('.views')
    config.add_static_view(name='static', path='fprinter.frontend:static')
    return config.make_wsgi_app()       
