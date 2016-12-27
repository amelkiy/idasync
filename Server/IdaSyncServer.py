from socket import *
from ..Common.Logger import Logger
from IdaSyncClient import IdaSyncClient
from ..VersionsManager.VersionsManager import VersionsManager
from ..Common.utils import Utils
import random
import simplejson as json


class IdaSyncServer(object):
    def __init__(self, port):
        self._port = port
        self._sock = None
        self._version_manager = VersionsManager.get_instance()
        self._version_manager.init_server()

    def _init_socket(self):
        self._sock = socket()
        self._sock.bind(('0.0.0.0', self._port))
        self._sock.listen(256)
        
    def _init_client_session(self, sock):
        data = Utils.recv_all_with_length(sock)
        msg = json.loads(data)
        db_name = msg["db_name"]
        version = msg["version"]
        changes = self._version_manager.get_all_changes_for_version(db_name, version)
        for change in changes:
            data = json.dumps(change)
            send_all_with_length(data)
        self._version_manager.add_client_socket(db_name, sock)

    def serve_forever(self):
        if not self._sock:
            self._init_socket()

        while True:
            accepted_socket, address = self._sock.accept()
            #client_id = random.randint(100000, 1000000)
            Logger.info("Accepted a connection from %s. Client id: %d" % (address, client_id))            
            #IdaSyncClient.start_threaded(accepted_socket, client_id)
            try:
                self._init_client_session(accepted_socket)
            except:
                try:
                    accepted_socket.close()
                except: 
                    pass
