from enum import Enum
import os

# for the socket communication
MAIN_DIR = '/tmp/fprinter'
MAIN_SOCKET = os.path.join(MAIN_DIR, 'main_socket')
ALIVE_SOCKET = os.path.join(MAIN_DIR, 'alive_socket')
IDENTITY_HEADER = b'FPrinter'
CONFIRMATION_MESSAGE = b'1'

SVG_FILE = os.path.join(MAIN_DIR, 'layers.svg')


class event(Enum):
    '''
    Event numbers definition for the event handlers
    '''

    pass
