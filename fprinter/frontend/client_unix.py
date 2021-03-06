import socket
import threading

from fprinter.backend import constants


class Client():
    def __init__(self):
        self.backend_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.mutex = threading.Lock()

    def connect(self):
        # connect to the backend

        self.backend_socket.connect(constants.MAIN_SOCKET)

        # exchange identification headers
        self.backend_socket.send(constants.MessageCode.IDENTITY_HEADER)
        self.backend_socket.settimeout(constants.TIMEOUT)
        try:
            confirmation = self.backend_socket.recv(constants.PAYLOAD_SIZE)
            if not confirmation or confirmation != constants.MessageCode.CONFIRM:
                raise Exception('ERROR: invalid backend response')

        except socket.timeout:
            raise Exception('no answer from backend')

    def request(self, message):
        # send a message and wait for answer
        with self.mutex:
            self.backend_socket.send(message)

            return self.backend_socket.recv(constants.PAYLOAD_SIZE)
