from enum import Enum, auto
import os

# files and sockets
MAIN_DIR = '/tmp/fprinter'

if not os.path.isdir(MAIN_DIR):
    os.mkdir(MAIN_DIR)

MAIN_SOCKET = os.path.join(MAIN_DIR, 'main_socket')
ALIVE_SOCKET = os.path.join(MAIN_DIR, 'alive_socket')

SVG_FILE = os.path.join(MAIN_DIR, 'layers.svg')
SVG_NAME = os.path.join(MAIN_DIR, 'svg_name')
PRINTER_STATUS = os.path.join(MAIN_DIR, 'status.dict')
LAYER_PNG = os.path.join(MAIN_DIR, 'layer.png')

# unix socket parameters
PAYLOAD_SIZE = 8
TIMEOUT = 5

# session authentication
UI_PING_INTERVAL = 1
SESSION_AUTH_KEY = 'auth_ID'

# printer parameters
EXPOSITION_TIME = 0.125


class MessageCode:
    '''
    Message codes for the unix communication
    '''
    IDENTITY_HEADER = b'FPrinter'

    FILE_LOADED = b'loaded'
    START_BUTTON = b'start'
    PAUSE_BUTTON = b'pause'
    RESUME_BUTTON = b'resume'
    ABORT_BUTTON = b'abort'

    CONFIRM = b'OK'
    REFUSE = b'KO'


class Event(Enum):
    '''
    Event numbers definition for the event handlers
    '''
    FILE_UPLOADED = auto()
    START_UI = auto()
    ABORT_UI = auto()
    PAUSE_UI = auto()
    RESUME_UI = auto()

    EXIT = auto()
