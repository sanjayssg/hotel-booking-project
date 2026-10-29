import threading


class KeyedLocks:
    def __init__(self):
        self._locks = {}
        self._guard = threading.Lock()

    def for_key(self, key):
        with self._guard:
            return self._locks.setdefault(key, threading.Lock())
