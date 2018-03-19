import socket
import threading

from ..backend import constants


class Client():
    def __init__(self):
        self.backend_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.mutex = threading.Lock()

    def connect(self):
        # connect to the backend

        self.backend_socket.connect(constants.MAIN_SOCKET)

        # exchange identification headers
        self.backend_socket.send(constants.IDENTITY_HEADER)
        self.backend_socket.settimeout(5)
        try:
            confirmation = self.backend_socket.recv(8)
            if not confirmation or confirmation != constants.CONFIRMATION_MESSAGE:
                raise Exception('ERROR: invalid backend response')

        except socket.timeout:
            raise Exception('no answer from backend')

    def request(self, message):
        # send a message and wait for answer
        with self.mutex:
            self.backend_socket.send(message)

            return self.backend_socket.recv(8)

    def send(self, message):
        # send a message without waiting for answer
        # NO RESPONSE SHOULD BE SENT it could break the pipeline
        with self.mutex:
            self.backend_socket.send(message)


