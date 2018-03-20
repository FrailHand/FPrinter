from enum import Enum, auto
import os

# for the socket communication
MAIN_DIR = '/tmp/fprinter'
MAIN_SOCKET = os.path.join(MAIN_DIR, 'main_socket')
ALIVE_SOCKET = os.path.join(MAIN_DIR, 'alive_socket')
IDENTITY_HEADER = b'FPrinter'
CONFIRMATION_MESSAGE = b'1'

SVG_FILE = os.path.join(MAIN_DIR, 'layers.svg')
SVG_NAME = os.path.join(MAIN_DIR, 'svg_name')
PRINTER_STATUS = os.path.join(MAIN_DIR, 'status.dict')

UI_PING_INTERVAL = 1
SESSION_AUTH_KEY = 'auth_ID'

class message_code:
    '''
    Message codes for the unix communication
    '''
    FILE_LOADED = b'loaded'
    START_BUTTON = b'start'
    PAUSE_BUTTON = b'pause'
    RESUME_BUTTON = b'resume'
    ABORT_BUTTON = b'abort'
    CONFIRM = b'OK'
    REFUSE = b'KO'


class event(Enum):
    '''
    Event numbers definition for the event handlers
    '''

    FILE_LOADED = auto()
    START_PRINTING = auto()
    ABORT = auto()
    PAUSE = auto()
    RESUME = auto()
