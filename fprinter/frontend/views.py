from pyramid.view import view_config
from pyramid.response import FileResponse
from pyramid.path import AssetResolver
import pyramid.httpexceptions as exc

import os
import shutil

from . import backend_socket
from ..backend.svg_slice_lib import check_valid_slic3r_svg

templates_path = AssetResolver('fprinter.frontend').resolve('templates').abspath()


def template(file):
    return os.path.join(templates_path, file)


@view_config(route_name='home')
def home(request):
    return FileResponse(template('index.html'))


@view_config(route_name='upload', renderer='json')
def upload(request):
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

    file_path = os.path.join('/tmp', 'print.svg')
    temp_file = file_path + '~'

    input_file.seek(0)
    with open(temp_file, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)

    os.rename(temp_file, file_path)

    return {'valid': True, 'name': files.filename}
