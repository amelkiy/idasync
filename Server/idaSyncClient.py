from thread import start_new_thread


class IdaSyncClient(object):
    def __init__(self, sock):
        self._sock = sock
        self._init_queue()

    def _init_queue(self):
        pass

    @classmethod
    def start_threaded(cls, sock):
        start_new_thread(cls._run, (sock.dup(),))

    @classmethod
    def _run(cls, sock):
        # This runs in a new thread
        IdaSyncClient(sock).start()

    def start(self):
        pass