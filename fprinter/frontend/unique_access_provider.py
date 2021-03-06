import random
import threading
import time

from fprinter.backend import constants


class Unique():
    SESSION_AUTH_KEY = 'auth_ID'

    def __init__(self):
        self.mutex = threading.Lock()
        self.last_ping = -1
        self.authorized_ID = -1

    def request_ID(self):
        with self.mutex:
            current = time.time()
            if current - self.last_ping > 3 * constants.UI_PING_INTERVAL:
                self.last_ping = current
                self.authorized_ID = random.randint(1, 99999)
                return self.authorized_ID

        return 0

    def allow(self, session):
        if Unique.SESSION_AUTH_KEY in session:
            with self.mutex:
                if self.authorized_ID == session[Unique.SESSION_AUTH_KEY]:
                    self.last_ping = time.time()
                    return True

        ID = self.request_ID()
        if ID != 0:
            session[Unique.SESSION_AUTH_KEY] = ID
            return True

        return False
