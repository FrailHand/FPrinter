import os
import shutil

import pyramid.httpexceptions as exc
from pyramid.path import AssetResolver
from pyramid.response import FileResponse
from pyramid.view import view_config

from fprinter.frontend import access_provider
from fprinter.frontend import backend_socket
from fprinter.backend import constants
from fprinter.backend.svg_slice_lib import check_valid_slic3r_svg

templates_path = AssetResolver('fprinter.frontend').resolve('templates').abspath()


def template(file):
    return os.path.join(templates_path, file)


@view_config(route_name='home', renderer='templates/index.jinja2')
def home(request):
    return {'granted': access_provider.allow(request.session)}


@view_config(route_name='status')
def status(request):
    return FileResponse(constants.PRINTER_STATUS)


@view_config(route_name='layer')
def layer(request):
    if os.path.exists(constants.LAYER_PNG):
        return FileResponse(constants.LAYER_PNG)

    else:
        raise exc.HTTPFound("/static/void.png")


@view_config(route_name='ping', renderer='json')
def ping(request):
    if access_provider.allow(request.session):
        return {'valid': True, 'interval': constants.UI_PING_INTERVAL}

    else:
        return {'valid': False, 'error': 'unauthorized session',
                'interval': constants.UI_PING_INTERVAL}


@view_config(route_name='buttons', renderer='json')
def buttons(request):
    if not access_provider.allow(request.session):
        return {'valid': False, 'error': 'unauthorized session'}

    type = request.matchdict['type']
    if type == 'start':
        try:
            backend_response = backend_socket.request(
                constants.MessageCode.START_BUTTON)
            if backend_response == constants.MessageCode.CONFIRM:
                return {'valid': True}
            else:
                return {'valid': False, 'error': 'failed to start printing'}

        except Exception as e:
            return {'valid': False, 'error': str(e)}

    elif type == 'pause':
        try:
            backend_response = backend_socket.request(
                constants.MessageCode.PAUSE_BUTTON)
            if backend_response == constants.MessageCode.CONFIRM:
                return {'valid': True}
            else:
                return {'valid': False, 'error': 'failed to pause printing'}

        except Exception as e:
            return {'valid': False, 'error': str(e)}

    elif type == 'resume':
        try:
            backend_response = backend_socket.request(
                constants.MessageCode.RESUME_BUTTON)
            if backend_response == constants.MessageCode.CONFIRM:
                return {'valid': True}
            else:
                return {'valid': False, 'error': 'failed to resume printing'}

        except Exception as e:
            return {'valid': False, 'error': str(e)}

    elif type == 'abort':
        try:
            backend_response = backend_socket.request(
                constants.MessageCode.ABORT_BUTTON)
            if backend_response == constants.MessageCode.CONFIRM:
                return {'valid': True}
            else:
                return {'valid': False, 'error': 'failed to abort printing'}

        except Exception as e:
            return {'valid': False, 'error': str(e)}

    else:
        return {'valid': False, 'error': 'invalid button name'}


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

    backend_response = backend_socket.request(constants.MessageCode.FILE_LOADED)
    if backend_response == constants.MessageCode.CONFIRM:
        return {'valid': True, 'name': files.filename}
    else:
        return {'valid': False, 'error': 'too big for printing area'}
