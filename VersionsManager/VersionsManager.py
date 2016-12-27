from threading import Lock
from thread import start_new_thread
from struct import pack, unpack
from idasync.Common.Utils import Utils
from socket import *
import json
from idasync.Common.Logger import Logger
from select import select

INIT_FILE_CMD = 1
SERVER_ADDR_NEW_CONNECTIONS = 12552
SERVER_ADDR_CLIENTS = 12553

_g_creation_lock = Lock()
_g_instance = None
#_g_server

class LockedFile(object):
    def __init__(self):
        self.versions = {}
        self.clients = {}
        self._lock = Lock()

    def __enter__(self):
        return self._lock.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._lock.__exit__(exc_type, exc_val, exc_tb)

class VersionsManager(object):
    def __init__(self):
        self._db_lock = Lock()
        self._ida_files = {}
        self._main_thread_client_sock = None
        self._main_thread_server_sock = None

    @classmethod
    def get_instance(cls):
        global _g_creation_lock, _g_instance
        with _g_creation_lock:
            _g_instance = cls()
            
        return _g_instance
        
    def create_client_socket(self, file_name, client_id):
        client_sock = socket()
        client_sock.connect(("localhost", SERVER_ADDR_NEW_CONNECTIONS))

        init_file_cmd = {
            'cmd': INIT_FILE_CMD,
            'client_id': client_id,
            'filename': file_name
        }
        Utils.send_all_with_length(self._main_thread_client_sock, json.dumps(init_file_cmd))
        if Utils.recv_all_with_length(self._main_thread_client_sock)['success']:
            raise Exception("Failed to initialize versions/sock for %s" % file_name)

        return client_sock

        '''
                
                self._locked_files[file_name] = LockedFile()
                
        with self._locked_files[file_name]:
            locked_file = self._locked_files[file_name]
        '''


    @classmethod
    def init_server(cls):
        start_new_thread(cls._server_new_connections, ())
        start_new_thread(cls._server_updates, ())

    @classmethod
    def _server_new_connections(cls):
        cls.get_instance()._server_new_connections_thread()

    @classmethod
    def _server_updates(cls):
        cls.get_instance()._server_updates_thread()

    def _server_new_connections_thread(self):
        sock = socket()
        sock.bind(("localhost", SERVER_ADDR_NEW_CONNECTIONS))
        sock.listen(256)
        while True:
            sock2 = sock.accept()[0]
            data = json.loads(Utils.recv_all_with_length(sock2))
            if data['cmd'] == SERVER_ADDR_NEW_CONNECTIONS:
                with self._db_lock:
                    filename = data['filename']
                    client_id = data['client_id']
                    if filename in self._locked_files:
                        self._locked_files[filename].clients[client_id] = sock2

            else:
                Logger.error("_server_new_connections_thread: Wrong cmd! %s" % str(data['cmd']))

    def _server_updates_thread(self):
        while True:
            sockets = []
            with self._db_lock:
                sockets = map(lambda x: x.clients.values(), self._ida_files.values())
            sockets.append(self._new_connections_sock)
            rdfs, _, _ = select(sockets, [], [])

            for sock in rdfs:
                if sock == self._new_connections_sock:
                    self._new_connections_sock.recv(1)
