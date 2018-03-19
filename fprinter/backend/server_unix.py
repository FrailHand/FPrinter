import socket
import os
import time

import threading
import queue

from . import constants
from .constants import event, message_code


class Server():

    def __init__(self, event_listener):
        if not os.path.isdir(constants.MAIN_DIR):
            os.mkdir(constants.MAIN_DIR)

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

            except socket.error as e:
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
                connection.settimeout(5)
                try:
                    received_data = connection.recv(8)
                except socket.timeout:
                    connection.close()
                    print('WARNING: Connection timed out')
                    continue

                if not received_data or received_data != constants.IDENTITY_HEADER:
                    connection.close()
                    print('WARNING: Invalid header')
                    continue

                print('INFO: Connection accepted!')
                connection.send(constants.CONFIRMATION_MESSAGE)

                with self._queue.mutex:
                    self._queue.queue.clear()

                connection.setblocking(False)

                while self.running:

                    # receive incoming data
                    try:
                        received_data = connection.recv(16)
                        if received_data:

                            if received_data == message_code.FILE_LOADED:
                                self.fire_event(event.FILE_LOADED)

                            elif received_data == message_code.START_BUTTON:
                                self.fire_event(event.START_PRINTING)

                            elif received_data == message_code.PAUSE_BUTTON:
                                self.fire_event(event.PAUSE)

                            elif received_data == message_code.RESUME_BUTTON:
                                self.fire_event(event.RESUME)

                            elif received_data == message_code.ABORT_BUTTON:
                                self.fire_event(event.ABORT)

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
