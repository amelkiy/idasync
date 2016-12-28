from socket import *
from Common.Logger import Logger
from Server.IdaSyncClient import IdaSyncClient
from VersionsManager.VersionsManager import VersionsManager

class IdaSyncServer(object):
    def __init__(self, port):
        self._port = port
        self._sock = None
        VersionsManager.init_server()

    def _init_socket(self):
        self._sock = socket()
        self._sock.bind(('0.0.0.0', self._port))
        self._sock.listen(256)

    def serve_forever(self):
        if not self._sock:
            self._init_socket()

        while 1:
            accepted_socket, address = self._sock.accept()
            client_id = randim.randint(100000, 1000000)
            Logger.info("Accepted a connection from %s. Client id: %d" % (address, client_id))
            IdaSyncClient.start_threaded(accepted_socket, client_id)
