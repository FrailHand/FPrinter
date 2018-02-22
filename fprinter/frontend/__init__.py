from pyramid.config import Configurator                                         
                                                                                
                                                                                
def main(global_config, **settings):
    print('\nLaunching the FPrinter frontend\n')
    config = Configurator(settings=settings)                                    
    config.include('pyramid_jinja2')                                            
    config.add_route('home', '/')                                               
    config.scan('.views')                                                       
    return config.make_wsgi_app()       
