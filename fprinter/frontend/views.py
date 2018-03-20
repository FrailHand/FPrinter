from pyramid.view import view_config
from pyramid.response import FileResponse
from pyramid.path import AssetResolver
import pyramid.httpexceptions as exc

import os
import shutil

from . import backend_socket
from . import access_provider
from ..backend import constants
from ..backend.svg_slice_lib import check_valid_slic3r_svg

templates_path = AssetResolver('fprinter.frontend').resolve('templates').abspath()


def template(file):
    return os.path.join(templates_path, file)


@view_config(route_name='home')
def home(request):
    if access_provider.allow(request.session):
        return FileResponse(template('index.html'))

    else:
        return FileResponse(template('index_busy.html'))


@view_config(route_name='status')
def status(request):
    return FileResponse(constants.PRINTER_STATUS)

@view_config(route_name='ping', renderer='json')
def ping(request):
    if access_provider.allow(request.session):
        return {'valid': True}

    else:
        return {'valid': False, 'error': 'unauthorized session'}


@view_config(route_name='buttons', renderer='json')
def buttons(request):
    if not access_provider.allow(request.session):
        return {'valid': False, 'error': 'unauthorized session'}

    type = request.matchdict['type']
    if type == 'start':
        try:
            backend_response = backend_socket.request(constants.message_code.START_BUTTON)
            if backend_response == constants.message_code.CONFIRM:
                return {'valid': True}
            else:
                return {'valid': False, 'error': 'failed to start printing'}

        except Exception as e:
            return {'valid': False, 'error':str(e)}

    elif type=='pause':
        try:
            backend_response = backend_socket.request(constants.message_code.PAUSE_BUTTON)
            if backend_response == constants.message_code.CONFIRM:
                return {'valid': True}
            else:
                return {'valid': False, 'error': 'failed to pause printing'}

        except Exception as e:
            return {'valid': False, 'error':str(e)}

    elif type=='resume':
        try:
            backend_response = backend_socket.request(constants.message_code.RESUME_BUTTON)
            if backend_response == constants.message_code.CONFIRM:
                return {'valid': True}
            else:
                return {'valid': False, 'error': 'failed to resume printing'}

        except Exception as e:
            return {'valid': False, 'error':str(e)}

    elif type=='abort':
        try:
            backend_response = backend_socket.request(constants.message_code.ABORT_BUTTON)
            if backend_response == constants.message_code.CONFIRM:
                return {'valid': True}
            else:
                return {'valid': False, 'error': 'failed to abort printing'}

        except Exception as e:
            return {'valid': False, 'error':str(e)}

    else:
        return {'valid': False, 'error':'invalid button name'}


@view_config(route_name='upload', renderer='json')
def upload(request):
    if not access_provider.allow(request.session):
        return {'valid': False, 'error': 'unauthorized session'}

    if request.content_length >= 1e9:
        return {'valid': False, 'error': 'file too big'}

    if not 'files[]' in request.POST:
        raise exc.HTTPForbidden()
    files = request.POST['files[]']

    extension = files.filename.split('.')[-1]
    if extension != 'svg':
        return {'valid': False, 'error': 'invalid format: {}'.format(extension)}

    input_file = files.file

    if check_valid_slic3r_svg(input_file) != 0:
        return {'valid': False, 'error': 'invalid svg syntax'}

    temp_file = constants.SVG_FILE + '~'

    input_file.seek(0)
    with open(temp_file, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)

    os.rename(temp_file, constants.SVG_FILE)

    with open(constants.SVG_NAME, 'w') as output_file:
        output_file.write(files.filename)

    backend_socket.send(constants.message_code.FILE_LOADED)

    return {'valid': True, 'name': files.filename}
