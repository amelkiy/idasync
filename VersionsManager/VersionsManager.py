from threading import Lock
from thread import start_new_thread
from idasync.Common.Utils import Utils
from socket import *
from idasync.Common.Logger import Logger
from select import select

SERVER_ADDR_NEW_CONNECTIONS = 12552

_g_creation_lock = Lock()
_g_instance = None


class IdaFile(object):
    def __init__(self):
        self.versions = []  # Version number: update
        self.clients = []   # [sock, sock, sock, ...]


class VersionsManager(object):
    def __init__(self):
        self._db_lock = Lock()
        self._ida_files = {}    # filename: IdaFile
        self._new_connections_sock = None
        self._sock_to_filename = {}     # sock: filename

    @classmethod
    def get_instance(cls):
        global _g_creation_lock, _g_instance
        with _g_creation_lock:
            _g_instance = cls()
            
        return _g_instance
        
    def add_client_socket(self, sock, filename, version):
        with self._db_lock:
            if filename not in self._ida_files:
                new_ida_file = IdaFile()
                new_ida_file.clients.append(sock)
                self._ida_files[filename] = new_ida_file
            else:
                changes = self.get_all_changes_for_version(filename, version)
                for change in changes:
                    Utils.send_all_with_length(sock, change)
                    self._ida_files[filename].clients.append(sock)

            self._sock_to_filename[sock] = filename

    @classmethod
    def init_server(cls):
        start_new_thread(cls._server_updates, ())

    @classmethod
    def _server_updates(cls):
        cls.get_instance()._server_updates_thread()

    def _server_updates_thread(self):
        while True:
            with self._db_lock:
                sockets = map(lambda x: x.clients.values(), self._ida_files.values())
            sockets.append(self._new_connections_sock)
            rdfs, _, _ = select(sockets, [], [])

            with self._db_lock:
                for sock in rdfs:
                    if sock == self._new_connections_sock:
                        self._new_connections_sock.recv(1)
                    else:
                        data = Utils.recv_all_with_length(sock)
                        filename = self._sock_to_filename[sock]
                        ida_file = self._ida_files[filename]
                        ida_file.versions.append(data)
                        for client_sock in ida_file.clients:
                            Utils.send_all_with_length(client_sock, data)
