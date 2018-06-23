import os
import queue
import socket
import threading
import time

from fprinter.backend import constants
from fprinter.backend.constants import Event, MessageCode


class Server:

    def __init__(self, event_listener):

        self.alive_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.alive_socket.setblocking(False)

        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.setblocking(False)

        self.running = False
        self._queue = queue.Queue()

        self.fire_event = event_listener

    def send(self, message):
        self._queue.put(message, block=False)

    def start(self):

        if os.path.exists(constants.ALIVE_SOCKET):
            print('WARNING: alive socket exists - checking status ...')
            # check if the server is already running
            try:
                self.alive_socket.connect(constants.ALIVE_SOCKET)
                self.alive_socket.close()
                raise Exception('backend already running (socket in use)')

            except socket.error:
                pass

            try:
                os.unlink(constants.ALIVE_SOCKET)
            except OSError as e:
                raise Exception('unlink socket - {}'.format(e))

        if os.path.exists(constants.MAIN_SOCKET):
            print('WARNING: server socket exists - deleting')
            try:
                os.unlink(constants.MAIN_SOCKET)
            except OSError as e:
                raise Exception('unlink socket - {}'.format(e))

        self.running = True

        # just a small socket to show the program is running
        self.alive_thread = threading.Thread(target=self.alive)
        self.alive_thread.start()

        # the main socket for communication with the UI
        self.accept_thread = threading.Thread(target=self.serve)
        self.accept_thread.start()

    def alive(self):
        # just allow incoming connections to show we are alive, then close immediately
        self.alive_socket.bind(constants.ALIVE_SOCKET)
        self.alive_socket.listen()

        while self.running:
            try:
                connection, client = self.alive_socket.accept()
                connection.close()
                print('INFO: Alive socket triggered')

            except BlockingIOError:
                time.sleep(1)
        self.alive_socket.close()

    def serve(self):
        self.server_socket.bind(constants.MAIN_SOCKET)
        self.server_socket.listen()

        while self.running:
            try:
                connection, client = self.server_socket.accept()
                print('INFO: Connection incoming')

                # the real UI must send the identification header within 5 seconds
                connection.settimeout(constants.TIMEOUT)
                try:
                    received_data = connection.recv(constants.PAYLOAD_SIZE)
                except socket.timeout:
                    connection.close()
                    print('WARNING: Connection timed out')
                    continue

                if not received_data or received_data != MessageCode.IDENTITY_HEADER:
                    connection.close()
                    print('WARNING: Invalid header')
                    continue

                print('INFO: Connection accepted!')
                connection.send(MessageCode.CONFIRM)

                with self._queue.mutex:
                    self._queue.queue.clear()

                connection.setblocking(False)

                while self.running:

                    # receive incoming data
                    try:
                        received_data = connection.recv(constants.PAYLOAD_SIZE)
                        if received_data:

                            if received_data == MessageCode.FILE_LOADED:
                                self.fire_event((Event.FILE_UPLOADED,))

                            elif received_data == MessageCode.START_BUTTON:
                                self.fire_event((Event.START_UI,))

                            elif received_data == MessageCode.PAUSE_BUTTON:
                                self.fire_event((Event.PAUSE_UI,))

                            elif received_data == MessageCode.RESUME_BUTTON:
                                self.fire_event((Event.RESUME_UI,))

                            elif received_data == MessageCode.ABORT_BUTTON:
                                self.fire_event((Event.ABORT_UI,))

                            else:
                                print(
                                    'WARNING: unknown message on unix socket - {}'.format(
                                        received_data))

                        else:
                            break

                    except BlockingIOError:
                        pass

                    # send outgoing data
                    try:
                        message = self._queue.get(block=False)
                        connection.send(message)

                    except queue.Empty:
                        pass

                    # slow down the pace
                    time.sleep(0.1)

                connection.close()

            except BlockingIOError:
                time.sleep(1)

        self.server_socket.close()

    def stop(self):
        self.running = False
        self.alive_thread.join()
        self.accept_thread.join()

        try:
            os.unlink(constants.ALIVE_SOCKET)
        except OSError as e:
            print('ERROR: unlink socket - {}'.format(e))

        try:
            os.unlink(constants.MAIN_SOCKET)
        except OSError as e:
            print('ERROR: unlink socket - {}'.format(e))

        print('INFO: Sockets correctly cleaned')
