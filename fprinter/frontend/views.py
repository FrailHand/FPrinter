from  pyramid.view import view_config
from pyramid.response import FileResponse, Response

@view_config(route_name='home')
def home(request):
    return FileResponse('templates/index.html')

@view_config(route_name='upload', renderer='json')
def upload(request):
    files= request.POST['files[]']
    print(help(files))
    print(files.name)
    return {'test':'value'}