from thread import start_new_thread

SERVER_ADDR = "2342323"

class IdaSyncClient(object):
    def __init__(self, change_callback):
        self._change_callback = change_callback
        self._sock = None

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