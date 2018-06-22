import os
from enum import Enum, auto

# files and sockets
MAIN_DIR = '/tmp/fprinter'

if not os.path.isdir(MAIN_DIR):
    os.mkdir(MAIN_DIR)

MAIN_SOCKET = os.path.join(MAIN_DIR, 'main_socket')
ALIVE_SOCKET = os.path.join(MAIN_DIR, 'alive_socket')

SVG_FILE = os.path.join(MAIN_DIR, 'layers.svg')
SVG_NAME = os.path.join(MAIN_DIR, 'svg_name.txt')
PRINTER_STATUS = os.path.join(MAIN_DIR, 'status.json')
LAYER_PNG = os.path.join(MAIN_DIR, 'layer.png')

# unix socket parameters
PAYLOAD_SIZE = 8
TIMEOUT = 5

# session authentication
UI_PING_INTERVAL = 1

# printer parameters
EXPOSITION_TIME_PER_MM = 5
PROJECTOR_DPI = 96

# these are used to position the plate to the top, the bottom or the printing position
PRINTER_HEIGHT = 0.3
PRINTING_AREA_HEIGHT = 50

# number of step of the motor for 1 revolution
MOTOR_STEP_PER_REVOLUTION = 200


class Pin:
    MOTOR_DIR = 20
    MOTOR_STEP = 21

    BUTTON_EMERGENCY = 5
    BUTTON_RESET = 6


class SpeedMode:
    SLOW = 0.140
    MEDIUM = 0.080
    FAST = 0.040


class MessageCode:
    """
    Message codes for the unix communication
    """
    IDENTITY_HEADER = b'FPrinter'

    FILE_LOADED = b'loaded'
    START_BUTTON = b'start'
    PAUSE_BUTTON = b'pause'
    RESUME_BUTTON = b'resume'
    ABORT_BUTTON = b'abort'

    CONFIRM = b'OK'
    REFUSE = b'KO'


class Event(Enum):
    """
    Event numbers definition for the event handlers
    """
    FILE_UPLOADED = auto()
    START_UI = auto()
    ABORT_UI = auto()
    PAUSE_UI = auto()
    RESUME_UI = auto()

    EMERGENCY_BTN = auto()
    RESET_BTN = auto()

    PROJECTOR_ERROR = auto()

    OVERHEAT = auto()

    EXIT = auto()


class ProjectorStatus(Enum):
    OFF = auto()
    ON = auto()
    WAITING = auto()
    ERROR = auto()
