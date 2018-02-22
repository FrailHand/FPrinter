from  pyramid.view import view_config
from pyramid.response import Response

@view_config(route_name='home')
def home(request):
    return Response('<body><h1>FPrinter home page</h1></body>')
