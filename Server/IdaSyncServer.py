from socket import *
from Common.Logger import Logger
from Server.IdaSyncClient import IdaSyncClient


class IdaSyncServer(object):
    def __init__(self, port):
        self._port = port
        self._sock = None

    def _init_socket(self):
        self._sock = socket()
        self._sock.bind(('0.0.0.0', self._port))
        self._sock.listen(256)

    def serve_forever(self):
        if not self._sock:
            self._init_socket()

        while 1:
            accepted_socket, address = self._sock.accept()
            Logger.info("Accepted a connection from %s" % address)
            IdaSyncClient.start_threaded(accepted_socket)
