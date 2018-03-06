from  pyramid.view import view_config
from pyramid.response import FileResponse, Response
import pyramid.httpexceptions as exc

import os
import zipfile
import shutil

@view_config(route_name='home')
def home(request):
    return FileResponse('templates/index.html')

@view_config(route_name='upload', renderer='json')
def upload(request):
    if request.content_length >= 1e9:
        return{'valid':False,'error':'file too big'}
    
    if not 'files[]' in request.POST:
        raise exc.HTTPForbidden()
    files= request.POST['files[]']

    extension = files.filename.split('.')[-1]
    if extension != 'zip':
        return {'valid':False, 'error':'invalid format: {}'.format(extension)}
    
    input_file = files.file

    try:
        with zipfile.ZipFile(input_file) as myzip:
            print(myzip.infolist())
            print('TODO: check that the file is valid for printing')
            
    except zipfile.BadZipFile as e:
        return {'valid':False, 'error':str(e)}
    
    file_path = os.path.join('/tmp','bidon.zip')
    temp_file = file_path+'~'

    input_file.seek(0)
    with open(temp_file, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)

    os.rename(temp_file, file_path)
    
    return {'valid':True, 'name':files.filename}
